"""
topics.py - High-retention, naturally pronounced Hindi scripts with bilingual captions (Hindi + English Translation).
Written specifically to avoid robotic TTS cadence, tongue twisters, and awkward number readings.
"""

import random

# Curated viral topics with natural conversational phrasing and bilingual translation segments
CURATED_TOPICS = [
    {
        "id": "space_diamond_star",
        "stock_video": "space_galaxy.mp4",
        "title": "अंतरिक्ष में मिला हीरे का तारा! 💎 #shorts #spacefacts #hindi",
        "description": "जानिए अंतरिक्ष के उस तारे के बारे में जो पूरे हीरे से बना हुआ है! #shorts #facts #universe #hindi",
        "tags": ["shorts", "space facts", "diamond star", "lucy star", "hindi facts", "science", "viral"],
        "segments": [
            {"hi": "क्या आप जानते हैं?", "en": "Did you know this?"},
            {"hi": "अंतरिक्ष में एक ऐसा अनोखा तारा है,", "en": "There is a unique star in space,"},
            {"hi": "जो पूरी तरह चमचमाते हीरे से बना है!", "en": "Which is made entirely of diamond!"},
            {"hi": "वैज्ञानिकों ने इस तारे का नाम रखा है, लूसी!", "en": "Scientists named this star, Lucy!"},
            {"hi": "यह हमारी पृथ्वी से पचास प्रकाश वर्ष दूर है।", "en": "It is fifty light years away from Earth."},
            {"hi": "अगर इसका छोटा सा टुकड़ा भी धरती पर आ जाए,", "en": "If a tiny piece ever reached Earth,"},
            {"hi": "तो पूरी दुनिया का हर इंसान अरबपति बन जाएगा!", "en": "Every human would become a billionaire!"},
            {"hi": "अंतरिक्ष के ऐसे ही रहस्यों के लिए सब्सक्राइब करें!", "en": "Subscribe for more amazing space facts!"}
        ]
    },
    {
        "id": "ocean_immortal_jellyfish",
        "stock_video": "ocean_jellyfish.mp4",
        "title": "यह जीव कभी नहीं मरता! 🌊 #shorts #amazingfacts",
        "description": "जानिए उस जेलीफ़िश के बारे में जो जैविक रूप से अमर है! #shorts #ocean #facts #hindi",
        "tags": ["shorts", "immortal jellyfish", "ocean mystery", "nature facts", "hindi shorts"],
        "segments": [
            {"hi": "क्या आप यकीन करेंगे,", "en": "Would you believe,"},
            {"hi": "कि धरती पर एक ऐसा जीव है जो कभी नहीं मरता?", "en": "A creature on Earth never dies?"},
            {"hi": "जी हां, इसे 'अमर जेलीफ़िश' कहा जाता है!", "en": "Yes, it is called the Immortal Jellyfish!"},
            {"hi": "जब यह जेलीफ़िश बूढ़ी या बीमार होती है,", "en": "When this jellyfish gets old or sick,"},
            {"hi": "तो यह अपनी उम्र को पीछे ले जाती है!", "en": "It reverses its aging process!"},
            {"hi": "और एक बच्चे की तरह दोबारा जवान हो जाती है!", "en": "And becomes young all over again!"},
            {"hi": "यानी यह चक्र हमेशा चलता रहता है!", "en": "This life cycle continues forever!"},
            {"hi": "प्रकृति के इस अनोखे जादू के लिए एक लाइक तो बनता है!", "en": "Hit like for this miracle of nature!"}
        ]
    },
    {
        "id": "brain_superpower",
        "stock_video": "space_galaxy.mp4",
        "title": "इंसानी दिमाग की हैरान कर देने वाली शक्ति! 🧠 #shorts #mindfacts",
        "description": "जानिए आपका दिमाग कैसे एक बल्ब जला सकता है! #shorts #psychology #hindi",
        "tags": ["shorts", "human brain", "mind facts hindi", "superpower", "science facts"],
        "segments": [
            {"hi": "क्या आप जानते हैं,", "en": "Did you know that,"},
            {"hi": "कि आपका दिमाग जागते समय इतनी बिजली बनाता है,", "en": "Your awake brain produces so much electricity,"},
            {"hi": "जिससे एक छोटा बल्ब आसानी से जल सकता है!", "en": "That a small bulb can easily light up!"},
            {"hi": "हमारे दिमाग में करीब छियासी अरब न्यूरॉन्स होते हैं,", "en": "There are eighty-six billion neurons in our brain,"},
            {"hi": "जो कंप्यूटर से भी तेज सिग्नल भेजते हैं!", "en": "Sending signals faster than a computer!"},
            {"hi": "दिमाग का वजन कुल शरीर का सिर्फ दो प्रतिशत है,", "en": "The brain is only two percent of body weight,"},
            {"hi": "लेकिन यह बीस प्रतिशत ऊर्जा अकेले इस्तेमाल करता है!", "en": "Yet it uses twenty percent of total energy!"},
            {"hi": "क्या आपको यह फैक्ट पता था? कमेंट में बताएं!", "en": "Did you know this? Tell us in comments!"}
        ]
    }
]

def get_curated_topic(topic_id: str = None):
    """Returns a curated topic by id or randomly."""
    if topic_id:
        for t in CURATED_TOPICS:
            if t["id"] == topic_id:
                return t
    return random.choice(CURATED_TOPICS)

def get_random_topic():
    """Returns a randomly selected curated viral topic."""
    return random.choice(CURATED_TOPICS)

def generate_ai_topic():
    """Fallback to curated topics."""
    return get_random_topic()
