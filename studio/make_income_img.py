"""ココナラ出品の画像3枚（マカスポくんの画像に文字を足すだけ・11/26 加藤さん「デザインは付け足し」）。1200×1200。
使い方: cd studio && python3 make_income_img.py"""
import os
from PIL import Image, ImageDraw, ImageFont
D = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(D, "..", "content", "income"); os.makedirs(OUT, exist_ok=True)
FB = os.path.join(D, "fonts", "NotoSansCJK-Black.ttc"); FM = os.path.join(D, "fonts", "NotoSansCJK-Bold.ttc")
NAVY, TEAL, YEL, WHITE = (20, 42, 92), (24, 160, 178), (255, 236, 30), (255, 255, 255)
M = Image.open(os.path.join(D, "mascot", "makaspo_cutout.png")).convert("RGBA")
def f(p, s): return ImageFont.truetype(p, s)
def base(title, sub):
    c = Image.new("RGB", (1200, 1200), (232, 243, 251)); d = ImageDraw.Draw(c)
    d.rectangle((0, 0, 1200, 230), fill=NAVY)
    d.text((600, 92), title, font=f(FB, 70), fill=WHITE, anchor="mm"); d.text((600, 175), sub, font=f(FM, 40), fill=YEL, anchor="mm")
    return c, d
def mascot(c, x, y, w):
    m = M.copy(); m.thumbnail((w, w)); c.paste(m, (x, y), m)
def rows(d, items, y, x=80, size=46, gap=92):
    for i, t in enumerate(items):
        d.rounded_rectangle((x, y + i * gap - 34, 1120, y + i * gap + 38), 20, fill=WHITE)
        d.text((x + 30, y + i * gap), t, font=f(FM, size), fill=NAVY, anchor="lm")
# 1 実績
c, d = base("Instagram を毎日自動で", "AI社員33人の仕組みで回しています")
mascot(c, 760, 260, 420)
for i, (big, small) in enumerate([("15本", "毎日のストーリー"), ("0件", "投稿の失敗（11/16〜）"), ("毎晩", "数字を見て1つ直す")]):
    y = 300 + i * 270; d.rounded_rectangle((70, y, 700, y + 230), 28, fill=WHITE)
    d.text((110, y + 95), big, font=f(FB, 110), fill=TEAL, anchor="lm"); d.text((110, y + 190), small, font=f(FM, 40), fill=NAVY, anchor="lm")
c.save(os.path.join(OUT, "coconala_1_実績.jpg"), quality=92)
# 2 流れ
c, d = base("お願いから投稿まで", "あなたがするのは「載せたい情報を送る」だけ")
rows(d, ["① 写真・日程・値段を送る", "② 3日ほどで最初の下書き", "③ 直したい所を伝える（何度でも）", "④ 毎日、決まった時間に自動で投稿", "⑤ 週1回、数字と次の改善をお届け"], 330)
mascot(c, 820, 830, 340); c.save(os.path.join(OUT, "coconala_2_流れ.jpg"), quality=92)
# 3 料金
c, d = base("料金", "運用代行（月額）と、仕組みづくり（1回）")
rows(d, ["お試し 1週間 10,000円", "スタンダード 月 40,000円", "しっかり 月 80,000円", "仕組みづくり 50,000円（1回）", "見守り 月 10,000円（任意）"], 330, size=50)
d.text((80, 1120), "※フォロワーの購入・自動いいねは行いません", font=f(FM, 34), fill=NAVY, anchor="lm")
mascot(c, 860, 800, 300); c.save(os.path.join(OUT, "coconala_3_料金.jpg"), quality=92)
print("ok")
