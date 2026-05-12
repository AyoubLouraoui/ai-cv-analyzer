def search_jobs_by_country(query, country="gb", results_per_page=5):
    url = f"https://api.adzuna.com/v1/api/jobs/{country}/search/1"

    params = {
        "app_id": 4562175b,
        "app_key": ae78902d3669d5730b5979629b75e177,
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
            "url": item.get("redirect_url", "#"),
            "query": query
        })

    return jobs


def search_multiple_jobs(queries, countries, max_jobs=8):
    all_jobs = []
    seen_urls = set()

    for country in countries:
        for query in queries:
            jobs = search_jobs_by_country(query, country=country, results_per_page=5)

            for job in jobs:
                if job["url"] not in seen_urls:
                    job["country"] = country.upper()
                    all_jobs.append(job)
                    seen_urls.add(job["url"])

                if len(all_jobs) >= max_jobs:
                    return all_jobs

    return all_jobs


def search_morocco_jobs(queries):
    return search_multiple_jobs(
        queries,
        countries=["ma"],
        max_jobs=6
    )


def search_international_jobs(queries):
    return search_multiple_jobs(
        queries,
        countries=["gb", "us", "ca"],
        max_jobs=8
    )