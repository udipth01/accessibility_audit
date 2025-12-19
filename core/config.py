import os

PUBLIC_BASE = os.getenv("TARGET_SITE", "https://www.finideas.com")
PUBLIC_START = PUBLIC_BASE + "/"

OUTPUT_XLSX = "developer_accessibility_report.xlsx"

CRAWL_STATE_FILE = "crawl_state.json"
ANALYSIS_STATE_FILE = "analysis_state.json"

REQUEST_TIMEOUT = 45
CRAWL_DELAY_SEC = 0.3
