"""
create_long_meditation_video.py - Dynamic Multi-Theme Long-Form Meditation Video Generator.
Branded with White Stone Music logo watermark in bottom-right corner.
Supports 30-Minute, 1-Hour, 2-Hour, and 3-Hour video durations with Ken Burns stream-looping.

5 Distinct Thematic Worlds (Never Repeats):
1. Himalayan Sunrise Dhyana (Mountain Yogi & Ancient Banyan Monk) - 432Hz
2. Sacred Temple & Floating Diyas (Ancient Sanctum & Zen Lotus Pond) - 528Hz
3. Golden Sunset Beach & Night Sky (Sunset Ocean Shore & Cosmic Yogi) - 432Hz
4. Sacred Bamboo Forest & Cascading Waters (Bamboo Waterfall & Forest Stream) - 432Hz
5. Cosmic Universe Deep Sleep (Milky Way Galaxy & Delta Wave Stillness) - 432Hz
"""

import gc
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
import imageio_ffmpeg

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

from config import BASE_DIR, OUTPUT_DIR, TEMP_DIR

ASSETS_DIR = BASE_DIR / "assets"
ASSETS_MEDITATION = ASSETS_DIR / "meditation"
MUSIC_MEDITATION = ASSETS_DIR / "music" / "meditation"
LOGO_PATH = ASSETS_DIR / "white_stone_logo.png"

# 5 Pure, High-Definition Thematic Worlds
THEMES = [
    {
        "id": "himalayan_sunrise",
        "name": "Himalayan Sunrise Dhyana",
        "scene_files": ["scene1_yogi.jpg", "scene4_banyan_monk.jpg"],
        "music_track": "track1.mp3",
        "title_template": "432Hz Himalayan Sunrise Meditation | {dur_label} Deep Inner Stillness, Pranayama & Peace 🧘‍♂️🌿",
        "chapters": [
            "Himalayan Yogi Sunrise (Mindful Breathing & Stillness)",
            "Sacred Banyan Monk at Dawn (Inner Peace & Awareness)"
        ],
        "tags": [
            "himalayan meditation", "yogi meditation", "432hz sunrise", "pranayama music",
            "inner peace", "dhyana meditation", "deep healing music", "white stone music"
        ]
    },
    {
        "id": "sacred_temple",
        "name": "Sacred Temple & Floating Diyas",
        "scene_files": ["scene5_temple_yogi.jpg", "scene7_lotus_pond.jpg"],
        "music_track": "track2.mp3",
        "title_template": "528Hz Sacred Temple Meditation | {dur_label} Positive Energy, Divine Aura & Deep Calm 🪔✨",
        "chapters": [
            "Sacred Temple Sanctuary (Divine Light & Aura Cleansing)",
            "Zen Lotus Pond at Twilight (Deep Spiritual Peace)"
        ],
        "tags": [
            "temple meditation", "528hz miracle tone", "sacred diyas", "spiritual healing",
            "aura cleansing", "divine meditation", "positive energy", "white stone music"
        ]
    },
    {
        "id": "sunset_beach",
        "name": "Golden Sunset Beach & Ocean Zen",
        "scene_files": ["scene3_beach.jpg", "scene6_night_stars.jpg"],
        "music_track": "track1.mp3",
        "title_template": "432Hz Sunset Beach Meditation | {dur_label} Stress Relief, Ocean Calm & Inner Peace 🌊🧘‍♀️",
        "chapters": [
            "Golden Beach Sunset (Deep Physical & Mental Release)",
            "Twilight Ocean Horizon (Surrender & Anxiety Relief)"
        ],
        "tags": [
            "ocean meditation", "beach relaxation", "sunset calm", "stress relief music",
            "anti anxiety", "peaceful sleep", "mindfulness waves", "white stone music"
        ]
    },
    {
        "id": "bamboo_waterfall",
        "name": "Sacred Bamboo Forest & Cascading Waters",
        "scene_files": ["scene2_waterfall.jpg", "scene8_forest_river.jpg"],
        "music_track": "track2.mp3",
        "title_template": "432Hz Bamboo Forest Waterfall Zen | {dur_label} Nature Healing, Mindful Peace & Stress Relief 🎋💧",
        "chapters": [
            "Sacred Bamboo Waterfall (Washing Away Tension & Negativity)",
            "Misty Forest River Cascade (Crystal Clear Harmony & Rest)"
        ],
        "tags": [
            "waterfall meditation", "nature sounds zen", "bamboo forest", "zen water healing",
            "nature therapy", "calming river", "deep relaxation", "white stone music"
        ]
    },
    {
        "id": "deep_sleep_cosmos",
        "name": "Cosmic Universe Deep Sleep",
        "scene_files": ["scene6_night_stars.jpg", "scene1_yogi.jpg"],
        "music_track": "track1.mp3",
        "title_template": "432Hz Deep Sleep Cosmic Meditation | {dur_label} Fall Asleep Fast, Insomnia Relief & Delta Healing 🌙✨",
        "chapters": [
            "Milky Way Galaxy Night (Cosmic Stillness & Sleep Drift)",
            "Sacred Mountain Solitude (Total Relaxation & Deep Delta Rest)"
        ],
        "tags": [
            "deep sleep music", "fall asleep fast", "insomnia cure", "cosmic meditation",
            "night relaxation", "delta wave healing", "sleep aid music", "white stone music"
        ]
    }
]

def build_meditation_video(duration_seconds: int = 3600, theme_index: int = None, output_name: str = "whitestone_meditation") -> Path:
    """
    Renders a Full HD 1080p (16:9) meditation video with curated themes
    and White Stone Music logo watermark in bottom-right corner.
    """
    t_start = time.time()
    mins = duration_seconds // 60
    hours = mins / 60.0

    dur_label = f"{int(hours)} Hour" if hours == int(hours) and hours >= 1 else f"{mins} Minutes"
    if hours > 1 and hours == int(hours):
        dur_label = f"{int(hours)} Hours"

    # Select theme dynamically if not specified
    if theme_index is None:
        # Rotate based on current day and hour
        theme_index = int((time.time() // (4 * 3600))) % len(THEMES)

    theme = THEMES[theme_index % len(THEMES)]

    print("=" * 75)
    print(f"🧘‍♂️ White Stone Music - Long-Form Video Generator")
    print(f"🎨 Selected Theme: [{theme['name']}]")
    print(f"⏱️ Duration: {dur_label} ({duration_seconds}s)")
    print("=" * 75)

    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()

    # Step 1: Prepare theme scene files
    scene_paths = [ASSETS_MEDITATION / f for f in theme["scene_files"]]
    for s in scene_paths:
        if not s.exists():
            raise FileNotFoundError(f"Missing scene asset: {s}")

    num_scenes = len(scene_paths)
    time_per_scene = duration_seconds / num_scenes
    clip_base_dur = 60  # 60-second micro-clip
    loops_per_scene = max(1, int(round(time_per_scene / clip_base_dur)))

    print(f"\n[Visuals] {num_scenes} Thematic Scenes for [{theme['name']}]:")
    for idx, s in enumerate(scene_paths):
        print(f"  {idx+1}. {s.name}")
    print(f"  • Logo: {LOGO_PATH.name} (Bottom-Right corner)")
    print(f"  • Each scene will run for ~{time_per_scene/60:.1f} minutes ({loops_per_scene} loops of 60s)")

    # Step 2: Render 60s Ken-Burns micro-clip with watermark for each scene
    scene_segment_paths = []
    fps = 24

    for idx, s_img in enumerate(scene_paths):
        clip_name = f"base_clip_{idx}.mp4"
        clip_path = TEMP_DIR / clip_name

        print(f"\n  [Rendering Base Clip {idx+1}/{num_scenes}] {s_img.name} (60s Ken Burns + Logo)...")
        vf_expr = (
            "scale=1920:1080:force_original_aspect_ratio=increase,"
            "crop=1920:1080,"
            "zoompan=z='min(zoom+0.000035,1.05)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1440:s=1920x1080:fps=24"
        )
        filter_complex = f"[0:v]{vf_expr}[zoomed];[zoomed][1:v]overlay=W-w-50:H-h-50[outv]"

        cmd_clip = [
            ffmpeg_exe, "-y",
            "-loop", "1", "-i", str(s_img),
            "-i", str(LOGO_PATH),
            "-filter_complex", filter_complex,
            "-map", "[outv]",
            "-t", str(clip_base_dur),
            "-c:v", "libx264", "-preset", "ultrafast", "-crf", "25",
            "-pix_fmt", "yuv420p",
            "-an",
            str(clip_path)
        ]
        subprocess.run(cmd_clip, capture_output=True, check=True)

        # Loop the clip to fill this scene's duration
        scene_long_path = TEMP_DIR / f"scene_long_{idx}.mp4"
        scene_segment_paths.append(scene_long_path)

        print(f"  [Looping] Scene {idx+1} -> {loops_per_scene * clip_base_dur}s with stream copy...")
        cmd_loop = [
            ffmpeg_exe, "-y",
            "-stream_loop", str(loops_per_scene - 1),
            "-i", str(clip_path),
            "-c", "copy",
            str(scene_long_path)
        ]
        subprocess.run(cmd_loop, capture_output=True, check=True)

    # Step 3: Concatenate scene segments
    print("\n[Visuals] Concatenating scenes into unified timeline...")
    concat_list = TEMP_DIR / "concat_scenes.txt"
    with open(concat_list, "w", encoding="utf-8") as f:
        for p in scene_segment_paths:
            f.write(f"file '{p.name}'\n")

    merged_video_visual = TEMP_DIR / "merged_visuals.mp4"
    cmd_concat = [
        ffmpeg_exe, "-y",
        "-f", "concat", "-safe", "0",
        "-i", "concat_scenes.txt",
        "-c", "copy",
        str(merged_video_visual)
    ]
    subprocess.run(cmd_concat, cwd=TEMP_DIR, capture_output=True, check=True)

    # Step 4: Prepare Looped Meditation Music
    print(f"\n[Audio] Synthesizing seamless {dur_label} healing soundscape...")
    chosen_track = MUSIC_MEDITATION / theme["music_track"]
    if not chosen_track.exists():
        chosen_track = MUSIC_MEDITATION / "track1.mp3"

    audio_loop_path = TEMP_DIR / "looped_meditation_audio.mp3"
    fade_start = max(1, duration_seconds - 5)
    af_filter = f"afade=t=in:ss=0:d=3,afade=t=out:st={fade_start}:d=5"

    cmd_audio = [
        ffmpeg_exe, "-y",
        "-stream_loop", "-1",
        "-i", str(chosen_track),
        "-t", str(duration_seconds),
        "-af", af_filter,
        "-c:a", "libmp3lame", "-b:a", "192k",
        str(audio_loop_path)
    ]
    subprocess.run(cmd_audio, capture_output=True, check=True)

    # Step 5: Final Muxing (Visuals + Audio)
    final_mp4 = OUTPUT_DIR / f"{output_name}.mp4"
    print(f"\n[Assembly] Finalizing Full HD 1080p MP4: {final_mp4.name}...")

    cmd_final = [
        ffmpeg_exe, "-y",
        "-i", str(merged_video_visual),
        "-i", str(audio_loop_path),
        "-c:v", "copy",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest",
        str(final_mp4)
    ]
    subprocess.run(cmd_final, capture_output=True, check=True)

    # Step 6: Dynamic SEO Metadata Generation
    sec_per = int(time_per_scene)
    def fmt_ts(s):
        h = s // 3600
        m = (s % 3600) // 60
        sec = s % 60
        if hours >= 1:
            return f"{h:02d}:{m:02d}:{sec:02d}"
        return f"{m:02d}:{sec:02d}"

    formatted_chapters = []
    for idx, ch_name in enumerate(theme["chapters"]):
        ts_str = fmt_ts(idx * sec_per)
        formatted_chapters.append(f"{ts_str} - {ch_name}")

    chapters_str = "\n".join(formatted_chapters)
    title = theme["title_template"].format(dur_label=dur_label)

    meta_path = final_mp4.with_suffix(".json")
    meta = {
        "title": title,
        "description": (
            "🧘‍♂️ Welcome to White Stone Music.\n"
            f"Immerse your mind, body, and soul in this peaceful {dur_label} healing meditation session: [{theme['name']}].\n\n"
            "Composed with sacred natural harmonic vibrations, this session guides "
            "you into deep theta and delta states for profound peace, anxiety relief, and restorative sleep.\n\n"
            "✨ PERFECT FOR:\n"
            "• Deep Sleep & Overcoming Insomnia\n"
            "• Reducing Anxiety, Tension & Overthinking\n"
            "• Daily Yoga, Pranayama & Dhyana Practice\n"
            "• Aura Cleansing & Positive Vibration\n"
            "• Study, Focus, Zen Mindfulness & Work Concentration\n\n"
            "⏱️ TIMESTAMPS / CHAPTERS:\n"
            f"{chapters_str}\n\n"
            "🎧 Headphones recommended for maximum binaural relaxation.\n"
            "🔔 Subscribe to White Stone Music for daily peaceful meditation videos!\n"
            "👍 If this music brought you peace, please like, share, and subscribe.\n\n"
            "#meditationmusic #432hz #528hz #whitestonemusic #deepsleep #stressrelief #zen #healingmusic #yoga #mindfulness"
        ),
        "tags": theme["tags"] + [
            "meditation music", "relaxing music", "peaceful sleep",
            f"{dur_label.lower()} meditation", f"{dur_label.lower()} sleep music"
        ],
        "video_path": str(final_mp4),
        "duration_minutes": mins,
        "is_short": False,
        "theme_id": theme["id"],
        "theme_name": theme["name"],
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S")
    }

    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    # Clean intermediate temporary files
    for p in scene_segment_paths:
        try:
            p.unlink(missing_ok=True)
        except Exception:
            pass
    for idx in range(num_scenes):
        try:
            (TEMP_DIR / f"base_clip_{idx}.mp4").unlink(missing_ok=True)
        except Exception:
            pass
    try:
        merged_video_visual.unlink(missing_ok=True)
        audio_loop_path.unlink(missing_ok=True)
    except Exception:
        pass

    elapsed = time.time() - t_start
    size_mb = final_mp4.stat().st_size / (1024 * 1024)

    print("\n" + "=" * 75)
    print(f"🎉 [White Stone Music] SUCCESS! [{theme['name']}] {dur_label} Video Generated in {elapsed:.1f}s!")
    print(f"📁 Video Location: {final_mp4}")
    print(f"📦 File Size: {size_mb:.2f} MB")
    print(f"📝 Metadata: {meta_path}")
    print("=" * 75 + "\n")

    return final_mp4

if __name__ == "__main__":
    dur = 3600  # Default 1 Hour (3600s)
    theme_idx = None
    if len(sys.argv) > 1:
        dur = int(sys.argv[1])
    if len(sys.argv) > 2:
        theme_idx = int(sys.argv[2])
    build_meditation_video(duration_seconds=dur, theme_index=theme_idx, output_name=f"whitestone_{dur//60}min")
