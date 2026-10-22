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

def get_target_publish_at(slots=[(6, 0), (11, 30), (16, 45), (21, 45)]):
    """
    Finds if an upcoming scheduled upload slot is within the next 2 hours.
    Returns (publish_at_iso, slot_name_ist) or (None, None).
    Enables pre-rendering so video is uploaded in advance and goes PUBLIC exactly on time.
    """
    from datetime import datetime, timezone, timedelta
    IST = timezone(timedelta(hours=5, minutes=30))
    now_ist = datetime.now(IST)
    for h, m in slots:
        candidate = now_ist.replace(hour=h, minute=m, second=0, microsecond=0)
        diff = (candidate - now_ist).total_seconds()
        if 120 < diff <= 7200:  # Between 2 minutes and 2 hours in the future
            utc_dt = candidate.astimezone(timezone.utc)
            return utc_dt.strftime("%Y-%m-%dT%H:%M:%S.000Z"), candidate.strftime("%I:%M %p IST")
    return None, None

def upload_direct(video_path: Path, title: str, description: str, tags: list, category_id: str = "10", is_short: bool = False):
    """Directly uploads a video to YouTube and cleans local file."""
    youtube = authenticate_youtube()
    if not youtube:
        return None

    print(f"\n[YouTube Direct] 🚀 Uploading: {title}...")

    # Check if this video should be scheduled for an upcoming daily slot
    publish_at_iso, slot_label = get_target_publish_at()
    if publish_at_iso:
        status_dict = {
            "privacyStatus": "private",
            "publishAt": publish_at_iso,
            "selfDeclaredMadeForKids": False,
            "containsSyntheticMedia": False
        }
        print(f"[YouTube Direct] ⏰ Advance Pre-Schedule Active: Video will automatically go PUBLIC at {slot_label} ({publish_at_iso})!")
    else:
        status_dict = {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": False,
            "containsSyntheticMedia": False
        }
        print(f"[YouTube Direct] 🚀 Immediate Public Release Active!")

    body = {
        "snippet": {
            "title": title[:100],
            "description": description[:5000],
            "tags": tags,
            "categoryId": category_id
        },
        "status": status_dict
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

    # Apply Custom Distinct Thumbnail if present
    thumb_path = video_path.with_suffix(".thumb.jpg")
    if thumb_path.exists():
        try:
            thumb_media = MediaFileUpload(str(thumb_path), mimetype="image/jpeg")
            youtube.thumbnails().set(videoId=video_id, media_body=thumb_media).execute()
            print(f"[YouTube Direct] 🖼️ Custom HD Thumbnail applied successfully!")
            del thumb_media
            gc.collect()
            time.sleep(1)
            thumb_path.unlink(missing_ok=True)
        except Exception as e:
            print(f"[YouTube Direct] Thumbnail notice: {e}")

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
