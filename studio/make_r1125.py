"""11/25(水) 19:00 前日リール「明日の木曜、仕事帰りにバドミントン。」（K1・K5：声を先に作り、画面の文字を声の始まりに合わせる・音量をそろえる）
テーマ案：A 明日11/26 仕事帰りのバド（採用：平日夜は初・前日で決めやすい）／B 1人参加の不安3つ（11/19 で使った）／C 今週のバド3回まとめ（金曜に回す）
使い方: cd studio && python3 make_r1125.py"""
import os, json, subprocess, shutil, tempfile, urllib.parse
import numpy as np
from tools import audio as A

D = os.path.dirname(os.path.abspath(__file__)); R = os.path.join(D, "r1125"); OUT = os.path.join(D, "out", "r1125"); os.makedirs(OUT, exist_ok=True)
MEDIA = os.path.join(D, "..", "content", "instagram", "media"); POSTS = os.path.join(D, "..", "content", "instagram", "posts")
LINES = ["明日の木曜、仕事帰りにバドミントン。",
         "じゅういちがつ、にじゅうろくにち。夕方6時から、まもりやまテラス。新代田駅から、徒歩やく5分です。",
         "まだ参加枠あります。参加費は、千五百円。当日、現金か、ペイペイです。",
         "ほとんどが1人参加。初心者7割、経験者3割くらい。ラケットの貸し出しもあります。",
         "予約は、プロフィールのリンクから、公式ラインへ。"]
# 1) 声を先に作り、1文ずつの始まりの秒を決める（K1）
import pyopenjtalk
SR = A.SR; t = 0.3; starts = []; clips = []
for s in LINES:
    x, sr = pyopenjtalk.tts(s, speed=1.25); x = x.astype(np.float32) / 32768.0
    if sr != SR: x = np.interp(np.linspace(0, len(x), int(len(x) * SR / sr), endpoint=False), np.arange(len(x)), x)
    starts.append(round(t, 2)); clips.append((t, x)); t += len(x) / SR + 0.35
total = t + 2.6
voice = np.zeros(int(total * SR), np.float32)
for st, x in clips: i = int(st * SR); voice[i:i + len(x)] += x
voice = voice / (np.abs(voice).max() or 1) * 0.9
print("starts", starts, "total", round(total, 2))
# 2) 画面（声の秒に合わせて動く）
fr = os.path.join(OUT, "frames"); shutil.rmtree(fr, ignore_errors=True)
h = urllib.parse.quote(json.dumps(starts))
subprocess.run(["node", os.path.join(R, "render.js"), "0", f"{total:.2f}", str(1 / 30), fr, h], check=True)
silent = os.path.join(OUT, "silent.mp4")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", "30", "-i", os.path.join(fr, "%04d.jpg"), "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", silent], check=True)
# 3) 曲（vidIQ の著作権フリー）＋声。声の間は曲を下げ、最後に音量をそろえる（-14 LUFS）
raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", "12", "-i", os.path.join(A.MUSIC_DIR, "pop_bright.m4a"), "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True, check=True).stdout
tr = np.frombuffer(raw, np.float32).copy(); n = len(voice); tr = np.tile(tr, n // max(len(tr), 1) + 1)[:n]
tr = tr / (np.abs(tr).max() or 1) * 0.30
env = np.convolve(np.abs(voice) > 0.02, np.ones(int(0.25 * SR)) / int(0.25 * SR), mode="same")
tr *= (1 - 0.6 * np.clip(env * 4, 0, 1)).astype(np.float32)
f = int(0.8 * SR); tr[:f] *= np.linspace(0, 1, f); tr[-f:] *= np.linspace(1, 0, f)
mix = voice + tr
with tempfile.TemporaryDirectory() as d:
    wav = os.path.join(d, "a.wav"); A._write(wav, mix / (np.abs(mix).max() or 1) * 0.9)
    final = os.path.join(OUT, "2026-11-25_reel_01.mp4")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", silent, "-i", wav, "-map", "0:v", "-map", "1:a", "-c:v", "copy",
                    "-af", "highpass=f=80,loudnorm=I=-14:TP=-1.5:LRA=11", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-shortest", "-movflags", "+faststart", final], check=True)
shutil.copy(final, MEDIA)
cap = ("明日の木曜、仕事帰りにバドミントン🏸\n\n"
       "・ほとんどが1人参加\n・初心者7割・経験者3割くらい\n・ラケット貸出あり（持ち物は着替え・体育館シューズ・飲み物）\n\n"
       "11/26(木) 18:00-21:00\n📍まもりやまテラス（京王井の頭線 新代田駅から徒歩約5分）\n\n"
       "まだ参加枠あります。\n参加費1,500円（当日、現金またはPayPay）\n予約はプロフィールのリンクから公式LINEへ（LINEで @827lnqaq を検索でもOK）\nわからないことはDMでお気軽にどうぞ\n\n"
       "#社会人スポーツ #社会人サークル #バドミントン #バドミントンサークル #仕事帰り #1人参加 #初心者歓迎 #東京スポーツ #マカシェットスポーツ")
json.dump({"id": "2026-11-25-reel-01", "type": "reel", "scheduled_at": "2026-11-25T19:00:00+09:00", "caption": cap,
           "media": ["2026-11-25_reel_01.mp4"],
           "note": f"前日リール（11/26 バド・仕事帰り）。studio/make_r1125.py＋r1125。K1・K5：声を先に作り文字を声の始まり{starts}秒に合わせた・曲 pop_bright・loudnorm -14LUFS。背景 play_bad（顔処理済み）。今週のリール1本目"},
          open(os.path.join(POSTS, "2026-11-25-reel-01.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("ok", final)
