import json
import os
from datetime import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# ── Configuration ──────────────────────────────────────────────
DRIVE_FOLDER_ID = os.environ.get("DRIVE_FOLDER_ID", "YOUR_FOLDER_ID_HERE")
LOCAL_FILE = "espn_season_long_by_team.csv"
# ───────────────────────────────────────────────────────────────

def upload():
    # Load credentials from GitHub secret
    creds_json = json.loads(os.environ["GOOGLE_CREDENTIALS"])
    creds = service_account.Credentials.from_service_account_info(
        creds_json, scopes=["https://www.googleapis.com/auth/drive.file"]
    )
    service = build("drive", "v3", credentials=creds)

    # Add today's date to the filename so you keep a history
    today = datetime.utcnow().strftime("%Y-%m-%d")
    drive_filename = f"espn_fantasy_{today}.csv"

    file_metadata = {
        "name": drive_filename,
        "parents": [DRIVE_FOLDER_ID],
    }
    media = MediaFileUpload(LOCAL_FILE, mimetype="text/csv", resumable=True)

    uploaded = service.files().create(
        body=file_metadata, media_body=media, fields="id, name"
    ).execute()

    print(f"Uploaded '{uploaded['name']}' (ID: {uploaded['id']})")


if __name__ == "__main__":
    upload()
