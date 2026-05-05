import os
import shutil
from fastapi import APIRouter, HTTPException, UploadFile, File

from api.models.ingest import UploadResponse, ReingestResponse
from api.config import RAW_DIR, ALLOWED_EXTENSIONS, MAX_UPLOAD_SIZE_MB
from api.services.ingestion_service import ingest_document, reingest_document, get_doc_name

router = APIRouter(tags=["ingest"])


@router.post("/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)):
    filename = file.filename or "unknown.pdf"
    ext = os.path.splitext(filename)[1].lower()

    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Only PDF files are allowed. Got: {ext}",
        )

    doc_name = get_doc_name(filename)

    file_path = RAW_DIR / f"{doc_name}.pdf"

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File save failed: {e}")

    try:
        result = ingest_document(str(file_path), doc_name)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {e}")

    return UploadResponse(
        doc_name=result["doc_name"],
        status=result["status"],
        section_count=result.get("section_count"),
        message=f"Document '{doc_name}' ingested successfully with {result.get('section_count', 0)} sections",
    )


@router.post("/reingest/{doc_name}", response_model=ReingestResponse)
async def reingest_document_route(doc_name: str):
    doc_name = doc_name.lower().strip()

    try:
        result = reingest_document(doc_name)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Re-ingestion failed: {e}")

    return ReingestResponse(
        doc_name=result["doc_name"],
        status=result["status"],
        section_count=result.get("section_count"),
        message=f"Document '{doc_name}' re-ingested successfully",
    )
