import requests
import re
from bs4 import BeautifulSoup
import time
import random

EMAIL_REGEX = r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"

def extract_email_from_website(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)

        time.sleep(random.uniform(2,4))

        if response.status_code != 200:
            return None

        emails = re.findall(EMAIL_REGEX, response.text)

        if emails:
            return emails[0]

        soup = BeautifulSoup(response.text, "lxml")

        for link in soup.find_all("a", href=True):
            if "contact" in link["href"]:
                contact_url = url + link["href"]
                contact_res = requests.get(contact_url, headers=headers, timeout=10)
                emails = re.findall(EMAIL_REGEX, contact_res.text)
                if emails:
                    return emails[0]

        return None

    except:
        return None