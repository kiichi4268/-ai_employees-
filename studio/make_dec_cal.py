"""12月カレンダー：11月カレンダー画像を元に日程を差し替え（12/29・12/30は仮）"""
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from make_1101 import brush, D

SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cal", "cal11_original.png")
OUT = os.path.join(D, "out", "dec"); os.makedirs(OUT, exist_ok=True)
BLK = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts", "NotoSansCJK-Black.ttc")
BLD = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts", "NotoSansCJK-Bold.ttc")
MED = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts", "NotoSansCJK-Medium.ttc")
def F(p, s): return ImageFont.truetype(p, s)
INK = (22, 28, 36)
GREEN, ORANGE, BLUE = (17, 151, 65), (245, 95, 9), (21, 101, 192)
GRAY = (150, 160, 165)

im = Image.open(SRC).convert("RGBA")
d = ImageDraw.Draw(im)

def pin(x, y, col, s=22):
    d.ellipse((x, y, x + s, y + s), fill=col)
    d.polygon([(x + 3, y + s * .62), (x + s - 3, y + s * .62), (x + s / 2, y + s * 1.25)], fill=col)
    d.ellipse((x + s * .32, y + s * .3, x + s * .68, y + s * .66), fill="white")

def date_pill(x, y, date, wd, col, h=40):
    a = F(BLK, 27); b = F(BLD, 18)
    wa = d.textlength(date, font=a); wb = d.textlength(f"({wd})", font=b)
    w = wa + wb + 34
    d.rounded_rectangle((x, y, x + w, y + h), h // 2, fill=col)
    d.text((x + 17, y + h / 2), date, font=a, fill="white", anchor="lm")
    d.text((x + 17 + wa + 1, y + h / 2 + 2), f"({wd})", font=b, fill="white", anchor="lm")
    return x + w

def kari(x, y, txt="仮・調整中"):
    f = F(BLK, 15); w = d.textlength(txt, font=f) + 16
    d.rounded_rectangle((x, y, x + w, y + 26), 8, fill=(226, 60, 60))
    d.text((x + 8, y + 13), txt, font=f, fill="white", anchor="lm")
    return x + w

def dotted(x0, x1, y, col):
    for x in range(x0, x1, 8): d.line((x, y, x + 3, y), fill=col, width=2)

# ---------- title 11月 -> 12月 ----------
br = brush(270, 175, (2, 130, 228, 255), seed=21, rough=16)
im.alpha_composite(br, (-5, 55)); d = ImageDraw.Draw(im)
t = Image.new("RGBA", (330, 220), (0, 0, 0, 0)); td = ImageDraw.Draw(t)
td.text((10, 10), "12", font=F(BLK, 150), fill=(252, 238, 80), stroke_width=7, stroke_fill=(15, 45, 110))
td.text((205, 62), "月", font=F(BLK, 98), fill=(252, 238, 80), stroke_width=6, stroke_fill=(15, 45, 110))
t = t.transform(t.size, Image.AFFINE, (1, 0.18, -30, 0, 1, 0), Image.BICUBIC).rotate(4, expand=False, resample=Image.BICUBIC)
im.alpha_composite(t, (18, 40)); d = ImageDraw.Draw(im)

# ---------- badminton column ----------
d.rectangle((24, 582, 344, 1098), fill=(241, 250, 236))
bad = [("12/5", "土", "19:00-22:00", "目黒区民センター", False),
       ("12/12", "土", "15:00-17:00", "まもり山テラス", False),
       ("12/13", "日", "18:00-21:00", "巣鴨体育館", False),
       ("12/24", "木", "18:00-21:00", "まもり山テラス", False),
       ("12/29", "火", "13:00-15:00", "港区内の体育館", True)]
y = 596
for i, (dt, wd, tm, vn, k) in enumerate(bad):
    xe = date_pill(34, y, dt, wd, GREEN)
    d.text((xe + 12, y + 20), tm, font=F(MED, 20), fill=INK, anchor="lm")
    pin(156, y + 48, GREEN, 20)
    d.text((184, y + 58), vn, font=F(BLD, 19), fill=INK, anchor="lm")
    if k: kari(34, y + 49, "仮")
    if i < len(bad) - 1: dotted(40, 330, y + 92, (140, 205, 120))
    y += 101

# ---------- volleyball column ----------
d.rectangle((364, 588, 662, 968), fill=(254, 247, 234))
y = 600
date_pill(378, y, "12/26", "土", ORANGE)
d.text((432, y + 66), "11:45-13:45", font=F(MED, 21), fill=INK, anchor="lm")
pin(404, y + 88, ORANGE, 21)
d.text((432, y + 99), "中野区中部", font=F(BLD, 19), fill=INK, anchor="lm")
d.text((432, y + 124), "コミュニティプラザ", font=F(BLD, 19), fill=INK, anchor="lm")
dotted(378, 650, y + 152, (245, 180, 120))
# year-end note card
d.rounded_rectangle((380, 770, 646, 950), 18, fill="white", outline=ORANGE, width=3)
d.text((513, 800), "年末も開催！", font=F(BLK, 30), fill=ORANGE, anchor="mm")
d.text((513, 846), "12/29 バドミントン", font=F(BLD, 21), fill=INK, anchor="mm")
d.text((513, 878), "12/30 野球", font=F(BLD, 21), fill=INK, anchor="mm")
d.text((513, 920), "港区で会場を調整中（仮）", font=F(BLD, 17), fill=(226, 60, 60), anchor="mm")

# ---------- table tennis / baseball column ----------
d.rectangle((692, 596, 1000, 1024), fill=(237, 248, 253))
tt = [("12/6", "日", "12:20-15:20", "卓球＠大久保プラザ", "tt", False),
      ("12/19", "土", "12:20-15:20", "卓球＠大久保プラザ", "tt", False),
      ("12/27", "日", "12:20-15:20", "卓球＠大久保プラザ", "tt", False),
      ("12/30", "水", "12:00-14:00", "野球＠港区内", "bb", True)]
y = 606
for i, (dt, wd, tm, vn, ic, k) in enumerate(tt):
    xe = date_pill(700, y, dt, wd, BLUE)
    d.text((xe + 10, y + 20), tm, font=F(MED, 20), fill=INK, anchor="lm")
    if ic == "tt":
        d.ellipse((706, y + 52, 728, y + 74), fill=BLUE); d.line((717, y + 72, 714, y + 86), fill=BLUE, width=5)
    else:
        d.ellipse((704, y + 52, 730, y + 78), outline=BLUE, width=3)
        d.arc((698, y + 50, 716, y + 80), -60, 60, fill=BLUE, width=2); d.arc((718, y + 50, 736, y + 80), 120, 240, fill=BLUE, width=2)
    d.text((740, y + 66), vn, font=F(BLD, 19), fill=INK, anchor="lm")
    if k: kari(int(740 + d.textlength(vn, font=F(BLD, 19)) + 10), y + 53)
    if i < len(tt) - 1: dotted(706, 990, y + 98, (130, 190, 230))
    y += 104

# ---------- how-to box ----------
boxes = [(284, 444, ["プロフィールの", "リンクから", "公式LINEを追加"]),
         (463, 589, ["イベント", "カレンダーから", "予約・フォーム入力"]),
         (608, 734, ["合言葉を送ると", "受付証が届く！"])]
for i, (x0, x1, lines) in enumerate(boxes):
    y1 = 1270 if i == 2 else 1318
    d.rectangle((x0 + 4, 1227, x1 - 4, y1), fill=(232, 244, 252))
    cy = 1246 if i < 2 else 1240
    for j, l in enumerate(lines):
        f = F(BLD, 17)
        while d.textlength(l, font=f) > (x1 - x0 - 12): f = F(BLD, f.size - 1)
        d.text(((x0 + x1) / 2, cy + j * 24), l, font=f, fill=INK, anchor="mm")

im = im.convert("RGB")
p1 = os.path.join(OUT, "12月カレンダー_1024x1536.png"); im.save(p1)
# 1080x1350 (fit with blurred fill)
bgimg = im.resize((1080, 1620)).crop((0, 135, 1080, 1485)).filter(ImageFilter.GaussianBlur(18))
fg = im.resize((900, 1350), Image.LANCZOS)
c = bgimg.copy(); c.paste(fg, (90, 0)); c.save(os.path.join(OUT, "12月カレンダー_1080x1350.png"))
print(p1)
