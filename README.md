📄 AI-Powered Resume Parser & Job Recommendation System

An intelligent end-to-end recruitment tool designed to parse unstructured resumes (PDF, DOCX, TXT), extract key candidate attributes into structured data, and match candidate profiles against relevant job descriptions using Natural Language Processing (NLP) and similarity matching.

---

## 🌟 Key Features

- **Automated Resume Parsing:** Extracts key entities such as:
  - Contact Information (Name, Email, Phone, LinkedIn, GitHub)
  - Core Skills & Technical Proficiencies
  - Education & Certifications
  - Work Experience & Projects
- **Information Extraction Pipeline:** Leverages regular expressions and `spaCy` NLP pipelines to transform unstructured text into structured `JSON` format.
- **Job Matching & Recommendation Engine:** Computes semantic similarity (TF-IDF / Cosine Similarity / Embeddings) between extracted resume profiles and a database of job descriptions.
- **Skill Gap Analysis & ATS Score:** Calculates compatibility scores and identifies missing skills relevant to target roles.

---

## 🛠️ Tech Stack

- **Language:** Python 3.9+
- **NLP & Text Processing:** `spaCy`, `NLTK`, `Regex`, `scikit-learn`
- **Document Extractors:** `pdfplumber`, `PyPDF2`, `python-docx`
- **Data Handling:** `pandas`, `NumPy`
- **User Interface / API (Optional):** `Streamlit` / `FastAPI` / `Flask`

---

## 📂 Project Structure

```text
├── data/
│   ├── sample_resumes/          # Sample PDF/DOCX resumes for testing
│   └── job_descriptions.csv     # Dataset containing job postings & skill requirements
├── src/
│   ├── parser/
│   │   ├── extractor.py         # Text extraction from PDF/DOCX
│   │   ├── entity_recognizer.py # spaCy & regex-based entity extraction
│   │   └── cleaner.py           # Preprocessing, tokenization, stopword removal
│   ├── recommender/
│   │   ├── matcher.py           # Cosine similarity & TF-IDF matching engine
│   │   └── scoring.py           # ATS compatibility & skill gap calculation
│   └── app.py                   # Main application / UI entry point
├── requirements.txt             # Project dependencies
├── setup.sh                     # Optional setup script (spaCy models, etc.)
└── README.md
🚀 Getting Started1. Clone the RepositoryBashgit clone [https://github.com/krishnasori/AI-powered-resume-parser-and-job-recommendation-system.git](https://github.com/krishnasori/AI-powered-resume-parser-and-job-recommendation-system.git)
cd AI-powered-resume-parser-and-job-recommendation-system
2. Set Up a Virtual EnvironmentBash# On Linux / macOS
python3 -m venv venv
source venv/bin/activate

# On Windows
python -m venv venv
venv\Scripts\activate
3. Install DependenciesBashpip install -r requirements.txt
python -m spacy download en_core_web_sm
💻 UsageCommand Line / Script ExecutionBashpython src/parser/extractor.py --file data/sample_resumes/sample.pdf
Running the Web Interface (if using Streamlit)Bashstreamlit run src/app.py
📊 How the Pipeline WorksText Extraction: Ingests documents (.pdf, .docx, .txt) and normalizes raw text.Entity Recognition & Parsing: Identifies names, contact details, universities, degrees, and domain skills via rule-based matchers and NER models.Feature Vectorization: Converts candidate skill profiles and job descriptions into vector spaces (e.g., TF-IDF / sentence transformers).Ranked Recommendations: Computes cosine similarity to return the top $N$ matching jobs alongside match percentages and keyword gaps.🗺️ Roadmap & Planned Enhancements[ ] Support for Transformer-based embeddings (sentence-transformers, BERT).[ ] Multi-lingual resume parsing support.[ ] Export parsed candidate data directly to standard ATS database schemas (PostgreSQL / MongoDB).[ ] Automated resume enhancement suggestions based on target job postings.🤝 ContributingContributions, issues, and feature requests are welcome! Feel free to check the issues page.📜 LicenseThis project is licensed under the MIT License.
