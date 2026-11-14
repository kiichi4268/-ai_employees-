"""ストーリーの見た目 v2（11/14 加藤さん「背景が貧相。他のスポーツイベントのInstagramを参考に」）。

見本アカウントの作り方（STORY_MODEL.md）から：
- 写真を画面いっぱいに（上下分割をやめる）。下を暗くして、太い大きな文字を重ねる。
- 情報（日付・会場・参加費）は小さな「札（チップ）」に分けて並べる。
- 写真を何枚か重ねたコラージュ、動画は何枚かの写真を短く切り替える（1枚に止まらない）。
写真は people_bg で顔が分からないぼかし済みのもの（make_week1.SRC）を使う。過去の写真には注記を入れる。
"""
import math
import subprocess
from PIL import Image, ImageDraw, ImageFilter

import make_week1 as w1
from make_1101 import BLACK, BOLD, F, text_img
from tools.craft import finish, tilt

W, H = 1080, 1920
NAVY = (20, 42, 92); YEL = (255, 236, 30); WHITE = (255, 255, 255); INK = (18, 22, 34)
NOTE = "※写真は過去の開催時のものです"


def _cover(im, w=W, h=H, zoom=1.0, fx=0.5, fy=0.5):
    r = max(w / im.width, h / im.height) * zoom
    im = im.resize((int(im.width * r) + 1, int(im.height * r) + 1), Image.LANCZOS)
    x0 = int((im.width - w) * fx); y0 = int((im.height - h) * fy)
    return im.crop((x0, y0, x0 + w, y0 + h))


def _shade(c, top=0.15, bottom=0.82, start=0.38):
    g = Image.new("L", (1, H))
    for y in range(H):
        t = max(0.0, (y / H - start) / (1 - start))
        g.putpixel((0, y), int(255 * (top + (bottom - top) * min(1, t ** 1.2))))
    g = g.resize((W, H))
    dark = Image.new("RGBA", (W, H), (8, 14, 30, 255)); dark.putalpha(g)
    return Image.alpha_composite(c.convert("RGBA"), dark)


def chip(text, bg=WHITE, fg=INK, size=40, pad=(26, 14)):
    t = text_img(text, F(BLACK, size), fg)
    im = Image.new("RGBA", (t.width + pad[0] * 2, t.height + pad[1] * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(im); d.rounded_rectangle((0, 0, im.width - 1, im.height - 1), radius=im.height // 2, fill=bg + (255,))
    im.alpha_composite(t, (pad[0], pad[1])); return im


def _brand(c):
    """11/14 夜の改善 D-1115（調べる担当）：上 約250px はアプリの表示で隠れるのでロゴはやめ、
    左上のアカウント名を指す矢印と「タップで日程」の札を安全地帯（y≈270）に置く。プロフィールアクセスを上げる。"""
    d = ImageDraw.Draw(c)
    d.line((92, 262, 92, 196), fill=YEL, width=7); d.polygon([(92, 176), (74, 206), (110, 206)], fill=YEL)
    k = chip("@macachette_sports をタップで 日程一覧", bg=WHITE, fg=INK, size=34)
    c.alpha_composite(k, (64, 270))


def _note(c, y=1838):
    d = ImageDraw.Draw(c); f = F(BOLD, 28)
    d.text((64, y), NOTE, font=f, fill=(235, 235, 235), stroke_width=2, stroke_fill=(10, 16, 30))


def full_bleed(key, kicker, lines, chips, accent=YEL, mark=None, seed=1, note=True, fx=0.5):
    """写真を画面いっぱいに。下に太い大きな見出し（mark の言葉だけ黄色の帯）、その下に情報の札。"""
    c = _shade(_cover(w1.SRC[key], fx=fx))
    _brand(c)
    y = 1010
    k = chip(kicker, bg=accent, fg=INK, size=38); c.alpha_composite(tilt(k, -2), (58, y)); y += k.height + 34
    sz = 116
    while sz > 80 and max(text_img(ln, F(BLACK, sz), WHITE).width for ln in lines) > W - 150: sz -= 4  # 端にかからないように縮める（11/14 夜）
    for ln in lines:
        t = text_img(ln, F(BLACK, sz), WHITE)
        if mark and mark in ln:  # 強調の言葉の下に黄色の帯
            band = Image.new("RGBA", (t.width + 20, int(t.height * 0.36)), YEL + (230,))
            c.alpha_composite(band, (54, y + int(t.height * 0.62)))
        c.alpha_composite(t, (64, y)); y += t.height + 6
    y += 30; x = 64
    for i, tx in enumerate(chips):
        ch = chip(tx, bg=WHITE if i else (255, 255, 255), size=36)
        if x + ch.width > W - 50: x = 64; y += ch.height + 14
        c.alpha_composite(ch, (x, y)); x += ch.width + 14
    if note: _note(c)
    return finish(c.convert("RGB"), seed=seed)


def collage(keys, kicker, lines, chips, accent=YEL, seed=2, note=True):
    """写真3枚を少し傾けて重ねる（写真の束）。上に見出し、下に札。"""
    bg = _cover(w1.SRC[keys[0]]).filter(ImageFilter.GaussianBlur(18))
    c = Image.blend(bg, Image.new("RGB", (W, H), NAVY), 0.55).convert("RGBA")
    _brand(c)
    y = 360  # 上の「タップで日程一覧」の札の下から（11/14 夜）
    k = chip(kicker, bg=accent, fg=INK, size=36); c.alpha_composite(tilt(k, -2), (58, y)); y += k.height + 18
    for ln in lines:
        t = text_img(ln, F(BLACK, 88), WHITE); c.alpha_composite(t, (64, y)); y += t.height + 2
    spots = [(70, 700, -6), (330, 880, 5), (110, 1120, -3)]
    for key, (x, yy, ang) in zip(keys, spots):
        ph = _cover(w1.SRC[key], 680, 460)
        fr = Image.new("RGBA", (ph.width + 28, ph.height + 28), (250, 250, 248, 255)); fr.paste(ph, (14, 14))
        fr = fr.rotate(ang, expand=True, resample=Image.BICUBIC)
        sh = Image.new("RGBA", fr.size, (0, 0, 0, 0)); sh.putalpha(fr.split()[3].point(lambda a: int(a * 0.45)))
        c.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10)), (x + 14, yy + 18)); c.alpha_composite(fr, (x, yy))
    y = 1650; x = 64
    for tx in chips:
        ch = chip(tx, size=36)
        if x + ch.width > W - 50: x = 64; y += ch.height + 12
        c.alpha_composite(ch, (x, y)); x += ch.width + 14
    if note: _note(c, y=1860)
    return finish(c.convert("RGB"), seed=seed)


def montage(keys, path, title, lines, dur_each=1.9, fps=30, note=True):
    """何枚かの写真を短く切り替える動画（ゆっくり寄る＋0.35秒の切り替え）。文字は上に1つ、下に2行まで。"""
    head = w1.fit(w1.shadowed(w1.headline(title, "", seed=4, size=110)))
    subs = [w1.fit(w1.shadowed(w1.pill([text_img(t, F(BLACK, 54), NAVY)], h=104))) for t in lines]
    n = len(keys); total = dur_each * n; frames = int(total * fps); xf = 0.35
    imgs = [w1.SRC[k] for k in keys]
    proc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(fps), "-i", "-",
                             "-c:v", "libx264", "-preset", "veryfast", "-crf", "22", "-pix_fmt", "yuv420p", "-movflags", "+faststart", path],
                            stdin=subprocess.PIPE)
    small = {}
    for f in range(frames):
        t = f / fps; i = min(int(t // dur_each), n - 1); lt = t - i * dur_each
        def frame(j, lt_):
            z = 1.04 + 0.08 * (lt_ / dur_each); fx = 0.5 + 0.08 * math.sin(j * 1.7)
            key = (j, round(z, 3))
            if key not in small: small[key] = _cover(imgs[j].resize((540, 960)), 540, 960, zoom=z, fx=fx).resize((W, H), Image.BILINEAR)
            return small[key]
        c = frame(i, lt)
        if i + 1 < n and lt > dur_each - xf:
            a = (lt - (dur_each - xf)) / xf; c = Image.blend(c, frame(i + 1, 0), a)
        c = _shade(c, top=0.25, bottom=0.6, start=0.0)
        a1 = min(1, t / 0.4); w1.place(c, head, W / 2, 300, a1)
        for k, s in enumerate(subs):
            w1.place(c, s, W / 2, 1180 + k * 140, min(1, max(0, (t - 0.8 - 0.5 * k) / 0.4)))
        w1.foot(c)
        if note: _note(c, y=1760)
        proc.stdin.write(c.convert("RGB").tobytes())
    proc.stdin.close(); proc.wait()
    return path
