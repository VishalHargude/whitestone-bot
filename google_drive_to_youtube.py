"""
google_drive_to_youtube.py - Fully Automated Google Drive to YouTube Pipeline.

How it works:
1. Connects to your Google Drive and searches for videos in the 'YouTube_Upload_Queue' folder.
2. Downloads each video temporarily.
3. Automatically uploads the video to your YouTube channel with Title, Tags, and Description.
4. IMMEDIATELY PERMANENTLY DELETES the video from Google Drive! (Drive storage never fills up!)
5. Deletes local temporary files so PC storage also stays 100% clean.
"""

import io
import json
import os
import pickle
import sys
import time
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# Base Configurations
BASE_DIR = Path(__file__).resolve().parent
TEMP_DIR = BASE_DIR / "temp"
TEMP_DIR.mkdir(parents=True, exist_ok=True)

CLIENT_SECRET_FILE = BASE_DIR / "client_secret.json"
TOKEN_FILE = BASE_DIR / "drive_youtube_token.pickle"

# Combined Scopes for both Google Drive and YouTube
SCOPES = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/youtube.upload"
]

# User's exact Google Drive folder name
DRIVE_FOLDER_NAME = "Meditation Video - White Stone Music"

def authenticate_services():
    """Authenticates both Google Drive and YouTube in a single one-time browser login."""
    creds = None
    if TOKEN_FILE.exists():
        with open(TOKEN_FILE, "rb") as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("[Auth] Refreshing expired credentials...")
            creds.refresh(Request())
        else:
            if not CLIENT_SECRET_FILE.exists():
                raise FileNotFoundError(
                    f"\n[!] Missing client_secret.json in:\n{CLIENT_SECRET_FILE}\n"
                    f"Please download client_secret.json from Google Cloud Console and place it here."
                )
            print("\n[Auth] Opening browser for one-time Google authorization...")
            print("[Auth] Please select the Google account associated with your YouTube Channel and Drive.\n")
            flow = InstalledAppFlow.from_client_secrets_file(str(CLIENT_SECRET_FILE), SCOPES)
            creds = flow.run_local_server(port=0)

        with open(TOKEN_FILE, "wb") as token:
            pickle.dump(creds, token)

    drive_service = build("drive", "v3", credentials=creds)
    youtube_service = build("youtube", "v3", credentials=creds)
    return drive_service, youtube_service

def get_or_create_drive_folder(drive):
    """Finds or creates the staging folder 'YouTube_Upload_Queue' in Google Drive."""
    query = f"name = '{DRIVE_FOLDER_NAME}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
    res = drive.files().list(q=query, spaces="drive", fields="files(id, name)").execute()
    files = res.get("files", [])

    if files:
        folder_id = files[0]["id"]
        return folder_id
    else:
        print(f"[Drive] Creating folder '{DRIVE_FOLDER_NAME}' in your Google Drive...")
        metadata = {
            "name": DRIVE_FOLDER_NAME,
            "mimeType": "application/vnd.google-apps.folder"
        }
        folder = drive.files().create(body=metadata, fields="id").execute()
        return folder["id"]

def list_videos_in_drive_folder(drive, folder_id):
    """Lists all video files inside the Google Drive queue folder."""
    query = f"'{folder_id}' in parents and (mimeType contains 'video/' or name contains '.mp4' or name contains '.mov') and trashed = false"
    res = drive.files().list(q=query, spaces="drive", fields="files(id, name, size)").execute()
    return res.get("files", [])

def download_file_from_drive(drive, file_id, destination_path):
    """Downloads a video file from Google Drive to local temp path."""
    print(f"[Drive] Downloading file from Drive to temp location...")
    request = drive.files().get_media(fileId=file_id)
    with open(destination_path, "wb") as f:
        downloader = MediaIoBaseDownload(f, request, chunksize=1024*1024*5)
        done = False
        while not done:
            status, done = downloader.next_chunk()
            if status:
                print(f"[Drive] Download Progress: {int(status.progress() * 100)}%")

def delete_file_from_drive(drive, file_id, file_name):
    """Permanently deletes the file from Google Drive to keep storage at 0% usage."""
    try:
        drive.files().delete(fileId=file_id).execute()
        print(f"[Drive] 🧹 Cleaned! Successfully deleted '{file_name}' from Google Drive. Storage saved!")
    except Exception as e:
        print(f"[Drive] Could not delete file {file_id}: {e}")

def upload_to_youtube(youtube, video_path, title, description, tags, is_short=True):
    """Uploads video to YouTube with resume capability."""
    print(f"\n[YouTube] Starting upload for: {title}")
    category_id = "10" if "meditation" in title.lower() or "music" in title.lower() else "22"

    body = {
        "snippet": {
            "title": title[:100],
            "description": description[:5000],
            "tags": tags,
            "categoryId": category_id
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": False
        }
    }

    media = MediaFileUpload(
        str(video_path),
        chunksize=1024*1024*8,
        resumable=True,
        mimetype="video/mp4"
    )

    request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media
    )

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"[YouTube] Uploading: {int(status.progress() * 100)}%")

    video_id = response.get("id")
    url_prefix = "https://youtube.com/shorts/" if is_short else "https://youtube.com/watch?v="
    video_url = f"{url_prefix}{video_id}"
    print(f"[YouTube] 🎉 Upload SUCCESS! URL: {video_url}")
    return video_id, video_url

def process_drive_queue():
    """Main execution loop: Fetches from Drive, uploads to YouTube, deletes from Drive."""
    print("=" * 65)
    print("🚀 Google Drive ➡️ YouTube Auto-Uploader & Cleaner")
    print("=" * 65)

    drive, youtube = authenticate_services()
    folder_id = get_or_create_drive_folder(drive)
    print(f"[Drive] Connected! Target Folder: '{DRIVE_FOLDER_NAME}' (Folder ID: {folder_id})")

    video_files = list_videos_in_drive_folder(drive, folder_id)
    if not video_files:
        print(f"\n[Drive] No videos found in '{DRIVE_FOLDER_NAME}' right now.")
        print(f"👉 Simply drag and drop your video files into the '{DRIVE_FOLDER_NAME}' folder in Google Drive!")
        print("=" * 65)
        return

    print(f"\n[Drive] Found {len(video_files)} video(s) ready to upload:")
    for v in video_files:
        print(f"  • {v['name']} (ID: {v['id']})")

    for file_info in video_files:
        file_id = file_info["id"]
        file_name = file_info["name"]
        print(f"\n" + "-" * 50)
        print(f"📦 Processing: {file_name}")

        local_temp_file = TEMP_DIR / file_name
        try:
            # 1. Download from Google Drive
            download_file_from_drive(drive, file_id, local_temp_file)

            # 2. Prepare high-converting Meditation & Relaxation metadata
            clean_name = Path(file_name).stem.replace("_", " ").replace("-", " ").title()
            title = f"{clean_name} | Deep Healing Meditation Music - White Stone Music 🧘‍♂️✨"
            description = (
                f"{clean_name} - Presented by White Stone Music 🌿\n\n"
                f"Close your eyes, take a deep breath, and let the soothing vibrations wash over your mind. "
                f"This frequency is crafted for deep sleep, stress relief, inner peace, and meditation.\n\n"
                f"🎧 Headphones recommended for the best immersion.\n"
                f"✨ Subscribe to White Stone Music for daily peaceful healing sounds!\n\n"
                f"#meditationmusic #whitestonemusic #deepsleep #432hz #healingmusic #stressrelief #zen"
            )
            tags = [
                "meditation music", "white stone music", "deep healing", "relaxing music",
                "432hz sleep music", "stress relief", "peaceful sleep", "yoga music",
                "calm piano", "zen meditation", "anxiety relief"
            ]

            # 3. Upload to YouTube (Category 10 = Music)
            video_id, video_url = upload_to_youtube(youtube, local_temp_file, title, description, tags, is_short=False)

            # 4. IMMEDIATELY DELETE FROM GOOGLE DRIVE!
            delete_file_from_drive(drive, file_id, file_name)

        except Exception as e:
            print(f"[Error] Failed to process {file_name}: {e}")
        finally:
            # 5. Clean local temp file
            if local_temp_file.exists():
                local_temp_file.unlink()
                print(f"[PC Cleaner] Local temp file removed. Laptop storage free! 🧹")

    print("\n" + "=" * 65)
    print("✅ All queued videos processed! Google Drive storage is 100% FREE!")
    print("=" * 65)

if __name__ == "__main__":
    process_drive_queue()
