"""
generate_golden_embers.py - Generates seamless loopable 10-second 1920x1080
warm golden sunlight embers / bokeh motes overlay video.
"""

import math
import random
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw

BASE_DIR = Path(r"C:\Users\Vishal Hargude\.gemini\antigravity\scratch\hindi_shorts_generator")
ASSETS_DIR = BASE_DIR / "assets"
OUT_EMBERS_MP4 = ASSETS_DIR / "golden_embers_sunlight.mp4"
ffmpeg_exe = r'C:\Users\Vishal Hargude\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe'

WIDTH, HEIGHT = 1920, 1080
FPS = 30
DURATION_SEC = 10
TOTAL_FRAMES = FPS * DURATION_SEC

random.seed(528)

NUM_EMBERS = 140
embers = []
for _ in range(NUM_EMBERS):
    radius = random.uniform(1.8, 5.5)
    alpha = random.randint(50, 130)
    wraps_y = random.choice([1, 2])
    wraps_x = random.choice([-1, 0, 1])
    init_x = random.uniform(0, WIDTH)
    init_y = random.uniform(0, HEIGHT)
    sway_amp = random.uniform(15, 35)
    sway_freq = random.randint(1, 2)

    embers.append({
        "init_x": init_x,
        "init_y": init_y,
        "radius": radius,
        "alpha": alpha,
        "wraps_y": wraps_y,
        "wraps_x": wraps_x,
        "sway_amp": sway_amp,
        "sway_freq": sway_freq
    })

print(f"[Embers Generator] Rendering {TOTAL_FRAMES} frames of golden sunlight embers overlay...")

cmd = [
    ffmpeg_exe, "-y",
    "-f", "rawvideo",
    "-vcodec", "rawvideo",
    "-s", f"{WIDTH}x{HEIGHT}",
    "-pix_fmt", "rgba",
    "-r", str(FPS),
    "-i", "-",
    "-c:v", "libx264",
    "-preset", "veryfast",
    "-crf", "18",
    "-pix_fmt", "yuv420p",
    str(OUT_EMBERS_MP4)
]

proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)

for f_idx in range(TOTAL_FRAMES):
    progress = f_idx / TOTAL_FRAMES
    frame = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    draw = ImageDraw.Draw(frame)

    for em in embers:
        # Drifting gently upwards/across
        y = (em["init_y"] - em["wraps_y"] * HEIGHT * progress) % HEIGHT
        sway = em["sway_amp"] * math.sin(2 * math.pi * em["sway_freq"] * progress)
        x = (em["init_x"] + em["wraps_x"] * (WIDTH * 0.2) * progress + sway) % WIDTH

        r = em["radius"]
        c = (255, 220, 140, em["alpha"])
        draw.ellipse([(x - r, y - r), (x + r, y + r)], fill=c)

    proc.stdin.write(frame.tobytes())

proc.stdin.close()
proc.wait()
print(f"[OK] Generated seamless golden embers overlay: {OUT_EMBERS_MP4} ({OUT_EMBERS_MP4.stat().st_size / (1024*1024):.2f} MB)")
