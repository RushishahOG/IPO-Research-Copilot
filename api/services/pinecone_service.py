import os
from pinecone import Pinecone
from api.config import PINECONE_INDEX, PINECONE_API_KEY


def get_pinecone_client() -> Pinecone:
    return Pinecone(api_key=PINECONE_API_KEY)


def get_all_namespaces() -> list[str]:
    pc = get_pinecone_client()
    index = pc.Index(PINECONE_INDEX)
    stats = index.describe_index_stats()
    namespaces = list(stats.namespaces.keys())
    return namespaces


def namespace_exists(doc_name: str) -> bool:
    pc = get_pinecone_client()
    index = pc.Index(PINECONE_INDEX)
    stats = index.describe_index_stats()
    return doc_name in stats.namespaces


def delete_namespace(doc_name: str) -> None:
    pc = get_pinecone_client()
    index = pc.Index(PINECONE_INDEX)
    index.delete(delete_all=True, namespace=doc_name)


def get_namespace_stats(doc_name: str) -> dict:
    pc = get_pinecone_client()
    index = pc.Index(PINECONE_INDEX)
    stats = index.describe_index_stats()
    ns = stats.namespaces.get(doc_name)
    if ns is None:
        return {"vector_count": 0}
    return {"vector_count": ns.vector_count}
