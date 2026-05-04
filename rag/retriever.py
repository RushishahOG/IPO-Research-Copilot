from langchain_pinecone import Pinecone
from utils.embeddings import get_embeddings
import os


def normalize(text):
    return text.lower().replace("–", "-").strip()


NOISE_PATTERNS = [
    "main objects of our company",
    "objects clause",
    "to carry on the business of",
    "incidental or conducive to",
    "main business is to",
    "the objects for which",
]

NOISE_CO_OCCURRENCE = [
    ("internet services", "web hosting"),
    ("portal development", "internet services"),
]

BUSINESS_POSITIVE = {
    "business": 2,
    "products": 2,
    "services": 2,
    "customers": 1,
    "stores": 1,
    "operations": 2,
    "revenue": 2,
    "sales": 1,
    "platform": 1,
    "manufacturing": 1,
    "retail": 2,
}

BUSINESS_NEGATIVE = {
    "objects clause": -3,
    "to carry on": -2,
    "incidental or": -2,
    "main objects": -2,
}


def is_noise_chunk(text):
    text_lower = text.lower()

    for pattern in NOISE_PATTERNS:
        if pattern in text_lower:
            return True

    for pair in NOISE_CO_OCCURRENCE:
        if pair[0] in text_lower and pair[1] in text_lower:
            return True

    return False


def relevance_score(doc):
    text = doc.page_content.lower()
    score = 0

    for term, weight in BUSINESS_POSITIVE.items():
        if term in text:
            score += weight

    for term, weight in BUSINESS_NEGATIVE.items():
        if term in text:
            score += weight

    return score


def filter_noise(docs):
    return [d for d in docs if not is_noise_chunk(d.page_content)]


def rank_by_relevance(docs, k=None):
    scored = sorted(docs, key=relevance_score, reverse=True)
    if k is not None:
        scored = scored[:k]
    return scored


def enrich_query(doc_name, query, section=None):
    parts = [doc_name]

    if section:
        sec_lower = normalize(section)
        if "company" in sec_lower or "about" in sec_lower:
            parts.append("business model services operations what does the company do")
        elif "financial" in sec_lower:
            parts.append("financial data revenue profit margins financial performance")
        elif "risk" in sec_lower:
            parts.append("risk factors risks challenges threats")
        elif "ipo" in sec_lower or "offer" in sec_lower:
            parts.append("issue size price band offer structure use of proceeds")
        elif "legal" in sec_lower:
            parts.append("legal proceedings litigation disputes")
        elif "regulatory" in sec_lower:
            parts.append("regulatory compliance SEBI statutory disclosures")

    parts.append(query)

    return " ".join(parts)


def build_retriever(doc_name, section, k=20, query=None):

    print(f"🔒 Namespace: {doc_name} | Section: {section} | k={k}")

    vectorstore = Pinecone.from_existing_index(
        index_name=os.getenv("PINECONE_INDEX"),
        embedding=get_embeddings(),
        namespace=doc_name
    )

    enriched = enrich_query(doc_name, query or "", section) if query else f"{section} content"

    print(f"  Enriched query: {enriched[:120]}...")

    return vectorstore.as_retriever(
        search_kwargs={
            "k": k,
            "filter": {
                "section": normalize(section),
                "doc_name": doc_name
            }
        }
    ), enriched


def retrieve_and_filter(doc_name, section, query, k=20):

    vectorstore, enriched = build_retriever(doc_name, section, k, query)

    raw_docs = vectorstore.invoke(enriched)

    print(f"  Raw docs retrieved: {len(raw_docs)}")

    validated = [
        d for d in raw_docs
        if normalize(d.metadata.get("section")) == normalize(section)
        and d.metadata.get("doc_name") == doc_name
    ]
    print(f"  After namespace + section validation: {len(validated)}")

    cleaned = filter_noise(validated)
    print(f"  After noise filtering: {len(cleaned)}")

    ranked = rank_by_relevance(cleaned, k=k)
    print(f"  After relevance re-ranking (top {k}): {len(ranked)}")

    if ranked:
        print(f"  Top-ranked doc preview: {ranked[0].page_content[:150]}...")

    return ranked


def get_retriever(doc_name, section, k=20):

    print(f"🔒 Namespace: {doc_name} | Section: {section} | k={k}")

    vectorstore = Pinecone.from_existing_index(
        index_name=os.getenv("PINECONE_INDEX"),
        embedding=get_embeddings(),
        namespace=doc_name
    )

    return vectorstore.as_retriever(
        search_kwargs={
            "k": k,
            "filter": {
                "section": normalize(section),
                "doc_name": doc_name
            }
        }
    )


def get_all_section_docs(doc_name, section, max_docs=120, query=None):

    print(f"🔒 Namespace: {doc_name} | Section: {section} | max_docs={max_docs}")

    vectorstore = Pinecone.from_existing_index(
        index_name=os.getenv("PINECONE_INDEX"),
        embedding=get_embeddings(),
        namespace=doc_name
    )

    enriched = enrich_query(doc_name, query or "", section)

    print(f"  Enriched query: {enriched[:120]}...")

    raw_docs = vectorstore.similarity_search(
        query=enriched,
        k=max_docs
    )

    print(f"  Raw docs retrieved: {len(raw_docs)}")

    filtered_docs = [
        d for d in raw_docs
        if normalize(d.metadata.get("section")) == normalize(section)
        and d.metadata.get("doc_name") == doc_name
    ]

    print(f"  Filtered docs (section + doc_name): {len(filtered_docs)}")

    cleaned = filter_noise(filtered_docs)
    print(f"  After noise filtering: {len(cleaned)}")

    ranked = rank_by_relevance(cleaned, k=max_docs)
    print(f"  After relevance re-ranking: {len(ranked)}")

    if ranked:
        print(f"  Top-ranked doc preview: {ranked[0].page_content[:150]}...")

    return ranked


def extract_sources(docs, max_sources=3):
    sources = []
    seen_pages = set()

    for doc in docs[:max_sources]:
        page = doc.metadata.get("page", "unknown")
        section = doc.metadata.get("section", "unknown")
        snippet = doc.page_content[:200].strip()

        if page != "unknown" and page in seen_pages:
            continue

        if page != "unknown":
            seen_pages.add(page)

        sources.append({
            "page": page,
            "section": section,
            "snippet": snippet
        })

    return sources
