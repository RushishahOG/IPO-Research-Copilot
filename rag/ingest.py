from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_pinecone import Pinecone as LC_Pinecone

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

    LC_Pinecone.from_documents(
        documents=all_docs,
        embedding=embeddings,
        index_name=index_name,
        namespace=doc_name
    )

    print("✅ Ingestion SUCCESSFUL")