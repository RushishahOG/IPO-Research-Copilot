# DRHP Analyst AI 📄🤖

> Multi-Agent RAG System API for intelligent Draft Red Herring Prospectus (DRHP) analysis

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.136+-009688.svg)](https://fastapi.tiangolo.com/)
[![LangGraph](https://img.shields.io/badge/LangGraph-Multi--Agent-orange.svg)](https://langchain-ai.github.io/langgraph/)
[![Pinecone](https://img.shields.io/badge/Pinecone-VectorDB-purple.svg)](https://www.pinecone.io/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 🚀 Project Overview

**DRHP Analyst AI** is an intelligent document analysis system designed to parse, understand, and answer questions about Draft Red Herring Prospectus (DRHP) filings. DRHPs are lengthy, legally dense documents filed by companies going public with an IPO. Extracting actionable insights from them requires understanding financial metrics, risk factors, industry positioning, and legal disclosures buried across hundreds of pages.

### Why This Matters
Traditional keyword search fails on DRHPs because:
- Critical information is scattered across non-contiguous sections
- Legal boilerplate creates massive noise
- Financial tables require structured reasoning
- Context from multiple sections must be synthesized

### Key Innovation
This system combines **multi-agent RAG (Retrieval-Augmented Generation)** with **section-aware retrieval** and **strict grounding** to deliver analyst-grade answers with page-level citations — without hallucination.

---

## 🧠 Architecture

```
User Query
    ↓
┌─────────────┐
│   Router    │ ← Classifies query intent (risk, financial, company, etc.)
└──────┬──────┘
       ↓
┌─────────────────────────────┐
│      Specialist Agents      │
│  ┌───────┐ ┌──────────┐    │
│  │ Risk  │ │ Financial│    │
│  └───────┘ └──────────┘    │
│  ┌───────┐ ┌──────────┐    │
│  │Company│ │  Object  │    │
│  └───────┘ └──────────┘    │
└──────────────┬──────────────┘
               ↓
┌─────────────────────────────┐
│  Section-Aware Retrieval    │
│  (Pinecone + Subsection     │
│   Filtering to remove noise)│
└──────────────┬──────────────┘
               ↓
┌─────────────────────────────┐
│     Scoring & Synthesis     │
│  (Relevance scoring →       │
│   Evidence-backed answer)   │
└──────────────┬──────────────┘
               ↓
         Final Answer
```

### Core Components

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Orchestration** | LangGraph | Multi-agent state machine with conditional routing |
| **Vector Store** | Pinecone | Embeddings with namespace isolation per document |
| **LLMs** | Gemini / Groq | Reasoning, classification, and answer generation |
| **Retrieval** | LangChain + Hybrid Search | Section + subsection-aware semantic search |
| **API** | FastAPI | REST endpoints for upload, query, and document management |

---

## 🔥 Features

- **🤖 Multi-Agent System** — Specialized agents for risk analysis, financial metrics, company overview, and object clause evaluation
- **🔒 Namespace Isolation** — Each document gets its own Pinecone namespace for safe multi-document querying
- **📖 Evidence-Backed Answers** — Every response includes page numbers, section names, and source snippets
- **📤 Upload & Delete** — Full lifecycle management for DRHP PDFs via REST API
- **🚫 No Hallucination** — Strict grounding with relevance scoring; refuses to answer if evidence is insufficient
- **🔍 Subsection Filtering** — Removes legal noise like standard "objects clause" boilerplate before retrieval
- **🔄 Dynamic Query Routing** — Automatically selects the right specialist agent based on query intent

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| **Language** | Python 3.10+ |
| **API Framework** | FastAPI + Uvicorn |
| **LLM Orchestration** | LangChain + LangGraph |
| **Vector Database** | Pinecone |
| **LLM Providers** | Google Gemini, Groq (LLaMA) |
| **Embeddings** | Sentence Transformers |
| **PDF Processing** | PyMuPDF, pypdf |

---

## 📁 Project Structure

```
backend/
├── api/                    # FastAPI application layer
│   ├── main.py             # App entry point & server config
│   ├── config.py           # Environment & path configuration
│   ├── routes/             # API route handlers
│   │   ├── chat.py         # POST /chat endpoint
│   │   ├── documents.py    # GET/DELETE /documents endpoints
│   │   └── ingest.py       # POST /upload & /reingest endpoints
│   ├── services/           # Business logic layer
│   │   ├── chat_service.py # Multi-agent pipeline orchestration
│   │   ├── ingestion_service.py  # PDF processing pipeline
│   │   └── pinecone_service.py   # Vector DB operations
│   └── models/             # Pydantic request/response schemas
│
├── agents/                 # Specialist agent definitions
│   ├── risk_agent.py       # Risk factor analysis
│   ├── financial_agent.py  # Financial metrics extraction
│   ├── company_agent.py    # Company overview & operations
│   └── scoring_agent.py    # Source relevance scoring
│
├── graph/                  # LangGraph workflow definitions
│   └── graph.py            # Agent orchestration state machine
│
├── rag/                    # Retrieval-Augmented Generation
│   └── retriever.py        # Section-aware semantic search
│
├── preprocessing/          # Document processing pipeline
│   ├── splitter.py         # Section & subsection splitting
│   └── cleaner.py          # Noise removal & filtering
│
├── data/                   # Runtime data storage
│   ├── raw/                # Uploaded PDF files
│   ├── metadata/           # Document metadata & section maps
│   └── section_maps/       # Section-to-page mappings
│
├── app.py                  # CLI entry point (non-API mode)
├── requirements.txt        # Python dependencies
└── .env.example            # Environment variable template
```

---

## ⚙️ Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/drhp-analyst-ai.git
cd drhp-analyst-ai/backend
```

### 2. Create Virtual Environment
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file in the `backend/` root:
```env
PINECONE_API_KEY=your_pinecone_api_key
GEMINI_API_KEY=your_gemini_api_key
GROQ_API_KEY=your_groq_api_key
```

> **Note:** Get your API keys from [Pinecone](https://www.pinecone.io/), [Google AI Studio](https://aistudio.google.com/), and [Groq](https://console.groq.com/).

### 5. Run the Server
```bash
python -m api.main
```

The API will be available at:
- **Base URL:** `http://localhost:8000`
- **Swagger Docs:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`

---

## 📥 Upload & Ingest DRHP

### How to Upload
```bash
curl -X POST http://localhost:8000/upload \
  -F "file=@your_drhp_document.pdf"
```

Or use the Swagger UI at `http://localhost:8000/docs`.

### What Happens Internally

1. **PDF Parsing** — Extracts text and preserves page numbers using PyMuPDF
2. **Section Splitting** — Identifies DRHP-specific sections (Risk Factors, Financials, Object of Issue, etc.)
3. **Noise Filtering** — Removes legal boilerplate and standard subsections that dilute retrieval quality
4. **Embedding Generation** — Converts each section chunk into vector embeddings using sentence transformers
5. **Namespace Creation** — Creates a Pinecone namespace named after the document for query isolation
6. **Index Upsert** — Stores vectors with metadata (page, section, subsection, file hash)

---

## 💬 API Usage

### POST `/chat`
Ask a question about an ingested DRHP document.

**Request:**
```json
{
  "query": "What are the main risk factors for this company?",
  "doc_name": "lenskart_drhp"
}
```

**Response:**
```json
{
  "answer": "The company identifies several key risk factors: (1) Intense competition in the eyewear market from both organized and unorganized players... (2) Heavy reliance on retail store expansion as primary growth driver... (3) Regulatory risks related to optical goods pricing...",
  "sources": [
    {
      "page": 45,
      "section": "Risk Factors",
      "snippet": "The company faces competition from both organized retail chains and local optical stores..."
    },
    {
      "page": 47,
      "section": "Risk Factors",
      "snippet": "Our growth strategy is substantially dependent on the success of our retail expansion plans..."
    }
  ],
  "agents_used": ["risk_agent", "scoring_agent", "synthesis_agent"],
  "query_type": "risk",
  "execution_time_ms": 3542.18
}
```

---

### GET `/documents`
List all ingested documents.

**Response:**
```json
{
  "documents": [
    {
      "doc_name": "lenskart_drhp",
      "uploaded_at": "2025-05-01T12:00:00Z",
      "status": "ready",
      "section_count": 12,
      "file_hash": "a1b2c3d4e5f6..."
    },
    {
      "doc_name": "zepto_drhp",
      "uploaded_at": "2025-05-03T14:30:00Z",
      "status": "ready",
      "section_count": 15,
      "file_hash": "f6e5d4c3b2a1..."
    }
  ]
}
```

---

### POST `/upload`
Upload and ingest a new DRHP PDF.

**Request:** `multipart/form-data` with field `file` (PDF, max 100MB)

**Response:**
```json
{
  "doc_name": "zepto_drhp",
  "status": "ingested",
  "section_count": 15,
  "message": "Document 'zepto_drhp' ingested successfully with 15 sections"
}
```

---

### DELETE `/documents/{doc_name}`
Delete a document and its Pinecone namespace.

**Response:**
```json
{
  "status": "deleted",
  "doc_name": "zepto_drhp"
}
```

---

## 🧪 Example Queries

| Query | Agent Used | Expected Output |
|-------|------------|-----------------|
| _"What does the company do?"_ | `company_agent` | Business model, product lines, target market |
| _"What are the key risks?"_ | `risk_agent` | Enumerated risk factors with page citations |
| _"How profitable is the company?"_ | `financial_agent` | Revenue trends, margins, loss/profit status |
| _"What will the IPO funds be used for?"_ | `object_agent` | Object of issue breakdown with percentages |
| _"Should I invest in this company?"_ | Multiple agents | Balanced view with pros, cons, and grounded caveats |

---

## 🧠 How It Avoids Hallucination

### 1. Namespace Locking
Every document gets an isolated Pinecone namespace. Queries **only** retrieve from the specified document's vectors — no cross-contamination between DRHPs.

### 2. Strict System Prompts
Agents are prompted with explicit instructions:
> _"Answer only using the provided context. If the context does not contain sufficient information, state that clearly. Do not invent or assume facts."_

### 3. Subsection Filtering
Standard legal boilerplate (e.g., generic "objects clause" language) is filtered out during ingestion so retrieval doesn't surface irrelevant noise.

### 4. Evidence Requirement
The `scoring_agent` evaluates each retrieved chunk for relevance before synthesis. Sources with low relevance scores are discarded. Every claim in the final answer must be backed by a cited page and section.

---

## 🚀 Future Improvements

- [ ] **DRHP Comparison Engine** — Side-by-side analysis of multiple IPO filings
- [ ] **Financial Ratio Extraction** — Automated computation of P/E, debt-to-equity, ROE, etc.
- [ ] **PDF Highlighting** — Return highlighted PDF pages alongside answers
- [ ] **Frontend UI** — Interactive chat interface with document management dashboard
- [ ] **Batch Processing** — Upload and ingest multiple DRHPs simultaneously
- [ ] **Caching Layer** — Redis cache for frequently asked questions

---

## 📌 Author / Credits

Built by **[Rushi Shah](https://github.com/your-username)**

> This project was developed as part of a portfolio showcase for AI/ML engineering roles. Contributions and feedback are welcome!

---

<div align="center">

**⭐ If you found this project useful, consider giving it a star!**

</div>
