"""
emotional_video_maker.py - Creates viral emotional 3D cartoon / animated Hindi Shorts.
Features:
- High-res 3D Disney/Pixar animated emotional scenes (Father-Child, Mother-Child, Friends)
- Cinematic camera slow zoompan motion
- Soft emotional piano background music (BGM)
- Touching, heartfelt Hindi voiceover
- Dual synchronized subtitles (Hindi + English Translation)
"""

import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path
import imageio_ffmpeg

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

from config import OUTPUT_DIR, TEMP_DIR, ASSETS_DIR, VIDEO_WIDTH, VIDEO_HEIGHT, FPS
from tts import create_tts_bilingual

CARTOON_DIR = ASSETS_DIR / "cartoon"
MUSIC_DIR = ASSETS_DIR / "music"

# Curated emotional stories requested by user: बाप-लेक, माय-लेक, मित्र
EMOTIONAL_STORIES = {
    "father_child": {
        "title": "एक पिता का छुपा हुआ दर्द... 🥺❤️ #shorts #fatherlove #emotional #papa",
        "description": "एक बाप की वो अनकही दास्तान जो आपकी आंखें नम कर देगी... हर पिता के लिए एक लाइक जरूर करें। #shorts #emotionalstory #hindi #father",
        "tags": ["shorts", "father love", "emotional story hindi", "papa status", "cartoon story", "sad emotional"],
        "image_file": "father_child.jpg",
        "voice": "hi-IN-MadhurNeural",
        "segments": [
            {"hi": "एक पिता कभी भी अपनी तकलीफ", "en": "A father never reveals his pain"},
            {"hi": "अपने बच्चों को नहीं बताता...", "en": "To his children..."},
            {"hi": "फटे हुए जूते पहनकर भी,", "en": "Even wearing worn-out shoes,"},
            {"hi": "वह अपने बच्चों को नए जूते दिलाता है।", "en": "He buys brand new shoes for his kids."},
            {"hi": "जब पूरी दुनिया आपका साथ छोड़ दे,", "en": "When the whole world leaves your side,"},
            {"hi": "तब सिर्फ पिता ही आपके कंधे पर हाथ रखकर कहता है -", "en": "Only a father puts his hand on your shoulder and says -"},
            {"hi": "'तू आगे बढ़, मैं तेरे पीछे खड़ा हूँ!'", "en": "'Keep moving forward, I am right behind you!'"},
            {"hi": "अगर आप भी अपने पापा से प्यार करते हैं,", "en": "If you truly love your father,"},
            {"hi": "तो कमेंट में 'Love You Papa' जरूर लिखें!", "en": "Drop a 'Love You Papa' in comments!"}
        ]
    },
    "mother_child": {
        "title": "मां की वो रोटी जो कभी खत्म नहीं होती... 🥺❤️ #shorts #motherlove #maa",
        "description": "मां के प्यार और त्याग की सबसे खूबसूरत कहानी... #shorts #maa #emotional #motherslove",
        "tags": ["shorts", "mother love", "maa status", "emotional hindi", "cartoon animation"],
        "image_file": "mother_child.jpg",
        "voice": "hi-IN-SwaraNeural",  # Gentle female voice
        "segments": [
            {"hi": "दुनिया में अगर साक्षात भगवान देखना हो,", "en": "If you want to see God in this world,"},
            {"hi": "तो सिर्फ अपनी मां को देख लेना...", "en": "Just look into your mother's eyes..."},
            {"hi": "जब घर में सिर्फ एक रोटी बचती है,", "en": "When only one piece of bread is left,"},
            {"hi": "तो वह हंसकर कह देती है,", "en": "She smiles and gently says,"},
            {"hi": "'बेटा तू खा ले, मुझे भूख नहीं है!'", "en": "'You eat it, my child, I am not hungry!'"},
            {"hi": "मां खुद गीले में सो जाती है,", "en": "A mother sleeps in the cold,"},
            {"hi": "मगर अपने बच्चे को सूखे में सुलाती है।", "en": "Just to keep her baby warm and safe."},
            {"hi": "अपनी प्यारी मां के लिए एक लाइक जरूर करें!", "en": "Hit a like for your loving mother!"}
        ]
    },
    "best_friends": {
        "title": "सच्चा दोस्त वही होता है... 🫂❤️ #shorts #friendship #dosti",
        "description": "सच्चे दोस्त की पहचान सिर्फ मुश्किल वक्त में होती है... #shorts #dosti #friends #emotional",
        "tags": ["shorts", "dosti status", "best friends", "emotional friendship", "cartoon short"],
        "image_file": "best_friends.jpg",
        "voice": "hi-IN-MadhurNeural",
        "segments": [
            {"hi": "दोस्त तो दुनिया में बहुत मिलते हैं,", "en": "You meet many people in life,"},
            {"hi": "लेकिन सच्चा दोस्त वही होता है,", "en": "But a true friend is the one,"},
            {"hi": "जो पूरी दुनिया के खिलाफ होकर भी", "en": "Who stands firmly by your side"},
            {"hi": "आपके साथ ढाल बनकर खड़ा रहे!", "en": "Even when the whole world turns against you!"},
            {"hi": "जो आपकी खामोशी समझ सके,", "en": "The one who understands your silence,"},
            {"hi": "और आपके आंसुओं को मुस्कान में बदल दे!", "en": "And turns your tears into smiles!"},
            {"hi": "अपने सबसे पक्के यार को यह वीडियो जरूर शेयर करें!", "en": "Share this with your best friend!"}
        ]
    }
}

def assemble_emotional_cartoon_short(story_key: str = "father_child", custom_output_name: str = None) -> dict:
    """Renders a complete emotional cartoon YouTube Short with music & captions."""
    story = EMOTIONAL_STORIES.get(story_key, EMOTIONAL_STORIES["father_child"])
    title = story["title"]
    print(f"\n[Emotional Maker] --- Creating Emotional Cartoon Short: {title} ---")

    # Step 1: Synthesize emotional speech and bilingual captions
    audio_path = TEMP_DIR / "emotional_voice.mp3"
    ass_path = TEMP_DIR / "subtitles.ass"
    duration = create_tts_bilingual(story["segments"], audio_path, ass_path, voice=story.get("voice", "hi-IN-MadhurNeural"))
    padded_duration = duration + 0.6
    print(f"[Emotional Maker] Voiceover duration: {duration:.2f} seconds")

    # Step 2: Render slow cinematic Ken Burns video from 3D Cartoon image
    image_path = CARTOON_DIR / story["image_file"]
    if not image_path.exists():
        fallback = CARTOON_DIR / "father_child.jpg"
        image_path = fallback if fallback.exists() else list(CARTOON_DIR.glob("*.jpg"))[0]

    bg_video_path = TEMP_DIR / "cartoon_motion.mp4"
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()

    total_frames = int(padded_duration * FPS) + 15
    zoom_speed = 0.18 / max(total_frames, 1)

    print(f"[Emotional Maker] Rendering cinematic camera motion on {image_path.name}...")
    cmd_motion = [
        ffmpeg_exe, "-y",
        "-loop", "1", "-i", str(image_path),
        "-vf", f"scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,zoompan=z='min(zoom+{zoom_speed:.6f},1.18)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={total_frames}:s={VIDEO_WIDTH}x{VIDEO_HEIGHT}:fps={FPS}",
        "-t", str(padded_duration),
        "-c:v", "libx264", "-preset", "fast", "-pix_fmt", "yuv420p",
        str(bg_video_path)
    ]
    subprocess.run(cmd_motion, capture_output=True, check=True)

    # Step 3: Combine Video + Voiceover + Soft Piano BGM + Subtitles
    bgm_path = MUSIC_DIR / "emotional_bgm.mp3"
    if custom_output_name:
        final_mp4 = OUTPUT_DIR / f"{custom_output_name}.mp4"
    else:
        timestamp = int(time.time())
        final_mp4 = OUTPUT_DIR / f"emotional_short_{timestamp}.mp4"

    print("[Emotional Maker] Mixing voiceover, emotional piano BGM, and burning captions...")
    # Filter complex to mix voice at full volume and piano BGM at -20dB (volume 0.12)
    filter_complex = (
        "[1:a]volume=1.0[voice];"
        "[2:a]volume=0.12,aloop=loop=-1:size=2e+09[bgm];"
        "[voice][bgm]amix=inputs=2:duration=first:dropout_transition=2[aout]"
    )

    cmd_final = [
        ffmpeg_exe, "-y",
        "-i", "cartoon_motion.mp4",
        "-i", "emotional_voice.mp3",
        "-i", str(bgm_path),
        "-filter_complex", filter_complex,
        "-map", "0:v", "-map", "[aout]",
        "-vf", "subtitles=subtitles.ass",
        "-c:v", "libx264", "-preset", "fast", "-crf", "19",
        "-c:a", "aac", "-b:a", "192k",
        "-pix_fmt", "yuv420p",
        "-shortest",
        str(final_mp4)
    ]

    res = subprocess.run(cmd_final, cwd=TEMP_DIR, capture_output=True, text=True)
    if res.returncode != 0:
        print("[Emotional Maker] Error:", res.stderr[-500:])
        raise RuntimeError("Final assembly failed")

    # Step 4: Metadata
    metadata_path = final_mp4.with_suffix(".json")
    meta_info = {
        "title": story["title"],
        "description": story["description"],
        "tags": story["tags"],
        "video_path": str(final_mp4),
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(meta_info, f, ensure_ascii=False, indent=2)

    print(f"[Emotional Maker] SUCCESS! Emotional Short generated at: {final_mp4}")
    print(f"[Emotional Maker] Size: {os.path.getsize(final_mp4) / (1024*1024):.2f} MB")
    return meta_info
