"""会議のまとめ動画（11/28 加藤さん「パッと見て分かる動画に」）。
台本は content/meeting/YYYY-MM-DD.json（軽いデータだけ）。画像は作らず、文字・数字・棒グラフをその場で描く。
使い方: python studio/make_meeting_video.py content/meeting/2026-11-29.json  → studio/out/meeting_日付.mp4
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

if __name__ == "__main__":
    main(sys.argv[1])
