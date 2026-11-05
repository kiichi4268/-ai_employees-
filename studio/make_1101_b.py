"""11/1 当日募集リール 別バージョン（Match Day型・問いかけフック）"""
import subprocess, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from make_1101 import (W, H, FPS, BLACK, BOLD, TEAL, YEL, NAVY, WHITE, F, text_img, cal_icon, pin_icon,
                       pill, shadowed, place, clip_frames, photo_bg, photo_frame, tone, appear, A, B, D, OUTD, brush)

def shear(im, k=-0.18):
    w, h = im.size; nw = int(w + abs(k) * h)
    return im.transform((nw, h), Image.AFFINE, (1, k, (k * h if k < 0 else 0), 0, 1, 0), Image.BICUBIC)

def title(word):
    a = shear(text_img(word, F(BLACK, 170), YEL, stroke=10, stroke_fill=(15, 15, 15)))
    b = shear(text_img("Match Day", F(BLACK, 150), WHITE, stroke=10, stroke_fill=(15, 15, 15)), -0.28)
    im = Image.new("RGBA", (max(a.width, b.width + 80), a.height + b.height - 30), (0, 0, 0, 0))
    im.alpha_composite(a, (0, 0)); im.alpha_composite(b, (80, a.height - 30))
    return shadowed(im.rotate(4, expand=True, resample=Image.BICUBIC))

def date_bar(date, time):
    t = text_img(f"{date}｜{time}", F(BLACK, 76), WHITE)
    w, h = t.width + 90, 150
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w - 1, h - 1), 75, fill=TEAL)
    im.alpha_composite(t, (45, (h - t.height) // 2)); return shadowed(im)

def venue_line(venue, access):
    v = text_img(venue, F(BLACK, 72), WHITE, stroke=6, stroke_fill=(15, 15, 15))
    a = text_img(access, F(BOLD, 40), WHITE, stroke=4, stroke_fill=(15, 15, 15))
    p = pin_icon(70, YEL)
    w = max(p.width + 16 + v.width, a.width) + 20
    im = Image.new("RGBA", (w, v.height + a.height + 40), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    x0 = (w - (p.width + 16 + v.width)) // 2
    im.alpha_composite(p, (x0, 10)); im.alpha_composite(v, (x0 + p.width + 16, 0))
    d.line((x0 + p.width + 16, v.height + 4, x0 + p.width + 16 + v.width, v.height + 4), fill=YEL, width=8)
    im.alpha_composite(a, ((w - a.width) // 2, v.height + 26)); return shadowed(im)

def feature_boxes(items):
    bw, bh, gap = 300, 150, 24
    im = Image.new("RGBA", (bw * 3 + gap * 2, bh), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for i, txt in enumerate(items):
        x = i * (bw + gap)
        d.rounded_rectangle((x, 0, x + bw - 1, bh - 1), 22, fill=(18, 18, 18, 235), outline=WHITE, width=4)
        lines = txt.split("\n"); fs = 44 if len(lines) == 1 else 38
        ts = [text_img(l, F(BLACK, fs), WHITE) for l in lines]
        th = sum(t.height for t in ts) - 10 * (len(ts) - 1); y = (bh - th) // 2
        for t in ts:
            im.alpha_composite(t, (x + (bw - t.width) // 2, y)); y += t.height - 10
    return shadowed(im)

def badge(l1, l2):
    s = 230; im = Image.new("RGBA", (s, s), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.ellipse((0, 0, s - 1, s - 1), fill=TEAL, outline=WHITE, width=8)
    a = text_img(l1, F(BLACK, 54), WHITE); b = text_img(l2, F(BLACK, 46), WHITE)
    im.alpha_composite(a, ((s - a.width) // 2, 52)); im.alpha_composite(b, ((s - b.width) // 2, 116))
    return shadowed(im)

def hook_text():
    a = text_img("日曜の夜、", F(BLACK, 120), WHITE, stroke=8, stroke_fill=(15, 15, 15))
    b = shear(text_img("ヒマしてない？", F(BLACK, 150), YEL, stroke=10, stroke_fill=(15, 15, 15)))
    im = Image.new("RGBA", (max(a.width, b.width), a.height + b.height), (0, 0, 0, 0))
    im.alpha_composite(a, ((im.width - a.width) // 2, 0)); im.alpha_composite(b, ((im.width - b.width) // 2, a.height - 10))
    return shadowed(im)

def fit(im, maxw=W - 70):
    if im.width <= maxw: return im
    r = maxw / im.width
    return im.resize((int(im.width * r), int(im.height * r)), Image.LANCZOS)

HOOK = fit(hook_text())
HOOK_SUB = shadowed(pill([text_img("今日、2つ開催します🏐🏸".replace("🏐🏸", ""), F(BLACK, 56), NAVY)]))
T_VOL, T_BAD = fit(title("Volleyball")), fit(title("Badminton"))
DB_VOL, DB_BAD = date_bar("11/1(日)", "18:00-21:00"), date_bar("11/1(日)", "19:00-22:00")
VN_VOL = venue_line("巣鴨体育館", "JR巣鴨駅・大塚駅から徒歩約10分")
VN_BAD = venue_line("目黒区民センター", "JR・東急 目黒駅から徒歩10分")
FB_VOL = feature_boxes(["初心者歓迎", "エンジョイ\n志向", "室内シューズ\n持参"])
FB_BAD = feature_boxes(["初心者歓迎", "ラケット\n貸出あり", "室内シューズ\n持参"])
BADGE = badge("ひとり", "参加OK")
END1 = shadowed(shear(text_img("どちらも", F(BLACK, 90), WHITE, stroke=8, stroke_fill=(15, 15, 15)), -0.1))
END2 = fit(shadowed(shear(text_img("まだ間に合う！", F(BLACK, 150), YEL, stroke=10, stroke_fill=(15, 15, 15)))))
FEE = shadowed(pill([text_img("参加費 各1,500円｜当日 現金・PayPay", F(BLACK, 46), NAVY)], h=96))
CTA = shadowed(pill([text_img("申し込みはプロフィールのリンクから", F(BLACK, 48), WHITE)], h=104, bg=TEAL))
HANDLE = shadowed(pill([text_img("@macachette_sports", F(BOLD, 44), WHITE)], h=92, bg=NAVY))

def flash(c, t, dur=0.12):
    if t < dur:
        a = int(200 * (1 - t / dur)); c.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, a)))

def pop(c, im, cx, y, t, start):
    p = appear(t, start, 0.22)
    if p <= 0: return
    s = 0.6 + 0.4 * min(1.0, p * 1.25) - (0.05 * max(0, p * 1.25 - 1)) * 4 if p < 1 else 1.0
    s = max(0.6, s)
    im2 = im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.BICUBIC)
    if p < 1: im2.putalpha(im2.split()[3].point(lambda v: int(v * min(1, p * 2))))
    c.alpha_composite(im2, (int(cx - im2.width / 2), int(y + (im.height - im2.height) / 2)))

def main():
    fa = clip_frames(A, 12, 2.6); fb = clip_frames(B, 24, 4.4); fa2 = clip_frames(A, 36, 3.6)
    gym = photo_bg(os.path.join(D, "photos", "IMG_3560.jpg"), blur=6, focus=(0.5, 0.55))
    def info(c, t, T, DB, VN, FB):
        pop(c, T, W / 2, 170, t, 0.0)
        pop(c, DB, W / 2, 820, t, 0.45)
        place(c, VN, W / 2, 1010, appear(t, 0.75))
        place(c, FB, W / 2, 1300, appear(t, 1.05))
        pop(c, BADGE, W - 190, 1560, t, 1.35)
    segs = [
        (2.6, lambda k, t: fa[min(k, len(fa) - 1)], lambda c, t: (
            pop(c, HOOK, W / 2, 560, t, 0.05), place(c, HOOK_SUB, W / 2, 1000, appear(t, 0.7)))),
        (4.4, lambda k, t: photo_frame(gym, t / 4.4), lambda c, t: info(c, t, T_VOL, DB_VOL, VN_VOL, FB_VOL)),
        (4.4, lambda k, t: fb[min(k, len(fb) - 1)], lambda c, t: info(c, t, T_BAD, DB_BAD, VN_BAD, FB_BAD)),
        (3.6, lambda k, t: fa2[min(k, len(fa2) - 1)], lambda c, t: (
            place(c, END1, W / 2, 400, appear(t, 0.0)), pop(c, END2, W / 2, 520, t, 0.2),
            place(c, FEE, W / 2, 900, appear(t, 0.6)), place(c, CTA, W / 2, 1060, appear(t, 0.9)),
            place(c, HANDLE, W / 2, 1240, appear(t, 1.1)))),
    ]
    out = os.path.join(OUTD, "1101_当日募集リール_バレー×バド_B案.mp4")
    proc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                             "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p",
                             "-movflags", "+faststart", out], stdin=subprocess.PIPE)
    for d, bgf, ov in segs:
        for k in range(int(d * FPS)):
            t = k / FPS; bg = bgf(k, t)
            if bg.size != (W, H): bg = bg.resize((W, H), Image.BICUBIC)
            c = tone(bg, 0.32); ov(c, t); flash(c, t)
            proc.stdin.write(c.convert("RGB").tobytes())
    proc.stdin.close(); proc.wait(); print(out)

if __name__ == "__main__":
    main()
