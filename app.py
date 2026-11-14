"""Structured Interview Questions Builder (v0.3, mock mode only).

Synthetic data only. Outputs are drafts, not validated assessment material.
This tool does not score candidates or make hiring decisions.
Roles, questions and anchors live in roles.json; theme lives in .streamlit/config.toml.
"""
import json
from pathlib import Path

import streamlit as st

HERE = Path(__file__).parent
DATA = json.loads((HERE / "roles.json").read_text(encoding="utf-8"))
ROLES = {r["id"]: r for r in DATA["roles"]}
STATUSES = ["Draft", "Approved", "Rejected"]

st.set_page_config(page_title="Structured Interview Builder", page_icon=str(HERE / "assets/mim-symbol.png"),
                   layout="wide")
st.logo(str(HERE / "assets/mim-symbol.png"), size="large")

# ---- Session state (nothing is saved after the tab closes) ----
ss = st.session_state
ss.setdefault("role_id", None)
ss.setdefault("qitems", [])  # list of dicts: competency, question, anchors, status
ss.setdefault("gen", 0)      # bumps on every new set so old widget values don't carry over


def reset_items():
    ss.qitems = []
    ss.gen += 1


def generate_mock(role):
    """Mock AI output: returns the role's synthetic question set. A live model call replaces this later."""
    ss.qitems = [
        {"competency": c["name"], "question": q, "anchors": c["anchors"], "status": "Draft"}
        for c in role["competencies"] for q in c["questions"]
    ]
    ss.gen += 1


st.title("Structured Interview Questions Builder")
st.caption(DATA["organization"])
st.warning("Draft tool, mock mode. Do not enter names, resumes, or any candidate information.")

tab1, tab2, tab3 = st.tabs(["1. Choose a role", "2. Questions & anchors", "3. Review & export"])

# ---- Step 1: role descriptions + selection ----
with tab1:
    st.subheader("Open roles")
    cols = st.columns(len(ROLES))
    for col, role in zip(cols, ROLES.values()):
        with col, st.container(border=True):
            st.markdown(f"### {role['title']}")
            st.write(role["summary"])
            st.markdown("**Key duties**\n" + "\n".join(f"- {d}" for d in role["duties"]))
            st.markdown("**Competencies**\n" + "\n".join(
                f"- **{c['name']}**: {c['definition']}" for c in role["competencies"]))

    st.selectbox("Select a role to build an interview guide for",
                 options=list(ROLES), format_func=lambda rid: ROLES[rid]["title"],
                 index=None, placeholder="Choose a role", key="role_id", on_change=reset_items)
    if ss.role_id:
        st.success(f"Selected: {ROLES[ss.role_id]['title']}. Go to step 2 to generate questions.")

role = ROLES.get(ss.role_id)

# ---- Step 2: generate ----
with tab2:
    if not role:
        st.info("Choose a role in step 1 first.")
    else:
        st.subheader(role["title"])
        if st.button("Generate questions and anchors (mock)", type="primary"):
            generate_mock(role)
        for it in ss.qitems:
            with st.expander(f"[{it['competency']}] {it['question']}"):
                for level, text in it["anchors"].items():
                    st.write(f"**{level}**: {text}")

# ---- Step 3: review + export ----
with tab3:
    if not ss.qitems:
        st.info("Generate questions in step 2 first.")
    for i, it in enumerate(ss.qitems):
        it["question"] = st.text_area(f"Question {i+1} ({it['competency']})", it["question"],
                                      key=f"q_{ss.gen}_{i}")
        it["status"] = st.radio("Decision", STATUSES, index=STATUSES.index(it["status"]),
                                horizontal=True, key=f"s_{ss.gen}_{i}")
    approved = [it for it in ss.qitems if it["status"] == "Approved"]
    if approved:
        guide = f"# Interview Guide: {role['title']}\n\nDRAFT. Requires HR/I-O review before use.\n\n"
        for it in approved:
            guide += f"## {it['competency']}\n{it['question']}\n\n"
            guide += "\n".join(f"- {k}: {v}" for k, v in it["anchors"].items()) + "\n\n"
        st.download_button("Download interview guide (.md)", guide,
                           file_name=f"interview_guide_{role['id']}.md")
    if ss.qitems:
        st.caption(f"Approved: {len(approved)} · Rejected: "
                   f"{sum(it['status'] == 'Rejected' for it in ss.qitems)} · Total: {len(ss.qitems)}")
