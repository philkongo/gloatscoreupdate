import json
import os
from datetime import datetime, timezone

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

print("USING OAUTH VERSION")

SCOPES = ["https://www.googleapis.com/auth/drive.file"]

DRIVE_FOLDER_ID = os.environ["DRIVE_FOLDER_ID"]
LOCAL_FILE = "espn_season_long_by_team.xlsx"
print("USING OAUTH VERSION")
def get_credentials():
    info = json.loads(os.environ["GOOGLE_CREDENTIALS"])
    creds = Credentials.from_authorized_user_info(info, scopes=SCOPES)

    if creds.expired and creds.refresh_token:
        creds.refresh(Request())

    return creds

def upload():
    creds = get_credentials()
    service = build("drive", "v3", credentials=creds)

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    drive_filename = f"gloat_score_bot_{today}.xlsx"

    file_metadata = {
        "name": drive_filename,
        "parents": [DRIVE_FOLDER_ID],
    }
    media = MediaFileUpload(LOCAL_FILE, mimetype="text/csv", resumable=True)

    uploaded = service.files().create(
        body=file_metadata,
        media_body=media,
        fields="id, name",
    ).execute()

    print(f"Uploaded '{uploaded['name']}' (ID: {uploaded['id']})")

if __name__ == "__main__":
    upload()
