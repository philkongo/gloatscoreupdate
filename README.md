# ESPN Fantasy Baseball → Google Drive (Nightly)

Automatically fetches ESPN fantasy baseball league data every night and uploads the XLSX to Google Drive.

## Schedule

Runs every night at **midnight Pacific** (7:00 AM UTC). Each run creates a dated file like `espn_fantasy_2026-04-14.xlsx` in your Drive folder.

## Files

| File                             | Purpose                          |
|----------------------------------|----------------------------------|
| `gloat_load_scores.py`           | Fetches league data, writes XLSX |
| `upload_to_drive.py`             | Uploads XLSX to Google Drive     |
| `.github/workflows/nightly.yml`  | GitHub Actions schedule config   |
| `requirements.txt`               | Python dependencies              |
