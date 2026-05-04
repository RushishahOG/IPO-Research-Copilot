def classify_query_type(query: str):

    q = query.lower()

    if any(k in q for k in ["all", "list all", "complete", "entire"]):
        return "full"

    elif any(k in q for k in ["summarize", "overview", "explain"]):
        return "broad"

    return "specific"