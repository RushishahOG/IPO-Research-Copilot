import os
import json
import shutil
import time
from pathlib import Path

from preprocessing.splitter import split_drhp
from rag.ingest import ingest_sections
from api.config import RAW_DIR, SECTIONS_DIR, METADATA_DIR, SECTION_MAPS_DIR
from api.services.pinecone_service import delete_namespace
from utils.file_utils import get_file_hash


def get_doc_name(pdf_path: str) -> str:
    filename = os.path.basename(pdf_path)
    return filename.replace(".pdf", "").lower().replace(" ", "_")


def normalize(text: str) -> str:
    return text.lower().replace("\u2013", "-").strip()


def build_section_map(sections: list[dict]) -> dict:
    mapping = {}
    for sec in sections:
        title = normalize(sec["title"])
        if "risk" in title:
            mapping["risk"] = title
        elif "about our company" in title:
            mapping["company"] = title
        elif "financial" in title:
            mapping["financial"] = title
        elif "offer" in title:
            mapping["ipo"] = title
        elif "legal" in title:
            mapping["legal"] = title
        elif "regulatory" in title:
            mapping["regulatory"] = title
    return mapping


def save_metadata(doc_name: str, file_hash: str, section_count: int, status: str = "ready") -> None:
    path = METADATA_DIR / f"{doc_name}.json"
    metadata = {
        "file_hash": file_hash,
        "section_count": section_count,
        "status": status,
        "uploaded_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    with open(path, "w") as f:
        json.dump(metadata, f, indent=2)


def load_metadata(doc_name: str) -> dict | None:
    path = METADATA_DIR / f"{doc_name}.json"
    if not path.exists():
        return None
    with open(path, "r") as f:
        return json.load(f)


def list_all_metadata() -> list[dict]:
    documents = []
    if not METADATA_DIR.exists():
        return documents
    for f in METADATA_DIR.iterdir():
        if f.suffix == ".json":
            with open(f, "r") as fh:
                meta = json.load(fh)
            documents.append({
                "doc_name": f.stem,
                "uploaded_at": meta.get("uploaded_at", "unknown"),
                "status": meta.get("status", "ready"),
                "section_count": meta.get("section_count", 0),
                "file_hash": meta.get("file_hash", ""),
            })
    documents.sort(key=lambda x: x.get("uploaded_at", ""), reverse=True)
    return documents


def ingest_document(pdf_path: str, doc_name: str | None = None) -> dict:
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    if doc_name is None:
        doc_name = get_doc_name(pdf_path)

    file_hash = get_file_hash(pdf_path)

    save_metadata(doc_name, file_hash, 0, status="ingesting")

    try:
        sections, section_files = split_drhp(pdf_path)
    except Exception as e:
        save_metadata(doc_name, file_hash, 0, status="failed")
        raise RuntimeError(f"Section splitting failed: {e}") from e

    section_map = build_section_map(sections)
    section_map_path = SECTION_MAPS_DIR / f"{doc_name}.json"
    with open(section_map_path, "w") as f:
        json.dump(section_map, f, indent=2)

    try:
        ingest_sections(section_files, doc_name)
    except Exception as e:
        save_metadata(doc_name, file_hash, 0, status="failed")
        raise RuntimeError(f"Pinecone ingestion failed: {e}") from e

    save_metadata(doc_name, file_hash, len(sections), status="ready")

    return {
        "doc_name": doc_name,
        "status": "ingested",
        "section_count": len(sections),
    }


def reingest_document(doc_name: str) -> dict:
    meta_path = METADATA_DIR / f"{doc_name}.json"
    if not meta_path.exists():
        raise ValueError(f"Document not found: {doc_name}")

    section_map_path = SECTION_MAPS_DIR / f"{doc_name}.json"
    if not section_map_path.exists():
        raise ValueError(f"Section map not found for: {doc_name}")

    save_metadata(doc_name, "", 0, status="reingesting")

    try:
        delete_namespace(doc_name)
    except Exception:
        pass

    try:
        with open(section_map_path, "r") as f:
            section_map = json.load(f)

        section_files = {}
        for section_key, section_title in section_map.items():
            safe_title = section_title.replace(" ", "_").replace("\u2013", "-")
            section_pdf = SECTIONS_DIR / f"{safe_title}.pdf"
            if section_pdf.exists():
                section_files[section_title] = str(section_pdf)

        if not section_files:
            raise FileNotFoundError(f"No section PDFs found for: {doc_name}")

        ingest_sections(section_files, doc_name)

        with open(meta_path, "r") as f:
            old_meta = json.load(f)

        save_metadata(doc_name, old_meta.get("file_hash", ""), len(section_files), status="ready")
    except Exception as e:
        save_metadata(doc_name, "", 0, status="failed")
        raise RuntimeError(f"Re-ingestion failed: {e}") from e

    return {
        "doc_name": doc_name,
        "status": "reingested",
        "section_count": len(section_files),
    }


def delete_document(doc_name: str) -> dict:
    try:
        delete_namespace(doc_name)
    except Exception:
        pass

    meta_path = METADATA_DIR / f"{doc_name}.json"
    if meta_path.exists():
        meta_path.unlink()

    section_map_path = SECTION_MAPS_DIR / f"{doc_name}.json"
    if section_map_path.exists():
        section_map_path.unlink()

    section_map_path_check = SECTION_MAPS_DIR / f"{doc_name}.json"
    if section_map_path_check.exists():
        with open(section_map_path_check, "r") as f:
            section_map = json.load(f)
        for section_title in section_map:
            safe_name = section_title.replace(" ", "_").replace("\u2013", "-")
            section_pdf = SECTIONS_DIR / (safe_name + ".pdf")
            if section_pdf.exists():
                section_pdf.unlink()

    return {"status": "deleted", "doc_name": doc_name}
