import time
from graph.graph import build_graph
from api.services.pinecone_service import namespace_exists


def chat_with_document(query: str, doc_name: str) -> dict:
    if not namespace_exists(doc_name):
        raise ValueError(f"Document not found: {doc_name}")

    start_time = time.time()

    graph = build_graph()

    result = graph.invoke({
        "query": query,
        "doc_name": doc_name,
    })

    elapsed_ms = round((time.time() - start_time) * 1000, 2)

    answer = result.get("response", "No answer generated.")
    sources = result.get("sources", [])
    agents = result.get("agents", [])
    query_type = result.get("query_type", "specific")

    formatted_sources = []
    for src in sources:
        formatted_sources.append({
            "page": src.get("page", "unknown"),
            "section": src.get("section", "unknown"),
            "snippet": src.get("snippet", "")[:200],
        })

    return {
        "answer": answer,
        "sources": formatted_sources,
        "agents_used": agents,
        "query_type": query_type,
        "execution_time_ms": elapsed_ms,
    }
