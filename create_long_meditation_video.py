"""
create_long_meditation_video.py - 100% Consistent Dhyanast / Meditating Humans Theme.
Branded with White Stone Music logo watermark in bottom-right corner.

Generates 15-minute, 30-minute, 1-hour, or 2-hour meditation videos in seconds using
Ken Burns stream-looping:
1. Pure Dhyanast Theme (ONLY real meditating humans in deep peaceful dhyana):
   - Scene 1: Himalayan Yogi atop mountain rock at golden sunrise
   - Scene 2: Enlightened Monk in lotus posture under ancient sacred Banyan tree
   - Scene 3: Serene Woman meditating on golden sand beach at sunset
   - Scene 4: Traditional Yogi in white meditating inside ancient temple sanctuary with glowing diyas
2. White Stone Music logo watermark in the bottom-right corner
3. Ultra-gentle cinematic Ken Burns breathing motion
4. 432Hz Deep Healing & Anxiety Relief Soundscape
5. Comprehensive YouTube SEO Metadata (Viral Tags, Description, Chapters)
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

def build_meditation_video(duration_seconds: int = 1800, output_name: str = "whitestone_meditation_30min") -> Path:
    """
    Renders a Full HD 1080p (16:9) meditation video with 100% consistent Dhyanast scenes
    and White Stone Music logo watermark in bottom-right corner.
    """
    t_start = time.time()
    mins = duration_seconds // 60
    print("=" * 75)
    print(f"🧘‍♂️ White Stone Music - Automated Video Generator: {mins} Minutes ({duration_seconds}s)")
    print("=" * 75)

    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()

    # Step 1: Pure Dhyanast Scenes (ONLY Meditating Humans)
    scene_files = [
        ASSETS_MEDITATION / "scene1_yogi.jpg",         # Himalayan Yogi sunrise
        ASSETS_MEDITATION / "scene4_banyan_monk.jpg",  # Sacred Banyan tree monk
        ASSETS_MEDITATION / "scene3_beach.jpg",        # Golden beach sunset woman
        ASSETS_MEDITATION / "scene5_temple_yogi.jpg"   # Ancient temple sanctuary yogi
    ]

    for s in scene_files:
        if not s.exists():
            raise FileNotFoundError(f"Missing meditation scene asset: {s}")

    num_scenes = len(scene_files)
    time_per_scene = duration_seconds / num_scenes
    clip_base_dur = 60  # 60-second micro-clip
    loops_per_scene = max(1, int(round(time_per_scene / clip_base_dur)))

    print(f"\n[Visuals] {num_scenes} Pure Dhyanast Scenes with White Stone Music Watermark:")
    print(f"  1. Himalayan Yogi at Golden Sunrise")
    print(f"  2. Sacred Banyan Tree Monk at Dawn")
    print(f"  3. Golden Beach Sunset Meditating Woman")
    print(f"  4. Sacred Temple Sanctuary Yogi with Glowing Diyas")
    print(f"  • Logo: {LOGO_PATH.name} (Bottom-Right corner)")
    print(f"  • Each scene will run for ~{time_per_scene/60:.1f} minutes ({loops_per_scene} loops of 60s)")

    # Step 2: Render 60s Ken-Burns micro-clip with watermark for each scene
    scene_segment_paths = []
    fps = 24

    for idx, s_img in enumerate(scene_files):
        clip_name = f"base_clip_{idx}.mp4"
        clip_path = TEMP_DIR / clip_name

        print(f"\n  [Rendering Base Clip {idx+1}/{num_scenes}] {s_img.name} (60s Ken Burns + Logo)...")
        # Subtly zoom from 1.0 to 1.05 over 60s (1440 frames) and overlay logo bottom-right
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

    # Step 3: Concatenate all scene segments
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

    # Step 4: Prepare Looped 432Hz Meditation Music
    print(f"\n[Audio] Synthesizing seamless {mins}-minute 432Hz ambient soundscape...")
    track1 = MUSIC_MEDITATION / "track1.mp3"
    track2 = MUSIC_MEDITATION / "track2.mp3"

    music_concat_txt = TEMP_DIR / "music_concat.txt"
    with open(music_concat_txt, "w", encoding="utf-8") as f:
        f.write(f"file '{track1.resolve().as_posix()}'\n")
        f.write(f"file '{track2.resolve().as_posix()}'\n")

    audio_loop_path = TEMP_DIR / "looped_meditation_audio.mp3"
    fade_start = max(1, duration_seconds - 5)
    af_filter = f"afade=t=in:ss=0:d=3,afade=t=out:st={fade_start}:d=5"

    cmd_audio = [
        ffmpeg_exe, "-y",
        "-f", "concat", "-safe", "0",
        "-stream_loop", "-1",
        "-i", str(music_concat_txt),
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

    # Step 6: Metadata Generation
    sec_per = int(time_per_scene)
    ch1 = "00:00 - Himalayan Yogi Sunrise (Mindful Breathing & Stillness)"
    ch2 = f"{sec_per//60:02d}:{sec_per%60:02d} - Sacred Banyan Monk (Inner Peace & Awareness)"
    ch3 = f"{sec_per*2//60:02d}:{sec_per*2%60:02d} - Golden Beach Sunset (Deep Physical & Mental Release)"
    ch4 = f"{sec_per*3//60:02d}:{sec_per*3%60:02d} - Sacred Temple Sanctuary (Divine Light & Restorative Sleep)"

    meta_path = final_mp4.with_suffix(".json")
    meta = {
        "title": f"432Hz Deep Healing Meditation Music | {mins}-Minute Stress Relief, Zen Mindfulness & Sleep 🧘‍♂️🌿",
        "description": (
            "🧘‍♂️ Welcome to White Stone Music.\n"
            f"Immerse your mind, body, and soul in this peaceful {mins}-minute 432Hz deep healing meditation session.\n\n"
            "Composed with sacred natural harmonic vibrations known as the 'Miracle Tone', this session guides "
            "you into deep theta states for profound peace, stress reduction, and restorative deep sleep.\n\n"
            "✨ PERFECT FOR:\n"
            "• Deep Sleep & Overcoming Insomnia\n"
            "• Reducing Anxiety, Tension & Overthinking\n"
            "• Daily Yoga, Pranayama & Dhyana Practice\n"
            "• Aura Cleansing & Positive Vibration\n"
            "• Study, Focus, Zen Mindfulness & Work Concentration\n\n"
            "⏱️ TIMESTAMPS / CHAPTERS:\n"
            f"{ch1}\n"
            f"{ch2}\n"
            f"{ch3}\n"
            f"{ch4}\n\n"
            "🎧 Headphones recommended for maximum 432Hz binaural relaxation.\n"
            "🔔 Subscribe to White Stone Music for daily peaceful meditation videos!\n"
            "👍 If this music brought you peace, please like, share, and subscribe.\n\n"
            "#meditationmusic #432hz #whitestonemusic #deepsleep #stressrelief #zen #healingmusic #yoga #mindfulness #dhyana"
        ),
        "tags": [
            "432hz meditation music", "deep healing music", "white stone music",
            "stress relief music", "peaceful sleep music", "relaxing music", "zen meditation",
            "healing frequency 432hz", "calm music for anxiety", "fall asleep in 10 minutes",
            "binaural beats", "yoga meditation music", "positive energy vibration",
            "insomnia cure music", "deep sleep relaxation", "dhyana meditation"
        ],
        "video_path": str(final_mp4),
        "duration_minutes": mins,
        "is_short": False,
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
    print(f"🎉 [White Stone Music] SUCCESS! Watermarked {mins}-Minute Video Generated in {elapsed:.1f}s!")
    print(f"📁 Video Location: {final_mp4}")
    print(f"📦 File Size: {size_mb:.2f} MB")
    print(f"📝 Metadata: {meta_path}")
    print("=" * 75 + "\n")

    return final_mp4

if __name__ == "__main__":
    dur = 1800  # Default 30 mins
    if len(sys.argv) > 1:
        dur = int(sys.argv[1])
    build_meditation_video(duration_seconds=dur, output_name=f"whitestone_meditation_{dur//60}min")
