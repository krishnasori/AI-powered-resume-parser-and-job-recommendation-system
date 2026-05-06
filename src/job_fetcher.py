"""
job_fetcher.py
Live job fetching from Adzuna (primary) and Indeed via Apify (secondary).
API keys loaded from .env file — never hardcoded.
"""
import os
import re
import requests
from dotenv import load_dotenv
from skills_engine import calculate_score

load_dotenv()

ADZUNA_APP_ID  = os.getenv("ADZUNA_APP_ID")
ADZUNA_APP_KEY = os.getenv("ADZUNA_APP_KEY")
APIFY_TOKEN    = os.getenv("APIFY_TOKEN")

SENIOR_FILTERS = [
    "senior","lead","principal","head","manager",
    "director","sr.","vp ","architect","chief",
]

def _is_senior(title: str) -> bool:
    return any(w in title.lower() for w in SENIOR_FILTERS)

# ---------------------------------------------------------------
# ADZUNA
# ---------------------------------------------------------------
def fetch_adzuna(role: str, results: int = 25) -> list:
    """
    Fetch fresher-level jobs from Adzuna India.
    Runs two queries (with/without 'fresher') for higher volume.
    Deduplicates by job title.
    """
    all_jobs = []
    seen     = set()

    for query in [f"{role} fresher", role]:
        try:
            response = requests.get(
                "https://api.adzuna.com/v1/api/jobs/in/search/1",
                params={
                    "app_id":           ADZUNA_APP_ID,
                    "app_key":          ADZUNA_APP_KEY,
                    "what":             query,
                    "where":            "India",
                    "results_per_page": results,
                    "content-type":     "application/json",
                },
                timeout=10,
            )
            response.raise_for_status()
            data = response.json()

            for item in data.get("results", []):
                title = item.get("title", "N/A")
                if _is_senior(title):
                    continue
                key = title.lower().strip()
                if key in seen:
                    continue
                seen.add(key)
                all_jobs.append({
                    "title":       title,
                    "company":     item.get("company", {}).get("display_name", "N/A"),
                    "location":    item.get("location", {}).get("display_name", "India"),
                    "description": item.get("description", ""),
                    "apply_url":   item.get("redirect_url", "#"),
                    "source":      "Adzuna",
                })
        except requests.exceptions.RequestException as e:
            print(f"[Adzuna] Request failed for query '{query}': {e}")
        except Exception as e:
            print(f"[Adzuna] Unexpected error: {e}")

    return all_jobs

# ---------------------------------------------------------------
# INDEED via Apify
# ---------------------------------------------------------------
def fetch_indeed(role: str, max_items: int = 15) -> list:
    """
    Fetch jobs from Indeed India via Apify scraper.
    Slower (~30s) but returns more Indian job postings.
    """
    try:
        from apify_client import ApifyClient
        client = ApifyClient(APIFY_TOKEN)
        run    = client.actor("misceres/indeed-scraper").call(run_input={
            "position": f"{role} fresher",
            "country":  "IN",
            "location": "India",
            "maxItems": max_items,
        })
        items = client.dataset(run["defaultDatasetId"]).list_items().items
        jobs  = []
        for item in items:
            title = item.get("positionName", "N/A")
            if _is_senior(title):
                continue
            jobs.append({
                "title":       title,
                "company":     item.get("company", "N/A"),
                "location":    item.get("location", "India"),
                "description": item.get("description", ""),
                "apply_url":   item.get("url", "#"),
                "source":      "Indeed",
            })
        return jobs
    except ImportError:
        print("[Indeed] apify_client not installed. Run: pip install apify-client")
        return []
    except Exception as e:
        print(f"[Indeed] Error: {e}")
        return []

# ---------------------------------------------------------------
# SCORE JOBS
# ---------------------------------------------------------------
def score_jobs(jobs: list, resume_skills: set) -> list:
    """Score each job against resume skills and sort by score descending."""
    scored = []
    for job in jobs:
        clean_desc = re.sub(r'<[^>]+>', ' ', job.get("description", ""))
        score, missing, _, common = calculate_score(
            resume_skills, clean_desc, job_title=job["title"]
        )
        scored.append({**job, "score": score, "missing": missing, "common": common})

    scored.sort(
        key=lambda x: x["score"] if x["score"] is not None else -1,
        reverse=True,
    )
    return scored