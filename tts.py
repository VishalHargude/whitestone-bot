"""
tts.py - Generates naturally spoken Hindi audio and 100% synchronized bilingual subtitles.
Features:
- Segment-level precise timing (Zero drift!)
- Dual-line subtitles: Spoken Hindi (Yellow) + English Translation (White)
- Placed in the mobile YouTube Shorts safe zone
"""

import asyncio
import io
import re
import subprocess
import tempfile
from datetime import timedelta
from pathlib import Path
import edge_tts
import imageio_ffmpeg

from config import VOICE_NAME, TEMP_DIR

def format_ass_time(seconds_val: float) -> str:
    """Formats float seconds into ASS timestamp format: H:MM:SS.cs"""
    td = timedelta(seconds=seconds_val)
    total_seconds = int(td.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    centiseconds = int(td.microseconds / 10000)
    return f"{hours}:{minutes:02d}:{seconds:02d}.{centiseconds:02d}"

async def get_segment_audio_and_duration(text: str, voice: str) -> tuple[bytes, float]:
    """Generates audio for a single segment and computes its exact duration."""
    communicate = edge_tts.Communicate(text, voice=voice, rate="+0%")
    audio_data = bytearray()
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_data.extend(chunk["data"])

    # Measure exact duration using FFmpeg
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
        tmp_name = tmp.name
        tmp.write(audio_data)

    duration = 2.5
    try:
        res = subprocess.run([ffmpeg_exe, "-i", tmp_name], capture_output=True, text=True)
        m = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)", res.stderr)
        if m:
            h, mins, s = m.groups()
            duration = int(h) * 3600 + int(mins) * 60 + float(s)
    finally:
        try:
            Path(tmp_name).unlink()
        except Exception:
            pass

    return bytes(audio_data), duration

async def synthesize_segments(segments: list, output_audio_path: Path, output_ass_path: Path, voice: str = VOICE_NAME):
    """
    Synthesizes each segment, calculates exact timing, and writes:
    1. Combined natural audio file
    2. ASS subtitle file with dual Hindi + English lines in YouTube Shorts safe zone
    """
    combined_audio = bytearray()
    current_time = 0.0

    ass_header = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: HindiText,Nirmala UI,62,&H0000FFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,5,2,2,40,40,750,1
Style: EnglishText,Arial,42,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,4,2,2,40,40,680,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    dialogues = []

    for seg in segments:
        hi_text = seg.get("hi", "").strip()
        en_text = seg.get("en", "").strip()
        if not hi_text:
            continue

        audio_bytes, dur = await get_segment_audio_and_duration(hi_text, voice)
        combined_audio.extend(audio_bytes)

        start_str = format_ass_time(current_time)
        end_time = current_time + dur
        end_str = format_ass_time(end_time)

        # Hindi spoken line (Yellow, bold)
        dialogues.append(f"Dialogue: 0,{start_str},{end_str},HindiText,,0,0,0,,{hi_text}")
        # English translation line (White, bold)
        if en_text:
            dialogues.append(f"Dialogue: 0,{start_str},{end_str},EnglishText,,0,0,0,,{en_text}")

        current_time = end_time

    with open(output_audio_path, "wb") as f:
        f.write(combined_audio)

    full_ass = ass_header + "\n".join(dialogues) + "\n"
    with open(output_ass_path, "w", encoding="utf-8") as f:
        f.write(full_ass)

    return current_time

def create_tts_bilingual(segments: list, output_audio: Path, output_ass: Path, voice: str = VOICE_NAME) -> float:
    return asyncio.run(synthesize_segments(segments, output_audio, output_ass, voice))
