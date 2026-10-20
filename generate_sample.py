"""
generate_sample.py - Immediate tester for Emotional, Lovable, Tear-Jerking Cartoon Shorts.
"""

import argparse
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

from emotional_engine import generate_daily_emotional_short
from cute_cartoon_maker import create_cute_cartoon_short

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test Emotional Cartoon Generator")
    parser.add_argument(
        "--type",
        choices=["father", "mother", "old_father", "friends", "cute_pari"],
        default="old_father",
        help="Story type: old_father (बूढ़े बाप का सहारा), father (पिता का त्याग), mother (मां का प्यार), friends (सच्चा दोस्त), cute_pari (पापा की परी)"
    )
    args = parser.parse_args()

    print("=" * 60)
    print(f"🎬 Generating Emotional Short: {args.type.upper()}...")
    print("=" * 60)

    if args.type == "cute_pari":
        create_cute_cartoon_short()
    else:
        mapping = {
            "father": "father_sacrifice",
            "mother": "mother_unconditional_love",
            "old_father": "elderly_father_pride",
            "friends": "true_friendship"
        }
        story_id = mapping.get(args.type, "elderly_father_pride")
        res = generate_daily_emotional_short(story_id=story_id)

    print("=" * 60)
