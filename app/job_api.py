import requests

APP_ID = "4562175b"
APP_KEY = "ae78902d3669d5730b5979629b75e177"


def search_jobs_by_country(query="Data Engineer", country="gb", results_per_page=5):
    url = f"https://api.adzuna.com/v1/api/jobs/{country}/search/1"

    params = {
        "app_id": APP_ID,
        "app_key": APP_KEY,
        "results_per_page": results_per_page,
        "what": query,
        "content-type": "application/json"
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
    except Exception:
        return []

    jobs = []

    for item in data.get("results", []):
        jobs.append({
            "title": item.get("title", "N/A"),
            "company": item.get("company", {}).get("display_name", "N/A"),
            "location": item.get("location", {}).get("display_name", "N/A"),
            "url": item.get("redirect_url", "#")
        })

    return jobs


def search_morocco_jobs(query="Data Engineer"):
    return search_jobs_by_country(query, country="ma", results_per_page=5)


def search_international_jobs(query="Data Engineer"):
    countries = ["gb", "us", "ca"]

    all_jobs = []

    for country in countries:
        jobs = search_jobs_by_country(query, country=country, results_per_page=3)

        for job in jobs:
            job["country"] = country.upper()

        all_jobs.extend(jobs)

    return all_jobs[:8]