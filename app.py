import os
import html

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
    "Latest trends in Generative AI",
    "How do AI agents work?",
]

st.set_page_config(
    page_title="AI Research Agent",
    page_icon="🔎",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ------------------------------------------------------------------
# Styling: light background, colored text, colorful report card
# (all colors are hex codes, easy to change)
# ------------------------------------------------------------------
st.markdown(
    """
<style>
/* ---------- Page background (light) ---------- */
.stApp { background: linear-gradient(135deg, #FFF7ED 0%, #FDF2F8 45%, #EEF2FF 100%); }
[data-testid="stHeader"] { background: transparent; }

/* ---------- Header card (light, dark colored text) ---------- */
.hero {
    background: #FFFFFF;
    border: 2px solid #E9D5FF;
    border-left: 10px solid #EC4899;
    border-radius: 20px;
    padding: 1.6rem 2rem;
    box-shadow: 0 8px 24px rgba(124, 58, 237, 0.10);
    margin-bottom: 1.4rem;
}
.hero-title { font-size: 2.3rem; font-weight: 800; line-height: 1.2; color: #4C1D95; }
.hero-title span { color: #DB2777; }
.hero-sub { font-size: 1.05rem; margin-top: .4rem; color: #374151; }
.chip {
    display: inline-block;
    padding: .28rem .9rem;
    border-radius: 999px;
    margin: .8rem .4rem 0 0;
    font-size: .85rem;
    font-weight: 700;
}
.c1 { background: #EDE9FE; color: #5B21B6; }
.c2 { background: #FCE7F3; color: #9D174D; }
.c3 { background: #FEF3C7; color: #92400E; }
.c4 { background: #DCFCE7; color: #166534; }

/* ---------- Sidebar ---------- */
[data-testid="stSidebar"] { background: linear-gradient(180deg, #EEF2FF 0%, #FDF2F8 100%); }
[data-testid="stSidebar"] h3 { color: #4C1D95; }
.step {
    background: #FFFFFF;
    border-left: 6px solid;
    border-radius: 12px;
    padding: .65rem .9rem;
    margin-bottom: .65rem;
    font-size: .92rem;
    color: #374151;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}
.step b { color: #1F2937; }
.s1 { border-color: #7C3AED; }
.s2 { border-color: #EC4899; }
.s3 { border-color: #F59E0B; }

/* ---------- 100era brand badge (light card, colored text) ---------- */
.brand {
    margin-top: 1.2rem;
    text-align: center;
    padding: .8rem;
    border-radius: 16px;
    background: #FFFFFF;
    border: 2px solid #F9A8D4;
    box-shadow: 0 4px 12px rgba(219, 39, 119, 0.12);
}
.brand-tag { color: #6B7280; font-size: .85rem; font-weight: 600; }
.brand-name { color: #DB2777; font-size: 1.6rem; font-weight: 800; letter-spacing: 1px; }

/* ---------- Text input label ---------- */
.stTextInput label p { color: #4C1D95; font-weight: 700; }

/* ---------- Buttons ---------- */
.st-key-examples button, .st-key-generate button, .st-key-download button {
    width: 100%;
    border-radius: 12px;
    font-weight: 700;
    transition: all .15s ease;
}
.st-key-examples button *, .st-key-generate button *, .st-key-download button * {
    color: inherit !important;
}

/* Example buttons: white -> soft yellow/pink on hover, dark rose text */
.st-key-examples button {
    background: #FFFFFF !important;
    color: #5B21B6 !important;
    border: 2px solid #C4B5FD !important;
}
.st-key-examples button:hover,
.st-key-examples button:focus:not(:active),
.st-key-examples button:active {
    background: linear-gradient(90deg, #FEF3C7, #FCE7F3) !important;
    color: #9D174D !important;
    border-color: #F472B6 !important;
}

/* Generate button */
.st-key-generate button {
    background: linear-gradient(90deg, #7C3AED, #EC4899) !important;
    color: #FFFFFF !important;
    border: none !important;
    padding: .65rem 1rem;
}
.st-key-generate button:hover,
.st-key-generate button:focus:not(:active),
.st-key-generate button:active {
    background: linear-gradient(90deg, #7C3AED, #EC4899) !important;
    color: #FFFFFF !important;
    filter: brightness(1.1);
}

/* Download button */
.st-key-download button {
    background: linear-gradient(90deg, #0D9488, #2563EB) !important;
    color: #FFFFFF !important;
    border: none !important;
    padding: .65rem 1rem;
}
.st-key-download button:hover,
.st-key-download button:focus:not(:active),
.st-key-download button:active {
    background: linear-gradient(90deg, #0D9488, #2563EB) !important;
    color: #FFFFFF !important;
    filter: brightness(1.1);
}

/* ---------- Metric cards ---------- */
[data-testid="stMetric"] {
    background: #FFFFFF;
    border-left: 6px solid #EC4899;
    border-radius: 14px;
    padding: .8rem 1rem;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.07);
}
[data-testid="stMetricLabel"] * { color: #6B21A8 !important; font-weight: 600; }
[data-testid="stMetricValue"] * { color: #DB2777 !important; }

/* ---------- Colorful report card ---------- */
.report-head {
    background: linear-gradient(90deg, #FEF3C7, #FCE7F3, #E0E7FF);
    color: #4C1D95;
    font-weight: 800;
    font-size: 1.05rem;
    padding: .7rem 1rem;
    border-radius: 12px;
    margin-bottom: 1rem;
}
.st-key-report_card {
    background: linear-gradient(180deg, #FFFFFF 0%, #FFFBEB 100%);
    border: 2px solid #C4B5FD;
    border-top: 8px solid #EC4899;
    border-radius: 18px;
    padding: 1.4rem 1.6rem;
    box-shadow: 0 8px 24px rgba(124, 58, 237, 0.12);
}
.st-key-report_card h1 { color: #6D28D9 !important; }
.st-key-report_card h2 {
    color: #DB2777 !important;
    border-bottom: 3px solid #FBCFE8;
    padding-bottom: .25rem;
}
.st-key-report_card h3 { color: #D97706 !important; }
.st-key-report_card p, .st-key-report_card li { color: #1F2937; }
.st-key-report_card strong { color: #4C1D95; }
.st-key-report_card a { color: #2563EB; }
.st-key-report_card li::marker { color: #EC4899; }
.st-key-report_card blockquote { border-left: 5px solid #F59E0B; background: #FEF3C7; }

/* ---------- Footer ---------- */
.footer { text-align: center; color: #6B7280; margin-top: 2.5rem; font-size: .9rem; }
.footer b { color: #DB2777; }
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
        f'<div class="brand"><div class="brand-tag">✨ {BRAND_TAGLINE}</div>'
        f'<div class="brand-name">{BRAND_NAME}</div></div>',
        unsafe_allow_html=True,
    )

# ------------------------------------------------------------------
# Header
# ------------------------------------------------------------------
st.markdown(
    """
<div class="hero">
  <div class="hero-title">🔎 AI <span>Research</span> Agent</div>
  <div class="hero-sub">Type any topic. The agent searches the web and writes a complete report for you.</div>
  <span class="chip c1">🤖 CrewAI</span>
  <span class="chip c2">⚡ Groq · gpt-oss-120b</span>
  <span class="chip c3">🦆 DuckDuckGo</span>
  <span class="chip c4">🎈 Streamlit</span>
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
with st.container(key="examples"):
    example_cols = st.columns(len(EXAMPLE_TOPICS))
    for col, example in zip(example_cols, EXAMPLE_TOPICS):
        col.button(example, on_click=set_topic, args=(example,), key=f"ex_{example}")

with st.container(key="generate"):
    generate_clicked = st.button("🚀 Generate Report", type="primary")

if generate_clicked:
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
    report_topic = st.session_state.get("report_topic", "")
    words = len(report.split())

    st.success(f"✅ Report ready: {report_topic}")

    m1, m2 = st.columns(2)
    m1.metric("📊 Words", words)
    m2.metric("⏱️ Reading time", f"{max(1, round(words / 200))} min")

    tab_report, tab_source = st.tabs(["📄 Report", "📝 Markdown (copy)"])
    with tab_report:
        with st.container(key="report_card"):
            st.markdown(
                f'<div class="report-head">📄 Research Report · {html.escape(report_topic)}</div>',
                unsafe_allow_html=True,
            )
            st.markdown(report)
    with tab_source:
        st.code(report, language="markdown")

    with st.container(key="download"):
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
