from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from pinecone import Pinecone, ServerlessSpec
import os
from dotenv import load_dotenv

from utils.embeddings import get_embeddings

load_dotenv()


def normalize(text):
    return text.lower().replace("–", "-").strip()


def ingest_sections(section_files, doc_name):

    print("🚀 Starting ingestion...")

    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    index_name = os.getenv("PINECONE_INDEX")

    # 🔥 IMPORTANT: using bge-small → 384 dim
    DIMENSION = 384

    # ✅ Create index if not exists
    existing_indexes = [i.name for i in pc.list_indexes()]

    if index_name not in existing_indexes:
        print("📦 Creating Pinecone index...")

        pc.create_index(
            name=index_name,
            dimension=DIMENSION,
            metric="cosine",
            spec=ServerlessSpec(
                cloud=os.getenv("PINECONE_CLOUD"),
                region=os.getenv("PINECONE_REGION")
            )
        )

    embeddings = get_embeddings()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=150
    )

    all_docs = []

    for section, path in section_files.items():

        print(f"\n📄 Processing: {section}")

        loader = PyPDFLoader(path)
        docs = loader.load()

        chunks = splitter.split_documents(docs)

        print(f"Chunks created: {len(chunks)}")

        for chunk in chunks:
            chunk.metadata["section"] = normalize(section)
            chunk.metadata["doc_name"] = doc_name

            if "page" not in chunk.metadata or chunk.metadata["page"] is None:
                chunk.metadata["page"] = "unknown"
            else:
                try:
                    chunk.metadata["page"] = int(chunk.metadata["page"])
                except (ValueError, TypeError):
                    chunk.metadata["page"] = "unknown"

        all_docs.extend(chunks)

    print(f"\n🔥 Total chunks: {len(all_docs)}")

    if len(all_docs) == 0:
        raise Exception("❌ No documents to ingest")

    print("📡 Uploading to Pinecone...")

    index = pc.Index(index_name)

    texts = [chunk.page_content for chunk in all_docs]
    print(f"⚡ Generating embeddings for {len(texts)} chunks (batched)...")
    batch_embeddings = embeddings.embed_documents(texts)

    vectors = []
    for i, embedding in enumerate(batch_embeddings):
        chunk = all_docs[i]
        vectors.append({
            "id": f"{doc_name}-{i}",
            "values": embedding,
            "metadata": {
                "text": chunk.page_content,
                "section": chunk.metadata["section"],
                "doc_name": chunk.metadata["doc_name"],
                "page": str(chunk.metadata["page"]),
                "source": chunk.metadata.get("source", ""),
            }
        })

    BATCH_SIZE = 100
    for i in range(0, len(vectors), BATCH_SIZE):
        batch = vectors[i:i + BATCH_SIZE]
        index.upsert(vectors=batch, namespace=doc_name)
        print(f"  Upserted batch {i // BATCH_SIZE + 1}/{(len(vectors) + BATCH_SIZE - 1) // BATCH_SIZE}")

    stats = index.describe_index_stats()
    ns_stats = stats.namespaces.get(doc_name)
    count = ns_stats.vector_count if ns_stats else 0
    print(f"✅ Ingestion SUCCESSFUL — {count} vectors in namespace '{doc_name}'")