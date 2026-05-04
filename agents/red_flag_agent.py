from utils.llms import get_groq
from utils.query_utils import classify_query_type

GROUNDING_RULES = """
STRICT RULES:
- Base your analysis ONLY on data retrieved from other agents.
- Do NOT use any external knowledge.
- Do NOT hallucinate or invent concerns not present in the DRHP.
- If no red flags can be identified from the provided data, respond with: "Not found in document."
"""


def red_flag_agent(state):

    print("red flag agent is running...")

    query = state["query"]
    doc_name = state["doc_name"]

    query_type = classify_query_type(query)
    llm = get_groq()

    prompt = f"""
    Identify RED FLAGS from the DRHP based on:

    - risks
    - financial weakness
    - legal issues

    Provide critical concerns only.

    {GROUNDING_RULES}
    """

    response = llm.invoke(prompt)

    print(f"\n📄 Retrieved sources (red_flag): none (cross-agent analysis)")

    return {
        **state,
        "intermediate_results": {
            **state.get("intermediate_results", {}),
            "red_flag": {"answer": response.content, "sources": []}
        },
        "query_type": query_type
    }
