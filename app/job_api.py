import requests
import re
from urllib.parse import quote, urljoin

APP_ID = "4562175b"
APP_KEY = "ae78902d3669d5730b5979629b75e177"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0 Safari/537.36"
    )
}


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
    "Civil Engineer": ["Civil Engineer", "Ingenieur Genie Civil", "Genie Civil", "BTP"],
    "Structural Engineer": ["Structural Engineer", "Ingenieur Structure", "Structure", "Genie Civil"],
    "BIM Engineer": ["BIM Engineer", "Ingenieur BIM", "BIM"],
    "Industrial Engineer": ["Industrial Engineer", "Ingenieur Genie Industriel", "Genie Industriel", "Production"],
    "Process Engineer": ["Process Engineer", "Ingenieur Process", "Process", "Methodes"],
    "Quality Engineer": ["Quality Engineer", "Ingenieur Qualite", "Qualite"],
    "Electrical Engineer": ["Electrical Engineer", "Ingenieur Genie Electrique", "Genie Electrique", "Electricite"],
    "Automation Engineer": ["Automation Engineer", "Ingenieur Automatisme", "Automatisme"],
    "PLC Engineer": ["PLC Engineer", "Automaticien", "Automatisme"],
    "Mechanical Engineer": ["Mechanical Engineer", "Ingenieur Genie Mecanique", "Genie Mecanique", "Mecanique"],
    "Maintenance Engineer": ["Maintenance Engineer", "Ingenieur Maintenance", "Maintenance"],
    "Telecommunications Engineer": ["Telecommunications Engineer", "Ingenieur Telecom", "Telecom"],
    "Telecom Engineer": ["Telecom Engineer", "Ingenieur Telecom", "Telecom"],
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
            headers=HEADERS,
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


def clean_html_text(value):
    value = re.sub(r"<[^>]+>", " ", value)
    value = value.replace("&amp;", "&")
    value = value.replace("&nbsp;", " ")
    value = value.replace("&#039;", "'")
    return re.sub(r"\s+", " ", value).strip()


def fetch_html(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=12)

        if response.status_code != 200:
            return None

        return response.text

    except Exception:
        return None


def get_soup(html):
    try:
        from bs4 import BeautifulSoup

        return BeautifulSoup(html, "html.parser")

    except Exception:
        return None


def slugify_query(query):
    replacements = {
        "AI Engineer": "ingenieur-ia",
        "Machine Learning Engineer": "ingenieur-machine-learning",
        "Data Scientist": "data-scientist",
        "Data Analyst": "data-analyst",
        "Business Intelligence Analyst": "business-intelligence",
        "Data Engineer": "ingenieur-data",
        "Software Engineer": "ingenieur-logiciel",
        "Full Stack Developer": "developpeur-full-stack",
        "Backend Developer": "developpeur-backend",
        "Cloud Engineer": "ingenieur-cloud",
        "DevOps Engineer": "ingenieur-devops",
        "Cybersecurity Engineer": "cybersecurite",
        "Network Engineer": "ingenieur-reseaux",
        "Civil Engineer": "ingenieur-genie-civil",
        "Structural Engineer": "ingenieur-structure",
        "BIM Engineer": "ingenieur-bim",
        "Industrial Engineer": "ingenieur-genie-industriel",
        "Process Engineer": "ingenieur-process",
        "Quality Engineer": "ingenieur-qualite",
        "Electrical Engineer": "ingenieur-genie-electrique",
        "Automation Engineer": "ingenieur-automatisme",
        "PLC Engineer": "automaticien",
        "Mechanical Engineer": "ingenieur-genie-mecanique",
        "Maintenance Engineer": "ingenieur-maintenance",
        "Telecommunications Engineer": "ingenieur-telecom",
        "Telecom Engineer": "ingenieur-telecom",
        "Business Analyst": "business-analyst",
    }

    if query in replacements:
        return replacements[query]

    return quote(query.lower().replace(" ", "-"))


def search_emploi_ma_jobs(queries, max_jobs=6):
    jobs = []
    seen_urls = set()

    for query in queries:
        slug = slugify_query(query)
        urls = [
            f"https://www.emploi.ma/recherche-jobs-maroc/{slug}",
            f"https://www.emploi.ma/emploi-{slug}",
        ]

        for url in urls:
            html = fetch_html(url)

            if not html:
                continue

            soup = get_soup(html)

            if soup:
                for title_tag in soup.find_all("h3"):
                    link = title_tag.find("a", href=True)

                    if not link:
                        continue

                    title = link.get_text(" ", strip=True)
                    job_url = urljoin("https://www.emploi.ma", link["href"])

                    if not title or job_url in seen_urls:
                        continue

                    company = "Emploi.ma"

                    company_link = title_tag.find_next("a")
                    if company_link and company_link.get_text(" ", strip=True) != title:
                        company = company_link.get_text(" ", strip=True)

                    jobs.append({
                        "title": title,
                        "company": company,
                        "location": "Morocco",
                        "url": job_url,
                        "query": query,
                        "country": "MA",
                        "source": "Emploi.ma"
                    })
                    seen_urls.add(job_url)

                    if len(jobs) >= max_jobs:
                        return jobs
            else:
                matches = re.findall(
                    r"<h3[^>]*>\s*<a[^>]+href=[\"']([^\"']+)[\"'][^>]*>(.*?)</a>",
                    html,
                    flags=re.IGNORECASE | re.DOTALL
                )

                for href, raw_title in matches:
                    title = clean_html_text(raw_title)
                    job_url = urljoin("https://www.emploi.ma", href)

                    if not title or job_url in seen_urls:
                        continue

                    jobs.append({
                        "title": title,
                        "company": "Emploi.ma",
                        "location": "Morocco",
                        "url": job_url,
                        "query": query,
                        "country": "MA",
                        "source": "Emploi.ma"
                    })
                    seen_urls.add(job_url)

                    if len(jobs) >= max_jobs:
                        return jobs

    return jobs


def search_rekrute_jobs(queries, max_jobs=6):
    jobs = []
    seen_urls = set()

    for query in queries:
        url = f"https://www.rekrute.com/offres.html?s=1&p=1&o=1&query={quote(query)}"
        html = fetch_html(url)

        if not html:
            continue

        soup = get_soup(html)

        if soup:
            for title_tag in soup.find_all(["h2", "h3"]):
                link = title_tag.find("a", href=True)
                title = title_tag.get_text(" ", strip=True)
                card_text = title_tag.parent.get_text(" ", strip=True)

                if not link or "(Maroc)" not in card_text:
                    continue

                job_url = urljoin("https://www.rekrute.com", link["href"])

                if not title or job_url in seen_urls:
                    continue

                location = "Morocco"
                if "|" in title:
                    location = title.split("|", 1)[1].strip()

                jobs.append({
                    "title": title,
                    "company": "Rekrute",
                    "location": location,
                    "url": job_url,
                    "query": query,
                    "country": "MA",
                    "source": "Rekrute"
                })
                seen_urls.add(job_url)

                if len(jobs) >= max_jobs:
                    return jobs
        else:
            matches = re.findall(
                r"<h[23][^>]*>\s*<a[^>]+href=[\"']([^\"']+)[\"'][^>]*>(.*?)</a>",
                html,
                flags=re.IGNORECASE | re.DOTALL
            )

            for href, raw_title in matches:
                title = clean_html_text(raw_title)

                if "(Maroc)" not in title:
                    continue

                job_url = urljoin("https://www.rekrute.com", href)

                if not title or job_url in seen_urls:
                    continue

                location = "Morocco"
                if "|" in title:
                    location = title.split("|", 1)[1].strip()

                jobs.append({
                    "title": title,
                    "company": "Rekrute",
                    "location": location,
                    "url": job_url,
                    "query": query,
                    "country": "MA",
                    "source": "Rekrute"
                })
                seen_urls.add(job_url)

                if len(jobs) >= max_jobs:
                    return jobs

    return jobs


def build_morocco_search_links(queries, max_links=6):
    links = []
    seen_urls = set()

    sources = [
        ("LinkedIn", "https://www.linkedin.com/jobs/search/?keywords={query}&location=Morocco"),
        ("Emploi.ma", "https://www.emploi.ma/recherche-jobs-maroc/{query}"),
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

    for source_jobs in [
        search_emploi_ma_jobs(morocco_queries, max_jobs=6),
        search_rekrute_jobs(morocco_queries, max_jobs=6),
    ]:
        for job in source_jobs:
            if job["url"] in seen_urls:
                continue

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
