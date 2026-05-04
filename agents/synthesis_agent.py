from utils.llms import get_groq

SYNTHESIS_GUARD = """
STRICT SYNTHESIS RULES:
- Use ONLY the agent outputs and supporting evidence provided below.
- Do NOT add any information not present in the agent outputs.
- Do NOT hallucinate, infer, or use external knowledge.
- If a claim cannot be supported by the provided evidence, state: "Not found in document."
- Avoid inference beyond what the context explicitly states.
- Cite page numbers when referencing facts.
"""


def extract_answer(value):
    if isinstance(value, dict):
        return value.get("answer", str(value))
    return str(value)


def collect_sources(insights):
    all_sources = []
    seen_pages = set()

    for agent_name, value in insights.items():
        if isinstance(value, dict):
            sources = value.get("sources", [])
        else:
            continue

        for src in sources:
            page = src.get("page", "unknown")

            if page != "unknown" and page in seen_pages:
                continue

            if page != "unknown":
                seen_pages.add(page)

            all_sources.append({
                "page": page,
                "section": src.get("section", "unknown"),
                "snippet": src.get("snippet", "")[:200]
            })

    return all_sources


def format_sources_display(sources):
    lines = []
    for src in sources:
        page = src["page"]
        section = src["section"]
        if page != "unknown":
            lines.append(f"  {section}, Page {page}")
        else:
            lines.append(f"  {section}")
    return "\n".join(lines)


def synthesis_agent(state):

    llm = get_groq()

    insights = state.get("intermediate_results", {})
    query = state.get("query")
    query_type = state.get("query_type", "specific")

    print("\n📊 Intermediate Results:")
    for k, v in insights.items():
        answer = extract_answer(v)
        print(f"\n--- {k.upper()} ---\n{answer[:200]}...")

    all_sources = collect_sources(insights)

    print(f"\n📄 Final selected sources ({len(all_sources)} total):")
    for s in all_sources:
        print(f"  Page {s['page']} | {s['section']} | {s['snippet'][:80]}...")

    sources_summary = []
    for src in all_sources:
        page = src["page"]
        section = src["section"]
        snippet = src["snippet"][:150]
        if page != "unknown":
            sources_summary.append(f"- Section: {section}, Page: {page}, Snippet: {snippet}")
        else:
            sources_summary.append(f"- Section: {section}, Snippet: {snippet}")

    sources_text = "\n".join(sources_summary) if sources_summary else "No source evidence available."

    insights_text = {}
    for k, v in insights.items():
        insights_text[k] = extract_answer(v)

    if query_type == "specific":

        prompt = f"""
        Answer directly using ONLY the provided agent outputs and supporting evidence.

        {SYNTHESIS_GUARD}

        Agent Outputs:
        {insights_text}

        Supporting Evidence:
        {sources_text}

        Question: {query}
        """

    elif query_type == "broad":

        prompt = f"""
        Provide a structured explanation using ONLY the provided agent outputs and supporting evidence.

        {SYNTHESIS_GUARD}

        Agent Outputs:
        {insights_text}

        Supporting Evidence:
        {sources_text}

        Question: {query}
        """

    else:

        prompt = f"""
        You are a financial analyst reviewing a DRHP document.

        IMPORTANT:
        - This is NOT personal advice.
        - Use ONLY the agent outputs and evidence provided.
        - DO NOT refuse to answer.

        {SYNTHESIS_GUARD}

        Provide:

        - Key drivers
        - Financial health
        - Risk level
        - Recommendation (Strong / Moderate / Weak)

        Agent Outputs:
        {insights_text}

        Supporting Evidence:
        {sources_text}
        """

    response = llm.invoke(prompt)

    print("🧩 Synthesizing final answer...")

    sources_display = format_sources_display(all_sources)

    if sources_display:
        final_output = f"{response.content}\n\nSources:\n{sources_display}"
    else:
        final_output = response.content

    return {
        **state,
        "response": final_output,
        "sources": all_sources
    }
