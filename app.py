"""Structured Interview Questions Builder (v0.4, question bank, mock mode).

Synthetic data only. Outputs are drafts, not validated assessment material.
This tool does not score candidates or make hiring decisions.

Questions come from a competency bank in roles.json. Only human-approved questions
(status "approved") are ever drawn. Theme lives in .streamlit/config.toml.
"""
import json
import random
from collections import Counter
from datetime import datetime
from pathlib import Path

import streamlit as st

HERE = Path(__file__).parent
DATA = json.loads((HERE / "roles.json").read_text(encoding="utf-8"))
ROLES = {r["id"]: r for r in DATA["roles"]}
BANK = DATA["competencies"]
SET_SIZE = 5
STATUSES = ["Draft", "Approved", "Rejected"]
REJECT_REASONS = ["Not job-related", "Unclear wording", "Potentially biased wording", "Duplicate", "Other"]

st.set_page_config(page_title="Structured Interview Builder", page_icon=str(HERE / "assets/mim-symbol.png"),
                   layout="wide")
st.logo(str(HERE / "assets/mim-symbol.png"), size="large")

# ---- Session state (nothing is saved after the tab closes) ----
ss = st.session_state
ss.setdefault("role_id", None)
ss.setdefault("qitems", [])        # current set: dicts with uid, qid, competency, question, status, reason, note
ss.setdefault("seen", {})          # competency -> question ids already shown this session (no repeats)
ss.setdefault("rejected_log", [])  # rejected items that were swapped out, kept for the review log
ss.setdefault("metrics", {"sets": 0, "swaps": 0})
ss.setdefault("swapped_out", Counter())
ss.setdefault("locked", False)
ss.setdefault("uid", 0)


def approved(comp):
    return [q for q in BANK[comp]["questions"] if q["status"] == "approved"]


def new_item(comp, q):
    ss.uid += 1
    ss.seen.setdefault(comp, set()).add(q["id"])
    return {"uid": ss.uid, "qid": q["id"], "competency": comp, "question": q["text"],
            "status": "Draft", "reason": None, "note": ""}


def draw(comp, exclude):
    """One approved question from comp, not in exclude, unseen if possible (cycles once the bank runs out)."""
    pool = [q for q in approved(comp) if q["id"] not in exclude]
    unseen = [q for q in pool if q["id"] not in ss.seen.get(comp, set())]
    if not unseen and pool:  # bank exhausted for this competency: start a new cycle
        ss.seen[comp] = {i for i in exclude}
        unseen = pool
    return random.choice(unseen) if unseen else None


def reset_role():
    ss.qitems, ss.seen, ss.rejected_log = [], {}, []
    ss.metrics, ss.swapped_out, ss.locked = {"sets": 0, "swaps": 0}, Counter(), False


def log_if_rejected(it):
    if it["status"] == "Rejected" and it["reason"]:
        ss.rejected_log.append(dict(it))


def generate_set():
    """Keep approved questions; refill to SET_SIZE so every competency is covered at least once."""
    role = ROLES[ss.role_id]
    keep = [it for it in ss.qitems if it["status"] == "Approved"]
    for it in ss.qitems:
        if it["status"] != "Approved":
            log_if_rejected(it)
            ss.swapped_out[it["qid"]] += 1
    items = list(keep)
    used = {it["qid"] for it in items}
    for comp in role["competencies"]:  # coverage rule
        if not any(it["competency"] == comp for it in items):
            q = draw(comp, used)
            if q:
                items.append(new_item(comp, q)); used.add(q["id"])
    while len(items) < SET_SIZE:  # fill the rest at random
        comps = [c for c in role["competencies"] if any(q["id"] not in used for q in approved(c))]
        if not comps:
            break
        comp = random.choice(comps)
        q = draw(comp, used)
        items.append(new_item(comp, q)); used.add(q["id"])
    order = {c: i for i, c in enumerate(role["competencies"])}
    ss.qitems = sorted(items, key=lambda it: order[it["competency"]])
    ss.metrics["sets"] += 1


def swap(uid):
    i = next(k for k, it in enumerate(ss.qitems) if it["uid"] == uid)
    old = ss.qitems[i]
    q = draw(old["competency"], {it["qid"] for it in ss.qitems})
    if q is None:
        st.toast(f"No other approved questions for {old['competency']} yet.")
        return
    log_if_rejected(old)
    ss.swapped_out[old["qid"]] += 1
    ss.metrics["swaps"] += 1
    ss.qitems[i] = new_item(old["competency"], q)


def lock_set():
    ss.locked = True


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
                f"- **{c}**: {BANK[c]['definition']}" for c in role["competencies"]))

    st.selectbox("Select a role to build an interview guide for",
                 options=list(ROLES), format_func=lambda rid: ROLES[rid]["title"],
                 index=None, placeholder="Choose a role", key="role_id", on_change=reset_role)
    if ss.role_id:
        st.success(f"Selected: {ROLES[ss.role_id]['title']}. Go to step 2 to generate questions.")

role = ROLES.get(ss.role_id)

# ---- Step 2: draw from the bank ----
with tab2:
    if not role:
        st.info("Choose a role in step 1 first.")
    else:
        st.subheader(role["title"])
        bank_size = sum(len(approved(c)) for c in role["competencies"])
        st.write(f"Draws {SET_SIZE} questions from {bank_size} reviewed questions in the bank, "
                 "with at least one per competency.")
        label = "Generate questions" if not ss.qitems else "Generate new set (keeps approved questions)"
        st.button(label, type="primary", on_click=generate_set, disabled=ss.locked)
        if ss.locked:
            st.info("This set is locked because the guide was exported. Every candidate for this "
                    "opening should get the same questions.")
        for it in ss.qitems:
            with st.expander(f"[{it['competency']}] {it['question']}"):
                for level, text in BANK[it["competency"]]["anchors"].items():
                    st.write(f"**{level}**: {text}")

# ---- Step 3: review, swap, export ----
with tab3:
    if not ss.qitems:
        st.info("Generate questions in step 2 first.")
    for n, it in enumerate(ss.qitems, start=1):
        uid = it["uid"]
        it["question"] = st.text_area(f"Question {n} ({it['competency']})", it["question"],
                                      key=f"q_{uid}", disabled=ss.locked)
        c1, c2 = st.columns([4, 1])
        with c1:
            it["status"] = st.radio("Decision", STATUSES, index=STATUSES.index(it["status"]),
                                    horizontal=True, key=f"s_{uid}", disabled=ss.locked)
        with c2:
            st.button("Swap question", key=f"swap_{uid}", on_click=swap, args=(uid,),
                      disabled=ss.locked or it["status"] == "Approved",
                      help="Replace with a different reviewed question for the same competency.")
        if it["status"] == "Rejected":
            it["reason"] = st.selectbox("Reason for rejecting (required)", REJECT_REASONS, index=None,
                                        placeholder="Choose a reason", key=f"r_{uid}", disabled=ss.locked)
            if it["reason"] == "Other":
                it["note"] = st.text_input("Briefly describe the reason (no candidate information)",
                                           key=f"n_{uid}", disabled=ss.locked)
            if not it["reason"]:
                st.error("Choose a reason, or swap this question for another.")
        else:
            it["reason"], it["note"] = None, ""
        st.divider()

    approved_items = [it for it in ss.qitems if it["status"] == "Approved"]
    rejected = [it for it in ss.qitems if it["status"] == "Rejected"] + ss.rejected_log
    missing_reason = [it for it in ss.qitems if it["status"] == "Rejected" and not it["reason"]]
    if approved_items and missing_reason:
        st.warning(f"{len(missing_reason)} rejected question(s) still need a reason before you can export.")
    elif approved_items:
        guide = (f"# Interview Guide: {role['title']}\n\n"
                 f"DRAFT. Requires HR/I-O review before use. Generated {datetime.now():%Y-%m-%d %H:%M}.\n"
                 "Use these same questions, in this order, for every candidate for this opening.\n\n")
        for it in approved_items:
            guide += f"## {it['competency']} ({it['qid']})\n{it['question']}\n\n"
            guide += "\n".join(f"- {k}: {v}" for k, v in BANK[it["competency"]]["anchors"].items()) + "\n\n"
        guide += ("---\n\n## Review log\n\n"
                  f"- Question sets generated: {ss.metrics['sets']}\n- Single-question swaps: {ss.metrics['swaps']}\n")
        if ss.swapped_out:
            guide += "- Swapped out (question id: times): " + ", ".join(
                f"{k}: {v}" for k, v in ss.swapped_out.most_common()) + "\n"
        if rejected:
            guide += "\n**Rejected questions**\n\n"
            for it in rejected:
                why = it["reason"] + (f": {it['note']}" if it["note"] else "")
                guide += f"- [{it['competency']}] ({it['qid']}) {it['question']} | Reason: {why}\n"
        st.download_button("Download interview guide (.md) and lock this set", guide,
                           file_name=f"interview_guide_{role['id']}.md", on_click=lock_set)
        if ss.locked:
            st.button("Unlock to edit", on_click=lambda: ss.update(locked=False),
                      help="Only unlock if no candidates have been interviewed with this set yet.")
    if ss.qitems:
        counts = Counter(it["reason"] for it in rejected if it["reason"])
        reasons = ", ".join(f"{r} {n}" for r, n in counts.items())
        st.caption(f"Approved: {len(approved_items)} · Rejected: {len(rejected)}"
                   f"{f' ({reasons})' if reasons else ''} · In set: {len(ss.qitems)} · "
                   f"Sets generated: {ss.metrics['sets']} · Swaps: {ss.metrics['swaps']}")
