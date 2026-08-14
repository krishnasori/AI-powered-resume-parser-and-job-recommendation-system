# 📄 AI-Powered Resume Parser & Job Recommendation System

An AI-driven recruitment and job recommendation platform built to extract structured data from resumes using **GLiNER (Generalist and Lightweight Model for Named Entity Recognition)**, map candidate skill sets, fetch live job postings, and compute candidate-to-job matching scores with persistent database tracking.

---

## 🌟 Key Features

- **Zero-Shot Named Entity Recognition (GLiNER):** Dynamically extracts candidate names, contact details, universities, degrees, job titles, and companies without rigid rule pipelines.
- **Skills Extraction & Taxonomy Engine (`skills_engine.py`):** Automatically detects, normalizes, and groups technical and domain skills from candidate resumes.
- **Automated Job Fetching (`job_fetcher.py`):** Ingests and aggregates live job postings and descriptions based on target roles.
- **Intelligent Job Matching & Recommendation:** Compares candidate skill profiles against job requirements to generate ATS compatibility scores and highlight missing skill gaps.
- **History & Profile Tracking (`database.py` / `saas_app.db`):** Stores user parsing sessions, past resume scans, and historical match results in a persistent SQLite database.
- **Interactive Web Interface (`app.py`):** Fast, user-friendly UI for uploading resumes, visualizing extracted data, and browsing ranked job recommendations.

---

## 🛠️ Tech Stack

- **Language:** Python 3.9+
- **Information Extraction (NER):** `GLiNER`
- **Data & Processing:** `pandas`, `numpy`, `scikit-learn`
- **Database:** SQLite (`saas_app.db` / `history.db`)
- **Document Ingestion:** `pdfplumber`, `PyPDF2`, `python-docx`
- **Frontend / Application:** Streamlit / Flask

---

## 📂 Repository Structure

```text
├── .gitignore
├── requirements.txt         # Project dependencies
├── saas_app.db              # Application database (history & user data)
├── src/
│   ├── app.py               # Main application entry point & UI
│   ├── database.py          # Database operations, session management & history tracking
│   ├── job_fetcher.py       # Job scraping / API fetching module
│   ├── models.py            # GLiNER model loading & entity extraction pipeline
│   ├── skills_engine.py     # Skill taxonomy matching & gap analysis engine
│   ├── old_app.py           # Legacy app implementation
│   └── old_database.py      # Legacy database schema/setup
└── README.md
🚀 Getting Started
1. Clone the Repository
Bash
git clone [https://github.com/krishnasori/AI-powered-resume-parser-and-job-recommendation-system.git](https://github.com/krishnasori/AI-powered-resume-parser-and-job-recommendation-system.git)
cd AI-powered-resume-parser-and-job-recommendation-system
2. Set Up a Virtual Environment
Bash
# On Linux / macOS
python3 -m venv venv
source venv/bin/activate

# On Windows
python -m venv venv
venv\Scripts\activate
3. Install Dependencies
Bash
pip install -r requirements.txt
⚡ How the Extraction & Matching Engine Works
Document Ingestion: The user uploads a resume (.pdf, .docx, or .txt) through src/app.py.

GLiNER Entity Extraction (src/models.py): Employs the GLiNER model to perform zero-shot entity extraction for names, experience, and education.

Skill Profiling (src/skills_engine.py): Normalizes candidate skills and constructs a structured profile.

Job Retrieval & Matching (src/job_fetcher.py): Fetches job requirements and computes similarity scores against the candidate's skill profile.

Persistence (src/database.py): Saves the parsed output and recommended matches to saas_app.db for session history tracking.

💻 Running the Application
Launch the main application via:

Bash
python src/app.py
(or streamlit run src/app.py if running as a Streamlit dashboard)

🤝 Contributing
Contributions, issues, and feature requests are welcome! Feel free to open an issue or submit a pull request on the repository.

📜 License
This project is open-source and available under the MIT License.
