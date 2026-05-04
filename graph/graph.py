from langgraph.graph import StateGraph, END

from graph.state import GraphState
from graph.router import route_query

from agents.risk_agent import risk_agent
from agents.company_agent import company_agent
from agents.financial_agent import financial_agent
from agents.ipo_agent import ipo_agent
from agents.legal_agent import legal_agent
from agents.regulatory_agent import regulatory_agent
from agents.red_flag_agent import red_flag_agent
from agents.scoring_agent import scoring_agent
from agents.synthesis_agent import synthesis_agent


AGENT_MAP = {
    "risk_agent": risk_agent,
    "company_agent": company_agent,
    "financial_agent": financial_agent,
    "ipo_agent": ipo_agent,
    "legal_agent": legal_agent,
    "regulatory_agent": regulatory_agent,
    "red_flag_agent": red_flag_agent,
    "scoring_agent": scoring_agent,
}


def execute_agents(state):

    agents = state.get("agents", [])

    print(f"\n⚡ Executing agents: {agents}")

    for agent_name in agents:
        agent_fn = AGENT_MAP[agent_name]
        state = agent_fn(state)

    return state


def build_graph():

    builder = StateGraph(GraphState)

    builder.add_node("router", route_query)
    builder.add_node("executor", execute_agents)
    builder.add_node("synthesis", synthesis_agent)

    builder.set_entry_point("router")

    builder.add_edge("router", "executor")
    builder.add_edge("executor", "synthesis")
    builder.add_edge("synthesis", END)

    return builder.compile()