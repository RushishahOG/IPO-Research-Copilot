from typing import TypedDict, Dict, List

class GraphState(TypedDict):
    query: str
    doc_name: str
    response: str
    intermediate_results: Dict
    agents: List[str]
    query_type: str
    sources: List