import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

from api.routes import chat, documents, ingest

app = FastAPI(
    title="DRHP RAG Chatbot API",
    description="Multi-document DRHP RAG chatbot with LangGraph multi-agent pipeline",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router)
app.include_router(documents.router)
app.include_router(ingest.router)

@app.get("/")
async def root():
    return {
        "message": "DRHP RAG System Backend Running",
        "docs": "/docs",
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "drhp-rag-api",
    }

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8000)),
    )