# ESPN Fantasy Baseball → Google Drive (Nightly)

Automatically fetches your ESPN fantasy baseball league data every night and uploads the CSV to Google Drive.

## Setup (one-time)

### 1. Google Drive API credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project (or use an existing one)
3. Go to **APIs & Services → Library** and enable the **Google Drive API**
4. Go to **APIs & Services → Credentials → Create Credentials → Service Account**
5. Give it a name, click through, and then click the service account to open it
6. Go to the **Keys** tab → **Add Key → Create new key → JSON** → download the file

### 2. Share your Drive folder with the service account

1. In Google Drive, create a folder for the CSVs (e.g. "ESPN Fantasy Data")
2. Right-click the folder → **Share**
3. Paste the service account email (looks like `name@project.iam.gserviceaccount.com`)
4. Give it **Editor** access
5. Copy the **folder ID** from the URL: `https://drive.google.com/drive/folders/THIS_PART_IS_THE_ID`

### 3. Add GitHub Secrets

In your GitHub repo, go to **Settings → Secrets and variables → Actions** and add:

| Secret name          | Value                                        |
|----------------------|----------------------------------------------|
| `GOOGLE_CREDENTIALS` | Entire contents of the JSON key file         |
| `DRIVE_FOLDER_ID`    | The folder ID from step 2                    |

### 4. Push and test

```bash
git push
```

Then go to **Actions** tab → **Nightly ESPN Fantasy Update** → **Run workflow** to test it manually.

## Schedule

Runs every night at **midnight Pacific** (7:00 AM UTC). Each run creates a dated file like `espn_fantasy_2026-04-14.xlsx` in your Drive folder.

## Files

| File                             | Purpose                          |
|----------------------------------|----------------------------------|
| `gloat_load_scores.py`           | Fetches league data, writes XLSX |
| `upload_to_drive.py`             | Uploads XLSX to Google Drive     |
| `.github/workflows/nightly.yml`  | GitHub Actions schedule config   |
| `requirements.txt`               | Python dependencies              |
