"""11/1 当日募集リール + ストーリーズ2枚（10月「〇〇開催！まだ参加枠あります」の型）"""
import subprocess, os, random, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps

D = os.path.dirname(os.path.abspath(__file__))
OUTD = os.path.join(D, "out"); os.makedirs(OUTD, exist_ok=True)
W, H, FPS = 1080, 1920, 30
BLACK = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts", "NotoSansCJK-Black.ttc")
BOLD = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts", "NotoSansCJK-Bold.ttc")
TEAL = (24, 160, 178); YEL = (255, 236, 30); NAVY = (20, 42, 92); WHITE = (255, 255, 255)
def F(p, s): return ImageFont.truetype(p, s)

# ---------- drawing parts ----------
def brush(w, h, color, seed=1, rough=14):
    """筆で塗ったような帯"""
    rnd = random.Random(seed)
    im = Image.new("RGBA", (w + 60, h + 40), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    top = [(30 + x, 20 + rnd.uniform(-rough, rough * 0.4)) for x in range(0, w + 1, 18)]
    bot = [(30 + x, 20 + h + rnd.uniform(-rough * 0.4, rough)) for x in range(w, -1, -18)]
    d.polygon(top + bot, fill=color)
    for side in (0, 1):  # ragged ends
        x = 30 if side == 0 else 30 + w
        for i in range(10):
            yy = 20 + rnd.uniform(0, h); r = rnd.uniform(6, 18)
            dx = -rnd.uniform(0, 26) if side == 0 else rnd.uniform(0, 26)
            d.ellipse((x + dx - r, yy - r, x + dx + r, yy + r), fill=color)
    for i in range(6):  # dry streaks
        yy = 20 + rnd.uniform(4, h - 4); xx = 30 + rnd.uniform(0, w * 0.3)
        d.line((xx, yy, xx + rnd.uniform(40, 160), yy), fill=(0, 0, 0, 0), width=2)
    return im

def text_img(txt, font, fill, stroke=0, stroke_fill=None, shadow=False):
    tmp = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    b = tmp.textbbox((0, 0), txt, font=font, stroke_width=stroke)
    im = Image.new("RGBA", (b[2] - b[0] + 16, b[3] - b[1] + 16), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    if shadow:
        d.text((8 - b[0] + 4, 8 - b[1] + 5), txt, font=font, fill=(0, 0, 0, 120), stroke_width=stroke, stroke_fill=(0, 0, 0, 120))
    d.text((8 - b[0], 8 - b[1]), txt, font=font, fill=fill, stroke_width=stroke, stroke_fill=stroke_fill)
    return im

def cal_icon(s, col):
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0)); d = ImageDraw.Draw(im); w = max(3, s // 12)
    d.rounded_rectangle((w, s * .18, s - w, s - w), s // 8, outline=col, width=w)
    d.rectangle((w, s * .18, s - w, s * .36), fill=col)
    for x in (.3, .7): d.line((s * x, s * .06, s * x, s * .26), fill=col, width=w)
    for r in range(2):
        for c in range(3):
            x = s * (.24 + c * .22); y = s * (.5 + r * .2); d.rectangle((x, y, x + s * .1, y + s * .1), fill=col)
    return im

def pin_icon(s, col):
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.ellipse((s * .15, 0, s * .85, s * .7), fill=col)
    d.polygon([(s * .2, s * .48), (s * .8, s * .48), (s * .5, s)], fill=col)
    d.ellipse((s * .35, s * .2, s * .65, s * .5), fill=WHITE)
    return im

def pill(parts, h=104, pad=34, bg=WHITE, radius=None):
    """parts: list of RGBA images placed in a row"""
    gap = 18
    w = sum(p.width for p in parts) + gap * (len(parts) - 1) + pad * 2
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w - 1, h - 1), radius or h // 2, fill=bg)
    x = pad
    for p in parts:
        im.alpha_composite(p, (int(x), int((h - p.height) / 2))); x += p.width + gap
    return im

def shadowed(im, r=14, off=8, a=110):
    sh = Image.new("RGBA", (im.width + 60, im.height + 60), (0, 0, 0, 0))
    m = im.split()[3].point(lambda v: int(v * a / 255))
    blk = Image.new("RGBA", im.size, (0, 0, 0, 255)); blk.putalpha(m)
    sh.alpha_composite(blk, (30, 30 + off)); sh = sh.filter(ImageFilter.GaussianBlur(r))
    sh.alpha_composite(im, (30, 30)); return sh

def headline(word, word2="開催！", seed=3, size=150):
    """teal brush + yellow word + white word"""
    a = text_img(word, F(BLACK, size), YEL, stroke=6, stroke_fill=(10, 60, 80))
    b = text_img(word2, F(BLACK, int(size * .78)), WHITE, stroke=6, stroke_fill=(10, 60, 80))
    w = a.width + b.width + 70; h = max(a.height, b.height) + 50
    br = brush(w, h, TEAL, seed=seed)
    br.alpha_composite(a, (60, 20 + (h - a.height) // 2))
    br.alpha_composite(b, (60 + a.width + 14, 20 + (h - b.height) // 2 + int(size * .08)))
    br = br.rotate(3, expand=True, resample=Image.BICUBIC)
    return br

def yellow_band(txt, size=104, seed=7):
    t = text_img(txt, F(BLACK, size), NAVY)
    br = brush(t.width + 60, t.height + 36, YEL, seed=seed)
    br.alpha_composite(t, (60, 38)); return br.rotate(-2, expand=True, resample=Image.BICUBIC)

def white_band(txt, size=60, seed=9):
    t = text_img(txt, F(BLACK, size), NAVY)
    br = brush(t.width + 50, t.height + 28, WHITE, seed=seed, rough=8)
    br.alpha_composite(t, (55, 34)); return br.rotate(-2, expand=True, resample=Image.BICUBIC)

def handle_pill():
    t = text_img("@macachette_sports", F(BOLD, 44), WHITE)
    p = pill([t], h=92, bg=NAVY)
    d = ImageDraw.Draw(p); d.rounded_rectangle((0, 0, p.width - 1, p.height - 1), 46, outline=WHITE, width=4)
    return p

def info_pills(date_txt, venue, access, extra=None, size=54):
    out = []
    out.append(pill([cal_icon(64, NAVY), text_img(date_txt, F(BLACK, size), NAVY)]))
    out.append(pill([pin_icon(60, NAVY), text_img(venue, F(BLACK, size), NAVY)]))
    sub = access + (f"｜{extra}" if extra else "")
    out.append(pill([text_img(sub, F(BOLD, 38), WHITE)], h=74, bg=(20, 42, 92, 225)))
    return out

def place(canvas, im, cx, y, p=1.0, slide=0):
    """p: 0..1 appear progress (fade+slide)"""
    if p <= 0: return
    e = p * p * (3 - 2 * p); im2 = im
    if e < 1:
        im2 = im.copy(); im2.putalpha(im.split()[3].point(lambda v: int(v * e)))
    x = int(cx - im.width / 2 + slide * (1 - e)); canvas.alpha_composite(im2, (x, int(y + 40 * (1 - e))))

# ---------- backgrounds ----------
def clip_frames(path, start, dur):
    w, h = 360, 640
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(start), "-i", path, "-t", str(dur), "-vf",
                          f"fps={FPS},scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h}",
                          "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
    n = len(raw) // (w * h * 3)
    return [Image.frombuffer("RGB", (w, h), raw[i * w * h * 3:(i + 1) * w * h * 3]).copy().filter(ImageFilter.GaussianBlur(4.6)) for i in range(n)]

def photo_bg(path, blur=6, focus=(0.5, 0.5)):
    im = ImageOps.exif_transpose(Image.open(path)).convert("RGB")
    r = max(W * 1.12 / im.width, H * 1.12 / im.height)
    im = im.resize((int(im.width * r), int(im.height * r)), Image.LANCZOS).filter(ImageFilter.GaussianBlur(blur))
    return im, focus

def photo_frame(pb, p):
    im, focus = pb; z = 1 + 0.06 * p
    cw, ch = im.width / 1.0 / z * (W / (im.width / 1.12 * 1.0)) / 1.12, 0
    cw, ch = W * (im.width / (W * 1.12)) / z * 1.0, H * (im.height / (H * 1.12)) / z
    cw, ch = min(cw, im.width), min(ch, im.height)
    x0 = min(max(focus[0] * im.width - cw / 2, 0), im.width - cw); y0 = min(max(focus[1] * im.height - ch / 2, 0), im.height - ch)
    return im.crop((int(x0), int(y0), int(x0 + cw), int(y0 + ch))).resize((W, H), Image.BILINEAR)

def tone(f, a=0.25):
    f = Image.blend(f, Image.new("RGB", (W, H), (10, 22, 52)), a).convert("RGBA")
    g = Image.new("RGBA", (W, H), (0, 0, 0, 0)); gd = ImageDraw.Draw(g)
    for yy in range(1100, H): gd.line([(0, yy), (W, yy)], fill=(8, 18, 45, int(150 * (yy - 1100) / (H - 1100))))
    return Image.alpha_composite(f, g)

C = os.path.join(D, "clips")
A = os.path.join(C, "96bd7101d80345dea32585cc72954439.MOV"); B = os.path.join(C, "29da73e9795845e4aea114b14fb8c95c.MOV")
gym = photo_bg(os.path.join(D, "photos", "IMG_3560.jpg"), blur=7, focus=(0.5, 0.55))

# ---------- parts ----------
HL_TODAY = shadowed(headline("本日", "開催！", seed=3, size=170))
SUB_TODAY = shadowed(pill([text_img("11/1(日)  バレー＆バドミントン", F(BLACK, 54), NAVY)]))
HL_VOL = shadowed(headline("バレーボール", "", seed=4, size=130))
HL_BAD = shadowed(headline("バドミントン", "", seed=5, size=130))
VOL = [shadowed(p) for p in info_pills("11/1(日) 18:00-21:00", "巣鴨体育館", "JR巣鴨駅・大塚駅から徒歩約10分")]
BAD = [shadowed(p) for p in info_pills("11/1(日) 19:00-22:00", "目黒区民センター", "JR・東急 目黒駅から徒歩10分", "ラケット貸出あり")]
YB = shadowed(yellow_band("まだ参加枠あります"))
WB = shadowed(white_band("初心者さん・ひとり参加大歓迎"))
FEE = shadowed(pill([text_img("参加費 1,500円｜当日 現金・PayPay", F(BLACK, 46), NAVY)], h=92))
CTA = shadowed(pill([text_img("申し込みはプロフィールのリンクから", F(BLACK, 46), WHITE)], h=96, bg=TEAL))
HANDLE = shadowed(handle_pill())

def appear(t, start, dur=0.35): return max(0.0, min(1.0, (t - start) / dur))

# ---------- reel ----------
def reel():
    fa = clip_frames(A, 10, 3.4); fb = clip_frames(B, 20, 3.9); fa2 = clip_frames(A, 30, 4.2)
    segs = [
        (3.2, lambda k, t: fa[min(k, len(fa) - 1)], lambda c, t: (
            place(c, HL_TODAY, W / 2, 230, appear(t, 0.0), slide=-300),
            place(c, SUB_TODAY, W / 2, 560, appear(t, 0.35)),
            place(c, YB, W / 2, 1180, appear(t, 0.8), slide=300),
            place(c, WB, W / 2, 1400, appear(t, 1.1)))),
        (3.9, lambda k, t: photo_frame(gym, t / 3.9), lambda c, t: (
            place(c, HL_VOL, W / 2, 260, appear(t, 0.0), slide=-300),
            [place(c, p, W / 2, 620 + i * 150, appear(t, 0.35 + i * 0.25)) for i, p in enumerate(VOL)])),
        (3.9, lambda k, t: fb[min(k, len(fb) - 1)], lambda c, t: (
            place(c, HL_BAD, W / 2, 260, appear(t, 0.0), slide=-300),
            [place(c, p, W / 2, 620 + i * 150, appear(t, 0.35 + i * 0.25)) for i, p in enumerate(BAD)])),
        (4.2, lambda k, t: fa2[min(k, len(fa2) - 1)], lambda c, t: (
            place(c, YB, W / 2, 360, appear(t, 0.0), slide=-300),
            place(c, WB, W / 2, 590, appear(t, 0.3)),
            place(c, FEE, W / 2, 900, appear(t, 0.6)),
            place(c, CTA, W / 2, 1080, appear(t, 0.9)),
            place(c, HANDLE, W / 2, 1260, appear(t, 1.1)))),
    ]
    out = os.path.join(OUTD, "1101_当日募集リール_バレー×バド.mp4")
    proc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                             "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p",
                             "-movflags", "+faststart", out], stdin=subprocess.PIPE)
    last = None
    for d, bgf, ov in segs:
        for k in range(int(d * FPS)):
            t = k / FPS; bg = bgf(k, t)
            if bg.size != (W, H): bg = bg.resize((W, H), Image.BICUBIC)
            c = tone(bg); ov(c, t); fr = c.convert("RGB")
            if last is not None and t < 0.25: fr = Image.blend(last, fr, t / 0.25)
            proc.stdin.write(fr.tobytes()); cur = fr
        last = cur
    proc.stdin.close(); proc.wait(); return out

# ---------- stories ----------
def event_card(label, color, time, venue, access, extra=None):
    w, h = 920, 330
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w - 1, h - 1), 34, fill=(255, 255, 255, 245))
    d.rounded_rectangle((0, 0, w - 1, 96), 34, fill=color); d.rectangle((0, 60, w - 1, 96), fill=color)
    im.alpha_composite(text_img(label, F(BLACK, 58), WHITE), (34, 6))
    im.alpha_composite(cal_icon(52, NAVY), (36, 118)); im.alpha_composite(text_img(time, F(BLACK, 52), NAVY), (102, 108))
    im.alpha_composite(pin_icon(50, NAVY), (37, 190)); im.alpha_composite(text_img(venue, F(BLACK, 52), NAVY), (102, 180))
    sub = access + (f"｜{extra}" if extra else "")
    im.alpha_composite(text_img(sub, F(BOLD, 34), (70, 90, 120)), (102, 258))
    return shadowed(im)

def story1():
    bg = Image.open(os.path.join(D, "photos", "IMG_3754.jpg")).convert("RGB")
    r = max(W / bg.width, H / bg.height); bg = bg.resize((int(bg.width * r), int(bg.height * r)), Image.LANCZOS)
    bg = bg.crop(((bg.width - W) // 2, (bg.height - H) // 2, (bg.width - W) // 2 + W, (bg.height - H) // 2 + H)).filter(ImageFilter.GaussianBlur(8))
    c = tone(bg, 0.35)
    place(c, HL_TODAY, W / 2, 220)
    place(c, shadowed(pill([text_img("11/1(日)", F(BLACK, 60), NAVY)])), W / 2, 540)
    place(c, event_card("バレーボール", (243, 128, 32), "18:00-21:00", "巣鴨体育館", "JR巣鴨駅・大塚駅から徒歩約10分"), W / 2, 680)
    place(c, event_card("バドミントン", (46, 150, 70), "19:00-22:00", "目黒区民センター", "JR・東急 目黒駅から徒歩10分", "ラケット貸出あり"), W / 2, 1030)
    place(c, YB, W / 2, 1390)
    t = text_img("申し込みはこちら ↓", F(BLACK, 50), WHITE, stroke=4, stroke_fill=NAVY)
    place(c, t, W / 2, 1590)
    p = os.path.join(OUTD, "1101_ストーリーズ1_朝8時.png"); c.convert("RGB").save(p, quality=95); return p

def story2():
    c = Image.new("RGBA", (W, H)); d = ImageDraw.Draw(c)
    for y in range(H): d.line([(0, y), (W, y)], fill=(11 + int(10 * y / H), 23 + int(16 * y / H), 51 + int(34 * y / H)))
    hl = shadowed(headline("11月は", "全12回開催！", seed=6, size=120)); place(c, hl, W / 2, 200)
    cal = Image.open(os.path.join(D, "cal", "cal11_fixed.png")).convert("RGBA").resize((680, 1020), Image.LANCZOS)
    m = Image.new("L", cal.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, cal.width, cal.height), 26, fill=255); cal.putalpha(m)
    fr = Image.new("RGBA", (cal.width + 16, cal.height + 16), (0, 0, 0, 0)); ImageDraw.Draw(fr).rounded_rectangle((0, 0, fr.width - 1, fr.height - 1), 32, fill=WHITE)
    fr.alpha_composite(cal, (8, 8)); place(c, shadowed(fr), W / 2, 450)
    place(c, shadowed(yellow_band("保存して予定に入れよう", size=78)), W / 2, 1480)
    t = text_img("申し込みはこちら ↓", F(BLACK, 50), WHITE, stroke=4, stroke_fill=NAVY); place(c, t, W / 2, 1680)
    p = os.path.join(OUTD, "1101_ストーリーズ2_夜20時.png"); c.convert("RGB").save(p, quality=95); return p

if __name__ == "__main__":
    print(story1(), story2())
