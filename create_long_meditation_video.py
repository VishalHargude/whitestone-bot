"""
create_long_meditation_video.py - Top-Creator Multi-Theme Relaxation Video Generator for White Stone Music.
Features:
1. Theme-Specific Multiple 8K Photos (5 to 6 scenes per theme)
2. Directional Ken Burns Pan: Gliding smoothly from top-right corner towards bottom-left corner
3. Seamless Crossfade Transitions: Smoothly dissolving between scenes
4. Dedicated Atmospheric Weather Overlays (Separate Snowfall, Gentle Rain, or Golden Embers per theme)
5. 100% Original 432Hz & 528Hz Copyright-Free Relaxing Music
6. White Stone Logo Watermark in bottom-right corner
7. Automatic High-CTR Title, Chapters & Tags generation
"""

import gc
import json
import math
import os
import random
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

# 10 Pure, High-Definition Thematic Worlds with Theme-Specific Weather Overlays
THEMES = [
    {
        "id": "celtic_sound_therapy",
        "name": "Ancient Celtic Sound Therapy & Overthinking Relief",
        "weather_overlay": "rain_falling_gentle.mp4",
        "scene_files": [
            "scene_celtic_waterfall.jpg",
            "scene_redwood_waterfall.jpg",
            "scene_celtic_highland.jpg",
            "scene8_forest_river.jpg",
            "scene_mossy_forest_stream.jpg",
            "scene2_waterfall.jpg"
        ],
        "music_track": "track_celtic_528hz.mp3",
        "title_template": "Clear Blockages & Overthinking | Ancient Celtic Sound Therapy | 528Hz Miracle Wave ({dur_label}) 🌿🌧️",
        "tags": [
            "celtic sound therapy", "528hz miracle wave", "clear blockages overthinking",
            "ancient celtic meditation", "remove all stress", "overthinking relief",
            "432hz healing music", "deep relaxation", "peaceful sleep music", "rain sounds",
            "white stone music", "vishal hargude", "sound therapy", "stress relief"
        ]
    },
    {
        "id": "bamboo_waterfall",
        "name": "Sacred Bamboo Forest & Cascading Waters",
        "weather_overlay": "rain_falling_gentle.mp4",
        "scene_files": [
            "scene2_waterfall.jpg",
            "scene_zen_bamboo_waterfall.jpg",
            "scene14_misty_bamboo_path.jpg",
            "scene_kyoto_bamboo_dawn.jpg",
            "scene8_forest_river.jpg",
            "scene_mossy_forest_stream.jpg"
        ],
        "music_track": "track4_bamboo_waterfall.mp3",
        "title_template": "432Hz Bamboo Forest Waterfall Zen | {dur_label} Nature Healing, Rain Calm & Stress Relief 🎋💧",
        "tags": [
            "bamboo waterfall", "432hz nature healing", "rain relaxation", "zen forest",
            "stress relief", "calm mind", "peaceful waterfall", "white stone music"
        ]
    },
    {
        "id": "himalayan_sunrise",
        "name": "Himalayan Sunrise Dhyana",
        "weather_overlay": "snowfall_diagonal_slow.mp4",
        "scene_files": [
            "scene1_yogi.jpg",
            "scene_yogi_sunrise.jpg",
            "scene4_banyan_monk.jpg",
            "scene_monk_banyan_tree.jpg",
            "scene15_himalayan_stupa.jpg",
            "scene_golden_stupa.jpg"
        ],
        "music_track": "track1_himalayan.mp3",
        "title_template": "432Hz Himalayan Sunrise Meditation | {dur_label} Deep Inner Stillness, Snowfall & Peace 🏔️❄️",
        "tags": [
            "himalayan meditation", "yogi meditation", "432hz sunrise", "snowfall meditation",
            "pranayama music", "inner peace", "dhyana meditation", "deep healing music", "white stone music"
        ]
    },
    {
        "id": "sacred_temple",
        "name": "Sacred Temple & Floating Diyas",
        "weather_overlay": "golden_embers_sunlight.mp4",
        "scene_files": [
            "scene5_temple_yogi.jpg",
            "scene_temple_sanctuary_yogi.jpg",
            "scene13_varanasi_ghat.jpg",
            "scene_sacred_ghat_sunrise.jpg",
            "scene7_lotus_pond.jpg",
            "scene_zen_lotus_twilight.jpg"
        ],
        "music_track": "track2_temple.mp3",
        "title_template": "528Hz Sacred Temple Meditation | {dur_label} Positive Energy, Golden Embers & Deep Calm 🛕✨",
        "tags": [
            "temple meditation", "528hz miracle tone", "sacred diyas", "spiritual healing",
            "golden embers", "divine meditation", "positive energy", "white stone music"
        ]
    },
    {
        "id": "sunset_beach",
        "name": "Golden Sunset Beach & Ocean Zen",
        "weather_overlay": "golden_embers_sunlight.mp4",
        "scene_files": [
            "scene3_beach.jpg",
            "scene16_beach_ocean_sunset.jpg",
            "scene_tranquil_sunset_beach.jpg",
            "scene17_zen_beach_cove.jpg",
            "scene_coastal_cove_dusk.jpg",
            "scene_woman_sunset_beach.jpg"
        ],
        "music_track": "track3_beach.mp3",
        "title_template": "432Hz Sunset Beach Meditation | {dur_label} Stress Relief, Ocean Calm & Inner Peace 🌊🌅",
        "tags": [
            "ocean meditation", "beach relaxation", "sunset calm", "stress relief music",
            "anti anxiety", "peaceful sleep", "mindfulness waves", "white stone music"
        ]
    },
    {
        "id": "cosmic_deep_sleep",
        "name": "Cosmic Universe Deep Sleep",
        "weather_overlay": "golden_embers_sunlight.mp4",
        "scene_files": [
            "scene18_deep_space_nebula.jpg",
            "scene_cosmic_nebula.jpg",
            "scene6_night_stars.jpg",
            "scene_himalayan_milkyway.jpg"
        ],
        "music_track": "track5_deep_sleep_cosmos.mp3",
        "title_template": "432Hz Cosmic Deep Sleep | {dur_label} Fall Asleep in Minutes, Stardust & Delta Waves 🌌✨",
        "tags": [
            "deep sleep music", "432hz cosmic sleep", "delta waves", "insomnia relief",
            "stardust meditation", "lucid dreaming", "fall asleep fast", "white stone music"
        ]
    },
    {
        "id": "tibetan_monastery",
        "name": "Tibetan Cliffside Monastery & Snow",
        "weather_overlay": "snowfall_diagonal_slow.mp4",
        "scene_files": [
            "scene11_tibetan_monastery.jpg",
            "scene_tibetan_cliffside.jpg",
            "scene15_himalayan_stupa.jpg",
            "scene_golden_stupa.jpg",
            "scene4_banyan_monk.jpg"
        ],
        "music_track": "track6_tibetan_monastery.mp3",
        "title_template": "528Hz Tibetan Monastery Meditation | {dur_label} Mountain Healing Chants & Snowfall 🏔️❄️",
        "tags": [
            "tibetan meditation", "528hz healing", "monastery chants", "snowfall calm",
            "mountain peace", "singing bowls", "white stone music"
        ]
    },
    {
        "id": "kyoto_zen",
        "name": "Kyoto Zen Rock Garden & Misty Paths",
        "weather_overlay": "rain_falling_gentle.mp4",
        "scene_files": [
            "scene9_zen_garden.jpg",
            "scene_kyoto_zen_twilight.jpg",
            "scene14_misty_bamboo_path.jpg",
            "scene_kyoto_bamboo_dawn.jpg",
            "scene7_lotus_pond.jpg"
        ],
        "music_track": "track7_kyoto_zen.mp3",
        "title_template": "432Hz Kyoto Zen Garden Meditation | {dur_label} Mindfulness, Gentle Rain & Inner Stillness ⛩️🌧️",
        "tags": [
            "zen garden", "kyoto meditation", "japanese zen", "gentle rain calm",
            "mindfulness music", "focus study peace", "white stone music"
        ]
    },
    {
        "id": "celestial_aurora",
        "name": "Celestial Aurora Borealis over Arctic Fjord",
        "weather_overlay": "snowfall_diagonal_slow.mp4",
        "scene_files": [
            "scene10_aurora_borealis.jpg",
            "scene_aurora_fjord.jpg",
            "scene6_night_stars.jpg",
            "scene18_deep_space_nebula.jpg"
        ],
        "music_track": "track8_aurora_sleep.mp3",
        "title_template": "432Hz Celestial Aurora Borealis | {dur_label} Northern Lights, Arctic Snowfall & Deep Sleep 🌌❄️",
        "tags": [
            "aurora borealis", "northern lights", "432hz deep sleep", "arctic snowfall",
            "dream meditation", "celestial calm", "white stone music"
        ]
    },
    {
        "id": "desert_solitude",
        "name": "Golden Desert Sunset Solitude",
        "weather_overlay": "golden_embers_sunlight.mp4",
        "scene_files": [
            "scene12_desert_yogi.jpg",
            "scene_desert_yogi_dune.jpg",
            "scene1_yogi.jpg",
            "scene_yogi_sunrise.jpg",
            "scene3_beach.jpg"
        ],
        "music_track": "track9_desert_solitude.mp3",
        "title_template": "432Hz Golden Desert Sunset Solitude | {dur_label} Solitary Yoga Dhyana & Warm Peace 🏜️✨",
        "tags": [
            "desert meditation", "sunset dunes", "solitary yogi", "432hz peace",
            "stress relief", "deep focus", "golden solitude", "white stone music"
        ]
    }
]

def render_scene_clip(ffmpeg_exe: str, img_path: Path, out_clip: Path, dur_sec: float = 14.0):
    """
    Renders a single scene with directional motion:
    Glides smoothly from the top-right corner towards the bottom-left corner.
    """
    filter_pan = (
        f"scale=2304:1296:force_original_aspect_ratio=increase,crop=2304:1296,"
        f"crop=1920:1080:x='384*(1-t/{dur_sec})':y='216*(t/{dur_sec})'"
    )
    cmd = [
        ffmpeg_exe, "-y",
        "-loop", "1", "-i", str(img_path),
        "-vf", filter_pan,
        "-t", str(dur_sec),
        "-r", "25",
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "18", "-pix_fmt", "yuv420p",
        "-an",
        str(out_clip)
    ]
    subprocess.run(cmd, check=True, capture_output=True)

def build_smooth_crossfade_cycle(ffmpeg_exe: str, scene_paths: list, out_cycle: Path, clip_dur: float = 14.0, fade_dur: float = 2.0) -> float:
    """
    Builds a seamless slideshow cycle with directional motion + smooth crossfade mixing between all scenes.
    """
    num_scenes = len(scene_paths)
    raw_clips = []
    for idx, s in enumerate(scene_paths):
        c_path = TEMP_DIR / f"raw_scene_{idx}.mp4"
        raw_clips.append(c_path)
        render_scene_clip(ffmpeg_exe, s, c_path, dur_sec=clip_dur)

    # Build multi-input xfade filter
    # Inputs: 0..N-1
    # total duration = num_scenes * clip_dur - (num_scenes - 1) * fade_dur
    inputs_cmd = []
    for c in raw_clips:
        inputs_cmd.extend(["-i", str(c)])

    filter_chains = []
    # Set timebases
    for i in range(num_scenes):
        filter_chains.append(f"[{i}:v]settb=AVTB[v{i}]")

    # Chain xfades
    curr_v = "[v0]"
    curr_offset = clip_dur - fade_dur
    for i in range(1, num_scenes):
        next_v = f"[v{i}]"
        out_v = f"[xf{i}]" if i < num_scenes - 1 else "[final_cycle]"
        filter_chains.append(f"{curr_v}{next_v}xfade=transition=fade:duration={fade_dur}:offset={curr_offset:.2f}{out_v}")
        curr_v = out_v
        curr_offset += (clip_dur - fade_dur)

    full_filter = ";".join(filter_chains)
    total_cycle_dur = curr_offset + fade_dur

    cmd = [
        ffmpeg_exe, "-y"
    ] + inputs_cmd + [
        "-filter_complex", full_filter,
        "-map", "[final_cycle]",
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "18", "-pix_fmt", "yuv420p",
        "-an",
        str(out_cycle)
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    return total_cycle_dur

def build_meditation_video(duration_seconds: int = 3600, theme_index: int = None, output_name: str = "whitestone_meditation") -> Path:
    """
    Renders Full HD 1080p meditation video with:
    1. Multiple 8K Theme Photos with Top-Right to Bottom-Left Gliding Motion
    2. Smooth Crossfade Dissolves between images
    3. Dedicated Theme Weather Overlay (Separate Snowfall, Gentle Rain, or Golden Embers)
    4. 100% Original 432Hz/528Hz Relaxing Music
    5. White Stone Watermark Logo
    """
    mins = duration_seconds // 60
    hours = mins / 60.0
    dur_label = f"{int(hours)} Hour" if hours == int(hours) and hours >= 1 else f"{mins} Minutes"
    if hours > 1 and hours == int(hours):
        dur_label = f"{int(hours)} Hours"

    if theme_index is None:
        theme_index = int((time.time() // (4 * 3600))) % len(THEMES)

    theme = THEMES[theme_index % len(THEMES)]

    print("=" * 80)
    print(f"🧘‍♂️ White Stone Music - Top-Creator Meditation Video Generator")
    print(f"🎨 Theme #{theme_index % len(THEMES) + 1}: [{theme['name']}]")
    print(f"⏱️ Duration: {dur_label} ({duration_seconds}s)")
    print(f"🌦️ Weather Overlay: {theme['weather_overlay']}")
    print("=" * 80)

    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()

    # Step 1: Collect all valid scene images for this theme
    scene_paths = []
    for fname in theme["scene_files"]:
        p = ASSETS_MEDITATION / fname
        if p.exists():
            scene_paths.append(p)

    if not scene_paths:
        raise FileNotFoundError(f"No scene images found for theme {theme['name']}")

    print(f"\n[Step 1/4] Found {len(scene_paths)} 8K Scene Images for [{theme['name']}]:")
    for idx, s in enumerate(scene_paths):
        print(f"  {idx+1}. {s.name}")

    # Step 2: Build Smooth Gliding + Crossfade Master Cycle (~60-90s)
    cycle_video = TEMP_DIR / f"smooth_cycle_{theme['id']}.mp4"
    print(f"\n[Step 2/4] Assembling Top-Right to Bottom-Left Gliding + Crossfade Cycle...")
    cycle_dur = build_smooth_crossfade_cycle(ffmpeg_exe, scene_paths, cycle_video, clip_dur=14.0, fade_dur=2.0)
    print(f"  [OK] Master Seamless Visual Cycle Ready: {cycle_dur:.1f}s")

    # Step 3: Check Weather Overlay
    weather_mp4 = ASSETS_DIR / theme["weather_overlay"]
    if not weather_mp4.exists():
        weather_mp4 = ASSETS_DIR / "rain_falling_gentle.mp4"

    # Step 4: Check Relaxing Music Track
    music_track = MUSIC_MEDITATION / theme["music_track"]
    if not music_track.exists():
        music_track = MUSIC_MEDITATION / "track_celtic_528hz.mp3"
        if not music_track.exists():
            music_track = MUSIC_MEDITATION / "track1.mp3"

    print(f"\n[Step 3/4] Audio & Atmosphere:")
    print(f"  • Music: {music_track.name}")
    print(f"  • Weather Effect: {weather_mp4.name} (Screen Blend @ 0.70)")
    print(f"  • Watermark Logo: {LOGO_PATH.name} (Bottom-Right)")

    # Step 5: Final Multi-Layer Assembly (Visual Cycle Stream-Loop + Weather Stream-Loop + Audio Loop + Logo)
    final_mp4 = OUTPUT_DIR / f"{output_name}.mp4"
    print(f"\n[Step 4/4] Finalizing Full HD 1080p Video -> {final_mp4.name}...")

    # Multi-stream composite filter:
    # 0:v = Visual Cycle (stream looped)
    # 1:v = Weather Overlay (stream looped)
    # 2:v = Logo PNG
    # 3:a = Audio (stream looped)
    filter_composite = (
        "[0:v]format=rgba[vbg];"
        "[1:v]scale=1920:1080,format=rgba[vweather];"
        "[vbg][vweather]blend=all_mode='screen':all_opacity=0.70[vcomp];"
        "[vcomp][2:v]overlay=W-w-50:H-h-50[vout]"
    )

    fade_start = max(1, duration_seconds - 5)
    af_filter = f"afade=t=in:ss=0:d=3,afade=t=out:st={fade_start}:d=5"

    cmd_final = [
        ffmpeg_exe, "-y",
        "-stream_loop", "-1", "-i", str(cycle_video),
        "-stream_loop", "-1", "-i", str(weather_mp4),
        "-i", str(LOGO_PATH),
        "-stream_loop", "-1", "-i", str(music_track),
        "-filter_complex", filter_composite,
        "-map", "[vout]",
        "-map", "3:a",
        "-af", af_filter,
        "-t", str(duration_seconds),
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "18", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k", "-ac", "2", "-ar", "44100",
        str(final_mp4)
    ]
    subprocess.run(cmd_final, check=True)

    title = theme["title_template"].format(dur_label=dur_label)

    # Save metadata JSON for uploader
    meta_json = final_mp4.with_suffix('.json')
    meta_data = {
        "title": title[:100],
        "theme_id": theme["id"],
        "theme_name": theme["name"],
        "weather": theme["weather_overlay"],
        "duration": duration_seconds,
        "video_file": final_mp4.name,
        "tags": theme["tags"]
    }
    with open(meta_json, "w", encoding="utf-8") as f:
        json.dump(meta_data, f, ensure_ascii=False, indent=2)

    print("\n" + "=" * 80)
    print(f"🎉 [Top-Creator Video Render Complete] {final_mp4.name} ({final_mp4.stat().st_size / (1024*1024):.2f} MB)")
    print(f"📌 Title: {title}")
    print("=" * 80 + "\n")
    return final_mp4

if __name__ == "__main__":
    dur = int(sys.argv[1]) if len(sys.argv) > 1 else 300  # Default 5-minute test
    t_idx = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    build_meditation_video(duration_seconds=dur, theme_index=t_idx, output_name="test_top_creator_meditation")
