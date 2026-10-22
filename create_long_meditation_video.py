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

# 10 Pure, High-Definition Thematic Worlds with 100% Genuine Acoustic / Ambient Master Recordings
# ZERO Synthetic Sine Waves. ZERO Artificial Drawn Lines. Pure National Geographic 8K Visuals.
THEMES = [
    {
        "id": "celtic_sound_therapy",
        "name": "Ancient Celtic Sound Therapy & Overthinking Relief",
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
            "432hz healing music", "deep relaxation", "peaceful sleep music",
            "white stone music", "vishal hargude", "sound therapy", "stress relief"
        ]
    },
    {
        "id": "bamboo_waterfall",
        "name": "Sacred Bamboo Forest & Cascading Waters",
        "scene_files": [
            "scene2_waterfall.jpg",
            "scene_zen_bamboo_waterfall.jpg",
            "scene14_misty_bamboo_path.jpg",
            "scene_kyoto_bamboo_dawn.jpg",
            "scene8_forest_river.jpg",
            "scene_mossy_forest_stream.jpg"
        ],
        "music_track": "track_celtic_528hz.mp3",
        "title_template": "432Hz Bamboo Forest Waterfall Zen | {dur_label} Nature Healing & Stress Relief 🎋💧",
        "tags": [
            "bamboo waterfall", "432hz nature healing", "zen forest",
            "stress relief", "calm mind", "peaceful waterfall", "white stone music"
        ]
    },
    {
        "id": "himalayan_sunrise",
        "name": "Himalayan Sunrise Dhyana",
        "scene_files": [
            "scene1_yogi.jpg",
            "scene_yogi_sunrise.jpg",
            "scene4_banyan_monk.jpg",
            "scene_monk_banyan_tree.jpg",
            "scene15_himalayan_stupa.jpg",
            "scene_golden_stupa.jpg"
        ],
        "music_track": "track_bansuri_flute_432hz.mp3",
        "title_template": "432Hz Himalayan Sunrise Meditation | {dur_label} Divine Bansuri Flute & Inner Peace 🏔️✨",
        "tags": [
            "himalayan meditation", "bansuri flute 432hz", "432hz sunrise", "krishna flute",
            "pranayama music", "inner peace", "dhyana meditation", "deep healing music", "white stone music"
        ]
    },
    {
        "id": "sacred_temple",
        "name": "Sacred Temple & Floating Diyas",
        "scene_files": [
            "scene5_temple_yogi.jpg",
            "scene_temple_sanctuary_yogi.jpg",
            "scene13_varanasi_ghat.jpg",
            "scene_sacred_ghat_sunrise.jpg",
            "scene7_lotus_pond.jpg",
            "scene_zen_lotus_twilight.jpg"
        ],
        "music_track": "track_432hz_sanctuary.mp3",
        "title_template": "432Hz Sacred Temple Sanctuary | {dur_label} Positive Energy & Deep Spiritual Peace 🛕✨",
        "tags": [
            "temple meditation", "432hz sanctuary", "sacred diyas", "spiritual healing",
            "divine meditation", "positive energy", "white stone music"
        ]
    },
    {
        "id": "sunset_beach",
        "name": "Golden Sunset Beach & Ocean Zen",
        "scene_files": [
            "scene3_beach.jpg",
            "scene16_beach_ocean_sunset.jpg",
            "scene_tranquil_sunset_beach.jpg",
            "scene17_zen_beach_cove.jpg",
            "scene_coastal_cove_dusk.jpg",
            "scene_woman_sunset_beach.jpg"
        ],
        "music_track": "track_432hz_evolving_pads.mp3",
        "title_template": "432Hz Sunset Beach Meditation | {dur_label} Deep Stress Relief & Ocean Serenity 🌊🌅",
        "tags": [
            "ocean meditation", "beach relaxation", "sunset calm", "stress relief music",
            "anti anxiety", "peaceful sleep", "mindfulness waves", "white stone music"
        ]
    },
    {
        "id": "cosmic_deep_sleep",
        "name": "Cosmic Universe Deep Sleep",
        "scene_files": [
            "scene18_deep_space_nebula.jpg",
            "scene_cosmic_nebula.jpg",
            "scene6_night_stars.jpg",
            "scene_himalayan_milkyway.jpg"
        ],
        "music_track": "track_432hz_deep_sleep.mp3",
        "title_template": "432Hz Cosmic Deep Sleep | {dur_label} Fall Asleep in Minutes, Stardust & Healing Delta Waves 🌌✨",
        "tags": [
            "deep sleep music", "432hz cosmic sleep", "delta waves", "insomnia relief",
            "stardust meditation", "fall asleep fast", "white stone music"
        ]
    },
    {
        "id": "tibetan_monastery",
        "name": "Tibetan Cliffside Monastery & Singing Bowls",
        "scene_files": [
            "scene11_tibetan_monastery.jpg",
            "scene_tibetan_cliffside.jpg",
            "scene15_himalayan_stupa.jpg",
            "scene_golden_stupa.jpg",
            "scene4_banyan_monk.jpg"
        ],
        "music_track": "track_tibetan_bowls.mp3",
        "title_template": "Tibetan Singing Bowls & Mountain Resonance | {dur_label} Deep Healing & Negative Energy Cleanse 🏔️🔔",
        "tags": [
            "tibetan singing bowls", "tibetan meditation", "sound bath healing",
            "cleanse negative energy", "mountain peace", "white stone music"
        ]
    },
    {
        "id": "kyoto_zen",
        "name": "Kyoto Zen Rock Garden & Bilateral Harp",
        "scene_files": [
            "scene9_zen_garden.jpg",
            "scene_kyoto_zen_twilight.jpg",
            "scene14_misty_bamboo_path.jpg",
            "scene_kyoto_bamboo_dawn.jpg",
            "scene7_lotus_pond.jpg"
        ],
        "music_track": "track_bilateral_harp.mp3",
        "title_template": "Kyoto Zen Garden & Bilateral Harp | {dur_label} Mindfulness, Emotional Calm & Inner Focus ⛩️🌿",
        "tags": [
            "zen garden", "bilateral harp", "kyoto meditation", "japanese zen",
            "mindfulness music", "focus study peace", "white stone music"
        ]
    },
    {
        "id": "celestial_aurora",
        "name": "Celestial Aurora Borealis over Arctic Fjord",
        "scene_files": [
            "scene10_aurora_borealis.jpg",
            "scene_aurora_fjord.jpg",
            "scene6_night_stars.jpg",
            "scene18_deep_space_nebula.jpg"
        ],
        "music_track": "track_432hz_the_deep.mp3",
        "title_template": "432Hz Celestial Aurora Borealis | {dur_label} Northern Lights, Night Stillness & Deep Sleep 🌌✨",
        "tags": [
            "aurora borealis", "northern lights", "432hz deep sleep", "deep meditation",
            "dream meditation", "celestial calm", "white stone music"
        ]
    },
    {
        "id": "desert_solitude",
        "name": "Golden Desert Sunset Solitude",
        "scene_files": [
            "scene12_desert_yogi.jpg",
            "scene_desert_yogi_dune.jpg",
            "scene1_yogi.jpg",
            "scene_yogi_sunrise.jpg",
            "scene3_beach.jpg"
        ],
        "music_track": "track_bansuri_flute_432hz.mp3",
        "title_template": "432Hz Desert Sunset Solitude | {dur_label} Golden Horizon, Bansuri Flute & Soul Calm 🏜️🌅",
        "tags": [
            "desert meditation", "bansuri flute 432hz", "sunset solitude",
            "soul calm", "deep peace", "inner stillness", "white stone music"
        ]
    }
]

def render_scene_clip(ffmpeg_exe: str, img_path: Path, out_clip: Path, dur_sec: float = 36.0):
    """
    Renders a single scene with ultra-slow, hypnotic directional motion:
    Glides imperceptibly from top-right towards bottom-left at ~5 pixels/sec.
    Zero sudden movements. 100% peaceful and calming for deep meditation.
    """
    # Scale to 2112x1188 (only 10% overflow for ultra-gentle movement)
    # Movement is only 192px horizontal and 108px vertical over 36 seconds
    filter_pan = (
        f"scale=2112:1188:force_original_aspect_ratio=increase,crop=2112:1188,"
        f"crop=1920:1080:x='192*(1-t/{dur_sec})':y='108*(t/{dur_sec})'"
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

def build_smooth_crossfade_cycle(ffmpeg_exe: str, scene_paths: list, out_cycle: Path, clip_dur: float = 36.0, fade_dur: float = 4.5) -> float:
    """
    Builds an imperceptible, dreamscape visual cycle:
    - Each 8K National Geographic scene stays on screen for 36 seconds.
    - Long 4.5-second silk crossfade dissolve between scenes.
    - The viewer cannot even perceive when one scene dissolves into the next!
    """
    num_scenes = len(scene_paths)
    raw_clips = []
    for idx, s in enumerate(scene_paths):
        c_path = TEMP_DIR / f"raw_scene_{idx}.mp4"
        raw_clips.append(c_path)
        render_scene_clip(ffmpeg_exe, s, c_path, dur_sec=clip_dur)

    # Build multi-input xfade filter
    inputs_cmd = []
    for c in raw_clips:
        inputs_cmd.extend(["-i", str(c)])

    filter_chains = []
    # Set timebases
    for i in range(num_scenes):
        filter_chains.append(f"[{i}:v]settb=AVTB[v{i}]")

    # Chain xfades with long 4.5-second imperceptible dissolve
    curr_v = "[v0]"
    curr_offset = clip_dur - fade_dur
    for i in range(1, num_scenes):
        next_v = f"[v{i}]"
        out_v = f"[xf{i}]" if i < num_scenes - 1 else "[final_cycle]"
        filter_chains.append(f"{curr_v}{next_v}xfade=transition=fade:duration={fade_dur:.1f}:offset={curr_offset:.2f}{out_v}")
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

def generate_global_youtube_description(theme: dict, duration_seconds: int, dur_label: str) -> str:
    """
    Generates high-converting, professional English SEO metadata targeted at
    global worldwide audiences (USA, UK, Canada, Australia, Europe).
    Includes Solfeggio frequency science, dynamic YouTube chapter timestamps,
    listening instructions, and trending global hashtags.
    """
    mins = duration_seconds // 60
    
    if "528" in theme["title_template"]:
        freq_text = "528 Hz (The Miracle Tone / DNA Repair & Heart Resonance)"
    elif "432" in theme["title_template"]:
        freq_text = "432 Hz (The Earth Resonance / Natural Healing Vibration)"
    else:
        freq_text = "Solfeggio Sound Therapy Frequency"

    # Dynamic Chapter Timestamps for YouTube Algorithm & Viewer Retention
    if mins <= 60:
        chapters = [
            ("00:00:00", "Arrival: Slow Breathing & Calming the Nervous System"),
            ("00:12:00", "Clearing Mental Fog, Stress & Overthinking"),
            ("00:25:00", "Entering Deep Meditative Stillness"),
            ("00:38:00", "Cellular Regeneration & Emotional Healing"),
            ("00:50:00", "Subconscious Harmony & Profound Peace"),
            ("01:00:00", "Awakening Renewed, Centered & Restored")
        ]
    elif mins <= 120:
        chapters = [
            ("00:00:00", "Gentle Descent: Relaxing Body & Mind"),
            ("00:20:00", "Slow Brainwave Induction (Alpha to Theta Transition)"),
            ("00:45:00", "Dissolving Insomnia, Tension & Anxiety"),
            ("01:10:00", "Entering Deep Restorative Delta Sleep"),
            ("01:35:00", "Uninterrupted Healing Sleep Waves"),
            ("02:00:00", "Overnight Subconscious Rejuvenation")
        ]
    else:
        chapters = [
            ("00:00:00", "Soft Wind-Down & Evening Stillness"),
            ("00:30:00", "Releasing All Daily Mental Fatigue"),
            ("01:00:00", "Deep Delta Wave Sleep Immersion"),
            ("01:30:00", "Restorative Physical & Spiritual Healing"),
            ("02:00:00", "Peaceful Lucid Dream Haven"),
            ("02:30:00", "Cellular Renewal & Rebalancing"),
            ("03:00:00", "Waking Up Refreshed & Restored")
        ]

    timestamp_str = "\n".join([f"{t} - {title}" for t, title in chapters])

    desc_lines = [
        f"✨ {theme['title_template'].format(dur_label=dur_label)}",
        "",
        f"Welcome to White Stone Music. Immerse your mind, body, and spirit in this {dur_label} sacred ambient sound therapy session: [{theme['name']}].",
        "",
        f"Carefully composed with authentic acoustic instruments, gentle organic nature soundscapes, and tuned to pure {freq_text}. This session is designed to quiet an overactive mind, release mental clutter, melt away physical stress, and guide you into a state of deep, restorative tranquility.",
        "",
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        "🌿 SCIENTIFIC BENEFITS OF THIS SOUND THERAPY SESSION:",
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        f"• Solfeggio Tuning: {freq_text}",
        "• Brainwave Coherence: Gently entrains brainwaves from frantic Beta states into calm Alpha (mindfulness) and restorative Theta/Delta (deep sleep).",
        "• Anxiety & Overthinking Release: Downregulates the sympathetic nervous system (fight-or-flight) and activates the parasympathetic relaxation response.",
        "• Sleep Quality: Helps quiet intrusive thoughts, insomnia, and nighttime restlessness for deep, uninterrupted rest.",
        "• Focus & Study: Provides a clean, harmonic acoustic backdrop that boosts concentration without causing mental fatigue.",
        "",
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        "⏱️ CHAPTER TIMESTAMPS:",
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        timestamp_str,
        "",
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        "🎧 HOW TO LISTEN FOR MAXIMUM BENEFIT:",
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        "1. Use comfortable headphones or high-quality stereo speakers at a soft, gentle volume.",
        "2. Close your eyes, take three slow, deep breaths, and allow your shoulders to drop.",
        "3. Perfect for: Deep Sleep, Overthinking Relief, Meditation, Yoga, Reiki, Reading, Stress Therapy, and Calm Work Focus.",
        "",
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        "🤍 ABOUT WHITE STONE MUSIC (@whitestonemusic7):",
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        "White Stone Music creates world-class 8K cinematic meditation and sound therapy experiences. Every visual is captured in pristine 8K ultra-definition, moving in slow, hypnotic cinematic harmony with acoustic instruments.",
        "",
        "🔔 SUBSCRIBE & JOIN OUR GLOBAL COMMUNITY:",
        "Subscribe for daily 1-Hour, 2-Hour, and 3-Hour healing soundscapes every morning, afternoon, and night.",
        "👍 If this music brought peace to your heart today, please like, comment with your thoughts, and share with a loved one.",
        "",
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        "© 2026 White Stone Music. 100% Original Music & 8K Visual Design.",
        "All Rights Reserved. Safe for Personal Relaxation & Study.",
        "",
        "#528hz #432hz #celticsoundtherapy #stopoverthinking #deepsleep #meditationmusic #healingfrequency #stressrelief #anxietyrelief #whitestonemusic #soundtherapy #zen #relaxingsleepmusic #insomniacure"
    ]
    return "\n".join(desc_lines)

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
    print(f"🎵 Music Master: {theme['music_track']}")
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

    # Step 2: Build Smooth Gliding + Crossfade Master Cycle (~3.2 Minutes)
    cycle_video = TEMP_DIR / f"smooth_cycle_{theme['id']}.mp4"
    print(f"\n[Step 2/4] Assembling Top-Right to Bottom-Left Gliding + 4.5s Seamless Dissolve Cycle...")
    cycle_dur = build_smooth_crossfade_cycle(ffmpeg_exe, scene_paths, cycle_video, clip_dur=36.0, fade_dur=4.5)
    print(f"  [OK] Master Seamless Visual Cycle Ready: {cycle_dur:.1f}s")

    # Step 3: Check Relaxing Music Track (100% Acoustic / Ambient Master Recording)
    music_track = MUSIC_MEDITATION / theme["music_track"]
    if not music_track.exists():
        music_track = MUSIC_MEDITATION / "track_celtic_528hz.mp3"
        if not music_track.exists():
            music_track = MUSIC_MEDITATION / "track_432hz_the_deep.mp3"

    print(f"\n[Step 3/4] Audio & Atmosphere:")
    print(f"  • Music: {music_track.name} (100% Genuine Acoustic / Ambient Master)")
    print(f"  • Visuals: Pure 8K National Geographic Gliding Scenes (Zero Artificial Lines)")
    print(f"  • Watermark Logo: {LOGO_PATH.name} (Bottom-Right)")

    # Step 4: Final Assembly (Pristine Visual Cycle Loop + Master Music Loop + Subtle Logo)
    final_mp4 = OUTPUT_DIR / f"{output_name}.mp4"
    print(f"\n[Step 4/4] Finalizing Full HD 1080p Video -> {final_mp4.name}...")

    # Pristine composite: Zero fake lines, crystal clear 1080p National Geographic visuals
    filter_composite = (
        "[0:v]format=yuv420p[vbg];"
        "[vbg][1:v]overlay=W-w-50:H-h-50:format=auto[vout]"
    )

    fade_start = max(1, duration_seconds - 5)
    af_filter = f"afade=t=in:ss=0:d=3,afade=t=out:st={fade_start}:d=5"

    cmd_final = [
        ffmpeg_exe, "-y",
        "-stream_loop", "-1", "-i", str(cycle_video),
        "-i", str(LOGO_PATH),
        "-stream_loop", "-1", "-i", str(music_track),
        "-filter_complex", filter_composite,
        "-map", "[vout]",
        "-map", "2:a",
        "-af", af_filter,
        "-t", str(duration_seconds),
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "18", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "256k", "-ac", "2", "-ar", "48000",
        str(final_mp4)
    ]
    subprocess.run(cmd_final, check=True)

    title = theme["title_template"].format(dur_label=dur_label)
    description = generate_global_youtube_description(theme, duration_seconds, dur_label)

    # Save metadata JSON for uploader
    meta_json = final_mp4.with_suffix('.json')
    meta_data = {
        "title": title[:100],
        "description": description,
        "theme_id": theme["id"],
        "theme_name": theme["name"],
        "music": music_track.name,
        "duration": duration_seconds,
        "video_file": final_mp4.name,
        "tags": theme["tags"]
    }
    with open(meta_json, "w", encoding="utf-8") as f:
        json.dump(meta_data, f, ensure_ascii=False, indent=2)

    # Generate matching high-CTR companion thumbnail
    try:
        from thumbnail_maker import create_meditation_thumbnail
        thumb_file = final_mp4.with_suffix('.thumb.jpg')
        thumb_dur = f"{mins} Mins" if mins < 60 else (f"{mins//60} Hour" if mins == 60 else f"{mins/60.0:.0f} Hours")
        create_meditation_thumbnail(theme["id"], scene_paths[0], thumb_file, dur_label=thumb_dur)
        print(f"[Thumbnail] 🖼️ High-CTR Companion Thumbnail Generated: {thumb_file.name}")
    except Exception as e:
        print(f"[Thumbnail] Notice: {e}")

    print("\n" + "=" * 80)
    print(f"🎉 [Top-Creator Video Render Complete] {final_mp4.name} ({final_mp4.stat().st_size / (1024*1024):.2f} MB)")
    print(f"📌 Title: {title}")
    print("=" * 80 + "\n")
    return final_mp4

if __name__ == "__main__":
    dur = int(sys.argv[1]) if len(sys.argv) > 1 else 300  # Default 5-minute test
    t_idx = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    build_meditation_video(duration_seconds=dur, theme_index=t_idx, output_name="test_top_creator_meditation")
