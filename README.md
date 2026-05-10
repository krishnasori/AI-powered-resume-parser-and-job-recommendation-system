# AI Resume Intelligence System

A smart recruiter tool that matches resumes to live jobs using NLP and vector scoring.

##  Key Features
* **Skill Extraction:** Uses the GLiNER model for high-accuracy entity recognition.
* **Live Job Data:** Real-time fetching from Adzuna and Indeed India.
* **Intelligent Matching:** Scores candidates based on Jaccard similarity logic[cite: 2].
* **AI Assistance:** Generates custom cover letters using Gemini AI.
* **Scan History:** Persistent storage using a local SQLite database.

##  Tech Stack
* **UI:** Streamlit[cite: 1]
* **Language:** Python
* **NLP:** GLiNER & Regular Expressions[cite: 2]
* **DB:** SQLite[cite: 4]