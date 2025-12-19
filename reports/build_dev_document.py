import json
import pandas as pd
import os

INPUT_JSON = "analysis_state.json"
OUTPUT_XLSX = "developer_accessibility_report.xlsx"

def get_latest_pages(data):
    latest_pages = []
    for url, versions in data.items():
        if versions:
            latest_pages.append(versions[-1])
    return latest_pages


def build_dev_document():
    if not os.path.exists(INPUT_JSON):
        print(f"❌ {INPUT_JSON} not found.")
        return

    # Load analysis JSON
    with open(INPUT_JSON, "r") as f:
        data = json.load(f)

    pages = get_latest_pages(data)

    # Prepare sheets
    summary_rows = []
    alt_rows = []
    link_rows = []
    button_rows = []
    input_rows = []
    heading_rows = []

    for p in pages:
        url = p["URL"]

        # -------- SUMMARY ----------
        summary_rows.append({
            "URL": url,
            "MissingAltCount": len(p["MissingAlt"]),
            "LinksNoNameCount": len(p["LinksNoName"]),
            "ButtonsNoLabelCount": len(p["ButtonsNoLabel"]),
            "InputsNoLabelCount": len(p["InputsNoLabel"]),
            "HeadingOrderIssuesCount": len(p["HeadingOrderIssues"]),
            "MultipleOrMissingH1": p["MultipleOrMissingH1"],
            "HasMainLandmark": p["HasMainLandmark"],
        })

        # -------- Missing ALT ----------
        for issue in p["MissingAlt"]:
            alt_rows.append({
                "URL": url,
                "ImageSrc": issue["src"],
                "HTML Snippet": issue["html"],
                "Suggested Fix": (
                    "Add a meaningful alt attribute describing the image purpose.\n"
                    "Example: <img src='...' alt='Describe what this graphic shows'>"
                )
            })

        # -------- Links Without Text ----------
        for issue in p["LinksNoName"]:
            link_rows.append({
                "URL": url,
                "Href": issue["href"],
                "HTML Snippet": issue["html"],
                "Suggested Fix": (
                    "Add visible link text or an aria-label/title so assistive "
                    "technology can announce the purpose.\n"
                    "Example: <a href='...' aria-label='Open Google Play Store'>"
                )
            })

        # -------- Buttons Without Label ----------
        for issue in p["ButtonsNoLabel"]:
            button_rows.append({
                "URL": url,
                "HTML Snippet": issue["html"],
                "Suggested Fix": (
                    "Add button text or aria-label describing the action.\n"
                    "Example: <button aria-label='Search'>🔍</button>"
                )
            })

        # -------- Inputs Without Labels ----------
        for issue in p["InputsNoLabel"]:
            input_rows.append({
                "URL": url,
                "HTML Snippet": issue["html"],
                "Suggested Fix": (
                    "Add <label for='...'> or aria-label so fields are announced.\n"
                    "Example:\n"
                    "<label for='email'>Email</label>\n"
                    "<input id='email' type='email'>"
                )
            })

        # -------- Heading order issues ----------
        for issue in p["HeadingOrderIssues"]:
            heading_rows.append({
                "URL": url,
                "Issue": issue,
                "Suggested Fix": (
                    "Fix incorrect heading hierarchy.\n"
                    "Ensure H1 → H2 → H3 order is maintained without skipping levels.\n"
                    "Example: Change <h3> to <h2> if it directly follows an <h1>."
                )
            })

    # Export Excel
    with pd.ExcelWriter(OUTPUT_XLSX, engine="xlsxwriter") as writer:
        pd.DataFrame(summary_rows).to_excel(writer, sheet_name="Summary", index=False)

        if alt_rows:
            pd.DataFrame(alt_rows).to_excel(writer, sheet_name="MissingAltImages", index=False)

        if link_rows:
            pd.DataFrame(link_rows).to_excel(writer, sheet_name="LinksNoName", index=False)

        if button_rows:
            pd.DataFrame(button_rows).to_excel(writer, sheet_name="ButtonsNoLabel", index=False)

        if input_rows:
            pd.DataFrame(input_rows).to_excel(writer, sheet_name="InputsNoLabel", index=False)

        if heading_rows:
            pd.DataFrame(heading_rows).to_excel(writer, sheet_name="HeadingOrder", index=False)

    print(f"✅ Developer report created → {OUTPUT_XLSX}")


if __name__ == "__main__":
    build_dev_document()
