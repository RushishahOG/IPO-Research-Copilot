from utils.llms import get_groq
from rag.retriever import get_retriever, get_all_section_docs, extract_sources, retrieve_and_filter
from utils.section_map import load_section_map
from utils.query_utils import classify_query_type

GROUNDING_RULES = """
STRICT RULES:
- Answer ONLY using the provided context from the DRHP document.
- Do NOT use any external knowledge.
- Do NOT hallucinate or infer beyond what is stated.
- If the information is not found in the context, respond with: "Not found in document."
- Cite page numbers when referencing specific facts.
"""


def ipo_agent(state):

    print("ipo agent running...")

    query = state["query"]
    doc_name = state["doc_name"]

    section = load_section_map(doc_name).get("ipo")

    if not section:
        return {**state, "response": "IPO section not found.", "query_type": classify_query_type(query)}

    query_type = classify_query_type(query)
    docs = retrieve_and_filter(doc_name, section, query, k=10)

    print(f"  Retrieved docs count: {len(docs)}")

    if not docs:
        print("  ⚠️ No valid docs after filtering — returning not found")
        return {
            **state,
            "intermediate_results": {
                **state.get("intermediate_results", {}),
                "ipo": {"answer": "Not found in document.", "sources": []}
            },
            "query_type": query_type
        }

    context = "\n\n".join([d.page_content for d in docs])

    llm = get_groq()

    prompt = f"""
    Extract IPO details:

    - issue size
    - price band
    - use of funds
    - offer structure

    {GROUNDING_RULES}

    Context:
    {context}
    """

    response = llm.invoke(prompt)

    sources = extract_sources(docs, max_sources=3)

    print(f"\n📄 Retrieved sources (ipo):")
    for s in sources:
        print(f"  Page {s['page']} | {s['section']} | {s['snippet'][:100]}...")

    return {
        **state,
        "intermediate_results": {
            **state.get("intermediate_results", {}),
            "ipo": {"answer": response.content, "sources": sources}
        },
        "query_type": query_type
    }
