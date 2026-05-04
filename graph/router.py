from utils.llms import get_groq
from utils.query_utils import classify_query_type

def route_query(state):

    query = state["query"]

    llm = get_groq()

    prompt = f"""
    Classify query into ALL relevant categories:

    - risk
    - company
    - financial
    - ipo
    - legal
    - regulatory
    - red_flag
    - scoring

    RULES:
    - "Should I invest" → financial, risk, scoring
    - "Why profits" → financial, company
    - "services" → company

    Output ONLY comma-separated categories.

    Query: {query}
    """

    decision = llm.invoke(prompt).content.lower().strip()

    labels = [d.strip() for d in decision.split(",")]

    mapping = {
        "risk": "risk_agent",
        "company": "company_agent",
        "financial": "financial_agent",
        "ipo": "ipo_agent",
        "legal": "legal_agent",
        "regulatory": "regulatory_agent",
        "red_flag": "red_flag_agent",
        "scoring": "scoring_agent"
    }

    agents = [mapping[l] for l in labels if l in mapping]

    if not agents:
        agents = ["company_agent"]

    print(f"\n🧠 Routing Decision → {agents}")

    return {
        **state,
        "agents": agents,
        "query_type": classify_query_type(query)
    }