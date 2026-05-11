# DRHP Analyst AI 📄🤖

> Multi-Agent RAG System + Streamlit Frontend for intelligent Draft Red Herring Prospectus (DRHP) analysis

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.136+-009688.svg)](https://fastapi.tiangolo.com/)
[![LangGraph](https://img.shields.io/badge/LangGraph-Multi--Agent-orange.svg)](https://langchain-ai.github.io/langgraph/)
[![Pinecone](https://img.shields.io/badge/Pinecone-VectorDB-purple.svg)](https://www.pinecone.io/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.40+-red.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 🚀 Project Overview

**DRHP Analyst AI** is an intelligent document analysis platform that parses, understands, and answers questions about Draft Red Herring Prospectus (DRHP) filings — the lengthy, legally dense documents companies file when going public via IPO.

### System Architecture

```
                            ┌─────────────┐
                            │  Streamlit   │  ← http://localhost:8501
                            │   Frontend   │
                            └──────┬──────┘
                                   │ REST API
                            ┌──────▼──────┐
                            │   FastAPI    │  ← http://localhost:2706
                            │   Backend    │
                            └──────┬──────┘
                                   │
        ┌──────────────────────────┼──────────────────────────┐
        │                          │                          │
   ┌────▼────┐             ┌───────▼───────┐          ┌──────▼──────┐
   │  Router  │             │   Pinecone    │          │   Agents    │
   │(LangGraph)│             │  Vector DB    │          │(8 Specialists)│
   └────┬────┘             └───────┬───────┘          └──────┬──────┘
        │                          │                          │
        └──────────────────────────┼──────────────────────────┘
                                   │
                            ┌──────▼──────┐
                            │  Synthesis   │
                            │    Agent     │
                            └──────┬──────┘
                                   │
                            ┌──────▼──────┐
                            │   Answer +   │
                            │   Sources    │
                            └─────────────┘
```

---

## 🔥 Features

### Backend
- **🤖 Multi-Agent System** — 8 specialist agents (Risk, Financial, Company, IPO, Legal, Regulatory, Red Flag, Scoring) coordinated via LangGraph
- **🔒 Namespace Isolation** — Each document gets its own Pinecone namespace for safe multi-document queries
- **📖 Evidence-Backed Answers** — Every response includes page numbers, section names, and source snippets
- **🚫 No Hallucination** — Strict grounding with relevance scoring; refuses to answer without sufficient evidence
- **🔍 Subsection Filtering** — Removes legal noise before retrieval
- **🔄 Dynamic Query Routing** — Automatically routes queries to the right specialist agent

### Frontend
- **🏠 Landing Page** — Premium fintech hero section with animated metrics and feature showcase
- **📂 Document Dashboard** — List, search, reingest, and delete documents
- **📤 Upload Page** — Drag-and-drop PDF upload with real-time ingestion progress
- **💬 AI Chat** — ChatGPT-style interface with document selector, suggested prompts, and source citations
- **📈 Analytics** — System metrics, document stats, and query performance charts (Plotly)

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| **Frontend** | Streamlit, Pandas, Plotly, CSS3 (Glassmorphism) |
| **Backend** | FastAPI, Uvicorn |
| **LLM Orchestration** | LangChain, LangGraph |
| **Vector Database** | Pinecone |
| **LLM Providers** | Google Gemini 2.0 Flash, Groq (LLaMA 3.1 8B) |
| **Embeddings** | Sentence Transformers (BAAI/bge-small-en-v1.5) |
| **PDF Processing** | PyMuPDF, pypdf |

---

## 📁 Project Structure

```
backend/
├── api/                      # FastAPI backend
│   ├── main.py               # Server entry point & config
│   ├── config.py             # Environment & path configuration
│   ├── routes/               # API route handlers
│   │   ├── chat.py           # POST /chat
│   │   ├── documents.py      # GET/DELETE /documents
│   │   └── ingest.py         # POST /upload & /reingest
│   ├── services/             # Business logic
│   │   ├── chat_service.py   # Multi-agent pipeline
│   │   ├── ingestion_service.py  # PDF processing
│   │   └── pinecone_service.py   # Vector DB ops
│   └── models/               # Pydantic schemas
│
├── frontend/                 # Streamlit frontend
│   ├── app.py                # Entry point + page routing
│   ├── views/                # Page components
│   │   ├── dashboard.py      # Document management
│   │   ├── upload.py         # PDF upload
│   │   ├── chat.py           # AI chat interface
│   │   └── analytics.py      # System analytics
│   ├── components/           # Reusable UI
│   │   ├── sidebar.py        # Navigation
│   │   ├── source_panel.py   # Evidence citations
│   │   ├── upload_zone.py    # Upload handler
│   │   ├── document_table.py # Document list
│   │   └── health_badge.py   # Backend status
│   ├── services/             # API client
│   │   └── api_client.py     # Centralized HTTP client
│   ├── styles/
│   │   └── main.css          # Dark glassmorphism theme
│   └── utils/
│       ├── constants.py      # App configuration
│       ├── theme.py          # Design tokens
│       ├── helpers.py        # Utility functions
│       └── session.py        # State management
│
├── agents/                   # Specialist AI agents
│   ├── risk_agent.py
│   ├── financial_agent.py
│   ├── company_agent.py
│   ├── ipo_agent.py
│   ├── legal_agent.py
│   ├── regulatory_agent.py
│   ├── red_flag_agent.py
│   ├── scoring_agent.py
│   └── synthesis_agent.py
│
├── graph/                    # LangGraph orchestration
│   ├── graph.py              # State machine
│   ├── router.py             # Query router
│   └── state.py              # Graph state
│
├── rag/                      # Retrieval pipeline
│   ├── ingest.py             # Pinecone ingestion
│   └── retriever.py          # Section-aware search
│
├── preprocessing/
│   └── splitter.py           # DRHP section splitter
│
├── utils/                    # Shared utilities
│   ├── embeddings.py
│   ├── llms.py
│   ├── file_utils.py
│   └── section_map.py
│
├── data/                     # Runtime data
│   ├── raw/                  # Uploaded PDFs
│   ├── metadata/             # Document metadata
│   └── section_maps/         # Section mappings
│
├── app.py                    # CLI entry point
├── requirements.txt
├── .env.example
└── README.md
```

---

## ⚙️ Setup Instructions

### Prerequisites

- Python 3.10+
- API keys for [Pinecone](https://www.pinecone.io/), [Google AI Studio](https://aistudio.google.com/), and [Groq](https://console.groq.com/)

### 1. Clone & Navigate

```bash
git clone https://github.com/your-username/drhp-analyst-ai.git
cd drhp-analyst-ai/backend
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux / macOS
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

Copy `.env.example` to `.env` and fill in your API keys:

```bash
cp .env.example .env   # Linux/macOS
copy .env.example .env # Windows
```

Required variables:
```
GROQ_API_KEY=gsk_your_key_here
GEMINI_API_KEY=AIza_your_key_here
PINECONE_API_KEY=pcsk_your_key_here
PINECONE_INDEX=drhp-index
PINECONE_CLOUD=aws
PINECONE_REGION=us-east-1
PORT=2706
API_BASE_URL=http://localhost:2706
```

### 5. Run the Backend

```bash
# Activate venv first, then:
python -m api.main
```

The API will be available at:
- **Base URL:** `http://localhost:2706`
- **Swagger Docs:** `http://localhost:2706/docs`

### 6. Run the Frontend (new terminal)

```bash
# Make sure venv is activated
streamlit run frontend/app.py
```

The frontend will be available at **`http://localhost:8501`**.

---

## 📥 Upload & Ingest DRHP

### Via Frontend UI
1. Open `http://localhost:8501`
2. Navigate to **Upload**
3. Drag & drop or select a PDF file (max 100 MB)
4. Wait for ingestion to complete

### Via API

```bash
curl -X POST http://localhost:2706/upload \
  -F "file=@your_drhp_document.pdf"
```

### What Happens Internally

1. **PDF Parsing** — Text extraction with page numbers via PyMuPDF
2. **Section Splitting** — Detects DRHP sections (Risk Factors, Financials, etc.)
3. **Noise Filtering** — Removes legal boilerplate
4. **Embedding** — Converts chunks to vectors via Sentence Transformers
5. **Indexing** — Stores in Pinecone with document-specific namespace

---

## 💬 Chat Usage

### Via Frontend UI
1. Open `http://localhost:8501`
2. Navigate to **Chat**
3. Select a document from the sidebar
4. Type your question or click a suggested prompt

### Via API

**Request:**
```bash
curl -X POST http://localhost:2706/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "What are the main risk factors?", "doc_name": "lenskart_drhp"}'
```

**Response:**
```json
{
  "answer": "The company identifies several key risk factors...",
  "sources": [
    {
      "page": 45,
      "section": "Risk Factors",
      "snippet": "The company faces competition..."
    }
  ],
  "agents_used": ["risk_agent", "synthesis_agent"],
  "query_type": "risk",
  "execution_time_ms": 3542.18
}
```

---

## 📡 API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Root health check |
| `GET` | `/health` | Service health status |
| `POST` | `/upload` | Upload & ingest PDF |
| `POST` | `/reingest/{doc_name}` | Re-ingest existing document |
| `GET` | `/documents` | List all documents |
| `DELETE` | `/documents/{doc_name}` | Delete document & namespace |
| `POST` | `/chat` | Ask a question about a document |

Full interactive docs at `http://localhost:2706/docs`.

---

## 🧪 Example Queries

| Query | Agent | Output |
|-------|-------|--------|
| "What does the company do?" | `company_agent` | Business model, products, market |
| "What are the key risks?" | `risk_agent` | Risk factors with page citations |
| "How profitable is it?" | `financial_agent` | Revenue, margins, P&L summary |
| "IPO price band details?" | `ipo_agent` | Price band, lot size, dates |
| "Any outstanding litigation?" | `legal_agent` | Legal proceedings summary |
| "Should I invest?" | Multiple agents | Scoring with pros/cons |

---

## 🧠 Hallucination Prevention

1. **Namespace Isolation** — Each document's vectors are separate
2. **Strict Prompts** — Agents must answer only from provided context
3. **Subsection Filtering** — Legal boilerplate removed before retrieval
4. **Evidence Requirement** — Every claim must cite a page and section

---

## 🚀 Future Improvements

- [ ] DRHP Comparison Engine — Side-by-side IPO analysis
- [ ] Financial Ratio Extraction — P/E, debt-to-equity, ROE
- [ ] PDF Highlighting — Annotated PDF pages with answers
- [x] Frontend UI — Streamlit dashboard + chat interface
- [ ] Batch Processing — Multi-PDF upload
- [ ] Caching Layer — Redis for frequent queries

---

## 📌 Author

Built by **[Rushi Shah](https://github.com/RushishahOG)**

---

<div align="center">
  <strong>⭐ If you find this project useful, consider giving it a star!</strong>
</div>
