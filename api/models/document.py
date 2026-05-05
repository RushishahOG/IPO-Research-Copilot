from pydantic import BaseModel
from typing import List, Optional


class DocumentInfo(BaseModel):
    doc_name: str
    uploaded_at: str
    status: str
    section_count: Optional[int] = None
    file_hash: Optional[str] = None


class DocumentListResponse(BaseModel):
    documents: List[DocumentInfo]


class DocumentDeleteResponse(BaseModel):
    status: str
    doc_name: str
