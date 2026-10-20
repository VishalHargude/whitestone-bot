"""
cute_cartoon_maker.py - Creates the viral "Papa ki Pari" animated cartoon Short.
Scenario requested by user:
Cute toddler girl running shouting "Papa! Papa!", jumping into Papa's arms,
giving Papa a sweet kiss, and playfully refusing to kiss Mummy!
"""

import json
import os
import re
import subprocess
import sys
import time
from datetime import timedelta
from pathlib import Path
import edge_tts
import imageio_ffmpeg

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

from config import OUTPUT_DIR, TEMP_DIR, ASSETS_DIR, VIDEO_WIDTH, VIDEO_HEIGHT, FPS, ENABLE_SUBTITLES

CARTOON_DIR = ASSETS_DIR / "cartoon"
MUSIC_DIR = ASSETS_DIR / "music"

# Character configs for distinct voice acting
VOICE_PROFILES = {
    "baby": {
        "voice": "hi-IN-SwaraNeural",
        "pitch": "+45Hz",
        "rate": "+20%"
    },
    "papa": {
        "voice": "hi-IN-MadhurNeural",
        "pitch": "-2Hz",
        "rate": "+0%"
    },
    "mummy": {
        "voice": "hi-IN-SwaraNeural",
        "pitch": "+6Hz",
        "rate": "+5%"
    },
    "narrator": {
        "voice": "hi-IN-MadhurNeural",
        "pitch": "-1Hz",
        "rate": "+0%"
    }
}

DIALOGUE_SCRIPT = [
    # Scene 1: Baby running
    {
        "scene": 1,
        "character": "baby",
        "hi": "पापा! पापा! पापा! रुको, मैं आ गई!",
        "en": "Papa! Papa! Papa! Wait, I am here! 🥰"
    },
    # Scene 2: In Papa's arms
    {
        "scene": 2,
        "character": "papa",
        "hi": "अरे मेरी लाडो! मेरा प्यारा बच्चा!",
        "en": "Aww my darling princess! ❤️"
    },
    {
        "scene": 2,
        "character": "baby",
        "hi": "उम्माह! लव यू पापा!",
        "en": "Muah! Love you Papa! 😘"
    },
    {
        "scene": 2,
        "character": "mummy",
        "hi": "और मम्मी को? मुझे पप्पी नहीं दोगी?",
        "en": "And what about mummy? Won't you kiss me? 🥺"
    },
    {
        "scene": 2,
        "character": "baby",
        "hi": "ना! पापा सिर्फ मेरे हैं! ही ही ही!",
        "en": "No! Papa is only mine! Hehe! 😜"
    },
    {
        "scene": 2,
        "character": "narrator",
        "hi": "बेटियां पापा के लिए हमेशा नन्हीं गुड़िया ही रहती हैं... क्या आपकी भी ऐसी लाडो है?",
        "en": "Daughters are always daddy's little princess... Drop a ❤️ if you agree!"
    }
]

def format_ass_time(seconds_val: float) -> str:
    td = timedelta(seconds=seconds_val)
    total_seconds = int(td.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    centiseconds = int(td.microseconds / 10000)
    return f"{hours}:{minutes:02d}:{seconds:02d}.{centiseconds:02d}"

async def generate_dialogue_audio():
    """Generates audio for each character line and measures exact durations."""
    combined_audio = bytearray()
    scene_durations = {1: 0.0, 2: 0.0}
    dialogues_ass = []
    current_time = 0.0

    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()

    for idx, item in enumerate(DIALOGUE_SCRIPT):
        char = item["character"]
        prof = VOICE_PROFILES[char]
        comm = edge_tts.Communicate(item["hi"], voice=prof["voice"], pitch=prof["pitch"], rate=prof["rate"])

        line_audio = bytearray()
        async for chunk in comm.stream():
            if chunk["type"] == "audio":
                line_audio.extend(chunk["data"])

        # Measure line duration
        tmp_line_path = TEMP_DIR / f"line_{idx}.mp3"
        tmp_line_path.write_bytes(line_audio)

        res = subprocess.run([ffmpeg_exe, "-i", str(tmp_line_path)], capture_output=True, text=True)
        m = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)", res.stderr)
        line_dur = 2.5
        if m:
            h, mins, s = m.groups()
            line_dur = int(h) * 3600 + int(mins) * 60 + float(s)

        # Track scene durations
        scene_durations[item["scene"]] += line_dur

        # Add slight natural pause between lines (0.25s)
        start_str = format_ass_time(current_time)
        end_time = current_time + line_dur
        end_str = format_ass_time(end_time)

        # Style by character: Baby (Bright Yellow), Papa (White), Mummy (Soft Green)
        style_name = "BabyText" if char == "baby" else ("MummyText" if char == "mummy" else "PapaText")
        dialogues_ass.append(f"Dialogue: 0,{start_str},{end_str},{style_name},,0,0,0,,{item['hi']}")

        combined_audio.extend(line_audio)
        current_time = end_time + 0.25

    # Write final combined speech
    speech_path = TEMP_DIR / "dialogue_voice.mp3"
    speech_path.write_bytes(combined_audio)

    # Write ASS subtitles (Pure Hindi, no English line)
    ass_path = TEMP_DIR / "subtitles.ass"
    ass_header = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: BabyText,Nirmala UI,65,&H0000FFFF,&H000000FF,&H00000000,&H90000000,-1,0,0,0,100,100,0,0,1,5,2,2,90,90,750,1
Style: PapaText,Nirmala UI,62,&H00FFFFFF,&H000000FF,&H00000000,&H90000000,-1,0,0,0,100,100,0,0,1,5,2,2,90,90,750,1
Style: MummyText,Nirmala UI,62,&H0080FF80,&H000000FF,&H00000000,&H90000000,-1,0,0,0,100,100,0,0,1,5,2,2,90,90,750,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    ass_content = ass_header + "\n".join(dialogues_ass) + "\n"
    ass_path.write_text(ass_content, encoding="utf-8")

    return speech_path, ass_path, scene_durations, current_time

def create_cute_cartoon_short():
    import asyncio
    print("\n[Cute Cartoon] Step 1: Synthesizing multi-character dialogue (Baby, Papa, Mummy)...")
    speech_path, ass_path, scene_dur, total_dur = asyncio.run(generate_dialogue_audio())
    print(f"[Cute Cartoon] Scene 1 (Running): {scene_dur[1]:.2f}s | Scene 2 (Kissing Papa): {scene_dur[2]:.2f}s | Total: {total_dur:.2f}s")

    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()

    # Step 2: Render 2 video clips from images
    print("[Cute Cartoon] Step 2: Rendering 3D animation scenes with camera zoom...")
    img_run = CARTOON_DIR / "baby_running.jpg"
    img_kiss = CARTOON_DIR / "baby_kiss_papa.jpg"

    vid_scene1 = TEMP_DIR / "scene1.mp4"
    vid_scene2 = TEMP_DIR / "scene2.mp4"

    dur1 = scene_dur[1] + 0.3
    dur2 = scene_dur[2] + 1.2

    # Scene 1: Zoom in fast as baby runs towards camera
    frames1 = int(dur1 * FPS)
    cmd_s1 = [
        ffmpeg_exe, "-y",
        "-loop", "1", "-i", str(img_run),
        "-vf", f"scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,zoompan=z='min(zoom+0.0018,1.25)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames1}:s={VIDEO_WIDTH}x{VIDEO_HEIGHT}:fps={FPS}",
        "-t", str(dur1),
        "-c:v", "libx264", "-preset", "fast", "-pix_fmt", "yuv420p",
        str(vid_scene1)
    ]
    subprocess.run(cmd_s1, capture_output=True, check=True)

    # Scene 2: Slow gentle pan on the sweet kiss & mummy's jealous face
    frames2 = int(dur2 * FPS)
    cmd_s2 = [
        ffmpeg_exe, "-y",
        "-loop", "1", "-i", str(img_kiss),
        "-vf", f"scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,zoompan=z='min(zoom+0.0007,1.15)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames2}:s={VIDEO_WIDTH}x{VIDEO_HEIGHT}:fps={FPS}",
        "-t", str(dur2),
        "-c:v", "libx264", "-preset", "fast", "-pix_fmt", "yuv420p",
        str(vid_scene2)
    ]
    subprocess.run(cmd_s2, capture_output=True, check=True)

    # Concatenate the 2 scenes into background.mp4
    concat_txt = TEMP_DIR / "scenes.txt"
    concat_txt.write_text(f"file 'scene1.mp4'\nfile 'scene2.mp4'\n", encoding="utf-8")

    bg_combined = TEMP_DIR / "cute_bg.mp4"
    cmd_concat = [
        ffmpeg_exe, "-y",
        "-f", "concat", "-safe", "0",
        "-i", "scenes.txt",
        "-c", "copy",
        str(bg_combined)
    ]
    subprocess.run(cmd_concat, cwd=TEMP_DIR, capture_output=True, check=True)

    # Step 3: Combine with cheerful Carefree BGM and burn subtitles
    print("[Cute Cartoon] Step 3: Mixing voices, cheerful Carefree music, and colorful captions...")
    bgm_path = MUSIC_DIR / "cute_bgm.ogg"
    final_output = OUTPUT_DIR / "papakipari_cute_cartoon.mp4"

    filter_complex = (
        "[1:a]volume=1.0[voice];"
        "[2:a]volume=0.15,aloop=loop=-1:size=2e+09[bgm];"
        "[voice][bgm]amix=inputs=2:duration=first:dropout_transition=2[aout]"
    )

    cmd_final = [
        ffmpeg_exe, "-y",
        "-i", str(bg_combined),
        "-i", str(speech_path),
        "-i", str(bgm_path),
        "-filter_complex", filter_complex,
        "-map", "0:v", "-map", "[aout]",
    ]

    if ENABLE_SUBTITLES:
        cmd_final.extend(["-vf", "subtitles=subtitles.ass"])

    cmd_final.extend([
        "-c:v", "libx264", "-preset", "fast", "-crf", "19",
        "-c:a", "aac", "-b:a", "192k",
        "-pix_fmt", "yuv420p",
        "-shortest",
        str(final_output)
    ])

    res = subprocess.run(cmd_final, cwd=TEMP_DIR, capture_output=True, text=True)
    if res.returncode != 0:
        print("[Cute Cartoon] Error:", res.stderr[-500:])
        raise RuntimeError("Final cartoon rendering failed")

    # Metadata
    meta_path = final_output.with_suffix(".json")
    meta = {
        "title": "पापा सिर्फ मेरे हैं! 😜❤️ छोटी बच्ची का पापा को प्यार! #shorts #papakipari #cutebaby #cartoon",
        "description": "पापा को पप्पी दी पर मम्मी को मना कर दिया! 😂❤️ हर बेटी और पिता के लिए एक लाइक जरूर करें। #shorts #funnybaby #cute #animation #papakipari",
        "tags": ["shorts", "papa ki pari", "cute baby cartoon", "3d animation hindi", "father daughter love", "funny baby video"],
        "video_path": str(final_output),
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    print(f"\n[Cute Cartoon] 🎉 SUCCESS! Viral Cartoon Video created at: {final_output}")
    print(f"[Cute Cartoon] Video Size: {os.path.getsize(final_output) / (1024*1024):.2f} MB")
    return final_output

if __name__ == "__main__":
    create_cute_cartoon_short()
