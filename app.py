import os

# Turn off CrewAI telemetry (must be set before importing crewai)
os.environ["CREWAI_DISABLE_TELEMETRY"] = "true"
os.environ["OTEL_SDK_DISABLED"] = "true"

import streamlit as st
from research_agent import run_research

st.set_page_config(page_title="AI Research Agent", page_icon="🔎", layout="centered")

st.title("🔎 AI Research Agent")
st.caption("Powered by CrewAI, Groq (gpt-oss-120b) and DuckDuckGo")

# Read the API key from Streamlit Secrets
try:
    api_key = st.secrets["GROQ_API_KEY"]
except Exception:
    st.error("GROQ_API_KEY not found. Add it in your app's Settings → Secrets on Streamlit Cloud.")
    st.stop()

topic = st.text_input("Research topic", placeholder="e.g. Impact of AI on healthcare in Pakistan")

if st.button("Generate Report", type="primary"):
    if not topic.strip():
        st.warning("Please enter a topic first.")
    else:
        with st.spinner("Researching... this can take 30-90 seconds"):
            try:
                report = run_research(topic.strip(), api_key)
                st.session_state["report"] = report
            except Exception as e:
                st.error(f"Something went wrong: {e}")

if "report" in st.session_state:
    st.divider()
    st.markdown(st.session_state["report"])
    st.download_button(
        "Download report (.md)",
        data=st.session_state["report"],
        file_name="research_report.md",
        mime="text/markdown",
    )
