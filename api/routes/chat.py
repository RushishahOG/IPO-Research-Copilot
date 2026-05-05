from fastapi import APIRouter, HTTPException

from api.models.chat import ChatRequest, ChatResponse, Source
from api.services.chat_service import chat_with_document
from api.services.pinecone_service import namespace_exists

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest):
    if not request.doc_name or not request.doc_name.strip():
        raise HTTPException(status_code=400, detail="doc_name is required for chat")

    if not namespace_exists(request.doc_name):
        raise HTTPException(status_code=404, detail=f"Document not found: {request.doc_name}")

    try:
        result = chat_with_document(
            query=request.query,
            doc_name=request.doc_name,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat failed: {e}")

    return ChatResponse(
        answer=result["answer"],
        sources=[Source(**s) for s in result["sources"]],
        agents_used=result["agents_used"],
        query_type=result["query_type"],
        execution_time_ms=result["execution_time_ms"],
    )
