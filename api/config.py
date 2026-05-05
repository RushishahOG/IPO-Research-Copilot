import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
SECTIONS_DIR = DATA_DIR / "sections"
METADATA_DIR = DATA_DIR / "metadata"
SECTION_MAPS_DIR = DATA_DIR / "section_maps"

for d in [DATA_DIR, RAW_DIR, SECTIONS_DIR, METADATA_DIR, SECTION_MAPS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

PINECONE_INDEX = os.getenv("PINECONE_INDEX", "drhp-index")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY", "")
PINECONE_CLOUD = os.getenv("PINECONE_CLOUD", "aws")
PINECONE_REGION = os.getenv("PINECONE_REGION", "us-east-1")

MAX_UPLOAD_SIZE_MB = 100
ALLOWED_EXTENSIONS = {".pdf"}
