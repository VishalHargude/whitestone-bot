# 🚀 Hindi AI YouTube Shorts Auto-Generator & Uploader

हे एक संपूर्ण ऑटोमेटेड टूल आहे जे दररोज ट्रेंडिंग/व्हायरल विषयांवर **हिंदी YouTube Shorts** आपोआप तयार करते आणि YouTube वर अपलोड करते.

---

## 📁 प्रोजेक्ट स्ट्रक्चर
```
hindi_shorts_generator/
├── config.py             # सर्व कॉन्फिगरेशन (आवाज, रिझोल्यूशन, API कीज)
├── topics.py             # व्हायरल हिंदी टॉपिक्स लायब्ररी + AI स्क्रिप्ट जनरेटर
├── tts.py                # Microsoft Edge TTS (Madhur / Swara Hindi Voice)
├── media.py              # Pexels API किंवा Built-in 9:16 Cinematic Video Generator
├── video_maker.py        # FFmpeg सबटायटल्स (Devanagari Hindi) आणि व्हिडिओ रेंडरर
├── uploader.py           # YouTube Data API v3 ऑटो-अपलोडर
├── scheduler.py          # दररोज ठरलेल्या वेळेला चालवणारा शेड्यूलर
├── generate_sample.py    # चाचणीसाठी लगेच १ व्हिडिओ बनवणारी स्क्रिप्ट
└── output/               # तयार झालेले सर्व Shorts MP4 आणि Metadata JSON
```

---

## ⚡ त्वरित चाचणी (Run Sample)
नवीन व्हिडिओ ताबडतोब बनवून पाहण्यासाठी:
```powershell
cd "C:\Users\Vishal Hargude\.gemini\antigravity\scratch\hindi_shorts_generator"
python generate_sample.py
```
हा व्हिडिओ `output/sample_hindi_short.mp4` येथे तयार होतो.

---

## ⏰ रोजच्या रोज आपोआप चालवण्यासाठी (Daily Automation)
दररोज संध्याकाळी ६:०० वाजता आपोआप नवीन व्हिडिओ तयार करून पब्लिश करण्यासाठी:
```powershell
python scheduler.py
```
किंवा त्वरित एकच वेळ चालवण्यासाठी:
```powershell
python scheduler.py --now
```

---

## 🔑 YouTube Auto-Upload कसे चालू करावे? (One-time Setup)
1. **Google Cloud Console** (console.cloud.google.com) वर जा.
2. एक नवीन प्रोजेक्ट बनवा आणि **YouTube Data API v3** सक्षम (Enable) करा.
3. **OAuth 2.0 Client ID (Desktop Application)** तयार करा.
4. तिथून डाऊनलोड केलेली JSON फाइल या फोल्डरमध्ये `client_secret.json` या नावाने ठेवा.
5. पहिल्यांदा चालवताना ब्राउझरमध्ये तुमच्या YouTube चॅनेलचे लॉगिन विचारले जाईल. एकदा लॉगिन झाले की `token.pickle` आपोआप सेव्ह होईल आणि नंतर आयुष्यभर काहीही न करता आपोआप व्हिडिओ अपलोड होत राहील!

---

## 🎨 पर्यायी मोफत सुधारणा (Optional API Keys)
`config.py` मध्ये खालील मोफत API Keys टाकू शकता:
- **PEXELS_API_KEY**: [Pexels API](https://www.pexels.com/api/) वरून मोफत की घेतल्यास खऱ्या HD व्हिडिओ क्लिप्स आपोआप डाउनलोड होतात.
- **GEMINI_API_KEY**: [Google AI Studio](https://aistudio.google.com/) वरून मोफत की टाकल्यास दररोज नवनवीन ताजा कंटेंट AI स्वतः लिहितो.
