import pandas as pd

from core.http import session
from core.config import PUBLIC_BASE, PUBLIC_START, ANALYSIS_STATE_FILE
from core.crawler import crawl_site_resumable
from core.analyzer import analyze_page
from core.diff import diff_issues
from core.storage import load_json, save_json

def main():
    all_urls = crawl_site_resumable(PUBLIC_BASE, PUBLIC_START, session)
    analysis_state = load_json(ANALYSIS_STATE_FILE) or {}
    results = []

    for url in all_urls:
        print(f"🔎 Checking: {url}")
        rep = analyze_page(url, session)
        if not rep:
            continue

        old_versions = analysis_state.get(url, [])

        if old_versions:
            last = old_versions[-1]
            if last["HTML_HASH"] == rep["HTML_HASH"]:
                results.append(last)
                continue
            rep["DIFF_FROM_LAST"] = diff_issues(last, rep)

        analysis_state[url] = old_versions + [rep]
        results.append(rep)
        save_json(ANALYSIS_STATE_FILE, analysis_state)

    if results:
        pd.DataFrame(results).to_excel("partial_results.xlsx", index=False)

    print("🎉 All done!")

if __name__ == "__main__":
    main()
