import json
import os


def load_section_map(doc_name):
    path = f"data/section_maps/{doc_name}.json"

    if not os.path.exists(path):
        return {}

    with open(path, "r") as f:
        return json.load(f)