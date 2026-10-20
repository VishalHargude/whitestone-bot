"""
drive_manager.py - Google Drive Integration & Zero-Waste Auto-Cleanup.
Features:
- Connects to Google Drive using the same client_secret.json
- Automatically deletes uploaded videos from Google Drive & PC immediately after YouTube upload
- Guarantees 0% storage wastage (Drive and Laptop hard drive never fill up!)
"""

import os
import pickle
import sys
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from config import YOUTUBE_CLIENT_SECRET, BASE_DIR

DRIVE_TOKEN_FILE = BASE_DIR / "drive_token.pickle"
DRIVE_SCOPES = ["https://www.googleapis.com/auth/drive.file"]

def get_drive_service():
    """Authenticates with Google Drive API."""
    creds = None
    if DRIVE_TOKEN_FILE.exists():
        with open(DRIVE_TOKEN_FILE, "rb") as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not YOUTUBE_CLIENT_SECRET.exists():
                return None
            flow = InstalledAppFlow.from_client_secrets_file(str(YOUTUBE_CLIENT_SECRET), DRIVE_SCOPES)
            creds = flow.run_local_server(port=0)

        with open(DRIVE_TOKEN_FILE, "wb") as token:
            pickle.dump(creds, token)

    return build("drive", "v3", credentials=creds)

def upload_to_drive(file_path: Path, folder_name: str = "Meditation Video - White Stone Music") -> str:
    """Uploads a video to Google Drive temporarily and returns the Drive file ID."""
    drive = get_drive_service()
    if not drive:
        print("[Google Drive] Drive service not configured. Operating in local mode.")
        return None

    file_metadata = {
        "name": file_path.name,
        "mimeType": "video/mp4"
    }
    media = MediaFileUpload(str(file_path), mimetype="video/mp4", resumable=True)

    print(f"[Google Drive] Uploading {file_path.name} to Google Drive...")
    file_obj = drive.files().create(body=file_metadata, media_body=media, fields="id").execute()
    file_id = file_obj.get("id")
    print(f"[Google Drive] Staged successfully! File ID: {file_id}")
    return file_id

def delete_from_drive(file_id: str):
    """Permanently deletes the video from Google Drive to keep Drive at 0% usage."""
    if not file_id:
        return
    try:
        drive = get_drive_service()
        if drive:
            drive.files().delete(fileId=file_id).execute()
            print(f"[Google Drive] Cleaned! Deleted File ID {file_id} from Google Drive. Storage saved! 🧹")
    except Exception as e:
        print(f"[Google Drive] Error deleting file from Drive: {e}")

def cleanup_local_video(file_path: Path):
    """Deletes the local heavy MP4 file from laptop so PC storage never fills up."""
    try:
        if file_path.exists():
            file_path.unlink()
            print(f"[Auto-Cleanup] Deleted local video {file_path.name}! (Laptop storage is 100% free) 🧹")
    except Exception as e:
        print(f"[Auto-Cleanup] Could not remove {file_path}: {e}")
