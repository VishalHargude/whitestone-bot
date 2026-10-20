import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "output"
TEMP_DIR = BASE_DIR / "temp"
ASSETS_DIR = BASE_DIR / "assets"

for d in [OUTPUT_DIR, TEMP_DIR, ASSETS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# Voice Configuration (edge-tts)
# Options: "hi-IN-MadhurNeural" (Male, high energy) or "hi-IN-SwaraNeural" (Female, clear & engaging)
VOICE_NAME = os.getenv("TTS_VOICE", "hi-IN-MadhurNeural")
TTS_RATE = "+5%"  # Slightly faster for high-retention shorts

# Video Specs (YouTube Shorts Vertical 9:16)
VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920
FPS = 30

# Optional API Keys
# Pexels API for HD vertical stock footage (Free from https://www.pexels.com/api/)
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY", "")

# Google Gemini API Key for generating fresh daily viral scripts (Free from Google AI Studio)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# YouTube Data API config
YOUTUBE_CLIENT_SECRET = BASE_DIR / "client_secret.json"
YOUTUBE_TOKEN_FILE = BASE_DIR / "token.pickle"

# Daily Schedule Times (3 Golden Viral Times: Morning 9 AM, Afternoon 2 PM, Night 8 PM)
DAILY_SCHEDULE_TIMES = ["09:00", "14:00", "20:00"]

# Subtitle Display Toggle
ENABLE_SUBTITLES = False  # Disabled as requested (Clean 100% full screen 3D animation)

# Storage & Auto-Cleanup Settings
AUTO_DELETE_VIDEO_AFTER_UPLOAD = True  # Automatically deletes the heavy MP4 once uploaded to YouTube
KEEP_METADATA_LOGS = True              # Retains lightweight 1KB JSON receipt with YouTube link and stats


