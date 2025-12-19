# scan_single_page.py
import json
from datetime import datetime, timezone
from core import http_client
from core.analyzer import analyze_page

OUTPUT_JSON = "analysis_state.json"

def scan_page(url: str):
    rep = analyze_page(url, http_client.session)
    if not rep:
        return False

    rep["SCANNED_AT"] = datetime.now(timezone.utc).isoformat()

    analysis_state = {
        url: [rep]
    }

    with open(OUTPUT_JSON, "w") as f:
        json.dump(analysis_state, f, indent=2)

    return True


if __name__ == "__main__":
    import sys
    scan_page(sys.argv[1])