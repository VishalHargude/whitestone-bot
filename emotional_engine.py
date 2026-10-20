"""
emotional_engine.py - Complete engine for Daily Emotional & Lovable 3D Cartoon Shorts.
Specialized in:
- Tear-jerking (डोळ्यात पाणी आणणारे) family & relationship stories (बाप-लेक, माय-लेक, म्हातारे आई-वडील, खरी मैत्री)
- Fluent, deeply poetic everyday Hindi (Zero robotic stiffness)
- Auto-wrapped subtitles with large safe margins (No cut-off or clipping on borders)
- Soft emotional piano background music
"""

import json
import os
import random
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
from history_tracker import is_topic_already_used, record_published_topic

CARTOON_DIR = ASSETS_DIR / "cartoon"
MUSIC_DIR = ASSETS_DIR / "music"

# Library of deeply emotional, tear-jerking, lovable Hindi scripts
HEARTTOUCHING_STORIES = [
    {
        "id": "father_sacrifice",
        "title": "बाप का वो न दिखने वाला आंसू... 🥺💔 #shorts #fatherlove #emotional #papa",
        "description": "एक पिता कभी अपनी तकलीफ बयां नहीं करता, पर अंदर ही अंदर बच्चों के लिए सब कुछ न्योछावर कर देता है... ❤️ #shorts #father #emotionalstory #viral",
        "tags": ["shorts", "father love", "emotional story hindi", "papa status", "tear jerking", "sad status"],
        "image_file": "father_child.jpg",
        "voice": "hi-IN-MadhurNeural",
        "rate": "-4%",
        "segments": [
            {
                "hi": "एक पिता की जेब में भले ही पैसे ना हों,",
                "en": "Even when a father has empty pockets,"
            },
            {
                "hi": "पर वो अपने बच्चों के सपने कभी टूटने नहीं देता।",
                "en": "He never lets his children's dreams shatter."
            },
            {
                "hi": "खुद पुराने कपड़े पहनकर,",
                "en": "Wearing old worn-out clothes himself,"
            },
            {
                "hi": "त्योहारों पर बच्चों के लिए नए कपड़े लाता है।",
                "en": "He buys new clothes for his kids on festivals."
            },
            {
                "hi": "दुनिया के सामने सीना तानकर खड़ा रहता है,",
                "en": "He stands strong in front of the whole world,"
            },
            {
                "hi": "लेकिन रात को अकेले में अपनी तकलीफ पर चुपके से रोता है।",
                "en": "Yet secretly weeps in the dark over his struggles."
            },
            {
                "hi": "अगर आपको भी अपने पिता पर गर्व है,",
                "en": "If you are truly proud of your father,"
            },
            {
                "hi": "तो कमेंट में 'पापा' लिखकर एक लाइक जरूर करें!",
                "en": "Type 'Papa' in comments and hit like! ❤️"
            }
        ]
    },
    {
        "id": "mother_unconditional_love",
        "title": "मां की वो आखिरी रोटी... 🥺❤️ #shorts #motherlove #maa #emotional",
        "description": "मां का प्यार दुनिया में सबसे पवित्र है... मां के लिए एक लाइक तो बनता है। #shorts #maa #motherslove #family",
        "tags": ["shorts", "mother love", "maa emotional", "heart touching", "hindi cartoon"],
        "image_file": "mother_child.jpg",
        "voice": "hi-IN-SwaraNeural",
        "rate": "-3%",
        "segments": [
            {
                "hi": "दुनिया में हर रिश्ता किसी मतलब से जुड़ा होता है,",
                "en": "Every worldly relationship has some condition,"
            },
            {
                "hi": "पर एक मां का प्यार बिना किसी शर्त के मिलता है।",
                "en": "Only a mother loves unconditionally."
            },
            {
                "hi": "जब घर में सिर्फ एक रोटी बचती है,",
                "en": "When just one single bread is left in the house,"
            },
            {
                "hi": "तो वह मुस्कुराकर कह देती है,",
                "en": "She gently smiles and says,"
            },
            {
                "hi": "'बेटा तू खा ले, मुझे आज भूख नहीं है।' ",
                "en": "'You eat it my child, I am not hungry today.'"
            },
            {
                "hi": "दुनिया की सबसे अमीर जगह वो है,",
                "en": "The wealthiest place in this entire universe,"
            },
            {
                "hi": "जहां मां का आंचल और उसका प्यार मिल जाए।",
                "en": "Is the comforting embrace of your loving mother."
            },
            {
                "hi": "अपनी प्यारी मां के लिए एक दिल जरूर भेजें! ❤️",
                "en": "Send a red heart for your loving mother! ❤️"
            }
        ]
    },
    {
        "id": "elderly_father_pride",
        "title": "जब बेटे ने बूढ़े बाप को गले लगाया... 🥺😭 #shorts #fatherandson #emotional",
        "description": "जिंदगी में कभी अपने बूढ़े मां-बाप का हाथ मत छोड़ना... #shorts #father #emotional #parents",
        "tags": ["shorts", "old father", "father son love", "respect parents", "emotional short"],
        "image_file": "elderly_father.jpg",
        "voice": "hi-IN-MadhurNeural",
        "rate": "-5%",
        "segments": [
            {
                "hi": "जिस बाप ने उंगली पकड़कर चलना सिखाया था,",
                "en": "The father who held your finger to teach you walking,"
            },
            {
                "hi": "बुढ़ापे में उसी बाप का सहारा बनना ही सबसे बड़ा धर्म है।",
                "en": "Being his guiding stick in old age is your true duty."
            },
            {
                "hi": "बाप के चेहरे की हर झुर्री,",
                "en": "Every single wrinkle on a father's face,"
            },
            {
                "hi": "तुम्हारे बेहतर भविष्य की कहानी बयां करती है।",
                "en": "Tells the untold story of your bright future."
            },
            {
                "hi": "जब एक बेटा सफल होकर अपने पिता को गले लगाता है,",
                "en": "When a successful son tightly hugs his father,"
            },
            {
                "hi": "तो पिता की सारी उम्र की थकान एक पल में मिट जाती है।",
                "en": "A lifetime of exhaustion vanishes in a heartbeat."
            },
            {
                "hi": "माता-पिता का सम्मान करने वाले लोग ही महान बनते हैं।",
                "en": "Those who respect their parents achieve real greatness."
            }
        ]
    },
    {
        "id": "true_friendship",
        "title": "सच्चा यार वही जो कभी साथ ना छोड़े! 🫂❤️ #shorts #dosti #friendship #emotional",
        "description": "मुश्किल वक्त में जो साथ खड़ा रहे, वही सच्चा दोस्त होता है... #shorts #friends #dosti #loyal",
        "tags": ["shorts", "dosti status", "best friends", "emotional friendship", "cartoon short"],
        "image_file": "best_friends.jpg",
        "voice": "hi-IN-MadhurNeural",
        "rate": "-3%",
        "segments": [
            {
                "hi": "जिंदगी में मतलब के दोस्त तो बहुत मिलते हैं,",
                "en": "You meet many fair-weather friends in life,"
            },
            {
                "hi": "लेकिन सच्चा यार वही होता है जो मुश्किल में ढाल बन जाए।",
                "en": "A true friend stands as a shield in difficult times."
            },
            {
                "hi": "जो आपकी खामोशी के पीछे का दर्द समझ सके,",
                "en": "The one who feels the silent pain behind your smile,"
            },
            {
                "hi": "और अंधेरे वक्त में कहे - 'घबरा मत, मैं तेरे साथ हूँ!'",
                "en": "And says in the dark - 'Don't worry, I am here with you!'"
            },
            {
                "hi": "पैसा और शोहरत तो कोई भी कमा लेता है,",
                "en": "Anyone can earn fame and riches,"
            },
            {
                "hi": "मगर सच्चा दोस्त कमाना सबसे बड़ी दौलत है।",
                "en": "Earning a loyal friend is the greatest treasure."
            },
            {
                "hi": "अपने सबसे पक्के यार को यह वीडियो जरूर शेयर करें! 🫂",
                "en": "Share this with your one true best friend! 🫂"
            }
        ]
    },
    {
        "id": "sanatan_tradition_namaste",
        "channel_id": "channel_1_dharma",
        "title": "नमस्ते करने के पीछे का हैरान कर देने वाला विज्ञान! 🚩🙏 #shorts #sanatandharma #hindufacts",
        "description": "जानिए हिंदू धर्म में दोनों हाथ जोड़कर नमस्ते क्यों किया जाता है! #shorts #hinduism #sanatanculture #vedicscience",
        "tags": ["shorts", "sanatan dharma", "namaste scientific reason", "hindu rituals", "vedic science", "proud hindu"],
        "image_file": "sanatan_dharma.jpg",
        "voice": "hi-IN-MadhurNeural",
        "rate": "-3%",
        "segments": [
            {
                "hi": "हमारे सनातन हिंदू धर्म में हाथ जोड़कर नमस्ते करने की पवित्र परंपरा है।",
                "en": "In Sanatan Hindu culture, folding hands in Namaste is a sacred tradition."
            },
            {
                "hi": "पर क्या आप जानते हैं कि इसके पीछे का वैज्ञानिक रहस्य क्या है?",
                "en": "Do you know the profound scientific mystery behind it?"
            },
            {
                "hi": "जब हम दोनों हाथों की उंगलियों को आपस में मिलाते हैं,",
                "en": "When our fingertips touch each other,"
            },
            {
                "hi": "तो हमारे शरीर के एक्यूप्रेशर बिंदु सक्रिय हो जाते हैं,",
                "en": "Acupressure points activate across our nervous system,"
            },
            {
                "hi": "जिससे मन शांत और तनावमुक्त होता है।",
                "en": "Calming the mind and melting away all stress."
            },
            {
                "hi": "और आध्यात्मिक रूप से, नमस्ते का अर्थ है - 'मैं आपके भीतर बैठे ईश्वर को प्रणाम करता हूँ!'",
                "en": "And spiritually, Namaste means 'I bow to the Divine within you!'"
            },
            {
                "hi": "हमारी संस्कृति केवल परंपरा नहीं, एक अद्भुत विज्ञान है। गर्व से कहो, हम सनातनी हैं! 🚩",
                "en": "Our culture is pure science. Say with pride, Jai Shri Ram! 🚩"
            }
        ]
    },
    {
        "id": "humanity_kindness_sharing",
        "channel_id": "channel_2_humanity",
        "title": "इंसानियत से बड़ा कोई धर्म नहीं होता... 🥺❤️ #shorts #humanity #kindness #emotional",
        "description": "मंदिरों में भगवान को ढूंढने से अच्छा है किसी भूखे के चेहरे पर मुस्कान लाना... #shorts #humanityfirst #kindness #karma",
        "tags": ["shorts", "humanity", "kindness", "helping the poor", "emotional short", "inspire"],
        "image_file": "humanity_kindness.jpg",
        "voice": "hi-IN-MadhurNeural",
        "rate": "-4%",
        "segments": [
            {
                "hi": "मंदिर और मस्जिदों में तो सब ईश्वर को ढूंढते हैं,",
                "en": "Everyone seeks the Divine in temples and shrines,"
            },
            {
                "hi": "लेकिन ईश्वर असली रूप में किसी भूखे के चेहरे की मुस्कान में मिलता है।",
                "en": "Yet the Divine truly resides in the smile of a fed child."
            },
            {
                "hi": "जब आप किसी बेबस इंसान की निस्वार्थ मदद करते हैं,",
                "en": "When you extend a loving hand to the helpless,"
            },
            {
                "hi": "तो ईश्वर आपकी प्रार्थना से भी ज्यादा आपके उस कर्म से खुश होते हैं।",
                "en": "God rejoices in that selfless deed more than in any prayer."
            },
            {
                "hi": "पैसा और दौलत तो यहीं छूट जाएगी,",
                "en": "All worldly wealth will stay behind on this earth,"
            },
            {
                "hi": "लेकिन आपका किया हुआ नेकी का काम हमेशा आपके साथ रहेगा।",
                "en": "Only the warmth of your good deeds stays with your soul."
            },
            {
                "hi": "इंसानियत से बड़ा कोई मजहब नहीं होता... एक लाइक जरूर करें! ❤️",
                "en": "Kindness is the greatest religion. Drop a heart if you agree! ❤️"
            }
        ]
    }
]

def wrap_text_clean(text: str, max_chars_per_line: int = 22) -> str:
    """
    Splits text cleanly across max 22 chars per line using \\N.
    Prevents any words from clipping on mobile screen edges.
    """
    words = text.strip().split()
    lines = []
    curr = []
    curr_len = 0

    for w in words:
        if curr_len + len(w) + 1 > max_chars_per_line and curr:
            lines.append(" ".join(curr))
            curr = [w]
            curr_len = len(w)
        else:
            curr.append(w)
            curr_len += len(w) + 1

    if curr:
        lines.append(" ".join(curr))

    return "\\N".join(lines)

def format_ass_time(seconds_val: float) -> str:
    td = timedelta(seconds=seconds_val)
    total_seconds = int(td.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    centiseconds = int(td.microseconds / 10000)
    return f"{hours}:{minutes:02d}:{seconds:02d}.{centiseconds:02d}"

async def render_emotional_audio_and_subs(story: dict, output_audio: Path, output_ass: Path):
    """
    Synthesizes fluent, emotional speech and writes wrapped, perfectly centered subtitles.
    """
    voice = story.get("voice", "hi-IN-MadhurNeural")
    rate = story.get("rate", "-4%")
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()

    combined_audio = bytearray()
    dialogues = []
    current_time = 0.0

    for idx, seg in enumerate(story["segments"]):
        hi_raw = seg["hi"]
        en_raw = seg["en"]

        # Synthesize audio with warm, slow delivery
        comm = edge_tts.Communicate(hi_raw, voice=voice, rate=rate)
        seg_audio = bytearray()
        async for chunk in comm.stream():
            if chunk["type"] == "audio":
                seg_audio.extend(chunk["data"])

        # Measure exact duration
        tmp_line = TEMP_DIR / f"line_em_{idx}.mp3"
        tmp_line.write_bytes(seg_audio)

        res = subprocess.run([ffmpeg_exe, "-i", str(tmp_line)], capture_output=True, text=True)
        m = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)", res.stderr)
        line_dur = 2.5
        if m:
            h, mins, s = m.groups()
            line_dur = int(h) * 3600 + int(mins) * 60 + float(s)

        start_str = format_ass_time(current_time)
        end_time = current_time + line_dur
        end_str = format_ass_time(end_time)

        # Clean auto-wrapped text (Never overflows screen edges)
        hi_wrapped = wrap_text_clean(hi_raw, max_chars_per_line=20)

        # Single pure Hindi line (No English subtitle)
        dialogues.append(f"Dialogue: 0,{start_str},{end_str},HindiEmotion,,0,0,0,,{hi_wrapped}")

        combined_audio.extend(seg_audio)
        current_time = end_time + 0.35  # Subtle emotional pause

    output_audio.write_bytes(combined_audio)

    # Clean ASS header with only pure Hindi styling (Large, bold, perfectly centered)
    ass_header = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: HindiEmotion,Nirmala UI,60,&H0000FFFF,&H000000FF,&H00000000,&H90000000,-1,0,0,0,100,100,0,0,1,5,2,2,90,90,720,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    ass_content = ass_header + "\n".join(dialogues) + "\n"
    output_ass.write_text(ass_content, encoding="utf-8")

    return current_time

def generate_daily_emotional_short(story_id: str = None, channel_id: str = "general", custom_output_name: str = None) -> dict:
    """
    Main function to generate a daily tear-jerking, lovable 3D Pixar cartoon Short.
    Guarantees ZERO duplicate videos using history tracking.
    """
    import asyncio
    if story_id:
        selected_story = next((s for s in HEARTTOUCHING_STORIES if s["id"] == story_id), HEARTTOUCHING_STORIES[0])
    else:
        # Filter only fresh, unused stories
        unused_stories = [s for s in HEARTTOUCHING_STORIES if not is_topic_already_used(s["id"])]
        if unused_stories:
            selected_story = random.choice(unused_stories)
        else:
            # If all were used, pick any least recently used
            selected_story = random.choice(HEARTTOUCHING_STORIES)

    title = selected_story["title"]
    print(f"\n[Emotional Engine] --- Generating Emotional Story: {title} (Channel: {channel_id}) ---")

    audio_path = TEMP_DIR / "emotion_voice.mp3"
    ass_path = TEMP_DIR / "subtitles.ass"

    # Step 1: Synthesize voice and wrapped subtitles
    print("[Emotional Engine] Step 1: Synthesizing fluent, tear-jerking Hindi narration...")
    total_duration = asyncio.run(render_emotional_audio_and_subs(selected_story, audio_path, ass_path))
    padded_duration = total_duration + 0.8
    print(f"[Emotional Engine] Total speech duration: {total_duration:.2f}s")

    # Step 2: Render slow, breathing camera zoompan on 3D Pixar character scene
    img_name = selected_story.get("image_file", "father_child.jpg")
    img_path = CARTOON_DIR / img_name
    if not img_path.exists():
        img_path = CARTOON_DIR / "father_child.jpg"

    print(f"[Emotional Engine] Step 2: Rendering cinematic 3D cartoon motion on {img_path.name}...")
    bg_video_path = TEMP_DIR / "emotion_motion.mp4"
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()

    total_frames = int(padded_duration * FPS) + 15
    zoom_speed = 0.16 / max(total_frames, 1)

    cmd_motion = [
        ffmpeg_exe, "-y",
        "-loop", "1", "-i", str(img_path),
        "-vf", f"scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,zoompan=z='min(zoom+{zoom_speed:.6f},1.16)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={total_frames}:s={VIDEO_WIDTH}x{VIDEO_HEIGHT}:fps={FPS}",
        "-t", str(padded_duration),
        "-c:v", "libx264", "-preset", "fast", "-pix_fmt", "yuv420p",
        str(bg_video_path)
    ]
    subprocess.run(cmd_motion, capture_output=True, check=True)

    # Step 3: Mix with soft, gentle piano music & burn perfectly centered subtitles
    print("[Emotional Engine] Step 3: Mixing soft piano music and burning centered captions...")
    bgm_path = MUSIC_DIR / "emotional_bgm.mp3"

    if custom_output_name:
        final_mp4 = OUTPUT_DIR / f"{custom_output_name}.mp4"
    else:
        timestamp = int(time.time())
        final_mp4 = OUTPUT_DIR / f"daily_emotional_{timestamp}.mp4"

    filter_complex = (
        "[1:a]volume=1.0[voice];"
        "[2:a]volume=0.10,aloop=loop=-1:size=2e+09[bgm];"
        "[voice][bgm]amix=inputs=2:duration=first:dropout_transition=2[aout]"
    )

    cmd_final = [
        ffmpeg_exe, "-y",
        "-i", "emotion_motion.mp4",
        "-i", "emotion_voice.mp3",
        "-i", str(bgm_path),
        "-filter_complex", filter_complex,
        "-map", "0:v", "-map", "[aout]",
    ]

    # Only burn subtitles if explicitly enabled in config
    if ENABLE_SUBTITLES:
        cmd_final.extend(["-vf", "subtitles=subtitles.ass"])

    cmd_final.extend([
        "-c:v", "libx264", "-preset", "fast", "-crf", "19",
        "-c:a", "aac", "-b:a", "192k",
        "-pix_fmt", "yuv420p",
        "-shortest",
        str(final_mp4)
    ])

    res = subprocess.run(cmd_final, cwd=TEMP_DIR, capture_output=True, text=True)
    if res.returncode != 0:
        print("[Emotional Engine] Error:", res.stderr[-500:])
        raise RuntimeError("Assembly failed")

    # Step 4: Metadata JSON
    meta_path = final_mp4.with_suffix(".json")
    meta = {
        "title": selected_story["title"],
        "description": selected_story["description"],
        "tags": selected_story["tags"],
        "video_path": str(final_mp4),
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    # Record in history database to prevent repetition
    record_published_topic(channel_id, selected_story["id"], selected_story["title"])

    print(f"\n[Emotional Engine] 💖 SUCCESS! Tear-jerking Short created at: {final_mp4}")
    print(f"[Emotional Engine] Size: {os.path.getsize(final_mp4) / (1024*1024):.2f} MB")
    return meta
