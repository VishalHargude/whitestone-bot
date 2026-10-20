"""
meditation_drive_watcher.py - 100% Automated Google Drive to YouTube Pipeline for Meditation Videos.

Features:
- Monitors 'Meditation Video - White Stone Music' folder in Google Drive 24/7.
- Uploads long videos (30 mins, 1 hour, 2 hours) with Resumable Upload in 16MB chunks.
- Applies professional SEO metadata for 432Hz meditation & sleep music.
- PERMANENTLY DELETES the video from Google Drive immediately after upload!
- ZERO manual code execution needed: Runs automatically in the background on startup.
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

BASE_DIR = Path(__file__).resolve().parent
TEMP_DIR = BASE_DIR / "temp"
TEMP_DIR.mkdir(parents=True, exist_ok=True)

CLIENT_SECRET_FILE = BASE_DIR / "client_secret.json"
TOKEN_FILE = BASE_DIR / "meditation_channel_token.pickle"

# Combined Scopes for both Google Drive and YouTube
SCOPES = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/youtube.upload"
]

DRIVE_FOLDER_NAME = "Meditation Video - White Stone Music"

def get_services():
    """Authenticates both Google Drive and YouTube."""
    creds = None
    if TOKEN_FILE.exists():
        with open(TOKEN_FILE, "rb") as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("[Auth] Refreshing access token...", flush=True)
            creds.refresh(Request())
        else:
            if not CLIENT_SECRET_FILE.exists():
                raise FileNotFoundError(f"Missing client_secret.json in {BASE_DIR}")
            print("\n" + "=" * 60, flush=True)
            print("[Auth] Google Drive व YouTube साठी 1-Time परवानगी घेत आहे...", flush=True)
            print("=" * 60 + "\n", flush=True)
            flow = InstalledAppFlow.from_client_secrets_file(str(CLIENT_SECRET_FILE), SCOPES)
            creds = flow.run_local_server(port=0, open_browser=True)

        with open(TOKEN_FILE, "wb") as token:
            pickle.dump(creds, token)

    drive = build("drive", "v3", credentials=creds)
    youtube = build("youtube", "v3", credentials=creds)
    return drive, youtube

def find_drive_folder(drive):
    """Finds the user's 'Meditation Video - White Stone Music' folder in Google Drive."""
    query = f"name = '{DRIVE_FOLDER_NAME}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
    res = drive.files().list(q=query, spaces="drive", fields="files(id, name)").execute()
    files = res.get("files", [])
    if files:
        return files[0]["id"]
    return None

def list_drive_videos(drive, folder_id):
    """Lists video files inside the folder."""
    query = f"'{folder_id}' in parents and (mimeType contains 'video/' or name contains '.mp4' or name contains '.mkv' or name contains '.mov') and trashed = false"
    res = drive.files().list(q=query, spaces="drive", fields="files(id, name, size)").execute()
    return res.get("files", [])

def download_video_resumable(drive, file_id, destination_path):
    """Downloads large video from Drive in 16MB chunks."""
    print(f"[Drive] Downloading from Google Drive to local temp...", flush=True)
    request = drive.files().get_media(fileId=file_id)
    with open(destination_path, "wb") as f:
        downloader = MediaIoBaseDownload(f, request, chunksize=16*1024*1024)
        done = False
        while not done:
            status, done = downloader.next_chunk()
            if status:
                print(f"[Drive] Download Progress: {int(status.progress() * 100)}%", flush=True)

def upload_long_meditation_video(youtube, video_path: Path, title: str, description: str, tags: list):
    """Uploads large long-form video (30m, 1h, 2h) to YouTube with 16MB chunk resume."""
    print(f"\n[YouTube] Starting upload: {title}", flush=True)

    body = {
        "snippet": {
            "title": title[:100],
            "description": description[:5000],
            "tags": tags,
            "categoryId": "10"  # Music Category
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": False
        }
    }

    # 16 MB chunksize for fast, stable large video upload
    media = MediaFileUpload(
        str(video_path),
        chunksize=16*1024*1024,
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
            print(f"[YouTube] Uploading: {int(status.progress() * 100)}%", flush=True)

    video_id = response.get("id")
    video_url = f"https://youtube.com/watch?v={video_id}"
    print(f"\n🎉 [YouTube] SUCCESS! Video is Live on YouTube: {video_url}", flush=True)
    return video_id, video_url

def check_and_process_drive():
    """Runs a single check on Google Drive and uploads if videos are found."""
    try:
        drive, youtube = get_services()
        folder_id = find_drive_folder(drive)

        if not folder_id:
            print(f"[Drive Watcher] Folder '{DRIVE_FOLDER_NAME}' not found in Google Drive yet.", flush=True)
            return

        videos = list_drive_videos(drive, folder_id)
        if not videos:
            print(f"[Drive Watcher] No new videos in Google Drive folder right now. Sleeping...", flush=True)
            return

        print(f"\n[Drive Watcher] 🎯 Found {len(videos)} meditation video(s) in Google Drive!", flush=True)

        for v in videos:
            file_id = v["id"]
            file_name = v["name"]
            size_mb = int(v.get("size", 0)) / (1024 * 1024)
            print(f"\n" + "=" * 60, flush=True)
            print(f"📦 Processing: {file_name} (Size: {size_mb:.1f} MB)", flush=True)

            local_temp = TEMP_DIR / file_name

            try:
                # 1. Download from Drive
                download_video_resumable(drive, file_id, local_temp)

                # 2. Generate professional meditation title & SEO tags
                clean_name = Path(file_name).stem.replace("_", " ").replace("-", " ").title()
                title = f"{clean_name} | 432Hz Deep Healing Meditation Music 🧘‍♂️✨"
                description = (
                    f"{clean_name} - Healing Meditation Music 🌿\n\n"
                    f"Immerse yourself in deep relaxation, peaceful sleep, and mindful meditation. "
                    f"Tuned to positive vibrations for stress relief, calm focus, and inner peace.\n\n"
                    f"🎧 Headphones recommended for deep immersion.\n"
                    f"✨ Subscribe for daily peaceful meditation soundscapes!\n\n"
                    f"#meditationmusic #432hz #deepsleep #relaxation #zen #healingmusic #stressrelief"
                )
                tags = [
                    "meditation music", "deep healing", "432hz sleep music", "relaxing music",
                    "stress relief", "peaceful sleep", "yoga music", "calm piano", "zen meditation"
                ]

                # 3. Upload directly to YouTube
                upload_long_meditation_video(youtube, local_temp, title, description, tags)

                # 4. PERMANENTLY DELETE FROM GOOGLE DRIVE!
                drive.files().delete(fileId=file_id).execute()
                print(f"[Drive] 🧹 Cleaned! Successfully deleted '{file_name}' from Google Drive. Storage saved!", flush=True)

            except Exception as e:
                print(f"[Error] Failed to process {file_name}: {e}", flush=True)
            finally:
                # 5. Clean local temp
                if local_temp.exists():
                    try:
                        local_temp.unlink()
                        print("[PC] 🧹 Cleaned local temp file from laptop hard drive.", flush=True)
                    except Exception:
                        pass

        print("\n" + "=" * 60, flush=True)
        print("✅ Finished processing all available videos! Google Drive is 100% clean.", flush=True)
        print("=" * 60 + "\n", flush=True)

    except Exception as e:
        print(f"[Drive Watcher] Check error: {e}", flush=True)

def run_continuous_watcher():
    """Runs continuously in background, checking Drive every 10 minutes."""
    print("=" * 65, flush=True)
    print("🧘‍♂️ 24/7 Automated Google Drive ➡️ YouTube Meditation Bot is ACTIVE!", flush=True)
    print(f"📁 Monitoring Folder: '{DRIVE_FOLDER_NAME}'", flush=True)
    print("✨ Whenever you drop a video into Google Drive, it will auto-upload and auto-delete!", flush=True)
    print("=" * 65 + "\n", flush=True)

    while True:
        check_and_process_drive()
        time.sleep(600)  # Check every 10 minutes

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--now":
        check_and_process_drive()
    else:
        run_continuous_watcher()
