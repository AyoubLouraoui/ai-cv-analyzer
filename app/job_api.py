import requests

APP_ID = "4562175b"
APP_KEY = "ae78902d3669d5730b5979629b75e177"


def search_real_jobs(query="Data Engineer"):

    url = f"https://api.adzuna.com/v1/api/jobs/gb/search/1"

    params = {
        "app_id": APP_ID,
        "app_key": APP_KEY,
        "results_per_page": 5,
        "what": query,
        "content-type": "application/json"
    }

    response = requests.get(url, params=params)

    data = response.json()

    jobs = []

    if "results" in data:

        for item in data["results"]:

            jobs.append({
                "title": item.get("title", "N/A"),
                "company": item.get("company", {}).get("display_name", "N/A"),
                "location": item.get("location", {}).get("display_name", "N/A"),
                "salary": item.get("salary_is_predicted", "N/A"),
                "url": item.get("redirect_url", "#")
            })

    return jobs