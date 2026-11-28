"""会議のまとめ動画（11/28 加藤さん「パッと見て分かる動画に」）。
台本は content/meeting/YYYY-MM-DD.json（軽いデータだけ）。画像は作らず、文字・数字・棒グラフをその場で描く。
使い方: python studio/make_meeting_video.py content/meeting/2026-11-29.json（場面に "talk" があれば2人の会話の形）  → studio/out/meeting_日付.mp4
JSON: {"date":"11/29","scenes":[{"title":"..","lines":["..",".."],"bars":[["アカウント2",12],["アカウント1",3]],"say":"読み上げ"}]}
"""
import json, os, subprocess, sys, tempfile
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tools.audio import add_voice_and_bgm
from make_1101 import BLACK, BOLD
W, H, SEC = 1080, 1920, 7.0
TEAL, YEL, NAVY = (24, 160, 178), (255, 236, 30), (20, 42, 92)

def slide(sc, i, n, head="会議のまとめ"):
    im = Image.new("RGB", (W, H), NAVY); d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W, 260], fill=TEAL); d.text((60, 90), f"{head} {i}/{n}", font=ImageFont.truetype(BOLD, 56), fill="white")
    d.text((60, 340), sc["title"], font=ImageFont.truetype(BLACK, 84), fill=YEL)
    y = 520
    for ln in sc.get("lines", [])[:5]:
        d.text((60, y), "・" + ln, font=ImageFont.truetype(BOLD, 54), fill="white"); y += 110
    bars = sc.get("bars") or []
    top = max([v for _, v in bars] or [1]) or 1
    for k, (lab, v) in enumerate(bars[:4]):
        by = 1200 + k * 150
        d.text((60, by), lab, font=ImageFont.truetype(BOLD, 44), fill="white")
        d.rectangle([420, by, 420 + int(480 * v / top), by + 70], fill=YEL); d.text((430 + int(480 * v / top), by), str(v), font=ImageFont.truetype(BOLD, 44), fill="white")
    return im

def main(path):
    m = json.load(open(path, encoding="utf-8")); sc = m["scenes"]; os.makedirs("studio/out", exist_ok=True)
    out = f"studio/out/meeting_{m['date'].replace('/', '')}.mp4"
    with tempfile.TemporaryDirectory() as t:
        lst = open(f"{t}/l.txt", "w")
        for i, s in enumerate(sc):
            slide(s, i + 1, len(sc), m.get("head", "会議のまとめ")).save(f"{t}/{i:02d}.png")
            lst.write(f"file '{t}/{i:02d}.png'\nduration {s.get('sec', SEC)}\n")
        lst.write(f"file '{t}/{len(sc)-1:02d}.png'\n"); lst.close()
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", f"{t}/l.txt", "-vf", "fps=15,format=yuv420p", "-c:v", "libx264", out], check=True)
    starts, t0 = [], 0.0
    for s in sc: starts.append(t0); t0 += s.get("sec", SEC)
    lines = [(starts[i] + 0.3, s["say"]) for i, s in enumerate(sc) if s.get("say")]
    print(add_voice_and_bgm(out, lines, mood="gentle", seed=len(sc)))



# ---------- 会話の形（11/28 加藤さん「人が話しているような自然な空気感」）----------
# 場面に "talk": [["ガイ助教","…"],["マカスポくん","…"]] を書くと、2人の声（高さを変える）で順番に話す。場面の長さは声に合わせて自動。
VOICE = {"ガイ助教": -1.5, "マカスポくん": 2.5}

def talk_slide(sc, i, n, head, shown):
    im = Image.new("RGB", (W, H), NAVY); d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W, 260], fill=TEAL); d.text((60, 90), f"{head} {i}/{n}", font=ImageFont.truetype(BOLD, 56), fill="white")
    d.text((60, 320), sc["title"], font=ImageFont.truetype(BLACK, 80), fill=YEL)
    y, f, fn = 500, ImageFont.truetype(BOLD, 46), ImageFont.truetype(BOLD, 34)
    for who, txt in shown[-4:]:
        left = who == "ガイ助教"; x0 = 60 if left else 240
        rows = [txt[k:k + 17] for k in range(0, len(txt), 17)]
        h = 70 + 62 * len(rows)
        d.rounded_rectangle([x0, y, x0 + 780, y + h], 28, fill="white" if left else YEL)
        d.text((x0 + 30, y + 14), who, font=fn, fill=TEAL if left else NAVY)
        for r, t in enumerate(rows): d.text((x0 + 30, y + 58 + 62 * r), t, font=f, fill=NAVY)
        y += h + 34
    mp = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mascot", "makaspo_cutout.png")
    if os.path.exists(mp):  # マカスポくん（加藤さんの画像そのまま・付け足しだけ）
        mk = Image.open(mp).convert("RGBA"); mk.thumbnail((440, 440)); im.paste(mk, (W - mk.width - 40, H - mk.height - 60), mk)
    return im

def make_talk(path):
    import numpy as np
    from tools.audio import narrate, bgm, _write, SR
    m = json.load(open(path, encoding="utf-8")); sc = m["scenes"]; head = m.get("head", "今日の振り返り")
    os.makedirs("studio/out", exist_ok=True); out = f"studio/out/talk_{m['date'].replace('/', '')}.mp4"
    clips, frames, t = [], [], 0.6
    for i, s in enumerate(sc):
        shown = []
        for who, txt in s["talk"]:
            a, ln = narrate([(0, txt)], speed=1.15, half_tone=VOICE.get(who, 0))
            shown = shown + [(who, txt)]
            frames.append((talk_slide(s, i + 1, len(sc), head, shown), ln + 0.45))
            clips.append((t, a)); t += ln + 0.45
        frames[-1] = (frames[-1][0], frames[-1][1] + 0.6); t += 0.6
    total = t + 0.6
    voice = np.zeros(int(total * SR) + SR, dtype=np.float32)
    for st, a in clips: i0 = int(st * SR); voice[i0:i0 + len(a)] += a
    mus = bgm(len(voice) / SR, mood="lofi", seed=len(sc))[:len(voice)] * 0.16
    env = np.convolve(np.abs(voice) > 0.02, np.ones(int(0.25 * SR)) / int(0.25 * SR), mode="same")
    mus *= 1 - 0.5 * np.clip(env * 4, 0, 1)
    mix = mus + voice; mix /= (np.abs(mix).max() or 1)
    with tempfile.TemporaryDirectory() as td:
        lst = open(f"{td}/l.txt", "w")
        for k, (im, du) in enumerate(frames):
            im.save(f"{td}/{k:03d}.png"); lst.write(f"file '{td}/{k:03d}.png'\nduration {du + (0.6 if k == 0 else 0):.2f}\n")
        lst.write(f"file '{td}/{len(frames)-1:03d}.png'\n"); lst.close()
        _write(f"{td}/a.wav", mix * 0.95)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", f"{td}/l.txt", "-i", f"{td}/a.wav",
                        "-vf", "fps=15,format=yuv420p", "-c:v", "libx264", "-c:a", "aac", "-b:a", "160k", "-shortest", out], check=True)
    print(out)

if __name__ == "__main__":
    p = sys.argv[1]
    make_talk(p) if "talk" in json.load(open(p, encoding="utf-8"))["scenes"][0] else main(p)
