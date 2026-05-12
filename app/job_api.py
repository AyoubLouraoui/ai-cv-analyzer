import requests

APP_ID = "4562175b"
APP_KEY = "ae78902d3669d5730b5979629b75e177"


MOROCCO_QUERY_VARIANTS = {
    "AI Engineer": ["AI Engineer", "Ingenieur IA", "Intelligence Artificielle"],
    "Machine Learning Engineer": ["Machine Learning Engineer", "Ingenieur Machine Learning"],
    "Data Scientist": ["Data Scientist", "Scientifique des donnees"],
    "Data Analyst": ["Data Analyst", "Analyste de donnees"],
    "Business Intelligence Analyst": ["Business Intelligence Analyst", "Consultant BI", "Power BI"],
    "Data Engineer": ["Data Engineer", "Ingenieur Data"],
    "Software Engineer": ["Software Engineer", "Ingenieur logiciel", "Developpeur"],
    "Full Stack Developer": ["Full Stack Developer", "Developpeur Full Stack"],
    "Backend Developer": ["Backend Developer", "Developpeur Backend"],
    "Cloud Engineer": ["Cloud Engineer", "Ingenieur Cloud"],
    "DevOps Engineer": ["DevOps Engineer", "Ingenieur DevOps"],
    "Cybersecurity Engineer": ["Cybersecurity Engineer", "Ingenieur Cybersecurite"],
    "Network Engineer": ["Network Engineer", "Ingenieur Reseaux"],
    "Civil Engineer": ["Civil Engineer", "Ingenieur Genie Civil"],
    "Structural Engineer": ["Structural Engineer", "Ingenieur Structure"],
    "BIM Engineer": ["BIM Engineer", "Ingenieur BIM"],
    "Industrial Engineer": ["Industrial Engineer", "Ingenieur Genie Industriel"],
    "Process Engineer": ["Process Engineer", "Ingenieur Process"],
    "Quality Engineer": ["Quality Engineer", "Ingenieur Qualite"],
    "Electrical Engineer": ["Electrical Engineer", "Ingenieur Genie Electrique"],
    "Automation Engineer": ["Automation Engineer", "Ingenieur Automatisme"],
    "PLC Engineer": ["PLC Engineer", "Automaticien"],
    "Mechanical Engineer": ["Mechanical Engineer", "Ingenieur Genie Mecanique"],
    "Maintenance Engineer": ["Maintenance Engineer", "Ingenieur Maintenance"],
    "Telecommunications Engineer": ["Telecommunications Engineer", "Ingenieur Telecom"],
    "Telecom Engineer": ["Telecom Engineer", "Ingenieur Telecom"],
    "Business Analyst": ["Business Analyst", "Analyste Fonctionnel"],
}


def expand_morocco_queries(queries):
    expanded = []

    for query in queries:
        expanded.extend(MOROCCO_QUERY_VARIANTS.get(query, [query]))

    return list(dict.fromkeys(expanded))


def search_jobs_by_country(query, country="gb", results_per_page=5, where=None):

    url = f"https://api.adzuna.com/v1/api/jobs/{country}/search/1"

    params = {
        "app_id": APP_ID,
        "app_key": APP_KEY,
        "results_per_page": results_per_page,
        "what": query,
        "content-type": "application/json"
    }

    if where:
        params["where"] = where

    try:

        response = requests.get(
            url,
            params=params,
            timeout=10
        )

        if response.status_code != 200:
            return []

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
            "query": query,
            "source": "Adzuna"
        })

    return jobs


def search_multiple_jobs(queries, countries, max_jobs=8):

    all_jobs = []
    seen_urls = set()

    for country in countries:

        for query in queries:

            jobs = search_jobs_by_country(
                query,
                country=country,
                results_per_page=5
            )

            for job in jobs:

                if job["url"] not in seen_urls:

                    job["country"] = country.upper()

                    all_jobs.append(job)

                    seen_urls.add(job["url"])

                if len(all_jobs) >= max_jobs:
                    return all_jobs

    return all_jobs


def build_morocco_search_links(queries, max_links=6):
    links = []
    seen_urls = set()

    sources = [
        ("LinkedIn", "https://www.linkedin.com/jobs/search/?keywords={query}&location=Morocco"),
        ("Emploi.ma", "https://www.emploi.ma/recherche-jobs-maroc?f%5B0%5D=im_field_offre_metiers%3A31&keys={query}"),
        ("Rekrute", "https://www.rekrute.com/offres.html?s=1&p=1&o=1&query={query}"),
    ]

    for query in queries:
        for source, url_template in sources:
            url = url_template.format(query=query.replace(" ", "%20"))

            if url in seen_urls:
                continue

            links.append({
                "title": f"Search {query} jobs in Morocco",
                "company": source,
                "location": "Morocco",
                "url": url,
                "query": query,
                "country": "MA",
                "source": "Search link"
            })
            seen_urls.add(url)

            if len(links) >= max_links:
                return links

    return links


def search_morocco_jobs(queries):
    morocco_queries = expand_morocco_queries(queries)

    jobs = search_multiple_jobs(
        morocco_queries,
        countries=["ma"],
        max_jobs=6
    )

    if jobs:
        return jobs

    jobs = []
    seen_urls = set()

    for country in ["gb", "us", "ca"]:
        for query in morocco_queries:
            for where in ["Morocco", "Maroc", "Casablanca", "Rabat", "Tanger"]:
                found_jobs = search_jobs_by_country(
                    query,
                    country=country,
                    results_per_page=3,
                    where=where
                )

                for job in found_jobs:
                    if job["url"] not in seen_urls:
                        job["country"] = "MA"
                        jobs.append(job)
                        seen_urls.add(job["url"])

                    if len(jobs) >= 6:
                        return jobs

    if jobs:
        return jobs

    return build_morocco_search_links(morocco_queries)


def search_international_jobs(queries):

    return search_multiple_jobs(
        queries,
        countries=["gb", "us", "ca"],
        max_jobs=8
    )
