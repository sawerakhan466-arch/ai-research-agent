# 🔎 AI Research Agent

A single-agent research app. Enter a topic and the agent searches the web (DuckDuckGo) and writes a structured report.

**Stack:** CrewAI · Groq (`openai/gpt-oss-120b`) · DuckDuckGo (`ddgs`) · Streamlit

## Deploy on Streamlit Community Cloud
1. Push this repo to GitHub.
2. On share.streamlit.io, create an app and set the main file to `app.py`.
3. In **Advanced settings**, choose **Python 3.12** and add this to **Secrets**:
   ```toml
   GROQ_API_KEY = "your_groq_api_key"
   ```
4. Deploy.

## Files
- `app.py` – Streamlit UI
- `research_agent.py` – CrewAI agent, task and crew
- `tools.py` – DuckDuckGo search tool
- `requirements.txt` – dependencies
