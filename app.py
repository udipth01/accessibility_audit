import os
from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import FileResponse
from scan_single_page import scan_page
from build_dev_document import build_dev_document

BASE_WEBSITE = os.environ.get("BASE_WEBSITE")

app = FastAPI(title="Finideas Accessibility Scanner")


@app.post("/scan")
def scan(subpath: str = Form(...)):
    if not BASE_WEBSITE:
        raise HTTPException(500, "BASE_WEBSITE not configured")

    if not subpath.startswith("/"):
        raise HTTPException(400, "Path must start with /")

    full_url = BASE_WEBSITE.rstrip("/") + subpath

    # 🔐 Hard restriction
    if not full_url.startswith(BASE_WEBSITE):
        raise HTTPException(403, "URL not allowed")

    success = scan_page(full_url)
    if not success:
        raise HTTPException(500, "Scan failed")

    build_dev_document()

    return {
        "message": "Scan completed",
        "download": "/download-report"
    }


@app.get("/download-report")
def download_report():
    return FileResponse(
        "developer_accessibility_report.xlsx",
        filename="accessibility_report.xlsx"
    )
