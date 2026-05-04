import os
import json
from preprocessing.splitter import split_drhp
from rag.ingest import ingest_sections
from graph.graph import build_graph
from utils.file_utils import get_file_hash

DATA_DIR = "data"


def normalize(text):
    return text.lower().replace("–", "-").strip()


def build_section_map(sections):
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

def get_doc_name(pdf_path):
    filename = os.path.basename(pdf_path)
    return filename.replace(".pdf", "").lower()


def get_metadata_path(doc_name):
    return f"data/metadata/{doc_name}.json"


def get_section_map_path(doc_name):
    return f"data/section_maps/{doc_name}.json"


def should_ingest(pdf_path, doc_name):
    current_hash = get_file_hash(pdf_path)
    metadata_path = get_metadata_path(doc_name)

    if not os.path.exists(metadata_path):
        return True, current_hash

    with open(metadata_path, "r") as f:
        metadata = json.load(f)

    if metadata.get("file_hash") != current_hash:
        return True, current_hash

    return False, current_hash


def save_metadata(doc_name, file_hash):
    path = get_metadata_path(doc_name)

    os.makedirs(os.path.dirname(path), exist_ok=True)

    with open(path, "w") as f:
        json.dump({"file_hash": file_hash}, f)


def save_section_map(doc_name, section_map):
    path = get_section_map_path(doc_name)

    os.makedirs(os.path.dirname(path), exist_ok=True)

    with open(path, "w") as f:
        json.dump(section_map, f, indent=2)


def setup_pipeline(pdf_path):

    doc_name = get_doc_name(pdf_path)

    needs_ingestion, file_hash = should_ingest(pdf_path, doc_name)

    if not needs_ingestion:
        print(f"✅ {doc_name} already ingested")
        return doc_name

    print(f"🔄 Processing {doc_name}")

    sections, section_files = split_drhp(pdf_path)

    section_map = build_section_map(sections)
    save_section_map(doc_name, section_map)

    ingest_sections(section_files, doc_name)

    save_metadata(doc_name, file_hash)

    return doc_name


def run_chat(doc_name):

    graph = build_graph()

    while True:
        query = input("\nAsk your DRHP question: ")

        result = graph.invoke({
            "query": query,
            "doc_name": doc_name
        })

        print("\nAnswer:\n", result["response"])

        sources = result.get("sources", [])
        if sources:
            print("\n📎 Evidence Details:")
            for s in sources:
                page = s.get("page", "unknown")
                section = s.get("section", "unknown")
                snippet = s.get("snippet", "")[:150]
                if page != "unknown":
                    print(f"  [{section}] Page {page}: {snippet}...")
                else:
                    print(f"  [{section}]: {snippet}...")


if __name__ == "__main__":

    pdf_path = input("Enter DRHP PDF path: ")

    doc_name = setup_pipeline(pdf_path)

    run_chat(doc_name)