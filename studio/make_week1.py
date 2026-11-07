"""1週目（11/2〜11/8）ストーリー63本：各枠 ①画像 ②動画 ③仕掛け"""
import os, subprocess, csv, sys
from PIL import Image, ImageDraw, ImageFilter, ImageOps
from make_1101 import (W, H, FPS, BLACK, BOLD, TEAL, YEL, NAVY, WHITE, F, text_img, cal_icon, pin_icon,
                       pill, shadowed, place, brush, headline, yellow_band, white_band, appear, A, B, D)

OUT = os.path.join(D, "out", "week1"); os.makedirs(OUT, exist_ok=True)
ORANGE, GREEN, RED = (243, 128, 32), (46, 150, 70), (226, 60, 60)
LINE_GREEN = (6, 199, 85)

def fit(im, maxw=W - 90):
    if im.width <= maxw: return im
    r = maxw / im.width; return im.resize((int(im.width * r), int(im.height * r)), Image.LANCZOS)

# ---------- backgrounds (faces always unrecognizable) ----------
def load(p): return ImageOps.exif_transpose(Image.open(p)).convert("RGB")
def cover(im, w=W, h=H, scale=1.0):
    r = max(w * scale / im.width, h * scale / im.height)
    im = im.resize((int(im.width * r) + 1, int(im.height * r) + 1), Image.LANCZOS)
    return im

def mosaic(img, boxes, pad=0.35):
    img = img.copy()
    for (x, y, w, h) in boxes:
        x0, y0 = max(0, int(x - w * pad)), max(0, int(y - h * pad)); x1, y1 = min(img.width, int(x + w * (1 + pad))), min(img.height, int(y + h * (1 + pad)))
        reg = img.crop((x0, y0, x1, y1)); n = max(2, (x1 - x0) // 8)
        reg = reg.resize((max(1, (x1 - x0) // n), max(1, (y1 - y0) // n)), Image.BILINEAR).resize((x1 - x0, y1 - y0), Image.NEAREST)
        img.paste(reg, (x0, y0))
    return img

TT = mosaic(load(os.path.join(D, "mat", "Gemini_Generated_Image_159bg159bg159bg1.jpeg")).crop((54, 420, 458, 866)),
            [(97, 102, 52, 62), (211, 78, 28, 30), (287, 108, 40, 40)])
SRC = {
    "gym": load(os.path.join(D, "photos", "IMG_3560.jpg")),
    "bad": load(os.path.join(D, "photos", "IMG_3754.jpg")),
    "gym2": load(os.path.join(D, "photos", "IMG_3750.jpg")),
    "base": mosaic(load(os.path.join(D, "clips", "IMG_4049.JPG")), [(440, 356, 64, 64), (1130, 276, 110, 130), (590, 432, 34, 34)]),
    "tt": TT,
    "cal": load(os.path.join(D, "cal", "cal11_fixed.png")),
}
# 人が写っていない部分だけを切り出した、くっきり使える背景（11/8 目視で確認。ぼかしは弱めでよい：still_bg(key, blur=2)）
_B4 = load(os.path.join(D, "photos", "IMG_3754.jpg")); _B0 = load(os.path.join(D, "photos", "IMG_3750.jpg"))
SRC.update({
    "court": _B4.crop((0, 2760, _B4.width, _B4.height)),      # コートのライン（床）
    "ceiling": _B4.crop((0, 0, _B4.width, 1270)),             # 体育館の天井と照明
    "floor": _B0.crop((0, 2220, 2950, _B0.height)),           # 木の床の光の反射
})
CLEAR_BG = {"court", "ceiling", "floor"}  # 人が写らない背景（ぼかし2でよい）
def still_bg(key, blur=None, dark=0.42):
    if blur is None: blur = 2 if key in CLEAR_BG else 14  # 人が写る写真は強くぼかす（顔を隠す決まり）
    if key == "navy":
        im = Image.new("RGB", (W, H)); d = ImageDraw.Draw(im)
        for y in range(H): d.line([(0, y), (W, y)], fill=(11 + int(10 * y / H), 23 + int(16 * y / H), 51 + int(34 * y / H)))
        return im.convert("RGBA")
    im = cover(SRC[key]); x0 = (im.width - W) // 2; y0 = (im.height - H) // 2
    im = im.crop((x0, y0, x0 + W, y0 + H)).filter(ImageFilter.GaussianBlur(blur))
    return Image.blend(im, Image.new("RGB", (W, H), (10, 22, 52)), dark).convert("RGBA")

# ---------- parts ----------
def hl(a, b="", size=130, seed=3): return fit(shadowed(headline(a, b, seed=seed, size=size)))
def card_lines(lines, w=920, title=None, color=TEAL):
    fs = 64; rows = [text_img(l, F(BLACK, fs), NAVY) for l in lines]
    rows = [fit(r, w - 80) for r in rows]
    th = 0 if not title else 96
    h = th + sum(r.height + 18 for r in rows) + 50
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w - 1, h - 1), 34, fill=(255, 255, 255, 245))
    if title:
        d.rounded_rectangle((0, 0, w - 1, th), 34, fill=color); d.rectangle((0, th - 34, w - 1, th), fill=color)
        im.alpha_composite(fit(text_img(title, F(BLACK, 56), WHITE), w - 60), (34, 10))
    y = th + 26
    for r in rows: im.alpha_composite(r, (40, y)); y += r.height + 18
    return shadowed(im)

def event_card(label, color, date, time, venue, access=None):
    lines = [f"{date}  {time}", venue] + ([access] if access else [])
    w = 920; im = Image.new("RGBA", (w, 120 + 82 * len(lines)), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w - 1, im.height - 1), 34, fill=(255, 255, 255, 245))
    d.rounded_rectangle((0, 0, w - 1, 100), 34, fill=color); d.rectangle((0, 66, w - 1, 100), fill=color)
    im.alpha_composite(text_img(label, F(BLACK, 60), WHITE), (34, 8))
    im.alpha_composite(cal_icon(54, NAVY), (36, 124)); im.alpha_composite(fit(text_img(lines[0], F(BLACK, 54), NAVY), w - 140), (104, 114))
    im.alpha_composite(pin_icon(52, NAVY), (37, 206)); im.alpha_composite(fit(text_img(lines[1], F(BLACK, 54), NAVY), w - 140), (104, 196))
    if access: im.alpha_composite(fit(text_img(access, F(BOLD, 38), (70, 90, 120)), w - 140), (104, 284))
    return shadowed(im)

HANDLE = shadowed(pill([text_img("@macachette_sports", F(BOLD, 40), WHITE)], h=84, bg=NAVY))
def foot(c): place(c, HANDLE, W / 2, 1640)

# ---------- ① image ----------
def make_image(spec, path):
    c = still_bg(spec.get("bg", "gym"))
    place(c, hl(spec["h1"], spec.get("h2", ""), seed=spec.get("seed", 3)), W / 2, 270)
    tot = sum(b.height + 10 for b in spec["blocks"])
    y = max(560, 560 + (1040 - tot) / 2)
    for blk in spec["blocks"]:
        place(c, blk, W / 2, y); y += blk.height + 10
    foot(c); c.convert("RGB").save(path, quality=93)

# ---------- ② video ----------
def clip_frames(path, start, dur, blur=4.6):
    w, h = 360, 640
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(start), "-i", path, "-t", str(dur), "-vf",
                          f"fps={FPS},scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h}",
                          "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
    n = len(raw) // (w * h * 3)
    return [Image.frombuffer("RGB", (w, h), raw[i * w * h * 3:(i + 1) * w * h * 3]).copy().filter(ImageFilter.GaussianBlur(blur)) for i in range(n)]

def kb_frames(key, dur, blur=6, focus=(0.5, 0.5)):
    im = cover(SRC[key], scale=1.12).filter(ImageFilter.GaussianBlur(blur)); out = []
    n = int(dur * FPS)
    for k in range(n):
        z = 1 + 0.07 * k / n; cw, ch = W * 1.0 / z * im.width / (W * 1.12) * 1.0, 0
        cw = min(im.width, im.width / 1.12 / z); ch = min(im.height, im.height / 1.12 / z)
        x0 = min(max(focus[0] * im.width - cw / 2, 0), im.width - cw); y0 = min(max(focus[1] * im.height - ch / 2, 0), im.height - ch)
        out.append(im.crop((int(x0), int(y0), int(x0 + cw), int(y0 + ch))).resize((360, 640), Image.BILINEAR))
    return out

def ref_frames(start, dur):
    """ユーザー制作の45秒LINE解説動画（人の顔なし）からスマホ画面だけ切り出す"""
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "inputs", "d2c9044b-Macachette_LINE___45s_SE__.mp4")
    w, h = 360, 640
    vf = (f"fps={FPS},crop=iw*0.70:ih*0.78:iw*0.15:ih*0.21,scale=-2:340,"
          f"pad={w}:{h}:(ow-iw)/2:205:color=0x0e1c3c")
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(start), "-i", p, "-t", str(dur), "-vf", vf,
                          "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
    n = len(raw) // (w * h * 3)
    return [Image.frombuffer("RGB", (w, h), raw[i * w * h * 3:(i + 1) * w * h * 3]).copy() for i in range(n)]

DUR = 8.0
def make_video(spec, path):
    src = spec["src"]
    if src == "clipA": fr = clip_frames(A, spec.get("ss", 12), DUR)
    elif src == "clipB": fr = clip_frames(B, spec.get("ss", 20), DUR)
    elif src == "ref": fr = ref_frames(spec.get("ss", 8), DUR)
    else: fr = kb_frames(src, DUR, blur=spec.get("blur", 6), focus=spec.get("focus", (0.5, 0.5)))
    parts = [hl(spec["h1"], spec.get("h2", ""), seed=spec.get("seed", 4), size=120)]
    parts += [fit(shadowed(pill([text_img(t, F(BLACK, 60), NAVY)], h=112))) for t in spec["lines"]]
    starts = [0.1] + [0.9 + 1.2 * i for i in range(len(spec["lines"]))]
    ys = [280] + [760 + 150 * i for i in range(len(spec["lines"]))]
    if src == "ref": ys = [250] + [445 + 130 * i for i in range(len(spec["lines"]))]
    elif spec.get("lower"): ys = [280] + [1080 + 150 * i for i in range(len(spec["lines"]))]
    g = Image.new("RGBA", (W, H), (0, 0, 0, 0)); gd = ImageDraw.Draw(g)
    for yy in range(H): gd.line([(0, yy), (W, yy)], fill=(10, 22, 52, int(70 + 60 * abs(yy - H / 2) / (H / 2))))
    proc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                             "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "24", "-pix_fmt", "yuv420p",
                             "-movflags", "+faststart", path], stdin=subprocess.PIPE)
    for k in range(int(DUR * FPS)):
        t = k / FPS; c = fr[min(k, len(fr) - 1)].resize((W, H), Image.BICUBIC).convert("RGBA")
        c = Image.alpha_composite(c, g)
        for p, s, y in zip(parts, starts, ys): place(c, p, W / 2, y, appear(t, s))
        foot(c); proc.stdin.write(c.convert("RGB").tobytes())
    proc.stdin.close(); proc.wait()

# ---------- ③ interactive ----------
KIND_HINT = {"poll": "↓ タップして投票してね", "quiz": "↓ 答えをタップしてね", "question": "↓ ここに書いて送ってね", "link": "↓ タップして公式LINEへ",
             "line": "プロフィールのリンクから公式LINEへ"}  # line＝スタンプなし（朝・昼の自動投稿用）
def make_ix(spec, path):
    c = still_bg(spec.get("bg", "gym2"), blur=18, dark=0.55)
    place(c, hl(spec["h1"], spec.get("h2", ""), seed=spec.get("seed", 5), size=120), W / 2, 270)
    if spec.get("sub"): place(c, fit(shadowed(pill([text_img(spec["sub"], F(BLACK, 46), NAVY)], h=90))), W / 2, 560)
    hint = text_img(KIND_HINT[spec["kind"]], F(BLACK, 50), YEL, stroke=4, stroke_fill=NAVY)
    place(c, hint, W / 2, 680)
    if spec["kind"] != "line":  # スタンプを置く場所（夜の手動投稿用）
        zone = Image.new("RGBA", (760, 420), (0, 0, 0, 0)); ImageDraw.Draw(zone).rounded_rectangle((0, 0, 759, 419), 40, fill=(255, 255, 255, 38))
        place(c, zone, W / 2, 790)
    if spec["kind"] in ("link", "line"):
        place(c, fit(shadowed(pill([text_img("初参加ガイドもLINEで受け取れます", F(BLACK, 44), WHITE)], h=92, bg=LINE_GREEN))), W / 2, 1230 if spec["kind"] == "link" else 900)
    foot(c); c.convert("RGB").save(path, quality=93)

# ---------- data ----------
BAD_CARD = lambda d: event_card("バドミントン", GREEN, d, "15:00-17:00", "まもり山テラス")
TT_CARD = event_card("卓球", RED, "11/3(火・祝)", "12:20-15:20", "大久保プラザ", "大久保駅・新大久保駅すぐ")
BAD15 = event_card("バドミントン", GREEN, "11/15(日)", "13:00-15:00", "代々木の杜", "JR代々木駅から徒歩5分")
JOIN = card_lines(["申し込みは", "プロフィールのリンク → 公式LINE"], title="参加の流れ", color=TEAL)
REST = card_lines(["11/14(土) バド まもり山テラス", "11/15(日) バド 代々木の杜", "11/21(土) バレー 中野", "11/22(日) 野球 芝公園", "11/23(月祝) バレー・卓球",
                   "11/26(木) バド まもり山テラス", "11/28(土) バド 渋谷", "11/29(日) バド 巣鴨"], title="11月の後半", color=ORANGE)

SLOTS = [
 # 11/2(月)
 ("1102", "0800", dict(h1="今週は", h2="卓球！", blocks=[TT_CARD, card_lines(["来週末はバドミントン2連続", "11/14(土)・11/15(日)"])]),
  dict(src="clipA", ss=12, h1="今週も", h2="体を動かそう", lines=["11/3(火・祝) 卓球", "11/14・15 バドミントン"]),
  dict(kind="poll", h1="気になるのは", h2="どっち？", opts="卓球／バドミントン")),
 ("1102", "1200", dict(h1="1人参加", h2="でも大丈夫？", blocks=[card_lines(["参加者の多くが", "1人で参加しています", "初心者7割・経験者3割くらい"])], bg="bad"),
  dict(src="clipB", ss=24, h1="初めてでも", h2="浮かない", lines=["ほとんどが1人参加", "上手さより楽しさ重視"]),
  dict(kind="question", h1="不安なこと", h2="教えて", sub="なんでも答えます！", bg="bad", opts="質問スタンプ")),
 ("1102", "2000", dict(h1="明日は", h2="卓球！", blocks=[TT_CARD, card_lines(["ラケット貸出あり", "参加費1,500円（当日 現金・PayPay）"])], bg="tt"),
  dict(src="tt", blur=3, h1="明日", h2="卓球開催", lines=["11/3(火・祝) 12:20-15:20", "大久保プラザ"], lower=True),
  dict(kind="link", h1="申し込みは", h2="公式LINEから", sub="11/3(火・祝) 卓球", opts="リンク：公式LINE")),
 # 11/3(火祝)
 ("1103", "0800", dict(h1="本日", h2="開催！", blocks=[TT_CARD, yellow_band("まだ参加枠あります", size=80)], bg="tt"),
  dict(src="tt", blur=3, h1="手ぶらで", h2="OK！", lines=["ラケット貸出あり", "初心者さん大歓迎"], lower=True),
  dict(kind="link", h1="今日の卓球", h2="まだ間に合う", sub="12:20〜 大久保プラザ", opts="リンク：公式LINE")),
 ("1103", "1200", dict(h1="持ち物", h2="チェック", blocks=[card_lines(["・着替え", "・体育館シューズ", "・飲み物", "（卓球・バドはラケット貸出あり）"])], bg="gym"),
  dict(src="gym", h1="これだけ", h2="あればOK", lines=["着替え", "体育館シューズ", "飲み物"]),
  dict(kind="quiz", h1="持ち物クイズ", sub="必要ないのはどれ？", opts="クイズ：着替え／体育館シューズ／ラケット（正解）")),
 ("1103", "2000", dict(h1="次は", h2="バドミントン", blocks=[BAD_CARD("11/14(土)"), card_lines(["ラケット貸出あり"])], bg="bad"),
  dict(src="clipB", ss=30, h1="次は", h2="11/14 バド", lines=["15:00-17:00", "まもり山テラス"]),
  dict(kind="link", h1="11/14 バド", h2="受付中", sub="まもり山テラス 15:00〜", opts="リンク：公式LINE")),
 # 11/4(水)
 ("1104", "0800", dict(h1="来週末は", h2="バド2連続！", blocks=[BAD_CARD("11/14(土)"), BAD15], bg="bad"),
  dict(src="clipA", ss=20, h1="ラケット", h2="貸出あり", lines=["手ぶらでOK", "初心者さん大歓迎"]),
  dict(kind="poll", h1="バドミントン", h2="経験ある？", opts="投票：ある／はじめて")),
 ("1104", "1200", dict(h1="当日の流れ", h2="（例）", blocks=[card_lines(["① 受付", "② ストレッチ・基礎練習", "③ シャッフルゲーム（試合）", "④ 片付け → 解散", "※時間は当日お伝えします"])], bg="gym"),
  dict(src="clipA", ss=36, h1="当日は", h2="こんな感じ", lines=["受付 → ストレッチ", "シャッフルゲーム", "片付け → 解散"]),
  dict(kind="question", h1="聞きたいこと", h2="ある？", sub="当日のこと、なんでもどうぞ", opts="質問スタンプ")),
 ("1104", "2000", dict(h1="LINE登録で", h2="プレゼント", blocks=[card_lines(["『初参加ガイド』", "持ち物・当日の流れ・", "一人参加のコツをまとめました"], title="公式LINE限定", color=LINE_GREEN)], bg="navy"),
  dict(src="ref", ss=1, h1="初参加ガイド", h2="もらえる", lines=["公式LINEに登録するだけ"], lower=True),
  dict(kind="link", h1="初参加ガイドを", h2="受け取る", sub="公式LINEに登録するだけ", opts="リンク：公式LINE")),
 # 11/5(木)
 ("1105", "0800", dict(h1="11月の", h2="残りの日程", blocks=[card_lines(["11/14(土) バド まもり山テラス", "11/15(日) バド 代々木の杜", "11/21〜23 バレー・野球・卓球", "11/26・28・29 バドミントン"], title="まだまだ開催", color=ORANGE)], bg="gym2"),
  dict(src="cal", blur=0, focus=(0.5, 0.45), h1="11月は", h2="全12回", lines=["保存して予定に入れよう"], lower=True),
  dict(kind="poll", h1="どの種目が", h2="いい？", opts="投票：バド／バレー／卓球／野球")),
 ("1105", "1200", dict(h1="どんな人が", h2="参加してる？", blocks=[card_lines(["20〜40代の社会人", "1人参加が多数", "初心者7割・経験者3割くらい"])], bg="gym"),
  dict(src="clipB", ss=40, h1="参加者は", h2="こんな人", lines=["20〜40代の社会人", "1人参加が多数", "初心者7割くらい"]),
  dict(kind="quiz", h1="クイズ", sub="初心者の割合は？", opts="クイズ：3割／5割／7割（正解）")),
 ("1105", "2000", dict(h1="新しい投稿", h2="あります", blocks=[card_lines(["はじめての1人参加ガイド", "保存して当日見返してね"], title="カルーセル投稿", color=TEAL)], bg="navy"),
  dict(src="gym2", h1="1人参加", h2="ガイド", lines=["不安なことを8枚にまとめました", "プロフィールから見てね"]),
  dict(kind="link", h1="もっと知りたい", h2="人は", sub="公式LINEで初参加ガイド", opts="リンク：公式LINE")),
 # 11/6(金)
 ("1106", "0800", dict(h1="来週末は", h2="バド2連続", blocks=[BAD_CARD("11/14(土)"), BAD15], bg="bad"),
  dict(src="clipA", ss=44, h1="11/14・15", h2="バド2連続", lines=["土 15:00 まもり山テラス", "日 13:00 代々木の杜"]),
  dict(kind="poll", h1="どっちに", h2="行きたい？", opts="投票：11/14(土)／11/15(日)")),
 ("1106", "1200", dict(h1="申し込みの", h2="流れ", blocks=[card_lines(["① 公式LINEに登録", "② イベント参加フォームで申し込み", "③ 合言葉をLINEに送る", "④ 参加受付証が届く → 当日見せるだけ"])], bg="navy"),
  dict(src="ref", ss=6, h1="申し込みは", h2="かんたん", lines=["フォーム → 合言葉 → 受付証"], lower=True),
  dict(kind="question", h1="分からない所", h2="ある？", sub="DMでも聞けます", opts="質問スタンプ")),
 ("1106", "2100", dict(h1="週末の予定", h2="決まった？", blocks=[card_lines(["11/14(土) バド まもり山テラス", "11/15(日) バド 代々木の杜", "11/21〜23 バレー・野球・卓球"], title="次の開催", color=ORANGE)], bg="gym2"),
  dict(src="clipB", ss=50, h1="申し込み", h2="受付中", lines=["11/14・15 バドミントン", "公式LINEから"]),
  dict(kind="link", h1="申し込みは", h2="公式LINEから", sub="11/14・15 バド受付中", opts="リンク：公式LINE")),
 # 11/7(土)
 ("1107", "0800", dict(h1="今週末は", h2="お休み", blocks=[card_lines(["次の開催はこちら↓"]), BAD_CARD("11/14(土)")], bg="bad"),
  dict(src="clipA", ss=52, h1="来週は", h2="バドミントン", lines=["11/14(土) 15:00-17:00", "ラケット貸出あり"]),
  dict(kind="poll", h1="今週末は", h2="何する？", opts="投票：体を動かす／ゆっくりする")),
 ("1107", "1200", dict(h1="参加費の", h2="こと", blocks=[card_lines(["1,500円", "当日、現金またはPayPay"], title="参加費", color=TEAL)], bg="gym"),
  dict(src="gym2", h1="参加費は", h2="1,500円", lines=["当日、現金またはPayPay"]),
  dict(kind="quiz", h1="クイズ", sub="参加費はいくら？", opts="クイズ：1,000円／1,500円（正解）／2,000円")),
 ("1107", "2100", dict(h1="来週末は", h2="2日連続！", blocks=[BAD_CARD("11/14(土)"), BAD15], bg="bad"),
  dict(src="clipB", ss=56, h1="来週末", h2="バド2連続", lines=["11/14(土) まもり山テラス", "11/15(日) 代々木の杜"]),
  dict(kind="link", h1="11/14・15", h2="申し込み", sub="公式LINEから", opts="リンク：公式LINE")),
 # 11/8(日)
 ("1108", "0800", dict(h1="来週末は", h2="2日連続！", blocks=[BAD_CARD("11/14(土)"), BAD15], bg="bad"),
  dict(src="clipA", ss=58, h1="来週末は", h2="バド2連続", lines=["11/14(土) まもり山テラス", "11/15(日) 代々木の杜"]),
  dict(kind="poll", h1="来週", h2="体動かす？", opts="投票：動かす！／ゆっくりする")),
 ("1108", "1200", dict(h1="よくある", h2="質問", blocks=[card_lines(["Q 1人でも平気？ → 多くが1人参加", "Q ラケットは？ → 貸出あり", "Q 支払いは？ → 当日 現金・PayPay"])], bg="gym"),
  dict(src="gym", h1="よくある", h2="質問", lines=["1人でも平気？ → 平気！", "ラケットは？ → 貸出あり", "支払いは？ → 現金・PayPay"]),
  dict(kind="question", h1="他に", h2="聞きたいことは？", sub="なんでもどうぞ", opts="質問スタンプ")),
 ("1108", "2000", dict(h1="11月後半の", h2="予定", blocks=[REST], bg="gym2"),
  dict(src="cal", blur=0, focus=(0.5, 0.55), h1="保存して", h2="予定に", lines=["11月後半も開催します"], lower=True),
  dict(kind="link", h1="気になる日は", h2="LINEで予約", sub="プロフィールからもOK", opts="リンク：公式LINE")),
]

if __name__ == "__main__":
    only = sys.argv[1:]  # e.g. 1102
    rows = []
    for day, tm, img, vid, ix in SLOTS:
        if only and day not in only: continue
        dd = os.path.join(OUT, day); os.makedirs(dd, exist_ok=True)
        p1 = os.path.join(dd, f"{day}_{tm}_1.png"); p2 = os.path.join(dd, f"{day}_{tm}_2.mp4"); p3 = os.path.join(dd, f"{day}_{tm}_3.png")
        make_image(img, p1); make_video(vid, p2); make_ix(ix, p3)
        rows.append([day, f"{tm[:2]}:{tm[2:]}", os.path.basename(p1), os.path.basename(p2), os.path.basename(p3), ix["opts"]])
        print("done", day, tm, flush=True)
    if not only:
        with open(os.path.join(OUT, "予約一覧.csv"), "w", encoding="utf-8-sig", newline="") as f:
            w = csv.writer(f); w.writerow(["日付", "時間", "1本目（画像）", "2本目（動画）", "3本目（仕掛け）", "3本目に付けるスタンプ"]); w.writerows(rows)
