"""
skills_engine.py
NLP Engine for Resume Intelligence System.
"""

import re
import streamlit as st

SKILL_ENGINE_VERSION = "skills-normalization-v5"

try:
    from rapidfuzz import process, fuzz
    FUZZY_OK = True
except ImportError:
    FUZZY_OK = False


SKILL_ALIASES = {
    "html5": "HTML",
    "html 5": "HTML",
    "css3": "CSS",
    "css3.0": "CSS",

    "javascript": "JavaScript",
    "java script": "JavaScript",
    "js": "JavaScript",
    "ecmascript": "JavaScript",
    "es6": "JavaScript",
    "es 6": "JavaScript",

    "typescript": "TypeScript",
    "type script": "TypeScript",

    "react": "React",
    "react.js": "React",
    "react. js": "React",
    "react-js": "React",
    "react js": "React",
    "reactjs": "React",

    "node.js": "Node.js",
    "node. js": "Node.js",
    "node-js": "Node.js",
    "node js": "Node.js",
    "nodejs": "Node.js",
    

    "express.js": "Express.js",
    "express. js": "Express.js",
    "express-js": "Express.js",
    "express js": "Express.js",
    "expressjs": "Express.js",

    "next.js": "Next.js",
    "next js": "Next.js",
    "nextjs": "Next.js",

    "fastapi": "FastAPI",
    "fast api": "FastAPI",
    "fast-api": "FastAPI",

    "vuejs": "Vue",
    "vue.js": "Vue",
    "vue js": "Vue",

    "sklearn": "Scikit-learn",
    "scikit learn": "Scikit-learn",
    "scikit-learn": "Scikit-learn",
    "scikitlearn": "Scikit-learn",
    "skikitlearn": "Scikit-learn",
    "skikit learn": "Scikit-learn",

    "tensorflow": "TensorFlow",
    "tensor flow": "TensorFlow",
    "pytorch": "PyTorch",
    "py torch": "PyTorch",
    "numpy": "NumPy",
    "pandas": "Pandas",
    "matplotlib": "Matplotlib",

    "mongodb": "MongoDB",
    "mongo db": "MongoDB",
    "mysql": "MySQL",
    "my sql": "MySQL",
    "postgresql": "PostgreSQL",
    "postgres": "PostgreSQL",
    "supabase": "Supabase",

    "rest api": "REST API",
    "rest apis": "REST API",
    "rest-api": "REST API",
    "rest-apis": "REST API",
    "restapi": "REST API",
    "restapis": "REST API",
    "restful api": "REST API",
    "restful apis": "REST API",
    "restful-api": "REST API",
    "restful-apis": "REST API",
    "restfulapi": "REST API",
    "restfulapis": "REST API",
    "api integration": "REST API",
    "apiintegration": "REST API",

    "mern": "Node.js",
    "mern stack": "Node.js",
    "mernstack": "Node.js",

    "nlp": "NLP",
    "ml": "Machine Learning",
    "ai": "Artificial Intelligence",
    "dl": "Deep Learning",
    "cv": "Computer Vision",

    "k8s": "Kubernetes",
    "gcp": "Google Cloud",
    "aws": "AWS",
    "ci/cd": "CI/CD",
    "devops": "DevOps",

    "oop": "Object Oriented Programming",
    "oops": "Object Oriented Programming",
    "dsa": "Data Structures",
    "ds": "Data Structures",
    "dbms": "DBMS",
    "os": "Operating Systems",
    "cn": "Computer Networks",

    "llm": "LLM",
    "genai": "Generative AI",
    "gen ai": "Generative AI",
    "cloud architecture": "Cloud Architecture",
   "cloud architect": "Cloud Architecture",
    "cloud solutions": "Cloud Architecture",

}


def canonicalize(skill: str, canonical_list: list) -> str:
    sl = skill.strip().lower()

    if sl in SKILL_ALIASES:
        return SKILL_ALIASES[sl]

    for raw in canonical_list:
        if raw.lower() == sl:
            return raw

    # Match punctuation/spacing variants such as Power-BI -> Power BI,
    # Cloud-Computing -> Cloud Computing, NextJS -> Next.js.
    normalized = re.sub(r"[\s._-]+", "", sl)
    for raw in canonical_list:
        raw_normalized = re.sub(r"[\s._-]+", "", raw.lower())
        if raw_normalized == normalized:
            return raw

    if FUZZY_OK and len(sl) > 3:
        result = process.extractOne(
            sl,
            [r.lower() for r in canonical_list],
            scorer=fuzz.WRatio,
            score_cutoff=88,
        )
        if result:
            _, _, idx = result
            return canonical_list[idx]

    return skill.strip().title()


@st.cache_resource(show_spinner="Loading NLP model...")
def load_ner_model():
    try:
        from gliner import GLiNER
        model = GLiNER.from_pretrained("urchade/gliner_medium-v2.1")
        print("GLiNER loaded successfully")
        return model
    except Exception as e:
        print(f"GLiNER failed to load: {e}")
        st.warning(f"GLiNER model could not load: {e}. Using regex fallback.")
        return None


NER_LABELS = [
    "programming language",
    "software framework",
    "machine learning skill",
    "database",
    "devops tool",
    "cloud platform",
    "soft skill",
]

GLINER_BLACKLIST = {
    "intern", "internship", "fundamentals", "developer intern",
    "web development intern", "certification", "coursework",
    "research", "academy", "university", "institute", "school",
    "notebook", "colab", "vs code", "postman", "vscode",
}


def extract_with_gliner(text: str, model) -> set:
    if model is None:
        return set()

    try:
        words = text.split()
        chunks = [" ".join(words[i:i + 400]) for i in range(0, len(words), 400)]
        found = set()

        for chunk in chunks:
            entities = model.predict_entities(chunk, NER_LABELS, threshold=0.55)
            for ent in entities:
                val = ent["text"].strip()
                val = re.sub(r"\s*\(.*?\)", "", val).strip()

                if any(bad in val.lower() for bad in GLINER_BLACKLIST):
                    continue
                if len(val) > 15 and " " not in val:
                    continue
                if not (1 < len(val) <= 30):
                    continue

                found.add(val)

        return found
    except Exception:
        return set()


RAW_SKILLS = [
    "Python", "Java", "C++", "C", "C#", "JavaScript", "TypeScript", "PHP", "Ruby",
    "Swift", "Kotlin", "Go", "Rust", "Dart", "Scala", "R", "SQL", "Perl", "Lua", "Matlab",

    "MySQL", "MongoDB", "PostgreSQL", "Supabase", "Firebase", "Redis", "SQLite", "Oracle",
    "Cassandra", "DynamoDB", "FAISS", "ChromaDB", "Pinecone", "Elasticsearch",

    "HTML", "CSS", "React", "Angular", "Vue", "Node.js", "Express.js", "Next.js",
    "Django", "Flask", "FastAPI", "Spring Boot", "Spring AI", "Bootstrap",
    "Tailwind CSS", "Redux", "jQuery", "SASS", "GraphQL", "REST API",
    "NestJS", "Laravel", "ASP.NET", "Gradio", "Streamlit",

    "Machine Learning", "Deep Learning", "Artificial Intelligence", "TensorFlow", "PyTorch",
    "Keras", "Scikit-learn", "Pandas", "NumPy", "Matplotlib", "Seaborn", "NLP",
    "Computer Vision", "OpenCV", "YOLO", "YOLOv5", "CNN", "RNN", "LSTM",
    "OCR", "EasyOCR", "Face Recognition", "Data Science", "Data Analysis",
    "Generative AI", "LLM", "BERT", "Transformers", "Hugging Face", "LangChain",
    "Spark", "Hadoop", "Tableau", "Power BI", "Excel", "OpenAI", "MiniLM",
    "Embeddings", "Vector Search", "NLTK", "spaCy", "Prompt Engineering", "Image Processing",

    "Git", "GitHub", "GitLab", "Docker", "Kubernetes", "Jenkins", "AWS", "Azure",
    "Google Cloud", "GCP", "Terraform", "Ansible", "Linux", "Unix", "Bash",
    "CI/CD", "DevOps", "JIRA", "Agile", "Scrum",
    "CloudFormation", "Lambda", "EC2", "S3", "Azure DevOps", "GKE",

    "Looker", "Data Warehousing", "ETL", "Airflow", "dbt", "Snowflake",
    "BigQuery", "Redshift", "Statistics", "Probability", "A/B Testing",

    "Data Structures", "Algorithms", "Object Oriented Programming", "OOP",
    "DBMS", "Operating Systems", "Computer Networks", "System Design",
    "Distributed Systems", "Cloud Computing", "Cybersecurity", "Blockchain",
    "IoT", "Multithreading", "LRU Cache", "Socket Programming", "Socket",

    "Penetration Testing", "Ethical Hacking", "Kali Linux", "Metasploit",
    "Wireshark", "Burp Suite", "OWASP", "Network Security", "Cryptography",
    "Vulnerability Assessment", "SIEM", "Nmap", "Forensics",

    "Solidity", "Ethereum", "Web3.js", "Smart Contracts", "NFT",
    "DeFi", "Hardhat", "Truffle", "IPFS", "Polygon", "Hyperledger",

    "Arduino", "Raspberry Pi", "MQTT", "Embedded Systems", "Sensors",
    "Firmware", "RTOS", "LoRa", "Zigbee", "ESP32",

    "SAP", "SAP ABAP", "SAP HANA", "SAP Fiori", "SAP MM", "SAP SD",
    "SAP FI", "SAP BASIS", "SAP BW", "S/4HANA",

    "Spring", "Hibernate", "Maven", "Gradle", "JUnit", "Microservices",
    "JPA", "JDBC", "Servlet", "JSP",

    "Communication", "Teamwork", "Problem Solving", "Leadership",
    "Time Management", "Critical Thinking", "Adaptability",

    "Android", "iOS", "Flutter", "React Native",
]


def _build_alias_set(aliases, canonical_list):
    canonical_lookup = {skill.lower() for skill in canonical_list}
    return {
        alias
        for alias, canonical in aliases.items()
        if canonical.lower() in canonical_lookup
    }


def _build_skill_set(raw):
    expanded = set()

    for skill in raw:
        expanded.add(skill)
        expanded.add(skill.lower())
        expanded.add(skill.upper())

        if " " in skill:
            expanded.add(skill.replace(" ", "-"))
            expanded.add(skill.replace(" ", ""))

        if "-" in skill:
            expanded.add(skill.replace("-", " "))
            expanded.add(skill.replace("-", ""))

        if "." in skill:
            expanded.add(skill.replace(".", ""))
            expanded.add(skill.replace(".", " "))

        if ".js" in skill.lower():
            base = skill.lower().replace(".js", "")
            expanded.add(base + "js")
            expanded.add(base + " js")
            expanded.add(base + "-js")

        if skill.lower().endswith("api") and len(skill) > 3:
            expanded.add(re.sub(r"api$", " api", skill, flags=re.IGNORECASE).lower())
            expanded.add(re.sub(r"api$", "-api", skill, flags=re.IGNORECASE).lower())

        if "++" in skill:
            expanded.add(skill.replace("++", "pp"))

        if skill[-1].isdigit():
            expanded.add(skill[:-1].lower())
            expanded.add(skill.lower())

    return expanded


_EXTRA_VARIANTS = {
    "rest api", "rest apis", "rest-api", "rest-apis",
    "restapi", "restapis", "restful api", "restful apis",
    "restful-api", "restful-apis", "restfulapi", "restfulapis",
    "api integration", "apiintegration",
    "reactjs", "react js", "react-js",
    "nodejs", "node js", "node-js",
    "expressjs", "express js", "express-js",
    "fastapi", "fast api", "fast-api",
}

SKILL_SET = _build_skill_set(RAW_SKILLS) | _build_alias_set(SKILL_ALIASES, RAW_SKILLS) | _EXTRA_VARIANTS


def clean_skill_name(skill: str) -> str:
    return canonicalize(skill, RAW_SKILLS)


def normalize_skill_set(skills: set) -> set:
    return {
        clean_skill_name(str(skill)).lower()
        for skill in skills
        if str(skill).strip()
    }


SKILL_IMPLICATIONS = {
    "typescript": {"javascript"},
   
    "react native": {"react", "javascript"},
    
    "node.js": {"javascript"},
   
    "fastapi": {"python", "rest api"},
    "django": {"python", "rest api"},
    "flask": {"python", "rest api"},
    "spring boot": {"java", "rest api"},
    "google cloud": {"gcp"},
}


def expand_skill_set_for_matching(skills: set) -> set:
    expanded = normalize_skill_set(skills)

    for skill in list(expanded):
        expanded.update(SKILL_IMPLICATIONS.get(skill, set()))

    return expanded


def split_merged_words(text: str) -> str:
    if not text:
        return ""

    replacements = {
        r"Java\s*Script": " javascript ",
        r"Type\s*Script": " typescript ",

        r"React\s*[\.\-]?\s*JS": " reactjs ",
        r"Node\s*[\.\-]?\s*JS": " nodejs ",
        r"Express\s*[\.\-]?\s*JS": " expressjs ",
        r"Next\s*[\.\-]?\s*JS": " nextjs ",

        r"REST\s*[\-]?\s*APIs?": " rest api ",
        r"REST\s*ful\s*[\-]?\s*APIs?": " rest api ",
        r"RESTfulAPIs?": " rest api ",

        r"API\s*integration": " api integration ",
        r"Fast\s*[\-]?\s*API": " fastapi ",

        r"Scikit\s*[\-]?\s*learn": " scikit learn ",
        r"Skikit\s*[\-]?\s*learn": " scikit learn ",
    }

    for pattern, replacement in replacements.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

    text = re.sub(r"([a-z])([A-Z])", r"\1 \2", text)
    text = re.sub(r"([a-zA-Z])([0-9])", r"\1 \2", text)
    text = re.sub(r"([0-9])([a-zA-Z])", r"\1 \2", text)

    return text


def _normalize_for_regex(value: str) -> str:
    value = value.lower()
    value = re.sub(r"[^a-zA-Z0-9+#\s]", " ", value)
    value = re.sub(r"\s+", " ", value).strip()
    return value


def extract_with_regex(text: str) -> set:
    text = split_merged_words(text)
    text = text.replace("&", " ")
    text_clean = _normalize_for_regex(text)

    found = set()

    for skill in sorted(SKILL_SET, key=len, reverse=True):
        sc = _normalize_for_regex(skill)

        if len(sc) < 2:
            continue

        pattern = r"(?<![a-zA-Z0-9+#])" + re.escape(sc) + r"(?![a-zA-Z0-9+#])"

        if re.search(pattern, text_clean):
            found.add(canonicalize(skill, RAW_SKILLS))

    return found


def extract_skills(text: str) -> set:
    model = load_ner_model()
    gliner_raw = extract_with_gliner(text, model)
    regex_skills = extract_with_regex(text)

    gliner_skills = {canonicalize(s, RAW_SKILLS) for s in gliner_raw}
    combined = gliner_skills | regex_skills

    print(f"\nGLiNER extracted ({len(gliner_skills)}): {sorted(gliner_skills)}")
    print(f"Regex extracted  ({len(regex_skills)}): {sorted(regex_skills)}")
    print(f"Combined total:  {len(combined)}\n")

    seen_lower = {}
    for skill in combined:
        key = skill.lower()
        if key not in seen_lower or skill in regex_skills:
            seen_lower[key] = skill

    deduped = set(seen_lower.values())
    deduped_lower = {s.lower() for s in deduped}
    canonical_lower = {s.lower() for s in RAW_SKILLS}

    final = set()
    noisy = {"api", "apis", "framework", "language", "tool", "tools"}

    for skill in deduped:
        sl = skill.lower()

        if sl in noisy:
            continue

        is_noncanonical_substring = (
            sl not in canonical_lower
            and any(other != sl and other.startswith(sl) for other in deduped_lower)
        )

        if not is_noncanonical_substring:
            final.add(skill)

    return final


ROLE_SIGNATURES = {
    "Computer Vision Engineer": {
        "opencv", "yolo", "yolov5", "computer vision", "cnn", "easyocr",
        "ocr", "face recognition", "tensorflow", "pytorch", "image processing"
    },
    "AI / LLM Engineer": {
        "langchain", "llm", "generative ai", "hugging face", "bert",
        "transformers", "openai", "spring ai", "embeddings", "vector search",
        "chromadb", "faiss", "prompt engineering"
    },
    "ML Engineer": {
        "machine learning", "deep learning", "tensorflow", "pytorch", "keras",
        "scikit-learn", "nlp", "data science", "pandas", "numpy", "matplotlib",
        "seaborn", "data analysis", "spark", "hadoop"
    },
    "Data Analyst": {
        "sql", "excel", "tableau", "power bi", "data analysis", "statistics",
        "python", "pandas", "numpy", "a/b testing", "looker", "bigquery",
        "data warehousing", "etl", "snowflake", "redshift"
    },
    "Backend Developer": {
        "java", "spring boot", "django", "flask", "fastapi", "express.js",
        "node.js", "postgresql", "mongodb", "mysql", "redis", "firebase",
        "rest api", "graphql", "socket", "microservices", "hibernate"
    },
    "Java Developer": {
        "java", "spring boot", "hibernate", "maven", "gradle", "junit",
        "microservices", "jpa", "jdbc", "mysql", "postgresql", "spring",
        "servlet", "jsp", "object oriented programming"
    },
    "Frontend Developer": {
        "react", "angular", "vue", "next.js", "tailwind css", "bootstrap",
        "redux", "sass", "html", "css", "javascript", "typescript", "jquery"
    },
    "Full Stack Developer": {
        "react", "node.js", "python", "sql", "html", "css", "javascript",
        "mongodb", "express.js", "django", "postgresql", "rest api"
    },

    "Cloud/ DevOps Engineer": {
        "docker", "kubernetes", "terraform", "ansible", "jenkins",
        "ci/cd", "linux", "bash", "aws", "azure", "gcp"
    },
    "Cloud Engineer": {
        "aws", "azure", "gcp", "docker", "kubernetes", "terraform",
        "cloudformation", "lambda", "ec2", "s3", "cloud computing",
        "devops", "linux", "ci/cd", "azure devops", "gke"
    },
    "Cybersecurity Engineer": {
        "penetration testing", "ethical hacking", "kali linux", "metasploit",
        "wireshark", "burp suite", "owasp", "network security", "cryptography",
        "vulnerability assessment", "siem", "nmap", "forensics", "cybersecurity"
    },
    "Blockchain Developer": {
        "solidity", "ethereum", "web3.js", "smart contracts", "nft",
        "defi", "hardhat", "truffle", "ipfs", "blockchain", "polygon", "hyperledger"
    },
    "IoT Engineer": {
        "arduino", "raspberry pi", "mqtt", "embedded systems", "sensors",
        "firmware", "rtos", "lora", "zigbee", "esp32", "iot", "c++", "python"
    },
    "SAP Consultant/Enterprise Consultant": {
        "sap", "sap abap", "sap hana", "sap fiori", "sap mm", "sap sd",
        "sap fi", "sap basis", "sap bw", "s/4hana"
    },
    "Android Developer": {
        "android", "kotlin", "java", "firebase", "sqlite", "flutter"
    },
    "Software Engineer": {
        "python", "java", "c++", "algorithms", "data structures", "git",
        "object oriented programming", "sql", "system design", "multithreading"
    },

}


def get_career_paths(skills_lower_set: set) -> list:
    skills_lower_set = expand_skill_set_for_matching(skills_lower_set)

    results = []
    for role, sig in ROLE_SIGNATURES.items():
        matched = skills_lower_set & sig
        score = round((len(matched) / len(sig)) * 100, 1)

        results.append({
            "role": role,
            "score": score,
            "matched": matched,
            "missing": sig - skills_lower_set,
        })

    results.sort(key=lambda x: x["score"], reverse=True)

    se = next((r for r in results if r["role"] == "Software Engineer"), None)
    if se:
        results.remove(se)
        results.append(se)

    return results


def predict_role(skills_lower_set: set, gemini_fn=None) -> str:
    paths = get_career_paths(skills_lower_set)
    top = paths[0]

    if top["score"] >= 20:
        return top["role"]

    if gemini_fn is not None:
        try:
            skills_str = ", ".join(list(normalize_skill_set(skills_lower_set))[:20])
            prompt = (
                f"Given these skills from a resume: {skills_str}\n"
                f"Suggest ONE most suitable job role title in 4 words or less.\n"
                f"Reply with only the job title, nothing else."
            )
            role = gemini_fn(prompt).strip().strip(".").strip()
            if role and len(role) < 40:
                return role
        except Exception:
            pass

    return top["role"] if top["score"] > 0 else "Software Engineer"


TITLE_SKILL_MAP = {
    "python": {"Python", "Django", "Flask", "FastAPI"},
    "java": {"Java", "Spring Boot", "MySQL", "Hibernate"},
    "data analyst": {"SQL", "Excel", "Tableau", "Power BI", "Python", "Pandas"},
    "data scientist": {"Machine Learning", "Python", "TensorFlow", "Scikit-learn", "Pandas"},
    "data": {"Python", "SQL", "Machine Learning", "Pandas", "NumPy"},
    "machine learning": {"Machine Learning", "Python", "TensorFlow", "Scikit-learn"},
    "frontend": {"HTML", "CSS", "JavaScript", "React"},
    "react": {"React", "JavaScript", "HTML", "CSS"},
    "full stack": {"HTML", "CSS", "JavaScript", "React", "Node.js", "SQL"},
    "fullstack": {"HTML", "CSS", "JavaScript", "React", "Node.js", "SQL"},
    "devops": {"Docker", "Kubernetes", "Linux", "AWS", "CI/CD"},
    "cloud": {"AWS", "Azure", "GCP", "Docker", "Kubernetes", "Terraform"},
    "android": {"Java", "Kotlin", "Firebase"},
    "computer vision": {"OpenCV", "Python", "TensorFlow", "CNN"},
    "nlp": {"Python", "NLP", "BERT", "Transformers"},
    "ai": {"Python", "Machine Learning", "TensorFlow", "LangChain"},
    "ml": {"Python", "Machine Learning", "Scikit-learn", "Pandas"},
    "generative": {"Python", "LLM", "Generative AI", "LangChain"},
    "llm": {"Python", "LLM", "LangChain", "Transformers"},
    "blockchain": {"Solidity", "Ethereum", "Web3.js", "Smart Contracts", "Python"},
    "cybersecurity": {"Kali Linux", "Metasploit", "Wireshark", "Python", "Linux"},
    "ethical hacking": {"Kali Linux", "Metasploit", "Wireshark", "Nmap", "Burp Suite"},
    "iot": {"Arduino", "Raspberry Pi", "C++", "Python", "MQTT"},
    "sap": {"SAP", "SAP ABAP", "SAP HANA", "SQL"},
    "node": {"Node.js", "JavaScript", "Express.js"},
    "angular": {"Angular", "TypeScript", "JavaScript"},
    "spring": {"Java", "Spring Boot", "MySQL"},
    "backend": {"Python", "Java", "SQL", "REST API", "Git"},
    "software": {"Python", "Java", "C++", "Data Structures", "Algorithms", "Git"},
    "intern": {"Python", "Java", "C++", "Git", "Data Structures"},
    "fresher": {"Python", "Java", "C++", "Git", "Data Structures"},
}


def calculate_score(resume_skills: set, jd_text: str, job_title: str = "") -> tuple:
    jd_skills = extract_with_regex(jd_text)

    if len(jd_skills) < 3 and job_title:
        implied = set()
        for kw, skills in TITLE_SKILL_MAP.items():
            if kw in job_title.lower():
                implied |= skills
        jd_skills = jd_skills | implied

    if not jd_skills:
        return None, set(), set(), set()

    r_set = expand_skill_set_for_matching(resume_skills)
    j_set = normalize_skill_set(jd_skills)

    common = r_set & j_set
    missing = j_set - r_set
    score = round((len(common) / len(j_set)) * 100, 1)

    return (
        score,
        {clean_skill_name(s) for s in missing},
        j_set,
        {clean_skill_name(s) for s in common},
    )
