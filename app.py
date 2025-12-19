import os
from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import FileResponse
from scan_single_page import scan_page
from reports.build_dev_document import build_dev_document
from fastapi.responses import HTMLResponse

BASE_WEBSITE = os.environ.get("BASE_WEBSITE")

app = FastAPI(title="Finideas Accessibility Scanner")

@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Finideas Accessibility Scanner</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 40px;
            }
            input {
                padding: 8px;
                width: 300px;
            }
            button {
                padding: 8px 16px;
                margin-left: 10px;
            }
        </style>
    </head>
    <body>
        <h2>Finideas Accessibility Scanner</h2>

        <form method="post" action="/scan">
            <label>
                Page path (example: <code>/ilts</code>)
            </label><br><br>

            <input
                type="text"
                name="subpath"
                placeholder="/ilts"
                required
            />

            <button type="submit">Scan</button>
        </form>

        <br>

        <p>
            After scan completes:
            <a href="/download-report">Download Report</a>
        </p>
    </body>
    </html>
    """

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
