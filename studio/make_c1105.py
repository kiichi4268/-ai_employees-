"""11/5 カルーセル「はじめての1人参加ガイド」8枚 1080x1350"""
import os, subprocess
from PIL import Image, ImageDraw, ImageFilter
from make_1101 import (BLACK, BOLD, TEAL, YEL, NAVY, WHITE, F, text_img, pill, shadowed, headline, yellow_band, D)
from make_week1 import SRC

W, H = 1080, 1350
OUT = os.path.join(D, "out", "c1105"); os.makedirs(OUT, exist_ok=True)
LINE_GREEN = (6, 199, 85); RED = (226, 60, 60); ORANGE = (243, 128, 32)

def fit(im, maxw=W - 90):
    if im.width <= maxw: return im
    r = maxw / im.width; return im.resize((int(im.width * r), int(im.height * r)), Image.LANCZOS)

def put(c, im, x, y):  # x center
    c.alpha_composite(im, (int(x - im.width / 2), int(y)))

# futsal frame
_fp = os.path.join(D, "clips", "IMG_4096.MOV")
_raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", "1", "-i", _fp, "-frames:v", "1", "-f", "image2pipe", "-vcodec", "png", "-"], capture_output=True).stdout
import io
SRC["fut"] = Image.open(io.BytesIO(_raw)).convert("RGB")

def bg(key, blur=10, dark=0.5):
    im = SRC[key]; r = max(W / im.width, H / im.height)
    im = im.resize((int(im.width * r) + 1, int(im.height * r) + 1), Image.LANCZOS)
    x0, y0 = (im.width - W) // 2, (im.height - H) // 2
    im = im.crop((x0, y0, x0 + W, y0 + H)).filter(ImageFilter.GaussianBlur(blur))
    return Image.blend(im, Image.new("RGB", (W, H), (10, 22, 52)), dark).convert("RGBA")

def card(lines, w=960, title=None, color=TEAL, fs=56, gap=20, pad=44):
    rows = [fit(text_img(l, F(BLACK, fs), NAVY), w - 2 * pad) for l in lines]
    th = 104 if title else 0
    h = th + sum(r.height + gap for r in rows) + 2 * pad - gap
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w - 1, h - 1), 36, fill=(255, 255, 255, 246))
    if title:
        d.rounded_rectangle((0, 0, w - 1, th), 36, fill=color); d.rectangle((0, th - 36, w - 1, th), fill=color)
        im.alpha_composite(fit(text_img(title, F(BLACK, 58), WHITE), w - 60), (36, 14))
    y = th + pad
    for r in rows: im.alpha_composite(r, (pad, y)); y += r.height + gap
    return shadowed(im)

def num_badge(n, color=TEAL, s=110):
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.ellipse((0, 0, s - 1, s - 1), fill=color); t = text_img(str(n), F(BLACK, 62), WHITE)
    im.alpha_composite(t, ((s - t.width) // 2, (s - t.height) // 2 - 4)); return im

def step_row(n, text, sub=None, w=960, color=TEAL):
    b = num_badge(n, color, 100)
    t = fit(text_img(text, F(BLACK, 52), NAVY), w - 190)
    s = fit(text_img(sub, F(BOLD, 36), (70, 90, 120)), w - 190) if sub else None
    h = max(124, t.height + (s.height + 6 if s else 0) + 40)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w - 1, h - 1), 30, fill=(255, 255, 255, 246))
    im.alpha_composite(b, (26, (h - 100) // 2))
    ty = (h - t.height - (s.height + 6 if s else 0)) // 2
    im.alpha_composite(t, (150, ty))
    if s: im.alpha_composite(s, (152, ty + t.height + 6))
    return shadowed(im)

def page_no(c, n):
    t = text_img(f"{n}/8", F(BOLD, 34), WHITE); c.alpha_composite(t, (W - t.width - 40, H - t.height - 40))
    h = text_img("@macachette_sports", F(BOLD, 34), WHITE); c.alpha_composite(h, (40, H - h.height - 40))

def head(c, a, b, y=60, size=104, seed=3):
    put(c, fit(shadowed(headline(a, b, seed=seed, size=size))), W / 2, y)

def save(c, n):
    page_no(c, n); p = os.path.join(OUT, f"1105_カルーセル_{n:02d}.png"); c.convert("RGB").save(p, quality=95); return p

# 1 cover
c = bg("bad", blur=6, dark=0.35)
put(c, fit(shadowed(pill([text_img("保存して当日見返してね", F(BLACK, 44), WHITE)], h=88, bg=RED))), W / 2, 230)
put(c, fit(shadowed(headline("はじめての", "社会人スポーツ", seed=3, size=110))), W / 2, 380)
put(c, fit(shadowed(yellow_band("1人参加ガイド", size=150, seed=7))), W / 2, 620)
put(c, fit(shadowed(pill([text_img("不安なことを8枚にまとめました", F(BLACK, 50), NAVY)], h=104))), W / 2, 900)
put(c, fit(shadowed(pill([text_img("バド・バレー・フットサル・卓球・野球", F(BOLD, 40), WHITE)], h=84, bg=(20, 42, 92, 225)))), W / 2, 1040)
save(c, 1)

# 2 worries
c = bg("gym"); head(c, "よくある不安", "3つ", seed=4)
y = 400
for i, (t, s) in enumerate([("1人で行って浮かない？", None), ("運動不足でもついていける？", None), ("何を持っていけばいい？", None)]):
    r = step_row(i + 1, t, s, color=ORANGE); put(c, r, W / 2, y); y += r.height + 20
put(c, fit(shadowed(pill([text_img("次のページで答えます →", F(BLACK, 50), WHITE)], h=100, bg=TEAL))), W / 2, y + 40)
save(c, 2)

# 3 who
c = bg("fut"); head(c, "どんな人が", "参加してる？", seed=5)
y = 330
for big, small in [("20〜40代", "の社会人が中心"), ("1人参加", "がほとんど"), ("初心者7割", "・経験者3割くらい")]:
    w = 960; bt = text_img(big, F(BLACK, 92), TEAL); st = text_img(small, F(BLACK, 50), NAVY)
    im = Image.new("RGBA", (w, 200), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w - 1, 199), 34, fill=(255, 255, 255, 246))
    x = (w - bt.width - st.width - 10) // 2; im.alpha_composite(bt, (x, (200 - bt.height) // 2)); im.alpha_composite(st, (x + bt.width + 10, (200 - st.height) // 2 + 18))
    put(c, shadowed(im), W / 2, y); y += 230
put(c, fit(shadowed(yellow_band("だから浮かない！", size=86))), W / 2, y + 10)
save(c, 3)

# 4 flow to apply
c = bg("gym2"); head(c, "申し込みから", "当日まで", seed=6)
y = 290
for i, (t, s) in enumerate([("公式LINEに登録", "プロフィールのリンクから"), ("参加フォームで申し込み", "LINEのメニュー「イベントカレンダーから予約」"),
                            ("合言葉をLINEに送る", "「参加受付証」が届きます"), ("当日は受付証を見せるだけ", "参加費はそのあとでOK")]):
    r = step_row(i + 1, t, s); put(c, r, W / 2, y); y += r.height + 8
save(c, 4)

# 5 belongings
c = bg("bad"); head(c, "持ち物は", "これだけ", seed=7)
items = [("着替え", "動きやすい服"), ("体育館シューズ", "室内用のくつ"), ("飲み物", "こまめに水分補給")]
x0 = 70; y = 330
for i, (t, s) in enumerate(items):
    w, h = 300, 330
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w - 1, h - 1), 34, fill=(255, 255, 255, 246))
    im.alpha_composite(num_badge(i + 1, TEAL, 96), ((w - 96) // 2, 34))
    tt = fit(text_img(t, F(BLACK, 46), NAVY), w - 30); im.alpha_composite(tt, ((w - tt.width) // 2, 160))
    st = fit(text_img(s, F(BOLD, 30), (70, 90, 120)), w - 30); im.alpha_composite(st, ((w - st.width) // 2, 245))
    c.alpha_composite(shadowed(im), (60 + i * 330 - 30, y - 30))
put(c, fit(shadowed(pill([text_img("バドミントン・卓球はラケット貸出あり", F(BLACK, 46), NAVY)], h=100, bg=YEL))), W / 2, 760)
put(c, fit(shadowed(yellow_band("手ぶら感覚でOK", size=90, seed=9))), W / 2, 900)
save(c, 5)

# 6 money
c = bg("tt"); head(c, "お金の", "こと", seed=8)
w, h = 960, 380
im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
d.rounded_rectangle((0, 0, w - 1, h - 1), 36, fill=(255, 255, 255, 246))
a = text_img("参加費", F(BLACK, 50), NAVY); im.alpha_composite(a, ((w - a.width) // 2, 40))
b = text_img("1,500円", F(BLACK, 170), RED); im.alpha_composite(b, ((w - b.width) // 2, 110))
put(c, shadowed(im), W / 2, 320)
pays = [shadowed(pill([text_img("現金", F(BLACK, 58), NAVY)], h=116)), shadowed(pill([text_img("PayPay", F(BLACK, 58), WHITE)], h=116, bg=(255, 0, 51)))]
put(c, pays[0], W / 2 - 190, 750); put(c, pays[1], W / 2 + 190, 750)
put(c, fit(shadowed(pill([text_img("当日、受付証を見せたあとにお支払い", F(BLACK, 44), WHITE)], h=96, bg=(20, 42, 92, 230)))), W / 2, 920)
save(c, 6)

# 7 day flow
c = bg("base"); head(c, "当日の流れ", "（例）", seed=10)
y = 280
for i, (t, s) in enumerate([("受付", "受付証を見せて参加費をお支払い"), ("ストレッチ・基礎練習", "体をほぐしてから"), ("シャッフルゲーム（試合）", "メンバーを入れ替えて楽しむ"), ("片付け → 解散", "※時間はイベントごとに当日お伝えします")]):
    r = step_row(i + 1, t, s, color=ORANGE); put(c, r, W / 2, y); y += r.height + 8
save(c, 7)

# 8 CTA
c = bg("fut", dark=0.45); head(c, "不安は", "これで解決！", seed=11, y=120)
put(c, card(["持ち物・当日の流れ・", "1人参加のコツをまとめた", "『初参加ガイド』をプレゼント"], title="公式LINE限定", color=LINE_GREEN), W / 2, 340)
put(c, fit(shadowed(pill([text_img("プロフィールのリンクから公式LINEへ", F(BLACK, 50), WHITE)], h=110, bg=LINE_GREEN))), W / 2, 810)
put(c, fit(shadowed(pill([text_img("11月の日程も公式LINEのEVENTから", F(BLACK, 44), NAVY)], h=96))), W / 2, 950)
put(c, fit(shadowed(yellow_band("保存して当日見返してね", size=76, seed=12))), W / 2, 1070)
save(c, 8)
print("ok")
