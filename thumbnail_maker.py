"""
thumbnail_maker.py - High-Converting YouTube Custom Thumbnail Generator.
Creates distinct, high-CTR 1280x720 thumbnails for each meditation theme:
- Distinct color themes (Golden Temple, Purple Galaxy, Emerald Waterfall, Pastel Beach, Mountain Sunrise)
- Radiant Frequency Badges (432Hz / 528Hz)
- Bold, High-Contrast Typography for mobile and desktop screens
- White Stone Music brand watermark
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = Path(__file__).resolve().parent
LOGO_PATH = BASE_DIR / "assets" / "white_stone_logo.png"

THEME_THUMB_STYLES = {
    "himalayan_sunrise": {
        "freq": "432 Hz",
        "badge_color": (212, 175, 55),
        "headline": "INNER PEACE",
        "subline": "& STILLNESS",
        "pill_text": "Mindful Breathing 🧘‍♂️",
        "pill_color": (255, 235, 150)
    },
    "sacred_temple": {
        "freq": "528 Hz",
        "badge_color": (230, 160, 40),
        "headline": "POSITIVE ENERGY",
        "subline": "& DIVINE AURA",
        "pill_text": "Cleanse Negative Energy 🪔",
        "pill_color": (255, 215, 120)
    },
    "sunset_beach": {
        "freq": "432 Hz",
        "badge_color": (220, 120, 70),
        "headline": "STRESS RELIEF",
        "subline": "& ANXIETY CALM",
        "pill_text": "Instant Deep Relaxation 🌊",
        "pill_color": (255, 200, 160)
    },
    "bamboo_waterfall": {
        "freq": "432 Hz",
        "badge_color": (46, 175, 100),
        "headline": "ZEN NATURE",
        "subline": "& MINDFUL FOCUS",
        "pill_text": "Wash Away Tension 🎋",
        "pill_color": (160, 240, 180)
    },
    "deep_sleep_cosmos": {
        "freq": "432 Hz",
        "badge_color": (140, 90, 220),
        "headline": "DEEP SLEEP",
        "subline": "& INSOMNIA CURE",
        "pill_text": "Fall Asleep In 10 Mins 🌙",
        "pill_color": (210, 180, 255)
    }
}

def generate_custom_thumbnail(scene_img_path: Path, theme_id: str, dur_label: str, output_path: Path) -> Path:
    """Renders a 1280x720 professional YouTube thumbnail with distinct visual branding."""
    style = THEME_THUMB_STYLES.get(theme_id, THEME_THUMB_STYLES["himalayan_sunrise"])

    img = Image.open(scene_img_path).convert('RGB')
    img = img.resize((1280, 720), Image.Resampling.LANCZOS)

    # Left-to-right subtle dark gradient overlay for crystal-clear text readability
    gradient = Image.new('RGBA', (1280, 720), (0, 0, 0, 0))
    g_draw = ImageDraw.Draw(gradient)
    for x in range(650):
        alpha = int(195 * (1.0 - (x / 650.0)))
        g_draw.line([(x, 0), (x, 720)], fill=(0, 0, 0, alpha))

    img = Image.alpha_composite(img.convert('RGBA'), gradient).convert('RGB')
    draw = ImageDraw.Draw(img)

    # Fonts
    try:
        font_badge = ImageFont.truetype('arialbd.ttf', 24)
        font_dur = ImageFont.truetype('arialbd.ttf', 22)
        font_head = ImageFont.truetype('impact.ttf', 72)
        font_sub = ImageFont.truetype('arialbd.ttf', 44)
        font_pill = ImageFont.truetype('arialbd.ttf', 28)
    except Exception:
        font_badge = font_dur = font_head = font_sub = font_pill = ImageFont.load_default()

    # 1. Frequency Badge (Golden / Emerald / Purple glow)
    b_color = style["badge_color"]
    draw.rounded_rectangle([(60, 55), (210, 105)], radius=12, fill=b_color, outline=(255, 255, 255), width=2)
    draw.text((78, 65), style["freq"], font=font_badge, fill=(10, 10, 10))

    # 2. Duration Badge (e.g. '1 HOUR' / '2 HOURS')
    draw.rounded_rectangle([(225, 55), (370, 105)], radius=12, fill=(0, 0, 0, 180), outline=(255, 255, 255, 120), width=1)
    draw.text((245, 66), dur_label.upper(), font=font_dur, fill=(255, 255, 255))

    # 3. Bold High-Impact Headlines
    draw.text((60, 135), style["headline"], font=font_head, fill=(255, 255, 255))
    draw.text((60, 225), style["subline"], font=font_sub, fill=(225, 230, 245))

    # 4. Benefit Pill Tag
    draw.rounded_rectangle([(60, 300), (460, 355)], radius=12, fill=(0, 0, 0, 180), outline=b_color, width=2)
    draw.text((80, 310), style["pill_text"], font=font_pill, fill=style["pill_color"])

    # 5. White Stone Music logo watermark in top-right
    if LOGO_PATH.exists():
        try:
            logo = Image.open(LOGO_PATH).convert('RGBA').resize((280, 60), Image.Resampling.LANCZOS)
            img.paste(logo, (1280 - 280 - 40, 40), logo)
        except Exception:
            pass

    img.save(output_path, "JPEG", quality=95)
    return output_path
