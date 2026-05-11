import os
from pathlib import Path

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:2706")

APP_TITLE = "DRHP Analyst AI"
APP_SUBTITLE = "Multi-Agent RAG System for Draft Red Herring Prospectus Analysis"
APP_ICON = "📊"

PAGE_CONFIG = {
    "page_title": APP_TITLE,
    "page_icon": APP_ICON,
    "layout": "wide",
    "initial_sidebar_state": "collapsed",
}

QUERY_TYPES = ["risk", "company", "financial", "ipo", "legal", "regulatory", "red_flag", "scoring"]

QUERY_TYPE_LABELS = {
    "risk": "Risk Analysis",
    "company": "Company Overview",
    "financial": "Financial Analysis",
    "ipo": "IPO Details",
    "legal": "Legal Analysis",
    "regulatory": "Regulatory Analysis",
    "red_flag": "Red Flag Detection",
    "scoring": "Investment Scoring",
}

SUGGESTED_PROMPTS = [
    "What are the key risk factors mentioned in the DRHP?",
    "Give me a company overview and business model",
    "Summarize the financial performance and key metrics",
    "What are the IPO details including price band and lot size?",
    "Analyze legal proceedings and outstanding litigations",
    "What regulatory approvals are required?",
    "Are there any red flags in this document?",
    "Provide an investment score and recommendation",
]

STATUS_COLORS = {
    "healthy": "#00e676",
    "unhealthy": "#ff1744",
    "loading": "#ffd600",
}

MAX_RETRIES = 3
TIMEOUT_SECONDS = 60
