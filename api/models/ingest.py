from pydantic import BaseModel
from typing import Optional


class UploadResponse(BaseModel):
    doc_name: str
    status: str
    section_count: Optional[int] = None
    message: Optional[str] = None


class ReingestResponse(BaseModel):
    doc_name: str
    status: str
    section_count: Optional[int] = None
    message: Optional[str] = None


class ErrorResponse(BaseModel):
    detail: str
