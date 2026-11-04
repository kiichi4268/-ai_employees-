"""11/2 前日リール：11/3 卓球（A案の型・15秒・音楽なし）"""
import os, subprocess
from PIL import Image, ImageFilter
from make_1101 import (W, H, FPS, BLACK, BOLD, TEAL, YEL, NAVY, WHITE, F, text_img, cal_icon, pin_icon, pill, shadowed,
                       place, headline, yellow_band, white_band, appear, tone, clip_frames, A, D, OUTD)
from make_week1 import SRC, cover

def kb(key, dur, focus, blur=0, z0=1.0, z1=1.08):
    im = cover(SRC[key], scale=1.15)
    if blur: im = im.filter(ImageFilter.GaussianBlur(blur))
    out = []; n = int(dur * FPS)
    for k in range(n):
        z = z0 + (z1 - z0) * k / n
        cw, ch = im.width / 1.15 / z, im.height / 1.15 / z
        x0 = min(max(focus[0] * im.width - cw / 2, 0), im.width - cw); y0 = min(max(focus[1] * im.height - ch / 2, 0), im.height - ch)
        out.append(im.crop((int(x0), int(y0), int(x0 + cw), int(y0 + ch))).resize((W, H), Image.BILINEAR))
    return out

HL = shadowed(headline("明日", "開催！", seed=3, size=170))
SUB = shadowed(pill([text_img("11/3(火・祝)  卓球", F(BLACK, 58), NAVY)]))
HL_TT = shadowed(headline("卓球", "交流会", seed=5, size=150))
INFO = [shadowed(pill([cal_icon(64, NAVY), text_img("11/3(火・祝) 12:20-15:20", F(BLACK, 54), NAVY)])),
        shadowed(pill([pin_icon(60, NAVY), text_img("大久保プラザ", F(BLACK, 54), NAVY)])),
        shadowed(pill([text_img("大久保駅・新大久保駅すぐ", F(BOLD, 38), WHITE)], h=74, bg=(20, 42, 92, 225)))]
YB = shadowed(yellow_band("まだ参加枠あります"))
WB = shadowed(white_band("初心者さん・ひとり参加大歓迎"))
HAND = shadowed(yellow_band("手ぶらでOK", size=110, seed=8))
RAK = shadowed(pill([text_img("ラケット貸出あり", F(BLACK, 56), NAVY)], h=104))
FEE = shadowed(pill([text_img("参加費 1,500円｜当日 現金・PayPay", F(BLACK, 46), NAVY)], h=92))
CTA = shadowed(pill([text_img("申し込みはプロフィールから公式LINEへ", F(BLACK, 44), WHITE)], h=96, bg=TEAL))
HANDLE = shadowed(pill([text_img("@macachette_sports", F(BOLD, 44), WHITE)], h=92, bg=NAVY))

def main():
    s1 = kb("tt", 3.4, (0.5, 0.55), blur=2); s2 = kb("gym", 3.9, (0.5, 0.55), blur=7)
    s3 = kb("tt", 3.9, (0.62, 0.62), blur=2, z0=1.12, z1=1.2); s4 = clip_frames(A, 40, 3.8)
    segs = [
        (3.4, lambda k: s1[k], lambda c, t: (place(c, HL, W / 2, 230, appear(t, 0), slide=-300), place(c, SUB, W / 2, 560, appear(t, .35)),
                                             place(c, YB, W / 2, 1180, appear(t, .8), slide=300), place(c, WB, W / 2, 1400, appear(t, 1.1)))),
        (3.9, lambda k: s2[k], lambda c, t: (place(c, HL_TT, W / 2, 260, appear(t, 0), slide=-300),
                                             [place(c, p, W / 2, 640 + i * 150, appear(t, .35 + i * .25)) for i, p in enumerate(INFO)])),
        (3.9, lambda k: s3[k], lambda c, t: (place(c, HAND, W / 2, 300, appear(t, 0), slide=-300), place(c, RAK, W / 2, 560, appear(t, .4)),
                                             place(c, WB, W / 2, 1360, appear(t, .8)))),
        (3.8, lambda k: s4[min(k, len(s4) - 1)], lambda c, t: (place(c, YB, W / 2, 360, appear(t, 0), slide=-300), place(c, FEE, W / 2, 680, appear(t, .4)),
                                                               place(c, CTA, W / 2, 860, appear(t, .7)), place(c, HANDLE, W / 2, 1040, appear(t, 1.0)))),
    ]
    out = os.path.join(OUTD, "1102_前日リール_1103卓球.mp4")
    proc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                             "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", "-movflags", "+faststart", out], stdin=subprocess.PIPE)
    last = None
    for d, bgf, ov in segs:
        for k in range(int(d * FPS)):
            t = k / FPS; bg = bgf(k)
            if bg.size != (W, H): bg = bg.resize((W, H), Image.BICUBIC)
            c = tone(bg, 0.28); ov(c, t); fr = c.convert("RGB")
            if last is not None and t < .25: fr = Image.blend(last, fr, t / .25)
            proc.stdin.write(fr.tobytes()); cur = fr
        last = cur
    proc.stdin.close(); proc.wait(); print(out)

if __name__ == "__main__":
    main()
