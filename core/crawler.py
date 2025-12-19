import time
from collections import deque
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

from core.storage import save_json, load_json
from core.utils import is_html_response, is_internal
from core.config import CRAWL_STATE_FILE, REQUEST_TIMEOUT, CRAWL_DELAY_SEC

def crawl_site_resumable(base_url, start_url, session, scope="public"):
    state = load_json(CRAWL_STATE_FILE)

    if state:
        visited = set(state["visited"])
        queue = deque(state["queue"])
    else:
        visited = set()
        queue = deque([start_url])

    all_urls = set(visited)
    counter = 0

    while queue:
        url = queue.popleft()
        if url in visited:
            continue

        visited.add(url)
        all_urls.add(url)

        print(f"[{scope}] Scanning: {url}")

        try:
            resp = session.get(url, timeout=REQUEST_TIMEOUT)
        except Exception as e:
            print(f"Error requesting {url}: {e}")
            continue

        counter += 1
        if counter % 5 == 0:
            save_json(CRAWL_STATE_FILE, {
                "visited": list(visited),
                "queue": list(queue),
            })

        if not is_html_response(resp):
            continue

        soup = BeautifulSoup(resp.text, "lxml")

        for a in soup.find_all("a", href=True):
            href = urljoin(url, a["href"])
            href = urlparse(href)._replace(fragment="").geturl()
            if is_internal(base_url, href) and href not in visited:
                queue.append(href)

        time.sleep(CRAWL_DELAY_SEC)

    save_json(CRAWL_STATE_FILE, {"visited": list(visited), "queue": []})
    return list(all_urls)
