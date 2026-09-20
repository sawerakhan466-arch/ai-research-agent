from crewai import Agent, Task, Crew, Process, LLM
from tools import search_web

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
