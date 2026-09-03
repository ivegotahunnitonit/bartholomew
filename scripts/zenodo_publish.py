"""
Zenodo REST API Automated Deposition Client
Uploads paper_v2_4.pdf and metadata to Zenodo and reserves a citable DOI.
"""

import os
import sys
import json
import requests

ZENODO_API_URL = os.getenv("ZENODO_API_URL", "https://zenodo.org/api/deposit/depositions")
# For testing in the sandbox, export ZENODO_API_URL="https://sandbox.zenodo.org/api/deposit/depositions"

def publish_to_zenodo():
    token = os.getenv("ZENODO_ACCESS_TOKEN")
    if not token:
        print("[INFO] ZENODO_ACCESS_TOKEN not found in environment.")
        print("To publish automatically via API:")
        print("  1. Create a Personal Access Token at https://zenodo.org/account/settings/applications/tokens/new/")
        print("  2. Run: $env:ZENODO_ACCESS_TOKEN='your_token_here'")
        print("  3. Run: python scripts/zenodo_publish.py")
        print("\nAlternatively, follow the Web GUI instructions in ZENODO_SUBMISSION_GUIDE.md.")
        return False

    headers = {"Authorization": f"Bearer {token}"}

    # 1. Load metadata
    metadata_path = os.path.abspath("zenodo.json")
    if not os.path.exists(metadata_path):
        print(f"[ERROR] Metadata file not found: {metadata_path}")
        return False

    with open(metadata_path, "r", encoding="utf-8") as f:
        meta = json.load(f)

    print("[1/4] Creating new deposition on Zenodo...")
    r = requests.post(ZENODO_API_URL, headers=headers, json=meta)
    if r.status_code not in (200, 201):
        print(f"[ERROR] Failed to create deposition: {r.status_code} {r.text}")
        return False

    deposition = r.json()
    dep_id = deposition["id"]
    bucket_url = deposition["links"]["bucket"]
    doi = deposition.get("metadata", {}).get("prereserve_doi", {}).get("doi", f"10.5281/zenodo.{dep_id}")
    print(f"      Deposition ID: {dep_id}")
    print(f"      Reserved DOI:  {doi}")

    # 2. Upload paper_v2_4.pdf
    pdf_path = os.path.abspath("paper_v2_4.pdf")
    print(f"[2/4] Uploading academic PDF: {pdf_path}...")
    with open(pdf_path, "rb") as fp:
        upload_resp = requests.put(
            f"{bucket_url}/paper_v2_4.pdf",
            data=fp,
            headers=headers
        )
    if upload_resp.status_code not in (200, 201):
        print(f"[ERROR] Upload failed: {upload_resp.status_code} {upload_resp.text}")
        return False
    print("      PDF uploaded successfully.")

    # 3. Confirmation
    print(f"\n[SUCCESS] Deposition draft created on Zenodo!")
    print(f"Review and publish draft at: https://zenodo.org/deposit/{dep_id}")
    return True

if __name__ == "__main__":
    publish_to_zenodo()
