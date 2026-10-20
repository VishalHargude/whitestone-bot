"""
uploader.py - Automates video upload to YouTube using YouTube Data API v3.
Features:
- One-time browser OAuth login, auto-saved in token.pickle
- Sets Title, Description, Tags, and Category
- Configurable Privacy (public / unlisted / private)
"""

import os
import pickle
import sys
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

from config import YOUTUBE_CLIENT_SECRET, YOUTUBE_TOKEN_FILE

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

def get_authenticated_service():
    """Authenticates the user and returns YouTube service instance."""
    creds = None
    if YOUTUBE_TOKEN_FILE.exists():
        with open(YOUTUBE_TOKEN_FILE, "rb") as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("[YouTube Uploader] Refreshing expired access token...")
            creds.refresh(Request())
        else:
            if not YOUTUBE_CLIENT_SECRET.exists():
                raise FileNotFoundError(
                    f"Missing {YOUTUBE_CLIENT_SECRET}. Please download client_secret.json from "
                    f"Google Cloud Console (YouTube Data API v3) and place it in the project root."
                )
            print("[YouTube Uploader] Initiating browser OAuth login (one-time setup)...")
            flow = InstalledAppFlow.from_client_secrets_file(str(YOUTUBE_CLIENT_SECRET), SCOPES)
            creds = flow.run_local_server(port=0)

        with open(YOUTUBE_TOKEN_FILE, "wb") as token:
            pickle.dump(creds, token)

    return build("youtube", "v3", credentials=creds)

def upload_video_to_youtube(video_path: str, title: str, description: str, tags: list, privacy_status: str = "public") -> str:
    """
    Uploads video to YouTube and returns the YouTube Video ID.
    privacy_status: 'public', 'private', or 'unlisted'
    """
    print(f"\n[YouTube Uploader] Preparing upload for: {title}")
    youtube = get_authenticated_service()

    body = {
        "snippet": {
            "title": title[:100],  # YouTube title max length 100
            "description": description[:5000],
            "tags": tags,
            "categoryId": "28"  # 28 = Science & Technology, 27 = Education
        },
        "status": {
            "privacyStatus": privacy_status,
            "selfDeclaredMadeForKids": False
        }
    }

    media = MediaFileUpload(
        video_path,
        chunksize=-1,
        resumable=True,
        mimetype="video/mp4"
    )

    request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media
    )

    print("[YouTube Uploader] Uploading video in progress...")
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"[YouTube Uploader] Upload progress: {int(status.progress() * 100)}%")

    video_id = response.get("id")
    video_url = f"https://youtube.com/shorts/{video_id}"
    print(f"[YouTube Uploader] Video uploaded successfully!")
    print(f"[YouTube Uploader] URL: {video_url}")

    # Release file handle before deletion on Windows
    del media
    del request
    import gc, time
    gc.collect()
    time.sleep(1.0)

    # Auto-Cleanup: Delete heavy video immediately so storage never fills up!
    from config import AUTO_DELETE_VIDEO_AFTER_UPLOAD
    if AUTO_DELETE_VIDEO_AFTER_UPLOAD:
        from drive_manager import cleanup_local_video
        cleanup_local_video(Path(video_path))

    return video_id
