import re
import requests
from bs4 import BeautifulSoup

def fetch_ogp_title(url: str) -> str:
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=headers, timeout=10)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")

        og_title = soup.find("meta", property="og:title")
        if og_title and og_title.get("content"):
            return og_title["content"]

        title_tag = soup.find("title")
        if title_tag and title_tag.text.strip():
            return title_tag.text.strip()

    except Exception:
        pass

    return url  # fallback

def replace_urls_with_ogp_links(text: str) -> str:
    url_pattern = re.compile(r'https?://[^\s"\'<>]+')

    def replacer(match):
        url = match.group(0)
        title = fetch_ogp_title(url)
        return f'<a href="{url}" class="ogp">{title}</a>'

    return url_pattern.sub(replacer, text)
