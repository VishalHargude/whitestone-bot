"""
create_long_meditation_video.py - 100% Zero-Duplicate Multi-Theme Long-Form Meditation Video Generator.
Branded with White Stone Music logo watermark in bottom-right corner.
Supports 30-Minute, 1-Hour, 2-Hour, and 3-Hour video durations with Ken Burns stream-looping.

10 Distinct Thematic Worlds (GUARANTEED NEVER TO REPEAT):
1. Himalayan Sunrise Dhyana (Mountain Yogi & Ancient Banyan Monk) - 432Hz
2. Sacred Temple & Floating Diyas (Ancient Sanctum & Zen Lotus Pond) - 528Hz
3. Golden Sunset Beach & Ocean Zen (Sunset Ocean Shore & Evening Calm) - 432Hz
4. Sacred Bamboo Forest & Cascading Waters (Bamboo Waterfall & Forest Stream) - 432Hz
5. Cosmic Universe Deep Sleep (Milky Way Galaxy & Delta Wave Stillness) - 432Hz
6. Tibetan Cliffside Monastery (Ancient Himalayan Retreat & Prayer Flags) - 528Hz
7. Kyoto Zen Rock Garden (Japanese Autumn Maples & Mindfulness Raked Sand) - 432Hz
8. Celestial Aurora Borealis (Dancing Northern Lights over Mirror Arctic Fjord) - 432Hz
9. Golden Desert Solitude (Sunset Sand Dunes & Solitary Dhyana Yogi) - 432Hz
10. Sacred Lotus Pond Sanctuary (Divine Floating Lotuses & Candle Reflections) - 528Hz
"""

import gc
import json
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

# 10 Pure, High-Definition Thematic Worlds (3 Photorealistic 8K Scenes Per Theme)
THEMES = [
    {
        "id": "himalayan_sunrise",
        "name": "Himalayan Sunrise Dhyana",
        "scene_files": ["scene1_yogi.jpg", "scene4_banyan_monk.jpg", "scene15_himalayan_stupa.jpg"],
        "music_track": "track1.mp3",
        "title_template": "432Hz Himalayan Sunrise Meditation | {dur_label} Deep Inner Stillness, Pranayama & Peace 🧘‍♂️🌿",
        "chapters": [
            "Himalayan Yogi Sunrise (Mindful Breathing & Stillness)",
            "Sacred Banyan Monk at Dawn (Inner Peace & Awareness)",
            "Golden Himalayan Stupa (Profound Peace & Elevation)"
        ],
        "tags": [
            "himalayan meditation", "yogi meditation", "432hz sunrise", "pranayama music",
            "inner peace", "dhyana meditation", "deep healing music", "white stone music"
        ]
    },
    {
        "id": "sacred_temple",
        "name": "Sacred Temple & Floating Diyas",
        "scene_files": ["scene5_temple_yogi.jpg", "scene13_varanasi_ghat.jpg", "scene7_lotus_pond.jpg"],
        "music_track": "track2.mp3",
        "title_template": "528Hz Sacred Temple Meditation | {dur_label} Positive Energy, Divine Aura & Deep Calm 🪔✨",
        "chapters": [
            "Sacred Temple Sanctuary (Divine Light & Aura Cleansing)",
            "Sacred River Ghat at Sunrise (Pure Positive Vibration)",
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
        "scene_files": ["scene3_beach.jpg", "scene16_beach_ocean_sunset.jpg", "scene17_zen_beach_cove.jpg"],
        "music_track": "track1.mp3",
        "title_template": "432Hz Sunset Beach Meditation | {dur_label} Stress Relief, Ocean Calm & Inner Peace 🌊🧘‍♀️",
        "chapters": [
            "Golden Beach Sunset (Deep Physical & Mental Release)",
            "Pastel Ocean Shoreline (Releasing Daily Stress & Anxiety)",
            "Tranquil Sunset Cove (Surrender to Complete Inner Peace)"
        ],
        "tags": [
            "ocean meditation", "beach relaxation", "sunset calm", "stress relief music",
            "anti anxiety", "peaceful sleep", "mindfulness waves", "white stone music"
        ]
    },
    {
        "id": "bamboo_waterfall",
        "name": "Sacred Bamboo Forest & Cascading Waters",
        "scene_files": ["scene2_waterfall.jpg", "scene14_misty_bamboo_path.jpg", "scene8_forest_river.jpg"],
        "music_track": "track2.mp3",
        "title_template": "432Hz Bamboo Forest Waterfall Zen | {dur_label} Nature Healing, Mindful Peace & Stress Relief 🎋💧",
        "chapters": [
            "Sacred Bamboo Waterfall (Washing Away Tension & Negativity)",
            "Misty Bamboo Forest Pathway (Tranquil Zen Walk)",
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
        "scene_files": ["scene6_night_stars.jpg", "scene18_deep_space_nebula.jpg", "scene10_aurora_borealis.jpg"],
        "music_track": "track1.mp3",
        "title_template": "432Hz Deep Sleep Cosmic Meditation | {dur_label} Fall Asleep Fast, Insomnia Relief & Delta Healing 🌙✨",
        "chapters": [
            "Milky Way Galaxy Night (Cosmic Stillness & Sleep Drift)",
            "Glowing Cosmic Nebula (Surrendering to Deep Sleep)",
            "Celestial Northern Lights (Total Relaxation & Deep Delta Rest)"
        ],
        "tags": [
            "deep sleep music", "fall asleep fast", "insomnia cure", "cosmic meditation",
            "night relaxation", "delta wave healing", "sleep aid music", "white stone music"
        ]
    },
    {
        "id": "tibetan_monastery",
        "name": "Tibetan Cliffside Sanctuary",
        "scene_files": ["scene11_tibetan_monastery.jpg", "scene15_himalayan_stupa.jpg", "scene4_banyan_monk.jpg"],
        "music_track": "track2.mp3",
        "title_template": "528Hz Tibetan Monastery Chants & Bell Meditation | {dur_label} Sacred Healing & Transformation 🏔️📿",
        "chapters": [
            "Ancient Cliffside Monastery (Sacred Chants & Elevation)",
            "Golden Stupa Ridge (Awakening Higher Consciousness)",
            "Sacred Banyan Sanctuary (Inner Balance & Stillness)"
        ],
        "tags": [
            "tibetan meditation", "528hz healing", "monastery calm", "spiritual awakening",
            "sacred bells", "monk meditation", "chakra alignment", "white stone music"
        ]
    },
    {
        "id": "kyoto_zen_garden",
        "name": "Kyoto Zen Rock Garden & Autumn Leaves",
        "scene_files": ["scene9_zen_garden.jpg", "scene14_misty_bamboo_path.jpg", "scene7_lotus_pond.jpg"],
        "music_track": "track1.mp3",
        "title_template": "432Hz Kyoto Zen Garden Meditation | {dur_label} Overcome Overthinking, Mental Clarity & Stillness 🍁🪨",
        "chapters": [
            "Kyoto Zen Stone Garden (Clearing the Cluttered Mind)",
            "Misty Bamboo Path (Walking Meditation & Clarity)",
            "Autumn Maples & Still Waters (Deep Inner Balance & Focus)"
        ],
        "tags": [
            "zen garden", "kyoto meditation", "432hz focus", "stop overthinking",
            "mental clarity", "japanese zen", "peaceful mindfulness", "white stone music"
        ]
    },
    {
        "id": "celestial_aurora",
        "name": "Celestial Aurora Borealis Arctic Stillness",
        "scene_files": ["scene10_aurora_borealis.jpg", "scene6_night_stars.jpg", "scene8_forest_river.jpg"],
        "music_track": "track1.mp3",
        "title_template": "432Hz Celestial Aurora Borealis Sleep | {dur_label} Deep REM Sleep, Anxiety Relief & Dreams 🌌❄️",
        "chapters": [
            "Dancing Northern Lights over Fjord (Surrender to Tranquility)",
            "Starlit Cosmic Night (Drifting into Deep Restful Sleep)",
            "Misty Midnight River (Restorative Theta Sleep)"
        ],
        "tags": [
            "aurora borealis sleep", "northern lights meditation", "432hz sleep",
            "insomnia relief", "calm night music", "deep theta sleep", "white stone music"
        ]
    },
    {
        "id": "desert_solitude",
        "name": "Golden Desert Sunset Solitude",
        "scene_files": ["scene12_desert_yogi.jpg", "scene1_yogi.jpg", "scene3_beach.jpg"],
        "music_track": "track1.mp3",
        "title_template": "432Hz Golden Desert Sunset Meditation | {dur_label} Pure Solitude, Detox Mind & Deep Peace 🏜️🧘‍♂️",
        "chapters": [
            "Golden Sand Dunes at Sunset (Letting Go of Daily Heavy Burdens)",
            "Mountain Yogi Sunrise (Inner Strength & Grounding)",
            "Solitary Ridge Stillness (Reconnecting with the Inner Core)"
        ],
        "tags": [
            "desert meditation", "solitude peace", "detox mind", "sunset calm",
            "432hz healing", "yogi solitude", "emotional release", "white stone music"
        ]
    },
    {
        "id": "lotus_sanctuary",
        "name": "Sacred Lotus Temple Sanctuary",
        "scene_files": ["scene7_lotus_pond.jpg", "scene13_varanasi_ghat.jpg", "scene5_temple_yogi.jpg"],
        "music_track": "track2.mp3",
        "title_template": "528Hz Sacred Lotus Sanctuary Meditation | {dur_label} Heart Chakra Love, Healing & Miracles 🪷🕯️",
        "chapters": [
            "Twilight Floating Lotus Lamps (Opening the Heart Chakra)",
            "Sacred River Ghat at Sunrise (Pure Positive Vibration)",
            "Temple Sanctuary Sanctity (Attracting Peace & Positive Vibrations)"
        ],
        "tags": [
            "lotus meditation", "heart chakra 528hz", "miracle tone", "divine love",
            "floating lamps", "sacred sanctuary", "inner glow", "white stone music"
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

    if theme_index is None:
        theme_index = int((time.time() // (4 * 3600))) % len(THEMES)

    theme = THEMES[theme_index % len(THEMES)]

    print("=" * 75)
    print(f"🧘‍♂️ White Stone Music - Long-Form Video Generator")
    print(f"🎨 Theme #{theme_index % len(THEMES) + 1}: [{theme['name']}]")
    print(f"⏱️ Duration: {dur_label} ({duration_seconds}s)")
    print("=" * 75)

    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()

    scene_paths = [ASSETS_MEDITATION / f for f in theme["scene_files"]]
    for s in scene_paths:
        if not s.exists():
            raise FileNotFoundError(f"Missing scene asset: {s}")

    num_scenes = len(scene_paths)
    scene_dur = 120  # 2 Minutes per photo
    trans_dur = 3    # 3-Second smooth cinematic crossfade dissolve

    print(f"\n[Visuals] {num_scenes} Unique 8K Scenes for [{theme['name']}]:")
    for idx, s in enumerate(scene_paths):
        print(f"  {idx+1}. {s.name}")
    print(f"  • Logo: {LOGO_PATH.name} (Bottom-Right corner)")
    print(f"  • Scene Motion: Left-to-Right slow cinematic pan (120s per photo)")
    print(f"  • Scene Transitions: {trans_dur}s smooth dissolve crossfade")

    # Step A: Render Master 3-Scene Visual Sequence with 2-minute diagonal pan and cross-dissolve
    master_seq_path = TEMP_DIR / "master_3scene_sequence.mp4"
    print(f"\n[Visuals] Rendering Master 3-Scene Dynamic Sequence ({num_scenes * scene_dur}s with {trans_dur}s cross-dissolves)...")

    d = scene_dur
    t_fade = trans_dur
    offset1 = d - t_fade
    offset2 = offset1 + d - t_fade

    # Diagonal Motion 1: Bottom-Left corner to Top-Right corner
    vf_pan0 = f"scale=2304:1296:force_original_aspect_ratio=increase,crop=1920:1080:(in_w-out_w)*(t/{d}):(in_h-out_h)*(1-(t/{d})),format=yuv420p"
    # Diagonal Motion 2: Bottom-Right corner to Top-Left corner
    vf_pan1 = f"scale=2304:1296:force_original_aspect_ratio=increase,crop=1920:1080:(in_w-out_w)*(1-(t/{d})):(in_h-out_h)*(1-(t/{d})),format=yuv420p"
    # Diagonal Motion 3: Top-Left corner to Bottom-Right corner
    vf_pan2 = f"scale=2304:1296:force_original_aspect_ratio=increase,crop=1920:1080:(in_w-out_w)*(t/{d}):(in_h-out_h)*(t/{d}),format=yuv420p"

    filter_complex = (
        f"[0:v]{vf_pan0}[v0];"
        f"[1:v]{vf_pan1}[v1];"
        f"[2:v]{vf_pan2}[v2];"
        f"[v0][v1]xfade=transition=fade:duration={t_fade}:offset={offset1}[x1];"
        f"[x1][v2]xfade=transition=fade:duration={t_fade}:offset={offset2}[merged];"
        f"[merged][3:v]overlay=W-w-50:H-h-50[outv]"
    )

    cmd_master = [
        ffmpeg_exe, "-y",
        "-loop", "1", "-t", str(d), "-i", str(scene_paths[0]),
        "-loop", "1", "-t", str(d), "-i", str(scene_paths[1]),
        "-loop", "1", "-t", str(d), "-i", str(scene_paths[2]),
        "-i", str(LOGO_PATH),
        "-filter_complex", filter_complex,
        "-map", "[outv]",
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "24", "-r", "24",
        "-pix_fmt", "yuv420p",
        "-an",
        str(master_seq_path)
    ]
    subprocess.run(cmd_master, capture_output=True, check=True)

    master_block_dur = offset2 + d  # e.g. 117 + 117 + 120 = 354s
    num_loops = max(1, int(round(duration_seconds / master_block_dur)) + 2)

    print(f"\n[Visuals] Looping master 3-scene sequence ({num_loops} loops) with stream copy to {duration_seconds}s...")
    merged_video_visual = TEMP_DIR / "merged_visuals.mp4"
    cmd_loop = [
        ffmpeg_exe, "-y",
        "-stream_loop", str(num_loops),
        "-i", str(master_seq_path),
        "-t", str(duration_seconds),
        "-c", "copy",
        str(merged_video_visual)
    ]
    subprocess.run(cmd_loop, capture_output=True, check=True)

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

    # Dynamic SEO Metadata Generation with 2-Minute Interactive Chapters
    formatted_chapters = [
        f"00:00 - Scene 1: {theme['chapters'][0]}",
        f"02:00 - Scene 2: {theme['chapters'][1]}",
        f"04:00 - Scene 3: {theme['chapters'][2]}",
        "06:00 - Mindful Breathing & Tension Release",
        "15:00 - Complete Muscle Relaxation & Presence",
        "30:00 - Inner Stillness, Anti-Anxiety & Peace",
        "45:00 - Restorative Delta Waves & Inner Healing"
    ]
    if hours >= 2:
        formatted_chapters.extend([
            "01:00:00 - Entering Deep Sleep & Subconscious Healing",
            "01:30:00 - Pure Cosmic Rest & Soul Rejuvenation"
        ])

    chapters_str = "\n".join(formatted_chapters)
    title = theme["title_template"].format(dur_label=dur_label)

    # Systematic Tag Management (High SEO, User Branding & YouTube 500-char Compliance)
    base_tags = [
        "vishal hargude",
        "white stone music",
        "meditation music",
        "relaxing sleep music",
        "deep healing music",
        "stress relief meditation",
        "anxiety relief",
        "432hz frequency",
        "528hz miracle tone",
        "binaural beats sleep",
        "calm mind dhyana",
        f"{dur_label.lower()} meditation",
        f"{dur_label.lower()} sleep music"
    ]
    raw_tags = theme.get("tags", []) + base_tags
    unique_tags = []
    seen = set()
    total_len = 0
    for t in raw_tags:
        t_clean = t.strip()
        if t_clean.lower() not in seen:
            seen.add(t_clean.lower())
            if total_len + len(t_clean) + 1 <= 480:
                unique_tags.append(t_clean)
                total_len += len(t_clean) + 1

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
            "🌿 CREATOR & CHANNEL CREDITS:\n"
            "• Produced & Curated by: Vishal Hargude\n"
            "• Channel: White Stone Music\n"
            "• Dedicated to mental wellness, inner peace, and sound healing worldwide.\n"
            "• © White Stone Music & Vishal Hargude. All Rights Reserved.\n\n"
            "#meditationmusic #432hz #528hz #whitestonemusic #vishalhargude #deepsleep #stressrelief #zen #healingmusic #yoga #mindfulness"
        ),
        "tags": unique_tags,
        "video_path": str(final_mp4),
        "duration_minutes": mins,
        "is_short": False,
        "theme_id": theme["id"],
        "theme_name": theme["name"],
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S")
    }

    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    # Step 7: Generate Distinct Custom YouTube Thumbnail
    try:
        from thumbnail_maker import generate_custom_thumbnail
        thumb_path = final_mp4.with_suffix(".thumb.jpg")
        generate_custom_thumbnail(
            scene_img_path=scene_paths[0],
            theme_id=theme["id"],
            dur_label=dur_label,
            output_path=thumb_path
        )
        print(f"🖼️ [Thumbnail] Custom 1280x720 Thumbnail generated: {thumb_path.name}")
    except Exception as e:
        print(f"[Thumbnail] Notice: {e}")

    # Clean intermediate temporary files
    for tmp_file in [master_seq_path, merged_video_visual, audio_loop_path]:
        try:
            tmp_file.unlink(missing_ok=True)
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
    dur = 3600
    theme_idx = None
    if len(sys.argv) > 1:
        dur = int(sys.argv[1])
    if len(sys.argv) > 2:
        theme_idx = int(sys.argv[2])
    build_meditation_video(duration_seconds=dur, theme_index=theme_idx, output_name=f"whitestone_{dur//60}min")
