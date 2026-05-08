from fastapi import APIRouter, HTTPException

from api.models.document import DocumentInfo, DocumentListResponse, DocumentDeleteResponse
# Deferred imports for speed

router = APIRouter(prefix="/documents", tags=["documents"])


@router.get("", response_model=DocumentListResponse)
async def list_documents():
    from api.services.ingestion_service import list_all_metadata
    documents = list_all_metadata()

    return DocumentListResponse(
        documents=[
            DocumentInfo(
                doc_name=d["doc_name"],
                uploaded_at=d["uploaded_at"],
                status=d["status"],
                section_count=d.get("section_count"),
                file_hash=d.get("file_hash"),
            )
            for d in documents
        ]
    )


@router.delete("/{doc_name}", response_model=DocumentDeleteResponse)
async def delete_document_route(doc_name: str):
    doc_name = doc_name.lower().strip()

    try:
        from api.services.ingestion_service import delete_document
        result = delete_document(doc_name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Delete failed: {e}")

    return DocumentDeleteResponse(
        status=result["status"],
        doc_name=result["doc_name"],
    )
