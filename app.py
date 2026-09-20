import os

# Turn off CrewAI telemetry (must be set before importing crewai)
os.environ["CREWAI_DISABLE_TELEMETRY"] = "true"
os.environ["OTEL_SDK_DISABLED"] = "true"

import streamlit as st
from research_agent import run_research

# ------------------------------------------------------------------
# Change these two lines anytime to update the branding
# ------------------------------------------------------------------
BRAND_NAME = "100era"
BRAND_TAGLINE = "Powered by"

EXAMPLE_TOPICS = [
    "Future of AI in healthcare",
    "Renewable energy in Pakistan",
    "How do AI agents work?",
]

st.set_page_config(
    page_title="AI Research Agent",
    page_icon="🔎",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ------------------------------------------------------------------
# Styling (colors, gradient header, cards)
# ------------------------------------------------------------------
st.markdown(
    """
<style>
.stApp { background: linear-gradient(180deg, #FAF5FF 0%, #FFFFFF 45%); }

/* Hero header */
.hero {
    background: linear-gradient(135deg, #7C3AED 0%, #EC4899 55%, #F59E0B 100%);
    padding: 2rem 2.2rem;
    border-radius: 22px;
    color: #FFFFFF;
    box-shadow: 0 10px 30px rgba(124, 58, 237, 0.25);
    margin-bottom: 1.4rem;
}
.hero-title { font-size: 2.3rem; font-weight: 800; line-height: 1.2; color: #FFFFFF; }
.hero-sub { font-size: 1.05rem; margin-top: .4rem; opacity: .95; color: #FFFFFF; }
.chip {
    display: inline-block;
    background: rgba(255, 255, 255, 0.22);
    padding: .25rem .85rem;
    border-radius: 999px;
    margin: .7rem .4rem 0 0;
    font-size: .85rem;
    font-weight: 600;
    color: #FFFFFF;
}

/* Buttons */
.stButton > button, .stDownloadButton > button {
    width: 100%;
    border-radius: 12px;
    font-weight: 600;
    border: 1px solid #DDD6FE;
}
.stButton > button:hover, .stDownloadButton > button:hover {
    border-color: #7C3AED;
    color: #7C3AED;
}
.stButton > button[kind="primary"],
button[data-testid="stBaseButton-primary"] {
    background: linear-gradient(90deg, #7C3AED, #EC4899);
    color: #FFFFFF;
    border: none;
    padding: .6rem 1rem;
}
.stButton > button[kind="primary"]:hover,
button[data-testid="stBaseButton-primary"]:hover {
    color: #FFFFFF;
    filter: brightness(1.08);
}

/* Sidebar */
[data-testid="stSidebar"] { background: linear-gradient(180deg, #F3E8FF 0%, #FCE7F3 100%); }
.step {
    background: #FFFFFF;
    border-left: 6px solid;
    border-radius: 12px;
    padding: .65rem .9rem;
    margin-bottom: .65rem;
    font-size: .92rem;
    color: #1F2937;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}
.s1 { border-color: #7C3AED; }
.s2 { border-color: #EC4899; }
.s3 { border-color: #F59E0B; }

/* Brand badge */
.brand {
    margin-top: 1.2rem;
    text-align: center;
    padding: .7rem;
    border-radius: 14px;
    background: linear-gradient(90deg, #7C3AED, #EC4899);
    color: #FFFFFF;
    font-weight: 600;
    font-size: .95rem;
}
.brand b { font-size: 1.15rem; letter-spacing: .5px; }

.footer { text-align: center; color: #6B7280; margin-top: 2.5rem; font-size: .9rem; }
.footer b { color: #7C3AED; }
</style>
""",
    unsafe_allow_html=True,
)

# ------------------------------------------------------------------
# Sidebar
# ------------------------------------------------------------------
with st.sidebar:
    st.markdown("### ⚙️ How it works")
    st.markdown('<div class="step s1"><b>1. Enter a topic</b><br>Any subject you want researched.</div>', unsafe_allow_html=True)
    st.markdown('<div class="step s2"><b>2. Agent searches</b><br>It searches the web with DuckDuckGo.</div>', unsafe_allow_html=True)
    st.markdown('<div class="step s3"><b>3. Get your report</b><br>Read it here or download it.</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="brand">✨ {BRAND_TAGLINE}<br><b>{BRAND_NAME}</b></div>',
        unsafe_allow_html=True,
    )

# ------------------------------------------------------------------
# Header
# ------------------------------------------------------------------
st.markdown(
    """
<div class="hero">
  <div class="hero-title">🔎 AI Research Agent</div>
  <div class="hero-sub">Type any topic. The agent searches the web and writes a complete report for you.</div>
  <span class="chip">🤖 CrewAI</span>
  <span class="chip">⚡ Groq · gpt-oss-120b</span>
  <span class="chip">🦆 DuckDuckGo</span>
  <span class="chip">🎈 Streamlit</span>
</div>
""",
    unsafe_allow_html=True,
)

# ------------------------------------------------------------------
# API key from Streamlit Secrets
# ------------------------------------------------------------------
try:
    api_key = st.secrets["GROQ_API_KEY"]
except Exception:
    st.error("GROQ_API_KEY not found. Add it in your app's Settings → Secrets on Streamlit Cloud.")
    st.stop()


# ------------------------------------------------------------------
# Input area
# ------------------------------------------------------------------
def set_topic(text):
    st.session_state["topic_input"] = text


topic = st.text_input(
    "📝 Research topic",
    key="topic_input",
    placeholder="e.g. Impact of AI on healthcare in Pakistan",
)

st.caption("💡 Or try an example:")
example_cols = st.columns(len(EXAMPLE_TOPICS))
for col, example in zip(example_cols, EXAMPLE_TOPICS):
    col.button(example, on_click=set_topic, args=(example,), key=f"ex_{example}")

if st.button("🚀 Generate Report", type="primary"):
    if not topic.strip():
        st.warning("Please enter a topic first.")
    else:
        with st.spinner("🔍 Researching the web and writing your report... (30-90 seconds)"):
            try:
                report = run_research(topic.strip(), api_key)
                st.session_state["report"] = report
                st.session_state["report_topic"] = topic.strip()
            except Exception as e:
                st.error(f"Something went wrong: {e}")

# ------------------------------------------------------------------
# Result
# ------------------------------------------------------------------
if "report" in st.session_state:
    report = st.session_state["report"]
    words = len(report.split())

    st.success(f"✅ Report ready: {st.session_state.get('report_topic', '')}")

    m1, m2 = st.columns(2)
    m1.metric("📊 Words", words)
    m2.metric("⏱️ Reading time", f"{max(1, round(words / 200))} min")

    tab_report, tab_source = st.tabs(["📄 Report", "📝 Markdown (copy)"])
    with tab_report:
        with st.container(border=True):
            st.markdown(report)
    with tab_source:
        st.code(report, language="markdown")

    st.download_button(
        "⬇️ Download report (.md)",
        data=report,
        file_name="research_report.md",
        mime="text/markdown",
    )

st.markdown(
    f'<div class="footer">Made with ❤️ using CrewAI &amp; Groq · <b>{BRAND_NAME}</b></div>',
    unsafe_allow_html=True,
)
