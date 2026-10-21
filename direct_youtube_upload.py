"""
direct_youtube_upload.py - Uploads videos DIRECTLY to YouTube (No Google Drive needed).
Supports both Long-Form Videos (16:9, Meditation, etc.) and Shorts (9:16).
Deletes the local video immediately after upload to keep laptop storage at 0%.
"""

import gc
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
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "output"
CLIENT_SECRET_FILE = BASE_DIR / "client_secret.json"
TOKEN_FILE = BASE_DIR / "youtube_direct_token.pickle"

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

def authenticate_youtube():
    """Authenticates directly with YouTube."""
    creds = None
    if TOKEN_FILE.exists():
        with open(TOKEN_FILE, "rb") as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("[Auth] Refreshing access token...")
            creds.refresh(Request())
        else:
            if not CLIENT_SECRET_FILE.exists():
                print("\n" + "=" * 65)
                print("⚠️ [client_secret.json] फाईल सापडली नाही!")
                print("=" * 65)
                return None

            print("\n" + "=" * 65, flush=True)
            print("[Auth] Google Login उघडत आहे...", flush=True)
            print("=" * 65 + "\n", flush=True)
            flow = InstalledAppFlow.from_client_secrets_file(str(CLIENT_SECRET_FILE), SCOPES)
            creds = flow.run_local_server(port=0, open_browser=True)

        with open(TOKEN_FILE, "wb") as token:
            pickle.dump(creds, token)

    return build("youtube", "v3", credentials=creds)

def upload_direct(video_path: Path, title: str, description: str, tags: list, category_id: str = "10", is_short: bool = False):
    """Directly uploads a video to YouTube and cleans local file."""
    youtube = authenticate_youtube()
    if not youtube:
        return None

    print(f"\n[YouTube Direct] 🚀 Uploading: {title}...")

    body = {
        "snippet": {
            "title": title[:100],
            "description": description[:5000],
            "tags": tags,
            "categoryId": category_id
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": False,
            "containsSyntheticMedia": True
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
            print(f"[YouTube Direct] Progress: {int(status.progress() * 100)}%")

    video_id = response.get("id")
    if is_short:
        video_url = f"https://youtube.com/shorts/{video_id}"
    else:
        video_url = f"https://www.youtube.com/watch?v={video_id}"

    print(f"\n🎉 [SUCCESS] Video is Live on YouTube!")
    print(f"👉 Link: {video_url}")

    # Explicit cleanup to release file lock on Windows
    del media
    del request
    gc.collect()
    time.sleep(1)

    # Immediately delete local video and metadata file to maintain 0% local disk usage
    try:
        video_path.unlink(missing_ok=True)
        meta_file = video_path.with_suffix(".json")
        meta_file.unlink(missing_ok=True)
        print(f"[Cleaner] 🧹 Local video & metadata files deleted! Laptop storage is 100% free.")
    except Exception as e:
        print(f"[Cleaner] Notice: {e}")

    return video_url

def upload_latest_video():
    """Uploads the latest generated video from output folder."""
    videos = sorted(OUTPUT_DIR.glob("*.mp4"), key=os.path.getmtime, reverse=True)
    if not videos:
        print("[!] No videos found in output folder. Please generate one first!")
        return None

    latest_video = videos[0]
    meta_file = latest_video.with_suffix(".json")

    title = "Peaceful Meditation & Deep Healing Music"
    description = "Relaxing peaceful meditation music. Subscribe for daily videos!"
    tags = ["meditation", "relaxing", "sleep"]
    category_id = "10"
    is_short = False

    if meta_file.exists():
        try:
            with open(meta_file, "r", encoding="utf-8") as f:
                meta = json.load(f)
                title = meta.get("title", title)
                description = meta.get("description", description)
                tags = meta.get("tags", tags)
                is_short = meta.get("is_short", False)
                if not is_short:
                    category_id = "10"  # Music
                else:
                    category_id = "22"  # People & Blogs
        except Exception:
            pass

    return upload_direct(latest_video, title, description, tags, category_id=category_id, is_short=is_short)

if __name__ == "__main__":
    upload_latest_video()
