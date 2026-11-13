"""Structured Interview Questions Development Tool — v0 (mock mode only).

Synthetic data only. Outputs are drafts, not validated assessment material.
This tool does not score candidates or make hiring decisions.
"""
import streamlit as st

st.set_page_config(page_title="Structured Interview Builder", layout="wide")

# ---- Synthetic sample job (fictional nonprofit) ----
SAMPLE_JOB = {
    "title": "Program Coordinator",
    "duties": "Coordinate community workshops, track participant enrollment, "
              "communicate with partner agencies, and prepare monthly program reports.",
    "competencies": [
        {"name": "Planning & Organizing", "definition": "Schedules tasks and resources to meet deadlines."},
        {"name": "Stakeholder Communication", "definition": "Shares clear, timely information with partners."},
        {"name": "Attention to Detail", "definition": "Produces accurate records and reports."},
    ],
}

# ---- Mock AI output (replaced by a live model call later) ----
def mock_questions(comp):
    n = comp["name"]
    return [
        f"Tell me about a time you had to manage several deadlines related to {n.lower()}. What did you do?",
        f"Describe a situation where your {n.lower()} made a difference to a project's outcome.",
    ]

def mock_anchors(comp):
    return {
        1: "Vague or general answer; no specific actions or results described.",
        3: "Describes a relevant situation and actions; results are partly clear.",
        5: f"Specific situation, clear actions showing {comp['name'].lower()}, and a measurable result.",
    }

# ---- Session state (nothing is saved after the tab closes) ----
ss = st.session_state
ss.setdefault("job", None)
ss.setdefault("items", [])  # list of dicts: competency, question, anchors, status

st.title("Structured Interview Questions Builder")
st.warning("Draft tool, mock mode. Do not enter names, resumes, or any candidate information.")

tab1, tab2, tab3 = st.tabs(["1. Job & competencies", "2. Questions & anchors", "3. Review & export"])

with tab1:
    if st.button("Load sample job"):
        ss.job = SAMPLE_JOB
        ss.items = []
    if ss.job:
        st.subheader(ss.job["title"])
        st.write(ss.job["duties"])
        for c in ss.job["competencies"]:
            st.markdown(f"- **{c['name']}**: {c['definition']}")

with tab2:
    if not ss.job:
        st.info("Load a job in step 1 first.")
    elif st.button("Generate questions and anchors (mock)"):
        ss.items = [
            {"competency": c["name"], "question": q, "anchors": mock_anchors(c), "status": "Draft"}
            for c in ss.job["competencies"] for q in mock_questions(c)
        ]
    for it in ss.items:
        with st.expander(f"[{it['competency']}] {it['question']}"):
            for level, text in it["anchors"].items():
                st.write(f"**{level}** — {text}")

with tab3:
    if not ss.items:
        st.info("Generate questions in step 2 first.")
    for i, it in enumerate(ss.items):
        it["question"] = st.text_area(f"Question {i+1} ({it['competency']})", it["question"], key=f"q{i}")
        it["status"] = st.radio("Decision", ["Draft", "Approved", "Rejected"],
                                index=["Draft", "Approved", "Rejected"].index(it["status"]),
                                horizontal=True, key=f"s{i}")
    approved = [it for it in ss.items if it["status"] == "Approved"]
    if approved:
        guide = f"# Interview Guide: {ss.job['title']}\n\nDRAFT — requires HR/I-O review before use.\n\n"
        for it in approved:
            guide += f"## {it['competency']}\n{it['question']}\n\n"
            guide += "\n".join(f"- {k}: {v}" for k, v in it["anchors"].items()) + "\n\n"
        st.download_button("Download interview guide (.md)", guide, file_name="interview_guide.md")
    st.caption(f"Approved: {len(approved)} · Rejected: "
               f"{sum(it['status'] == 'Rejected' for it in ss.items)} · Total: {len(ss.items)}")
