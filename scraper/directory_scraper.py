import requests
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from concurrent.futures import ThreadPoolExecutor

EMAIL_REGEX = r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"

def scrape_directory(url):

    headers = {"User-Agent": "Mozilla/5.0"}
    base_domain = urlparse(url).netloc

    visited = set()
    emails_found = set()
    results = []

    def crawl_page(page_url):
        try:
            response = requests.get(page_url, headers=headers, timeout=10)
            if response.status_code != 200:
                return

            emails = re.findall(EMAIL_REGEX, response.text)

            for email in emails:
                if email not in emails_found:
                    emails_found.add(email)

                    results.append({
                        "directory_source": url,
                        "company_name": "N/A",
                        "email": email,
                        "phone": None,
                        "website": None,
                        "address": None,
                        "industry": None
                    })

            soup = BeautifulSoup(response.text, "lxml")

            links = []

            for a in soup.find_all("a", href=True):
                link = urljoin(page_url, a["href"])
                parsed = urlparse(link)

                if parsed.netloc == base_domain and link not in visited:
                    visited.add(link)
                    links.append(link)

            return links

        except:
            return []

    # Crawl first page
    visited.add(url)
    links = crawl_page(url)

    # Crawl additional pages in parallel
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = []

        for link in list(links)[:50]:  # limit safety
            futures.append(executor.submit(crawl_page, link))

        for future in futures:
            future.result()

    return results