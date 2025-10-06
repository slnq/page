import re
import requests
from bs4 import BeautifulSoup

def fetch_youtube_oembed(url: str) -> str:
    oembed_url = f"https://www.youtube.com/oembed?url={url}&format=json"
    try:
        res = requests.get(oembed_url, timeout=10)
        res.raise_for_status()
        data = res.json()
        title = data.get("title")
        author = data.get("author_name")
        if title and author:
            return f"{title} – {author}"
        elif title:
            return title
    except Exception:
        pass
    return url


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


def fetch_title_auto(url: str) -> str:
    if "youtube" in url or "youtu.be" in url:
        return fetch_youtube_oembed(url)
    else:
        return fetch_ogp_title(url)


def replace_urls_with_ogp_links(text: str) -> str:
    url_pattern = re.compile(r'https?://[^\s"\'<>]+')

    def replacer(match):
        url = match.group(0)
        title = fetch_title_auto(url)
        return f'<a href="{url}" class="ogp">{title}</a>'

    return url_pattern.sub(replacer, text)
