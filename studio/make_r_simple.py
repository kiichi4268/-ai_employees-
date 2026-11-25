"""前日・開催後・保存型リールを r1125 の型（声を先に作り、文字を声の始まりに合わせる・-14LUFS）で作る共通の作り方。
使い方: cd studio && python3 make_r_simple.py r1127   （REELS に足して使う）"""
import os, sys, json, subprocess, shutil, tempfile, urllib.parse
import numpy as np
from tools import audio as A
D = os.path.dirname(os.path.abspath(__file__)); BASE = os.path.join(D, "r1125")
MEDIA = os.path.join(D, "..", "content", "instagram", "media"); POSTS = os.path.join(D, "..", "content", "instagram", "posts")
BGDIR = os.path.join(MEDIA, "bg")
REPL_KEYS = ["明日のお知らせ", "明日の木曜、", "仕事帰りに", "バドミントン。", "11/26(木) バド", "18:00-21:00", "まもりやまテラス", "京王井の頭線 新代田駅から徒歩約5分",
             "まだ参加枠あります", "参加費1,500円", "当日 現金・PayPay", "ほとんど1人参加", "初心者7割・経験者3割くらい", "ラケット貸出あり"]
REELS = {
 "r1127": dict(day="2026-11-27", time="19:00", bg="play_bad", music="pop_bright",
   text=["きのうの開催", "昨日は", "仕事帰りの", "バドでした。", "次は 11/28(土)", "13:00-15:00", "渋谷区本町コミュニティセンター", "京王新線 初台駅から徒歩約13分",
         "日曜もあります", "11/29(日) 18:00-21:00", "巣鴨体育館（巣鴨駅・大塚駅 徒歩約10分）", "ほとんど1人参加", "初心者7割・経験者3割くらい", "参加費1,500円（当日）"],
   lines=["昨日は、仕事帰りのバドミントンでした。", "次は、あさっての土曜。お昼1時から、渋谷区本町コミュニティセンター。初台駅から、徒歩やく13分です。",
          "日曜の夜も、あります。夕方6時から、巣鴨体育館です。", "ほとんどが1人参加。初心者7割、経験者3割くらい。参加費は、千五百円です。", "予約は、プロフィールのリンクから、公式ラインへ。"],
   cap=("昨日は仕事帰りのバドミントンでした🏸\n\n週末もバドミントンがあります\n・11/28(土) 13:00-15:00 渋谷区本町コミュニティセンター（京王新線 初台駅から徒歩約13分）\n"
        "・11/29(日) 18:00-21:00 巣鴨体育館（JR巣鴨駅・大塚駅から徒歩約10分）\n\nほとんどが1人参加で、初心者7割・経験者3割くらい。ラケット貸出あり。\n"
        "参加費1,500円（当日、現金またはPayPay）\n予約はプロフィールのリンクから公式LINEへ（LINEで @827lnqaq を検索でもOK）\nわからないことはDMでお気軽にどうぞ\n\n"
        "#社会人スポーツ #社会人サークル #バドミントン #バドミントンサークル #1人参加 #初心者歓迎 #東京スポーツ #マカシェットスポーツ"),
   note="開催後リール（11/26 バド・平日は翌日19:00＝11/25 加藤さん）＋週末の予告。studio/make_r_simple.py r1127。声→文字の型（K1・K5）。曲:pop_bright。今週のリール2本目"),
 "r1129": dict(day="2026-11-29", time="12:00", bg="b14_wide", music="acoustic_morning",
   text=["保存して当日見返してね", "初参加の", "持ち物は", "これだけ。", "持ち物 3つ", "着替え", "体育館シューズ", "飲み物",
         "お金は参加費だけ", "参加費1,500円", "当日 現金・PayPay", "ラケット貸出あり", "ほとんど1人参加", "今夜18時 巣鴨でバド"],
   lines=["初参加の持ち物は、これだけ。", "着替え、体育館シューズ、飲み物。この3つです。", "お金は、参加費の千五百円だけ。当日、現金かペイペイです。",
          "バドミントンと卓球は、ラケットの貸し出しがあります。ほとんどが1人参加です。今夜は6時から、巣鴨でバドミントン。", "予約は、プロフィールのリンクから、公式ラインへ。"],
   cap=("保存しておくと、当日の朝に見返せます📌\n\n初参加の持ち物はこれだけ\n・着替え\n・体育館シューズ\n・飲み物\n（バドミントン・卓球はラケット貸出あり）\n\n"
        "お金は参加費1,500円だけ（当日、現金またはPayPay）\n\n今夜 11/29(日) 18:00-21:00 バドミントン｜巣鴨体育館（JR巣鴨駅・大塚駅から徒歩約10分）\n"
        "予約はプロフィールのリンクから公式LINEへ（LINEで @827lnqaq を検索でもOK）\n\n#社会人スポーツ #持ち物 #初参加 #バドミントン #1人参加 #初心者歓迎 #東京スポーツ #マカシェットスポーツ"),
   note="案A：11/26 の持ち物カルーセルをリールに作り直し（見出しと冒頭2秒を変えた）。studio/make_r_simple.py r1129。曲:acoustic_morning。今週のリール3本目"),
}


def build(key):
    c = REELS[key]; R = os.path.join(D, key); OUT = os.path.join(D, "out", key); os.makedirs(R, exist_ok=True); os.makedirs(OUT, exist_ok=True)
    html = open(os.path.join(BASE, "anim.html"), encoding="utf-8").read()
    for a, b in zip(REPL_KEYS, c["text"]): html = html.replace(">" + a + "<", ">" + b + "<", 1)
    open(os.path.join(R, "anim.html"), "w", encoding="utf-8").write(html); shutil.copy(os.path.join(BASE, "render.js"), R)
    shutil.copy(os.path.join(BGDIR, c["bg"] + ".jpg"), os.path.join(R, "bg.jpg"))
    import pyopenjtalk
    SR = A.SR; t = 0.3; starts = []; clips = []
    for s in c["lines"]:
        x, sr = pyopenjtalk.tts(s, speed=1.25); x = x.astype(np.float32) / 32768.0
        if sr != SR: x = np.interp(np.linspace(0, len(x), int(len(x) * SR / sr), endpoint=False), np.arange(len(x)), x)
        starts.append(round(t, 2)); clips.append((t, x)); t += len(x) / SR + 0.35
    total = t + 2.6; voice = np.zeros(int(total * SR), np.float32)
    for st, x in clips: i = int(st * SR); voice[i:i + len(x)] += x
    voice = voice / (np.abs(voice).max() or 1) * 0.9
    fr = os.path.join(OUT, "frames"); shutil.rmtree(fr, ignore_errors=True)
    subprocess.run(["node", os.path.join(R, "render.js"), "0", f"{total:.2f}", str(1 / 30), fr, urllib.parse.quote(json.dumps(starts))], check=True)
    silent = os.path.join(OUT, "silent.mp4")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", "30", "-i", os.path.join(fr, "%04d.jpg"), "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", silent], check=True)
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", "12", "-i", os.path.join(A.MUSIC_DIR, c["music"] + ".m4a"), "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True, check=True).stdout
    tr = np.frombuffer(raw, np.float32).copy(); n = len(voice); tr = np.tile(tr, n // max(len(tr), 1) + 1)[:n]; tr = tr / (np.abs(tr).max() or 1) * 0.30
    env = np.convolve(np.abs(voice) > 0.02, np.ones(int(0.25 * SR)) / int(0.25 * SR), mode="same"); tr *= (1 - 0.6 * np.clip(env * 4, 0, 1)).astype(np.float32)
    f = int(0.8 * SR); tr[:f] *= np.linspace(0, 1, f); tr[-f:] *= np.linspace(1, 0, f)
    name = f"{c['day']}_reel_01.mp4"; final = os.path.join(OUT, name)
    with tempfile.TemporaryDirectory() as d:
        wav = os.path.join(d, "a.wav"); A._write(wav, (voice + tr) / (np.abs(voice + tr).max() or 1) * 0.9)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", silent, "-i", wav, "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-af", "highpass=f=80,loudnorm=I=-14:TP=-1.5:LRA=11",
                        "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-shortest", "-movflags", "+faststart", final], check=True)
    shutil.copy(final, MEDIA)
    json.dump({"id": f"{c['day']}-reel-01", "type": "reel", "scheduled_at": f"{c['day']}T{c['time']}:00+09:00", "caption": c["cap"], "media": [name],
               "note": c["note"] + f"（文字は声の始まり {starts} 秒）"}, open(os.path.join(POSTS, f"{c['day']}-reel-01.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print("ok", key, final, starts)


if __name__ == "__main__":
    for k in sys.argv[1:] or REELS: build(k)
