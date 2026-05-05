from pydantic import BaseModel, Field
from typing import List, Optional


class Source(BaseModel):
    page: int | str
    section: str
    snippet: str


class ChatRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=2000, examples=["What are the main risk factors?"])
    doc_name: str = Field(..., min_length=1, max_length=100, examples=["lenskart_drhp"])


class ChatResponse(BaseModel):
    answer: str
    sources: List[Source]
    agents_used: List[str]
    query_type: str
    execution_time_ms: float
