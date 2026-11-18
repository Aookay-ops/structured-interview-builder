# Structured Interview Questions Builder (v0.7)

A Streamlit prototype that helps a hiring manager build a **structured, behavioral interview guide** for one opening. Every candidate gets the same questions, in the same order, rated against the same behavioral anchors.

> **Synthetic data only.** The organization, Minds in Motion (MiM), is fictional. The tool does not collect candidate information, score candidates, or make hiring decisions. Exported guides are drafts that need HR or I-O review before use.

- **Live app:** https://structured-interview-builder-ga4yyukgsub7fgxmmp5vhq.streamlit.app/
- **Course:** IOP 563, AI in I-O Psychology, California Baptist University (Milestone 3, Prototype v1)

## What it does (v1 features)

1. **Role library.** Three synthetic MiM roles, each with a summary, key duties, and three competencies with definitions.
2. **Question bank draw.** Draws 5 questions from human-approved questions only (54 in the bank, 18 per role), with at least one question per competency and no repeats within a session.
3. **Behavioral anchors.** Each competency has rating anchors at 1, 3, and 5. Guidance explains that 2 and 4 fall between anchors.
4. **Human review gate.** The user marks each question Draft, Approved, or Rejected. A rejection needs a reason (not job-related, unclear wording, potentially biased wording, duplicate, other). Rejected questions can be swapped for another approved question in the same competency.
5. **Word export with set lock.** Downloads an interviewer guide (.docx) with one question per page: the question, its anchors, a rating line, and space for notes, plus a review log. Exporting locks the set so every candidate for the opening gets the same questions.

## How to use it

1. **Choose a role** (tab 1). Read the duties and competencies, then select the role.
2. **Generate questions** (tab 2). Expand any question to see its anchors.
3. **Review and export** (tab 3). Approve, reject (with a reason), or swap each question. When at least one question is approved and every rejection has a reason, download the guide.

Do not type names, resumes, or any candidate information into the app.

## Run it locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

Requires Python 3.10 or later. No API keys or secrets are needed.

## Files

| File | Purpose |
|---|---|
| `app.py` | The Streamlit app: role selection, question draw, review gate, Word export |
| `roles.json` | Synthetic roles, competencies, anchors, and the question bank with review status |
| `.streamlit/config.toml` | Theme (MiM colors and fonts) |
| `assets/mim-symbol.png` | Logo |
| `requirements.txt` | Python dependencies |

## Data and privacy

- **Entities:** Role (id, title, summary, duties, competencies); Competency (definition, anchors 1/3/5, questions); Question (id, text, status, version added, review note). Session-only items: the current question set, decisions, rejection reasons, and counts.
- **Aggregation:** The app reports only counts (sets generated, swaps, approved and rejected totals, rejection reasons). No user-level tracking.
- **Access:** Public demo app with no login. Only the repository owner can change the bank.
- **Retention and deletion:** Nothing is stored on a server. Session data is cleared when the browser tab closes or a new role is chosen. The exported Word file is stored only where the user saves it.
- **Secrets:** None used. No API keys are in the code, repository, or deployment settings.

## Question bank governance

AI-drafted questions enter `roles.json` with status `pending_review`. Only questions a human reviewer marks `approved` are shown. Review date and reviewer role are recorded on each question.

## Known limits

- Anchors are written by the project owner and have not been tested for inter-rater agreement.
- The bank was reviewed by one person. An independent reviewer has not yet checked it.
- The content linkage between duties, competencies, and questions is based on judgment, not a formal job analysis.
- Some questions assume experience with outside partners or clients (see the Milestone 3 fairness check).
- In a competency-sorting check, three questions (PC-02, FT-02, AP-02) were often matched to the wrong competency and are queued for rewording.

## Version history

- **v0.7** (Nov 2026): Changes from usability testing and peer review. Added an in-app "How this tool works" panel, next-step prompts between tabs, and an 8-line notes area that stays on the same page as its question.

- **v0.6** (Nov 2026): Added guidance that examples can come from any setting, and how to use ratings 2 and 4. Moved the theme into `.streamlit/config.toml`. Added this README.
- **v0.5:** Question bank v3 (54 questions), Word export, set lock, review log.
