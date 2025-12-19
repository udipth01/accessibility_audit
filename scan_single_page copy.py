import json
import pandas as pd
from datetime import datetime, timezone
from core import http_client
from core.analyzer import analyze_page

OUTPUT_JSON = "analysis_state.json"

def main():
    url = "https://www.finideas.com/ilts"

    print(f"🔎 Scanning single page: {url}")
    rep = analyze_page(url, http_client.session)

    if not rep:
        print("❌ Failed to analyze page")
        return

    # add timestamp (same as full scan)
    rep["SCANNED_AT"] = datetime.now(timezone.utc).isoformat()

    # wrap in analysis_state format
    analysis_state = {
        url: [rep]
    }

    with open(OUTPUT_JSON, "w") as f:
        json.dump(analysis_state, f, indent=2)

    print(f"💾 Saved single-page JSON → {OUTPUT_JSON}")

    # optional raw excel (debug)
    pd.DataFrame([rep]).to_excel("ilts_single_page_raw.xlsx", index=False)

    print("✅ Single-page scan completed")

if __name__ == "__main__":
    main()
