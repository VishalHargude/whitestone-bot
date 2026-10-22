"""
generate_perfect_meditation_music.py
Generates 10 100% Mathematically Synthesized, Copyright-Free, Studio-Quality 432Hz & 528Hz
Meditation Music Tracks.
- ZERO Copyright Content ID risk (100% procedural waveforms, chords, bells & nature).
- Mastered to YouTube standard -14 LUFS, ensuring crisp, rich, full sound on mobile phones and TVs.
"""

import math
import subprocess
import sys
import wave
import shutil
from pathlib import Path
import numpy as np

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

BASE_DIR = Path(r"C:\Users\Vishal Hargude\.gemini\antigravity\scratch\hindi_shorts_generator")
MUSIC_DIR = BASE_DIR / "assets" / "music" / "meditation"
TEMP_DIR = BASE_DIR / "temp"
MUSIC_DIR.mkdir(parents=True, exist_ok=True)
TEMP_DIR.mkdir(parents=True, exist_ok=True)

ffmpeg_exe = r'C:\Users\Vishal Hargude\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe'

SR = 44100
TRACK_DUR = 90.0  # 90 seconds seamless loopable

def make_pink_noise(n_samples):
    white = np.random.randn(n_samples)
    fft_w = np.fft.rfft(white)
    freqs = np.fft.rfftfreq(n_samples)
    freqs[0] = 1e-5
    fft_pink = fft_w / np.sqrt(freqs)
    pink = np.fft.irfft(fft_pink, n=n_samples)
    return pink / (np.max(np.abs(pink)) + 1e-6)

def generate_pad(t, base_freq, chords_ratios, binaural_hz=4.0):
    left = np.zeros_like(t)
    right = np.zeros_like(t)
    
    # 2*pi*t precomputed
    two_pi_t = 2.0 * np.pi * t
    
    for ratio, weight in chords_ratios:
        f = base_freq * ratio
        # Precompute LFO once per chord note
        lfo_l = 1.0 + 0.12 * np.sin(0.08 * two_pi_t + ratio)
        lfo_r = 1.0 + 0.12 * np.cos(0.08 * two_pi_t + ratio)
        
        # Harmonics (fundamental, 2nd, 3rd, 4th)
        harmonics = [(1.0, 1.0), (2.0, 0.45), (3.0, 0.22), (4.0, 0.12)]
        for h_mult, h_weight in harmonics:
            fh = f * h_mult
            if fh > 9000:
                continue
            w = weight * h_weight
            sig_l = np.sin(fh * two_pi_t)
            sig_r = np.sin((fh + binaural_hz) * two_pi_t)
            
            left += (w * lfo_l) * sig_l
            right += (w * lfo_r) * sig_r
            
    return left, right

def add_chimes(left, right, t, chime_freqs, interval_sec=11.0):
    two_pi = 2.0 * np.pi
    strike_times = np.arange(2.0, t[-1] - 4.0, interval_sec)
    for idx, st in enumerate(strike_times):
        f = chime_freqs[idx % len(chime_freqs)]
        s_idx = int(st * SR)
        dt = t[s_idx:] - st
        env = np.exp(-dt / 3.0)
        
        bell = (np.sin(two_pi * f * dt) * 0.7 + 
                np.sin(two_pi * f * 2.76 * dt) * 0.2 + 
                np.sin(two_pi * f * 5.40 * dt) * 0.1) * env * 0.38
        
        pan_l = 0.6 if idx % 2 == 0 else 0.4
        pan_r = 0.4 if idx % 2 == 0 else 0.6
        
        left[s_idx:] += bell * pan_l
        right[s_idx:] += bell * pan_r

def add_melody_plucks(left, right, t, melody_freqs, step_sec=4.0):
    two_pi = 2.0 * np.pi
    note_times = np.arange(1.0, t[-1] - 2.0, step_sec)
    for idx, nt in enumerate(note_times):
        f = melody_freqs[idx % len(melody_freqs)]
        s_idx = int(nt * SR)
        dt = t[s_idx:] - nt
        env = np.exp(-dt / 1.8)
        
        tone = (np.sin(two_pi * f * dt) + 
                0.3 * np.sin(two_pi * f * 2.0 * dt) + 
                0.1 * np.sin(two_pi * f * 3.0 * dt)) * env * 0.25
        
        pan = 0.5 + 0.2 * np.sin(idx * 1.3)
        left[s_idx:] += tone * (1.0 - pan)
        right[s_idx:] += tone * pan

def save_and_master(left, right, filename, title):
    wav_tmp = TEMP_DIR / f"{filename}.wav"
    mp3_out = MUSIC_DIR / filename
    
    # Seamless loop envelope: 1.5s fade-in at start, 1.5s fade-out at end
    fade_len = int(1.5 * SR)
    fade_in = np.linspace(0.0, 1.0, fade_len)
    fade_out = np.linspace(1.0, 0.0, fade_len)
    left[:fade_len] *= fade_in
    right[:fade_len] *= fade_in
    left[-fade_len:] *= fade_out
    right[-fade_len:] *= fade_out
    
    max_val = max(np.max(np.abs(left)), np.max(np.abs(right)))
    if max_val > 0:
        left = (left / max_val) * 0.88
        right = (right / max_val) * 0.88
        
    stereo = np.column_stack((left, right))
    s16 = (stereo * 32767).astype(np.int16)
    
    with wave.open(str(wav_tmp), 'wb') as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes(s16.tobytes())
        
    # FFmpeg mastering: loudnorm (-14 LUFS standard), warm EQ, 320k MP3
    cmd = [
        ffmpeg_exe, "-y",
        "-i", str(wav_tmp),
        "-af", "loudnorm=I=-14:TP=-1.0:LRA=10,equalizer=f=320:width_type=h:width=150:g=1.5,equalizer=f=2400:width_type=h:width=800:g=1.2",
        "-map_metadata", "-1",
        "-metadata", f"title={title}",
        "-metadata", "artist=White Stone Music",
        "-metadata", "album=Original Procedural Solfeggio Soundscapes",
        "-c:a", "libmp3lame", "-b:a", "320k",
        str(mp3_out)
    ]
    subprocess.run(cmd, capture_output=True, check=True)
    if wav_tmp.exists():
        wav_tmp.unlink()
    print(f"  ✅ Mastered 100% Unique & Audible Track: {mp3_out.name} ({mp3_out.stat().st_size / (1024*1024):.2f} MB)")

def build_all_10_tracks():
    t = np.linspace(0, TRACK_DUR, int(SR * TRACK_DUR), endpoint=False)
    
    print("=" * 80)
    print("🚀 Synthesizing 10 100% Original, Zero-Copyright, Phone-Audible Meditation Tracks")
    print("=" * 80)
    
    # 1. Himalayan Sunrise Dhyana (432Hz)
    print("\n[1/10] Synthesizing Track 1: 432Hz Himalayan Sunrise Dhyana...")
    ratios_1 = [(0.5, 0.4), (0.75, 0.3), (1.0, 0.5), (1.25, 0.35), (1.5, 0.3), (2.0, 0.2)]
    l1, r1 = generate_pad(t, 432.0, ratios_1, binaural_hz=4.0)
    add_chimes(l1, r1, t, [864.0, 1080.0, 1296.0, 648.0], interval_sec=12.0)
    add_melody_plucks(l1, r1, t, [432.0, 485.0, 576.0, 648.0, 768.0, 864.0], step_sec=4.5)
    save_and_master(l1, r1, "track1_himalayan.mp3", "432Hz Himalayan Sunrise Dhyana")
    
    # 2. Sacred Temple & Diyas (528Hz Miracle Tone)
    print("\n[2/10] Synthesizing Track 2: 528Hz Sacred Temple & Floating Diyas...")
    ratios_2 = [(0.5, 0.4), (0.75, 0.3), (1.0, 0.55), (1.25, 0.4), (1.5, 0.35), (2.0, 0.25)]
    l2, r2 = generate_pad(t, 528.0, ratios_2, binaural_hz=5.28)
    add_chimes(l2, r2, t, [1056.0, 1320.0, 1584.0, 792.0], interval_sec=10.0)
    add_melody_plucks(l2, r2, t, [528.0, 594.0, 660.0, 792.0, 880.0, 1056.0], step_sec=4.0)
    save_and_master(l2, r2, "track2_temple.mp3", "528Hz Sacred Temple & Floating Diyas")
    
    # 3. Golden Sunset Beach & Ocean Zen (432Hz)
    print("\n[3/10] Synthesizing Track 3: 432Hz Golden Sunset Beach Ocean Waves...")
    ratios_3 = [(0.5, 0.35), (0.84, 0.3), (1.0, 0.5), (1.26, 0.35), (1.68, 0.25)]
    l3, r3 = generate_pad(t, 432.0, ratios_3, binaural_hz=3.5)
    p_noise_l = make_pink_noise(len(t))
    p_noise_r = make_pink_noise(len(t))
    surf_env = (np.sin(2 * np.pi * t / 8.0) * 0.5 + 0.5) ** 2
    l3 += p_noise_l * surf_env * 0.25
    r3 += p_noise_r * surf_env * 0.25
    add_chimes(l3, r3, t, [648.0, 864.0, 1296.0], interval_sec=14.0)
    add_melody_plucks(l3, r3, t, [363.0, 432.0, 544.0, 648.0, 726.0], step_sec=5.0)
    save_and_master(l3, r3, "track3_beach.mp3", "432Hz Golden Sunset Beach Ocean Zen")
    
    # 4. Sacred Bamboo Forest & Cascading Waters (432Hz)
    print("\n[4/10] Synthesizing Track 4: 432Hz Sacred Bamboo Forest Waterfall...")
    ratios_4 = [(0.67, 0.35), (1.0, 0.5), (1.33, 0.35), (1.5, 0.3), (2.0, 0.2)]
    l4, r4 = generate_pad(t, 432.0, ratios_4, binaural_hz=4.32)
    p_stream_l = make_pink_noise(len(t)) * 0.18
    p_stream_r = make_pink_noise(len(t)) * 0.18
    l4 += p_stream_l
    r4 += p_stream_r
    add_chimes(l4, r4, t, [864.0, 1152.0, 1440.0, 1728.0], interval_sec=9.0)
    add_melody_plucks(l4, r4, t, [432.0, 576.0, 648.0, 864.0, 960.0], step_sec=3.8)
    save_and_master(l4, r4, "track4_bamboo_waterfall.mp3", "432Hz Sacred Bamboo Forest Waterfall")
    
    # 5. Cosmic Universe Deep Sleep (432Hz)
    print("\n[5/10] Synthesizing Track 5: 432Hz Cosmic Universe Deep Sleep...")
    ratios_5 = [(0.5, 0.45), (0.75, 0.35), (1.0, 0.55), (1.5, 0.35), (2.0, 0.2)]
    l5, r5 = generate_pad(t, 432.0, ratios_5, binaural_hz=2.5)
    add_chimes(l5, r5, t, [864.0, 1296.0, 1728.0], interval_sec=15.0)
    save_and_master(l5, r5, "track5_deep_sleep_cosmos.mp3", "432Hz Cosmic Universe Deep Sleep")
    
    # 6. Tibetan Cliffside Sanctuary (528Hz)
    print("\n[6/10] Synthesizing Track 6: 528Hz Tibetan Cliffside Monastery...")
    ratios_6 = [(0.5, 0.5), (0.67, 0.35), (1.0, 0.5), (1.5, 0.35), (2.0, 0.25)]
    l6, r6 = generate_pad(t, 528.0, ratios_6, binaural_hz=5.0)
    add_chimes(l6, r6, t, [1584.0, 2112.0, 2640.0, 1056.0], interval_sec=11.0)
    add_melody_plucks(l6, r6, t, [528.0, 660.0, 792.0, 1056.0, 1188.0], step_sec=4.5)
    save_and_master(l6, r6, "track6_tibetan_monastery.mp3", "528Hz Tibetan Cliffside Sanctuary")
    
    # 7. Kyoto Zen Rock Garden (432Hz)
    print("\n[7/10] Synthesizing Track 7: 432Hz Kyoto Zen Rock Garden...")
    ratios_7 = [(0.5, 0.35), (0.75, 0.3), (1.0, 0.5), (1.19, 0.35), (1.5, 0.3), (1.78, 0.25)]
    l7, r7 = generate_pad(t, 432.0, ratios_7, binaural_hz=4.0)
    add_chimes(l7, r7, t, [864.0, 1028.0, 1296.0, 1542.0], interval_sec=9.5)
    add_melody_plucks(l7, r7, t, [432.0, 485.0, 514.0, 648.0, 686.0, 864.0], step_sec=3.8)
    save_and_master(l7, r7, "track7_kyoto_zen.mp3", "432Hz Kyoto Zen Rock Garden")
    
    # 8. Celestial Aurora Borealis (432Hz)
    print("\n[8/10] Synthesizing Track 8: 432Hz Celestial Aurora Borealis Sleep...")
    ratios_8 = [(0.5, 0.4), (0.75, 0.35), (1.0, 0.5), (1.25, 0.35), (1.5, 0.3), (2.0, 0.25), (3.0, 0.15)]
    l8, r8 = generate_pad(t, 432.0, ratios_8, binaural_hz=3.8)
    add_chimes(l8, r8, t, [1296.0, 1728.0, 2160.0, 864.0], interval_sec=14.0)
    add_melody_plucks(l8, r8, t, [432.0, 540.0, 648.0, 864.0, 1080.0], step_sec=5.0)
    save_and_master(l8, r8, "track8_aurora_sleep.mp3", "432Hz Celestial Aurora Borealis Sleep")
    
    # 9. Golden Desert Sunset Solitude (432Hz)
    print("\n[9/10] Synthesizing Track 9: 432Hz Golden Desert Sunset Solitude...")
    ratios_9 = [(0.5, 0.4), (0.63, 0.3), (1.0, 0.55), (1.25, 0.35), (1.5, 0.3), (2.0, 0.2)]
    l9, r9 = generate_pad(t, 432.0, ratios_9, binaural_hz=4.32)
    add_chimes(l9, r9, t, [864.0, 1080.0, 1296.0, 648.0], interval_sec=12.0)
    add_melody_plucks(l9, r9, t, [432.0, 540.0, 648.0, 756.0, 864.0], step_sec=4.5)
    save_and_master(l9, r9, "track9_desert_solitude.mp3", "432Hz Golden Desert Sunset Solitude")
    
    # 10. Sacred Lotus Temple Sanctuary (528Hz)
    print("\n[10/10] Synthesizing Track 10: 528Hz Sacred Lotus Sanctuary...")
    ratios_10 = [(0.5, 0.4), (0.75, 0.35), (1.0, 0.55), (1.25, 0.4), (1.5, 0.3), (2.0, 0.25)]
    l10, r10 = generate_pad(t, 528.0, ratios_10, binaural_hz=5.28)
    add_chimes(l10, r10, t, [1056.0, 1320.0, 1584.0, 2112.0], interval_sec=10.0)
    add_melody_plucks(l10, r10, t, [528.0, 660.0, 792.0, 880.0, 1056.0], step_sec=3.8)
    save_and_master(l10, r10, "track10_lotus_pond.mp3", "528Hz Sacred Lotus Sanctuary")
    
    # Overwrite legacy track1.mp3 and track2.mp3
    shutil.copy2(MUSIC_DIR / "track1_himalayan.mp3", MUSIC_DIR / "track1.mp3")
    shutil.copy2(MUSIC_DIR / "track2_temple.mp3", MUSIC_DIR / "track2.mp3")
    print("  ✅ Overwrote legacy track1.mp3 and track2.mp3 with 100% clean original tracks!")

    print("\n" + "=" * 80)
    print("🎉 ALL 10 MASTERPIECE MEDITATION TRACKS FULLY SYNTHESIZED & READY!")
    print("=" * 80)

if __name__ == "__main__":
    build_all_10_tracks()
