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

BUSINESS_CONTENT_GUARD = """
BUSINESS CONTENT RULES:
- You must extract ONLY actual business services, operations, and revenue sources.
- Ignore "objects clause" or legal descriptions entirely.
- Ignore generic phrases like "to carry on business of..." or "main objects of the company".
- Do NOT list legal/incidental objects as business services.
- Only include real services provided to paying customers.
- If not clearly present in context → return "Not found in document."
"""


def map_reduce_company(docs, llm, batch_size=15):

    print("company agent running...")

    results = []

    print(f"⚙️ Running company map-reduce on {len(docs)} docs")

    for i in range(0, len(docs), batch_size):
        batch = docs[i:i + batch_size]

        print(f"🔹 Processing batch {i // batch_size + 1}")

        context = "\n\n".join([d.page_content for d in batch])

        prompt = f"""
        Extract key company information.

        Focus on:
        - business model
        - services
        - operations
        - revenue sources

        {GROUNDING_RULES}
        {BUSINESS_CONTENT_GUARD}

        Context:
        {context}
        """

        res = llm.invoke(prompt).content
        results.append(res)

    final_prompt = f"""
    Combine and structure the company insights from the batches.

    {GROUNDING_RULES}
    {BUSINESS_CONTENT_GUARD}

    Batch results:
    {results}

    Return clean structured summary.
    """

    return llm.invoke(final_prompt).content


def _not_found_response(query_type):
    return {
        "answer": "Not found in document.",
        "sources": []
    }


def company_agent(state):

    query = state["query"]
    doc_name = state["doc_name"]

    section = load_section_map(doc_name).get("company")

    if not section:
        return {**state, "response": "Company section not found.", "query_type": classify_query_type(query)}

    query_type = classify_query_type(query)
    llm = get_groq()

    if query_type == "full":
        print("🚀 COMPANY FULL MODE")

        docs = get_all_section_docs(doc_name, section, max_docs=120, query=query)

        if not docs:
            print("  ⚠️ No valid docs after filtering — returning not found")
            return {
                **state,
                "intermediate_results": {
                    **state.get("intermediate_results", {}),
                    "company": _not_found_response(query_type)
                },
                "query_type": query_type
            }

        response = map_reduce_company(docs, llm)

        sources = extract_sources(docs, max_sources=3)

        print(f"\n📄 Retrieved sources (company):")
        for s in sources:
            print(f"  Page {s['page']} | {s['section']} | {s['snippet'][:100]}...")

        return {
            **state,
            "intermediate_results": {
                **state.get("intermediate_results", {}),
                "company": {"answer": response, "sources": sources}
            },
            "query_type": query_type
        }

    elif query_type == "broad":
        print("📊 COMPANY BROAD MODE")
        docs = retrieve_and_filter(doc_name, section, query, k=20)

    else:
        print("⚡ COMPANY SPECIFIC MODE")
        docs = retrieve_and_filter(doc_name, section, query, k=5)

    print(f"  Retrieved docs count: {len(docs)}")

    if not docs:
        print("  ⚠️ No valid docs after filtering — returning not found")
        return {
            **state,
            "intermediate_results": {
                **state.get("intermediate_results", {}),
                "company": _not_found_response(query_type)
            },
            "query_type": query_type
        }

    sources = extract_sources(docs, max_sources=3)

    print(f"\n📄 Retrieved sources (company):")
    for s in sources:
        print(f"  Page {s['page']} | {s['section']} | {s['snippet'][:100]}...")

    context = "\n\n".join([d.page_content for d in docs])

    prompt = f"""
    {GROUNDING_RULES}
    {BUSINESS_CONTENT_GUARD}

    Context:
    {context}

    Question: {query}
    """

    response = llm.invoke(prompt)

    return {
        **state,
        "intermediate_results": {
            **state.get("intermediate_results", {}),
            "company": {"answer": response.content, "sources": sources}
        },
        "query_type": query_type
    }
