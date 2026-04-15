import json
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Load credentials from the GitHub secret
creds_json = json.loads(os.environ["GOOGLE_CREDENTIALS"])
creds = service_account.Credentials.from_service_account_info(
    creds_json, scopes=["https://www.googleapis.com/auth/drive.file"]
)
service = build("drive", "v3", credentials=creds)

# Upload the file
# Change 'output.csv' to whatever your script produces
file_metadata = {
    "name": "output.csv",
    "parents": ["YOUR_GOOGLE_DRIVE_FOLDER_ID"]  # Replace this
}
media = MediaFileUpload("output.csv", resumable=True)
file = service.files().create(
    body=file_metadata, media_body=media, fields="id"
).execute()

print(f"Uploaded file with ID: {file.get('id')}")