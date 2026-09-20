# ---------------------------------------------------------------
# FIXES for CrewAI + Groq (keep this block ABOVE "from crewai import ...")
#  1. Removes the internal 'cache_breakpoint' key that Groq rejects.
#  2. If Groq says "rate limit reached" (free tier = 8000 tokens/minute),
#     it waits a few seconds and retries that one call automatically.
# ---------------------------------------------------------------
import re
import time

import litellm

_BAD_KEY = "cache_breakpoint"
_MAX_TRIES = 6


def _clean_messages(messages):
    if not isinstance(messages, list):
        return messages
    cleaned = []
    for m in messages:
        if isinstance(m, dict) and _BAD_KEY in m:
            m = {k: v for k, v in m.items() if k != _BAD_KEY}
        cleaned.append(m)
    return cleaned


def _wait_seconds(error_text):
    """Reads 'Please try again in 9.3s' or '1m12.5s' from Groq's message."""
    m = re.search(r"try again in (?:(\d+)m)?\s*([\d.]+)s", error_text)
    if not m:
        return 15
    return int(m.group(1) or 0) * 60 + float(m.group(2)) + 2


if not getattr(litellm.completion, "_cache_fix", False):
    _original_completion = litellm.completion

    def _patched_completion(*args, **kwargs):
        if "messages" in kwargs:
            kwargs["messages"] = _clean_messages(kwargs["messages"])
        for attempt in range(1, _MAX_TRIES + 1):
            try:
                return _original_completion(*args, **kwargs)
            except litellm.RateLimitError as e:
                if attempt == _MAX_TRIES:
                    raise
                time.sleep(min(_wait_seconds(str(e)), 60))

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


def _run_once(topic: str, api_key: str) -> str:
    """Runs the single research agent one time and returns the report as text."""

    llm = LLM(
        model=MODEL_NAME,
        api_key=api_key,
        temperature=0.3,
        max_tokens=3000,  # smaller = fits Groq's free per-minute limit better
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
        max_iter=6,  # stops the agent from searching forever
    )

    task = Task(
        description=(
            "Research the topic: {topic}\n\n"
            "Use the DuckDuckGo Search tool 2 to 3 times with different queries. "
            "Then write a report of about 600 to 800 words based only on what you found."
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


def run_research(topic: str, api_key: str) -> str:
    """Runs the agent. If Groq's free per-minute limit is hit, waits and tries again."""
    tries = 3
    for attempt in range(1, tries + 1):
        try:
            return _run_once(topic, api_key)
        except Exception as e:
            low = f"{type(e).__name__} {e}".lower()
            is_rate_limit = "rate limit" in low or "ratelimit" in low or "rate_limit" in low
            if is_rate_limit and attempt < tries:
                # wait at least 30 seconds so Groq's 1-minute window can clear
                time.sleep(min(max(_wait_seconds(str(e)), 30), 90))
                continue
            raise
