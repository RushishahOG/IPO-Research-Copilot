from utils.llms import get_groq
from utils.query_utils import classify_query_type

GROUNDING_RULES = """
STRICT RULES:
- Base your evaluation ONLY on data retrieved from other agents.
- Do NOT use any external knowledge.
- Do NOT hallucinate or invent scores not justified by the DRHP data.
- If insufficient data exists for scoring, respond with: "Not found in document."
"""


def scoring_agent(state):

    print("scoring agent is running...")

    query = state["query"]
    doc_name = state["doc_name"]

    query_type = classify_query_type(query)
    llm = get_groq()

    prompt = f"""
    Evaluate the company on:

    - Risk (1-10)
    - Financial strength (1-10)
    - Governance (1-10)

    Provide:
    - scores
    - reasoning

    {GROUNDING_RULES}
    """

    response = llm.invoke(prompt)

    print(f"\n📄 Retrieved sources (scoring): none (cross-agent analysis)")

    return {
        **state,
        "intermediate_results": {
            **state.get("intermediate_results", {}),
            "scoring": {"answer": response.content, "sources": []}
        },
        "query_type": query_type
    }
