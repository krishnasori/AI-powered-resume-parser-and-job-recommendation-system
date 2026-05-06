"""
app.py
AI Resume Intelligence System.
"""

import os
import json
import streamlit as st
import pdfplumber
import docx
import plotly.graph_objects as go
from dotenv import load_dotenv

load_dotenv()

from skills_engine import (
    SKILL_ENGINE_VERSION,
    extract_skills,
    clean_skill_name,
    get_career_paths,
    predict_role,
)
from job_fetcher import fetch_adzuna, fetch_indeed, score_jobs
from database import save_scan, get_history, clear_history


GEMINI_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_OK = False

try:
    from google import genai
    _gem = genai.Client(api_key=GEMINI_KEY)
    GEMINI_OK = True
except Exception:
    pass


def gemini_generate(prompt: str) -> str:
    if not GEMINI_OK:
        return "Gemini unavailable. Check GEMINI_API_KEY in .env and run: pip install google-genai"

    try:
        return _gem.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        ).text
    except Exception as e:
        return f"Gemini error: {e}"


def gen_cover_letter(skills, title):
    return gemini_generate(
        f"Write a professional cover letter body, 3 short paragraphs, for a fresher "
        f"applying for {title}. Their skills: {', '.join(list(skills)[:15])}. "
        f"No placeholder text. Be confident and role-specific."
    )


def gen_gap_advice(missing, title):
    return gemini_generate(
        f"A fresher applying for {title} is missing: {', '.join(list(missing)[:8])}. "
        f"Give 3 numbered actionable tips to learn these fast. "
        f"Format: 1. tip  2. tip  3. tip. Be specific, mention real resources."
    )


def parse_resume(uploaded_file) -> str:
    try:
        name = uploaded_file.name.lower()

        if name.endswith(".pdf"):
            with pdfplumber.open(uploaded_file) as pdf:
                pages = [p.extract_text() for p in pdf.pages if p.extract_text()]
                return " ".join(pages)

        if name.endswith(".docx"):
            doc = docx.Document(uploaded_file)
            return "\n".join([p.text for p in doc.paragraphs])

    except Exception as e:
        st.error(f"Could not read file: {e}")

    return ""


def radar_chart(skills_lower):
    s = set(skills_lower)

    cats = {
        "Languages": s & {
            "python", "java", "c++", "javascript", "typescript", "go",
            "kotlin", "swift", "php", "c", "sql", "r", "dart"
        },
        "Web/Backend": s & {
            "react", "html", "css", "angular", "vue", "node.js", "django",
            "flask", "spring boot", "express.js", "rest api", "fastapi"
        },
        "AI / ML": s & {
            "machine learning", "deep learning", "tensorflow", "pytorch",
            "nlp", "keras", "scikit-learn", "pandas", "numpy", "opencv",
            "langchain", "llm", "yolov5", "cnn"
        },
        "DevOps/DB": s & {
            "docker", "kubernetes", "aws", "azure", "git", "linux", "ci/cd",
            "mysql", "mongodb", "postgresql", "firebase", "redis", "github",
            "supabase"
        },
        "CS Concepts": s & {
            "data structures", "algorithms", "oop", "dbms",
            "computer networks", "system design", "multithreading"
        },
    }

    labels = list(cats.keys())
    values = [min(len(v), 5) for v in cats.values()]
    values += values[:1]
    labels += labels[:1]

    fig = go.Figure(go.Scatterpolar(
        r=values,
        theta=labels,
        fill="toself",
        line_color="royalblue",
        fillcolor="rgba(65,105,225,0.25)",
    ))

    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 5])),
        showlegend=False,
        margin=dict(l=30, r=30, t=30, b=30),
        paper_bgcolor="rgba(0,0,0,0)",
        height=260,
    )

    return fig


def render_career_cards(career_paths, resume_skills):
    top = career_paths[0]
    matched = sorted([clean_skill_name(s) for s in top["matched"]])
    missing = sorted([clean_skill_name(s) for s in list(top["missing"])[:5]])

    with st.container(border=True):
        st.markdown(f"### ⭐  {top['role']}")

        m1, m2 = st.columns([1, 3])

        with m1:
            st.metric("Skill Match", f"{top['score']}%")

        with m2:
            if matched:
                st.markdown("**Skills you have:**")
                st.success(" · ".join(matched[:8]))

            if missing:
                st.markdown("**To improve, learn:**")
                st.warning(" · ".join(missing))

        if st.button(f"View {top['role']} Jobs", key="card_top"):
            st.session_state.card_role = top["role"]
            st.session_state.card_jobs = None
            st.session_state.card_active = True
            st.rerun()

    st.markdown("---")

    rest = career_paths[1:7]

    for row_i in range(0, len(rest), 2):
        row = rest[row_i:row_i + 2]
        cols = st.columns(2)

        for col, path in zip(cols, row):
            score = path["score"]
            matched = sorted([clean_skill_name(s) for s in path["matched"]])
            missing = sorted([clean_skill_name(s) for s in list(path["missing"])[:3]])
            color = "🟢"  if score >= 40 else "🟡" if score >= 20 else "🔴"

            with col:
                with st.container(border=True):
                    st.markdown(f"**{color}: {path['role']}**")
                    st.metric("Skill Match", f"{score}%", label_visibility="collapsed")

                    if matched:
                        st.caption("✅" + " · ".join(matched[:4]))

                    if missing:
                        st.caption("❌ Missing: " + ", ".join(missing))

                    if st.button("🔍 View Jobs", key=f"card_{path['role']}"):
                        st.session_state.card_role = path["role"]
                        st.session_state.card_jobs = None
                        st.session_state.card_active = True
                        st.rerun()

    if st.session_state.get("card_active") and st.session_state.get("card_role"):
        role = st.session_state.card_role

        st.markdown("---")
        st.subheader(f"Live Jobs - {role}")

        if st.session_state.get("card_jobs") is None:
            with st.spinner(f"Fetching {role} jobs..."):
                raw = fetch_adzuna(role)
                st.session_state.card_jobs = score_jobs(raw, resume_skills)

        render_job_list(st.session_state.card_jobs[:10], resume_skills, prefix="card")

        if st.button("Close jobs", key="close_card"):
            st.session_state.card_active = False
            st.session_state.card_jobs = None
            st.rerun()


def render_job_list(jobs, resume_skills, prefix="main"):
    for i, job in enumerate(jobs):
        score = job["score"]
        common = job["common"]
        missing = job["missing"]
        key = f"{prefix}_{i}"

        if score is None:
            label = "No skill data"
        elif score >= 60:
            label = f"🟢{score}% Match"
        elif score >= 30:
            label = f"🟡{score}% Match"
        else:
            label = f"🔴{score}% Match"

        with st.expander(f"**{job['title']}** @ {job['company']} - {label}"):
            c1, c2 = st.columns(2)

            with c1:
                st.markdown(f"**Location:** {job['location']}")

                if score is None:
                    st.info("Listing had insufficient skill keywords.")
                elif common:
                    st.write(f"**You have:** {', '.join(sorted(common))}")
                else:
                    st.write("**You have:** None matched")

            with c2:
                if score is not None:
                    if missing:
                        st.write(f"**Missing:** {', '.join(sorted(missing))}")
                    elif score > 0:
                        st.success("You match all listed requirements.")
                    else:
                        st.write("No skill overlap found.")

            st.link_button("Apply Now", job["apply_url"])

            g1, g2 = st.columns(2)

            with g1:
                if st.button("Cover Letter", key=f"cl_btn_{key}"):
                    if key not in st.session_state.cover_letters:
                        with st.spinner("Writing with Gemini..."):
                            st.session_state.cover_letters[key] = gen_cover_letter(
                                resume_skills,
                                job["title"],
                            )

                if key in st.session_state.cover_letters:
                    st.text_area(
                        "",
                        st.session_state.cover_letters[key],
                        height=200,
                        key=f"cl_txt_{key}",
                    )

            with g2:
                if missing and st.button("How to Improve", key=f"gap_btn_{key}"):
                    if key not in st.session_state.gap_advice:
                        with st.spinner("Analysing..."):
                            st.session_state.gap_advice[key] = gen_gap_advice(
                                missing,
                                job["title"],
                            )

                if key in st.session_state.gap_advice:
                    st.info(st.session_state.gap_advice[key])


for k, v in {
    "resume_skills": None,
    "last_file": None,
    "adzuna_jobs": None,
    "adzuna_query": "",
    "indeed_jobs": None,
    "last_text": "",
    "cover_letters": {},
    "gap_advice": {},
    "card_role": None,
    "card_jobs": None,
    "card_active": False,
    "skill_engine_version": "",
}.items():
    if k not in st.session_state:
        st.session_state[k] = v


st.set_page_config(page_title="Resume Intelligence", layout="wide")
st.title("AI Resume Intelligence System")
st.caption("Powered by GLiNER NLP, Adzuna and Indeed APIs, Gemini AI")

st.sidebar.title("Your Profile")
uploaded_file = st.sidebar.file_uploader("Upload Resume (PDF / DOCX)", type=["pdf", "docx"])

if uploaded_file:
    force_rescan = st.sidebar.button("Re-analyze Resume")

    should_scan = (
        st.session_state.last_file != uploaded_file.name
        or st.session_state.skill_engine_version != SKILL_ENGINE_VERSION
        or force_rescan
    )

    if should_scan:
        with st.spinner("Extracting skills..."):
            text = parse_resume(uploaded_file)
            skills = extract_skills(text)

        st.session_state.resume_skills = skills
        st.session_state.last_file = uploaded_file.name
        st.session_state.skill_engine_version = SKILL_ENGINE_VERSION
        st.session_state.last_text = text

        st.session_state.adzuna_jobs = None
        st.session_state.indeed_jobs = None
        st.session_state.cover_letters = {}
        st.session_state.gap_advice = {}
        st.session_state.card_active = False
        st.session_state.card_jobs = None
        st.session_state.card_role = None

        s_lower = {s.lower() for s in skills}
        role = predict_role(s_lower)

        save_scan(uploaded_file.name, skills, role)

    resume_skills = st.session_state.resume_skills or set()

    if len(resume_skills) < 3:
        st.warning(
            "Very few skills detected. Use a text-based PDF, make sure the resume has "
            "a Skills section, or try DOCX format."
        )
        st.stop()

    st.sidebar.success(f"{len(resume_skills)} Skills Detected")

    with st.sidebar.expander(f"View All Detected Skills ({len(resume_skills)})", expanded=False):
        st.write(" · ".join(sorted(resume_skills)) if resume_skills else "None")

    s_lower = {s.lower() for s in resume_skills}
    predicted_role = predict_role(s_lower, gemini_fn=gemini_generate)
    career_paths = get_career_paths(s_lower)

    tab1, tab2, tab3, tab4 = st.tabs([
        "Career Paths",
        "Job Matches (Adzuna)",
        "More Jobs (Indeed)",
        "Scan History",
    ])

    with tab1:
        st.subheader("What's your next career move?")
        st.caption("Scores computed using Jaccard similarity against role skill signatures")

        left, right = st.columns([3, 2])

        with left:
            render_career_cards(career_paths, resume_skills)

        with right:
            st.markdown("### Skill Radar")
            st.plotly_chart(radar_chart(s_lower), use_container_width=True)

            st.markdown("### Detected Skills")
            st.write(" · ".join(sorted(resume_skills)))

    with tab2:
        query = st.text_input(
            "Search query, edit and press Enter:",
            value=predicted_role,
            key="adzuna_search",
        )

        if st.session_state.adzuna_jobs is None or st.session_state.adzuna_query != query:
            with st.spinner(f"Fetching jobs for {query}..."):
                raw = fetch_adzuna(query)

            if raw:
                st.session_state.adzuna_jobs = score_jobs(raw, resume_skills)
                st.session_state.adzuna_query = query
            else:
                st.error("No jobs found. Try a different query.")
                st.stop()

        jobs = st.session_state.adzuna_jobs or []
        st.caption(f"{len(jobs)} jobs from Adzuna India")
        render_job_list(jobs[:15], resume_skills, prefix="az")

    with tab3:
        st.subheader("Indeed Live Jobs (India)")
        st.caption("Via Apify scraper. This may take around 30 seconds.")

        if st.button("Fetch Indeed Jobs", key="indeed_fetch"):
            with st.spinner("Fetching from Indeed via Apify..."):
                raw = fetch_indeed(predicted_role)

            if raw:
                st.session_state.indeed_jobs = score_jobs(raw, resume_skills)
                st.success(f"Found {len(raw)} jobs from Indeed.")
            else:
                st.warning("No Indeed jobs found or apify-client is not installed.")

        if st.session_state.indeed_jobs:
            render_job_list(st.session_state.indeed_jobs[:10], resume_skills, prefix="ind")

    with tab4:
        st.subheader("Resume Scan History")
        st.caption("Tracked in local SQLite database across sessions")

        rows = get_history()

        if not rows:
            st.info("No scans yet. Upload a resume to create your first record.")
        else:
            for row in rows:
                filename, role, skills_json, skill_count, timestamp = row

                try:
                    skills_list = json.loads(skills_json)
                except Exception:
                    skills_list = []

                with st.expander(f"**{filename}** - {role} - {skill_count} skills - {timestamp}"):
                    st.write(f"**Predicted Role:** {role}")
                    st.write(f"**Skills ({skill_count}):** {', '.join(skills_list)}")

        if rows and st.button("Clear History"):
            clear_history()
            st.success("History cleared.")
            st.rerun()

else:
    st.info("Upload your resume from the sidebar to get started.")
    st.markdown(
        """
        **How it works:**

        1. GLiNER NLP and regex extract skills from your resume.
        2. Career Path Analysis scores your profile across role signatures.
        3. Live jobs are fetched from Adzuna India.
        4. Optional Indeed jobs can be fetched through Apify.
        5. Every job is scored by skill match percentage.
        6. Gemini AI can generate cover letters and learning advice.
        7. Scan history is saved locally in SQLite.
        """
    )
