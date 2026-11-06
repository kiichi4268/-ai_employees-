"""参加の流れ動画：①Instagram→公式LINE ②予約→受付証 ③現地受付 ＋ 全体版（音楽なし）"""
import os, subprocess, sys
from PIL import Image, ImageDraw, ImageFilter
from make_1101 import (W, H, FPS, BLACK, BOLD, TEAL, YEL, NAVY, WHITE, F, text_img, pill, shadowed, place,
                       headline, yellow_band, appear, D)

OUT = os.path.join(D, "out", "flow"); os.makedirs(OUT, exist_ok=True)
SHORT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "inputs", "7f1d85cf-ScreenRecording_11-02-2026_22.MP4")
LONG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "inputs", "ScreenRecording_11-02-2026_20-46-38_1.MP4")
RECEIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mat", "receipt.jpg")
LINE_GREEN = (6, 199, 85)

PW, PH = 640, 1385            # phone screen size on canvas (1170x2532 scaled)
SC = PW / 1170
PX, PY = (W - PW) // 2, 470

def fit(im, maxw=W - 80):
    if im.width <= maxw: return im
    r = maxw / im.width; return im.resize((int(im.width * r), int(im.height * r)), Image.LANCZOS)

# background
BG = Image.new("RGB", (W, H)); _d = ImageDraw.Draw(BG)
for y in range(H): _d.line([(0, y), (W, y)], fill=(11 + int(10 * y / H), 23 + int(16 * y / H), 51 + int(34 * y / H)))
BG = BG.convert("RGBA")
FRAME = Image.new("RGBA", (W, H), (0, 0, 0, 0)); _f = ImageDraw.Draw(FRAME)
_f.rounded_rectangle((PX - 18, PY - 18, PX + PW + 18, PY + PH + 18), 60, fill=(15, 15, 18, 255), outline=(90, 100, 120, 255), width=4)
SH = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(SH).rounded_rectangle((PX - 10, PY + 10, PX + PW + 26, PY + PH + 40), 60, fill=(0, 0, 0, 150))
SH = SH.filter(ImageFilter.GaussianBlur(20))
MASK = Image.new("L", (PW, PH), 0); ImageDraw.Draw(MASK).rounded_rectangle((0, 0, PW - 1, PH - 1), 44, fill=255)

def step_tag(n, label):
    t = text_img(f"STEP {n}", F(BLACK, 40), NAVY); l = text_img(label, F(BLACK, 40), WHITE)
    return shadowed(pill([t, l], h=82, bg=(255, 255, 255, 0), pad=0)) if False else _tag(t, l)

def _tag(t, l):
    w = t.width + l.width + 90; h = 84
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w - 1, h - 1), 42, fill=TEAL)
    d.rounded_rectangle((6, 6, t.width + 46, h - 7), 36, fill=YEL)
    im.alpha_composite(t, (26, (h - t.height) // 2)); im.alpha_composite(l, (t.width + 64, (h - l.height) // 2))
    return shadowed(im)

def cap(text, sub=None):
    parts = [fit(shadowed(pill([text_img(text, F(BLACK, 54), NAVY)], h=108)))]
    if sub: parts.append(fit(shadowed(pill([text_img(sub, F(BOLD, 40), WHITE)], h=80, bg=(20, 42, 92, 235)))))
    return parts

# ---------- phone source ----------
def phone_frames(path, start, dur, speed=1.0, blurs=(), soft=0, highlight=None):
    """yield phone-screen RGBA frames (PW x PH). blurs: [(x0,y0,x1,y1)] in original px."""
    vf = f"fps={FPS / speed:.4f},scale={PW}:{PH}"
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-ss", str(start), "-i", path, "-t", str(dur), "-vf", vf,
                          "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    n = PW * PH * 3; last = None
    while True:
        b = p.stdout.read(n)
        if len(b) < n: break
        im = Image.frombuffer("RGB", (PW, PH), b).copy()
        if soft: im = im.filter(ImageFilter.GaussianBlur(soft))
        for (x0, y0, x1, y1) in blurs:
            box = tuple(int(v * SC) for v in (x0, y0, x1, y1))
            im.paste(im.crop(box).filter(ImageFilter.GaussianBlur(14)), box[:2])
        last = im; yield im
    p.wait()

def hl_box(c, box, t):
    """pulsing yellow box over phone area; box in original px"""
    x0, y0, x1, y1 = [int(v * SC) for v in box]
    a = 0.6 + 0.4 * abs(((t * 1.6) % 2) - 1)
    o = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(o)
    d.rounded_rectangle((PX + x0, PY + y0, PX + x1, PY + y1), 18, outline=YEL + (int(255 * a),), width=9)
    c.alpha_composite(o)

def compose(phone, t, tag, caps, cap_t0=0.15, hbox=None):
    c = BG.copy(); c.alpha_composite(SH); c.alpha_composite(FRAME)
    c.paste(phone.convert("RGB"), (PX, PY), MASK)
    if hbox: hl_box(c, hbox, t)
    place(c, tag, W / 2, 70)
    y = 180
    for i, p in enumerate(caps):
        place(c, p, W / 2, y, appear(t, cap_t0 + 0.25 * i)); y += p.height - 6
    return c

def still(img_rgba):
    while True: yield img_rgba

# ---------- graphics for STEP 3 ----------
def icon_circle(txt, color, size=230, fs=64):
    im = Image.new("RGBA", (size, size), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.ellipse((0, 0, size - 1, size - 1), fill=color, outline=WHITE, width=8)
    t = text_img(txt, F(BLACK, fs), WHITE); im.alpha_composite(t, ((size - t.width) // 2, (size - t.height) // 2 - 4))
    return shadowed(im)

RECEIPT_IMG = Image.open(RECEIPT).convert("RGB")

def receipt_phone():
    r = RECEIPT_IMG.resize((PW, int(RECEIPT_IMG.height * PW / RECEIPT_IMG.width)), Image.LANCZOS)
    ph = Image.new("RGB", (PW, PH), (10, 22, 52)); ph.paste(r, (0, (PH - r.height) // 2)); return ph

# ---------- segments ----------
def seg(frames_gen, n_sec, tag, caps, hbox=None, cap_t0=0.15):
    """returns list of (generator of composed frames)"""
    def gen():
        k = 0; last = None
        for ph in frames_gen:
            if k >= int(n_sec * FPS): break
            last = ph; yield compose(ph, k / FPS, tag, caps, cap_t0, hbox); k += 1
        while k < int(n_sec * FPS):  # hold last frame
            yield compose(last, k / FPS, tag, caps, cap_t0, hbox); k += 1
    return gen

def title_card(n_sec, big, sub, step=None):
    hlimg = fit(shadowed(headline(big[0], big[1], seed=3, size=120)))
    s = fit(shadowed(pill([text_img(sub, F(BLACK, 52), NAVY)], h=106)))
    st = icon_circle(step, TEAL, 260, 70) if step else None
    def gen():
        for k in range(int(n_sec * FPS)):
            t = k / FPS; c = BG.copy()
            if st: place(c, st, W / 2, 470, appear(t, 0))
            place(c, hlimg, W / 2, 800, appear(t, 0.15), slide=-250)
            place(c, s, W / 2, 1090, appear(t, 0.45))
            place(c, shadowed(pill([text_img("@macachette_sports", F(BOLD, 40), WHITE)], h=84, bg=NAVY)), W / 2, 1640)
            yield c
    return gen

def step3_gen(n_sec):
    tag = _tag(text_img("STEP 3", F(BLACK, 40), NAVY), text_img("当日の受付", F(BLACK, 40), WHITE))
    ph = receipt_phone()
    items = [
        (0.0, cap("① 会場に着いたら", "主催者のところへ")),
        (3.0, cap("② 「参加受付証」を見せる", "LINEに届いた画像を見せるだけ")),
        (6.5, cap("③ 参加費をお支払い", "1,500円｜現金 または PayPay")),
        (10.0, cap("受付完了！", "あとは思いきり楽しむだけ")),
    ]
    yen = icon_circle("¥1,500", (226, 60, 60), 300, 60)
    pay = [shadowed(pill([text_img("現金", F(BLACK, 52), NAVY)], h=104)), shadowed(pill([text_img("PayPay", F(BLACK, 52), WHITE)], h=104, bg=(255, 0, 51)))]
    ok = icon_circle("OK!", LINE_GREEN, 300, 90)
    def gen():
        for k in range(int(n_sec * FPS)):
            t = k / FPS
            idx = max(i for i, (s, _) in enumerate(items) if t >= s); s0, cp = items[idx]
            c = BG.copy()
            if idx <= 1:
                c.alpha_composite(SH); c.alpha_composite(FRAME); c.paste(ph, (PX, PY), MASK)
                if idx == 1: hl_box(c, (40, 380, 1130, 2100), t)
            elif idx == 2:
                place(c, yen, W / 2, 700, appear(t, s0 + .2))
                place(c, pay[0], W / 2 - 160, 1100, appear(t, s0 + .6)); place(c, pay[1], W / 2 + 160, 1100, appear(t, s0 + .8))
                place(c, shadowed(pill([text_img("受付証を見せた後にお支払い", F(BOLD, 42), WHITE)], h=84, bg=(20, 42, 92, 235))), W / 2, 1300, appear(t, s0 + 1.0))
            else:
                place(c, ok, W / 2, 750, appear(t, s0 + .2))
                place(c, shadowed(yellow_band("いってらっしゃい！", size=96)), W / 2, 1150, appear(t, s0 + .5))
            place(c, tag, W / 2, 70)
            y = 180
            for i, p in enumerate(cp):
                place(c, p, W / 2, y, appear(t, s0 + 0.15 + 0.25 * i)); y += p.height - 6
            yield c
    return gen

def outro(n_sec):
    a = fit(shadowed(headline("参加の流れは", "かんたん！", seed=6, size=110)))
    lines = [shadowed(pill([text_img(s, F(BLACK, 50), NAVY)], h=100)) for s in
             ["① Instagram → 公式LINEを追加", "② 予約 → 合言葉 → 参加受付証", "③ 当日は受付証を見せてお支払い"]]
    cta = fit(shadowed(pill([text_img("プロフィールのリンクから公式LINEへ", F(BLACK, 46), WHITE)], h=100, bg=LINE_GREEN)))
    def gen():
        for k in range(int(n_sec * FPS)):
            t = k / FPS; c = BG.copy()
            place(c, a, W / 2, 330, appear(t, 0), slide=-250)
            for i, l in enumerate(lines): place(c, l, W / 2, 700 + 150 * i, appear(t, .4 + .3 * i))
            place(c, cta, W / 2, 1260, appear(t, 1.5))
            place(c, shadowed(pill([text_img("@macachette_sports", F(BOLD, 40), WHITE)], h=84, bg=NAVY)), W / 2, 1640)
            yield c
    return gen

# ---------- STEP definitions ----------
def step1():
    tag = _tag(text_img("STEP 1", F(BLACK, 40), NAVY), text_img("公式LINEを追加", F(BLACK, 40), WHITE))
    return [
        seg(phone_frames(SHORT, 2.5, 3.0), 3.0, tag, cap("Instagramのプロフィールを開く", "@macachette_sports"), hbox=(20, 965, 760, 1065)),
        seg(phone_frames(SHORT, 8.5, 1.3, speed=0.5), 2.8, tag, cap("「公式LINE」をタップ", "プロフィールのリンクから"), hbox=(20, 1060, 1150, 1260)),
        seg(phone_frames(SHORT, 12.0, 3.0, blurs=[(0, 230, 1170, 1470)]), 3.6, tag, cap("「追加」で友だち登録", "トーク画面が開いたらOK！")),
    ]

CHAT_BLUR = [(0, 300, 1170, 1450)]
CARD_BLUR = [(0, 270, 1170, 1150)]
CARD_BLUR2 = [(0, 270, 1170, 1215)]
def step2():
    tag = _tag(text_img("STEP 2", F(BLACK, 40), NAVY), text_img("予約して受付証をもらう", F(BLACK, 40), WHITE))
    return [
        seg(phone_frames(LONG, 0.0, 2.8, blurs=CHAT_BLUR), 3.2, tag, cap("「イベントカレンダーから予約」", "メニューのEVENTからタップ"), hbox=(10, 1640, 1160, 1940)),
        seg(phone_frames(LONG, 3.0, 12.0, speed=3, blurs=CARD_BLUR), 4.0, tag, cap("「お申し込みはこちら」をタップ", "参加したいイベントを選ぶ"), hbox=(560, 1225, 1150, 1335)),
        seg(phone_frames(LONG, 20.0, 52.0, speed=5, soft=7), 10.4, tag, cap("参加フォームに入力して「送信」", "イベントを選ぶ → 名前などを入力")),
        seg(phone_frames(LONG, 72.5, 4.0, speed=1), 4.0, tag, cap("「合言葉」が表示される", "長押しでコピー（例：申込完了1129バド）"), hbox=(20, 780, 1150, 1000)),
        seg(phone_frames(LONG, 96.0, 4.5, speed=1.5), 3.0, tag, cap("「LINEで開く」→「開く」", "公式LINEのトーク画面へ")),
        seg(phone_frames(LONG, 100.5, 21.0, speed=4, blurs=CARD_BLUR2), 5.25, tag, cap("合言葉を貼り付けて送信", "トークにコメントするだけ"), hbox=(560, 1230, 1160, 1335)),
        seg(still(receipt_phone()), 3.6, tag, cap("「参加受付証」が届いて完了！", "当日まで保存しておこう")),
    ]

def write(path, gens):
    proc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                             "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", "-movflags", "+faststart", path], stdin=subprocess.PIPE)
    last = None
    for g in gens:
        for i, fr in enumerate(g()):
            fr = fr.convert("RGB")
            if last is not None and i < 6: fr = Image.blend(last, fr, (i + 1) / 7)
            proc.stdin.write(fr.tobytes()); cur = fr
        last = cur
    proc.stdin.close(); proc.wait(); print("done", path, flush=True)

if __name__ == "__main__":
    which = sys.argv[1:] or ["1", "2", "3", "all"]
    T1 = title_card(1.8, ("STEP1", "公式LINEを追加"), "Instagram → リンク → 公式LINE", "1")
    T2 = title_card(1.8, ("STEP2", "予約して受付証"), "予約 → フォーム → 合言葉 → 受付証", "2")
    T3 = title_card(1.8, ("STEP3", "当日の受付"), "受付証を見せて → お支払い", "3")
    if "1" in which: write(os.path.join(OUT, "参加の流れ_①Instagram→公式LINE.mp4"), [T1] + step1() + [outro(3.0)])
    if "2" in which: write(os.path.join(OUT, "参加の流れ_②予約→受付証.mp4"), [T2] + step2() + [outro(3.0)])
    if "3" in which: write(os.path.join(OUT, "参加の流れ_③当日の受付.mp4"), [T3, step3_gen(13.5), outro(3.0)])
    if "all" in which:
        intro = title_card(2.2, ("参加の流れ", "まるわかり"), "はじめての方も3ステップでOK")
        write(os.path.join(OUT, "参加の流れ_全体.mp4"), [intro, T1] + step1() + [T2] + step2() + [T3, step3_gen(13.5), outro(4.0)])
