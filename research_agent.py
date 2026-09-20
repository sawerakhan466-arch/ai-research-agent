# ---------------------------------------------------------------
# FIX for CrewAI + Groq bug ("property 'cache_breakpoint' is unsupported")
# CrewAI adds an internal 'cache_breakpoint' key to messages and Groq rejects it.
# This code removes that key before the request is sent.
# It must stay ABOVE "from crewai import ..." below.
# ---------------------------------------------------------------
import litellm

_BAD_KEY = "cache_breakpoint"


def _clean_messages(messages):
    if not isinstance(messages, list):
        return messages
    cleaned = []
    for m in messages:
        if isinstance(m, dict) and _BAD_KEY in m:
            m = {k: v for k, v in m.items() if k != _BAD_KEY}
        cleaned.append(m)
    return cleaned


if not getattr(litellm.completion, "_cache_fix", False):
    _original_completion = litellm.completion

    def _patched_completion(*args, **kwargs):
        if "messages" in kwargs:
            kwargs["messages"] = _clean_messages(kwargs["messages"])
        return _original_completion(*args, **kwargs)

    _patched_completion._cache_fix = True
    litellm.completion = _patched_completion
# ---------------------------------------------------------------

from crewai import Agent, Task, Crew, Process, LLM
from tools import search_web

# Extra safety: stop CrewAI from adding the key at all (ignored if not possible)
try:
    import crewai.llms.cache as _crewai_cache

    _crewai_cache.mark_cache_breakpoint = lambda msg, *a, **k: msg
except Exception:
    pass

MODEL_NAME = "groq/openai/gpt-oss-120b"


def run_research(topic: str, api_key: str) -> str:
    """Runs the single research agent and returns the report as text."""

    llm = LLM(
        model=MODEL_NAME,
        api_key=api_key,
        temperature=0.3,
        max_tokens=4000,
    )

    researcher = Agent(
        role="Senior Research Analyst",
        goal="Research topics using web search and write clear, accurate, well-structured reports.",
        backstory=(
            "You are an experienced analyst who searches the web, compares sources, "
            "and writes factual reports. You never invent facts or links."
        ),
        tools=[search_web],
        llm=llm,
        verbose=False,
        allow_delegation=False,
        max_iter=8,  # stops the agent from searching forever
    )

    task = Task(
        description=(
            "Research the topic: {topic}\n\n"
            "Use the DuckDuckGo Search tool 3 to 5 times with different queries. "
            "Then write a report based only on what you found."
        ),
        expected_output=(
            "A markdown report with these sections: "
            "Title, Executive Summary, Key Findings (bullet points), "
            "Detailed Analysis, Conclusion, and Sources (list of URLs used)."
        ),
        agent=researcher,
    )

    crew = Crew(
        agents=[researcher],
        tasks=[task],
        process=Process.sequential,
        verbose=False,
    )

    result = crew.kickoff(inputs={"topic": topic})
    return result.raw
