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


def map_reduce_risks(docs, llm, batch_size=15):

    results = []

    print(f"⚙️ Running map-reduce on {len(docs)} docs")

    for i in range(0, len(docs), batch_size):
        batch = docs[i:i + batch_size]

        print(f"🔹 Processing batch {i // batch_size + 1}")

        context = "\n\n".join([d.page_content for d in batch])

        prompt = f"""
        Extract ALL risk factors from the text.

        Rules:
        - Return bullet points
        - Do NOT skip any risks
        - Keep original meaning

        {GROUNDING_RULES}

        Text:
        {context}
        """

        res = llm.invoke(prompt).content
        results.append(res)

    final_prompt = f"""
    Combine and deduplicate the following risk factors from the DRHP document.

    {GROUNDING_RULES}

    Batch results:
    {results}

    Return a clean numbered list of ALL risks.
    """

    return llm.invoke(final_prompt).content


def risk_agent(state):

    print("risk agent is running...")

    query = state["query"]
    doc_name = state["doc_name"]

    section = load_section_map(doc_name).get("risk")

    if not section:
        return {**state, "response": "Risk section not found.", "query_type": classify_query_type(query)}

    query_type = classify_query_type(query)
    llm = get_groq()

    if query_type == "full":
        print("🚀 FULL MODE")

        docs = get_all_section_docs(doc_name, section, max_docs=120, query=query)

        if not docs:
            print("  ⚠️ No valid docs after filtering — returning not found")
            return {
                **state,
                "intermediate_results": {
                    **state.get("intermediate_results", {}),
                    "risk": {"answer": "Not found in document.", "sources": []}
                },
                "query_type": query_type
            }

        response = map_reduce_risks(docs, llm)

        sources = extract_sources(docs, max_sources=3)

        print(f"\n📄 Retrieved sources (risk):")
        for s in sources:
            print(f"  Page {s['page']} | {s['section']} | {s['snippet'][:100]}...")

        return {
            **state,
            "intermediate_results": {
                **state.get("intermediate_results", {}),
                "risk": {"answer": response, "sources": sources}
            },
            "query_type": query_type
        }

    elif query_type == "broad":
        print("📊 BROAD MODE")
        docs = retrieve_and_filter(doc_name, section, query, k=20)

    else:
        print("⚡ SPECIFIC MODE")
        docs = retrieve_and_filter(doc_name, section, query, k=5)

    print(f"  Retrieved docs count: {len(docs)}")

    if not docs:
        print("  ⚠️ No valid docs after filtering — returning not found")
        return {
            **state,
            "intermediate_results": {
                **state.get("intermediate_results", {}),
                "risk": {"answer": "Not found in document.", "sources": []}
            },
            "query_type": query_type
        }

    sources = extract_sources(docs, max_sources=3)

    print(f"\n📄 Retrieved sources (risk):")
    for s in sources:
        print(f"  Page {s['page']} | {s['section']} | {s['snippet'][:100]}...")

    context = "\n\n".join([d.page_content for d in docs])

    prompt = f"""
    {GROUNDING_RULES}

    Context:
    {context}

    Question: {query}
    """

    response = llm.invoke(prompt)

    return {
        **state,
        "intermediate_results": {
            **state.get("intermediate_results", {}),
            "risk": {"answer": response.content, "sources": sources}
        },
        "query_type": query_type
    }
