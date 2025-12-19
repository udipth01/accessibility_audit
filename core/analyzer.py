from datetime import datetime, timezone
from bs4 import BeautifulSoup
from urllib.parse import urljoin

from core.utils import normalize_html, hash_html, is_html_response
from core.config import REQUEST_TIMEOUT

def analyze_page(url, session):
    try:
        resp = session.get(url, timeout=REQUEST_TIMEOUT,allow_redirects=True)
    except Exception as e:
        print("❌ Request failed:", e)
        return None
    
    print("STATUS:", resp.status_code)
    print("CONTENT-TYPE:", resp.headers.get("Content-Type"))

    if not is_html_response(resp):
        print("❌ Not HTML response")
        return None

    html = normalize_html(resp.text)
    if not html.strip():
        print("❌ Empty HTML")
        return None

    print("✅ HTML received, length:", len(html))
    
    html_hash = hash_html(html)
    soup = BeautifulSoup(html, "lxml")

    page = {
        "URL": url,
        "HTML_HASH": html_hash,
        "MissingAlt": [],
        "LinksNoName": [],
        "ButtonsNoLabel": [],
        "InputsNoLabel": [],
        "HeadingOrderIssues": [],
        "MultipleOrMissingH1": False,
        "HasMainLandmark": False,
        "SCANNED_AT": datetime.now(timezone.utc).isoformat()
    }

    page["HasMainLandmark"] = bool(soup.find("main") or soup.find(attrs={"role": "main"}))

    headings = []
    for tag in soup.find_all(["h1","h2","h3","h4","h5","h6"]):
        headings.append(int(tag.name[1]))

    last = None
    for lvl in headings:
        if last and (lvl - last) > 1:
            page["HeadingOrderIssues"].append(f"H{lvl} follows H{last}")
        last = lvl

    page["MultipleOrMissingH1"] = headings.count(1) != 1


    for img in soup.find_all("img"):
        src = (
            img.get("src")
            or img.get("data-src")
            or img.get("data-src-img")
            or img.get("data-lazy-src")
            )
        
        if not src:
            continue

        alt = (img.get("alt") or "").strip()

        aria_hidden = img.get("aria-hidden")
        role = img.get("role")

        # Skip decorative images
        if aria_hidden == "true" or role == "presentation":
            continue

        if not alt:
            page["MissingAlt"].append({
                "src": urljoin(url, src),
                "html": str(img)[:200]
            })
            
    for a in soup.find_all("a", href=True):
        if not ((a.get_text() or "").strip() or a.get("aria-label")):
            page["LinksNoName"].append({
                "href": urljoin(url, a["href"]),
                "html": str(a)[:200]
            })

    return page
