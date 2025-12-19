import hashlib
from bs4 import BeautifulSoup
from urllib.parse import urlparse

def hash_html(html):
    return hashlib.sha256(html.encode("utf-8")).hexdigest()

def is_html_response(resp):
    ctype = resp.headers.get("Content-Type", "")
    return "text/html" in ctype or "application/xhtml" in ctype

def is_internal(base, url):
    return urlparse(url).netloc == urlparse(base).netloc

def normalize_html(html):
    soup = BeautifulSoup(html, "lxml")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    return str(soup)
