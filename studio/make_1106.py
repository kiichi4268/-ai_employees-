"""11/6(金) リール「1人参加Q&A（新規向け）」約22秒・音楽なし（設計書「投稿企画」のQ&A型）
最後に「来週末 11/14・15 はバド2連続」。背景はイベント動画を強くぼかしたもの（人が誰か分からないように）。"""
import os, subprocess
from PIL import Image, ImageDraw, ImageOps
from make_1101 import (W, H, FPS, BLACK, BOLD, TEAL, YEL, NAVY, WHITE, F, text_img, pill, shadowed, place,
                       headline, yellow_band, white_band, appear, tone, clip_frames, event_card, A, B, D, OUTD)

LINE_GREEN = (6, 199, 85)


def fit(im, maxw=W - 80):
    if im.width <= maxw: return im
    r = maxw / im.width
    return im.resize((int(im.width * r), int(im.height * r)), Image.LANCZOS)


def q_pill(q):
    return fit(shadowed(pill([text_img("Q.", F(BLACK, 64), YEL), text_img(q, F(BLACK, 62), WHITE)], h=128, bg=NAVY)))


def a_band(a, size=88, seed=7):
    return fit(shadowed(yellow_band(a, size=size, seed=seed)))


def receipt_card():
    im = ImageOps.exif_transpose(Image.open(os.path.join(D, "mat", "receipt.jpg"))).convert("RGBA")
    im = im.resize((340, int(im.height * 340 / im.width)), Image.LANCZOS)
    fr = Image.new("RGBA", (im.width + 20, im.height + 20), (0, 0, 0, 0))
    ImageDraw.Draw(fr).rounded_rectangle((0, 0, fr.width - 1, fr.height - 1), 24, fill=WHITE)
    fr.alpha_composite(im, (10, 10))
    return shadowed(fr.rotate(-4, expand=True, resample=Image.BICUBIC))


HOOK1 = fit(shadowed(text_img("社会人スポーツ、", F(BLACK, 96), WHITE, stroke=8, stroke_fill=(15, 15, 15))))
HOOK2 = a_band("1人で行っても大丈夫？", size=100, seed=3)
HOOK3 = fit(shadowed(pill([text_img("はじめての方によく聞かれる4つに答えます", F(BLACK, 44), NAVY)], h=96)))

Q1, A1 = q_pill("1人で浮かない？"), a_band("参加者のほとんどが1人参加")
Q2, A2 = q_pill("運動不足でも平気？"), a_band("初心者7割・経験者3割くらい", seed=8)
A2B = fit(shadowed(white_band("上手さより楽しさ重視", size=64)))
Q3, A3 = q_pill("当日どうすればいい？"), a_band("受付で参加受付証を見せるだけ", seed=9)
A3B = fit(shadowed(pill([text_img("参加費 1,500円｜当日 現金・PayPay", F(BLACK, 46), NAVY)], h=92)))
RECEIPT = receipt_card()
Q4, A4 = q_pill("何を持っていく？"), a_band("着替え・体育館シューズ・飲み物", size=78, seed=10)
A4B = fit(shadowed(pill([text_img("バドミントン・卓球はラケット貸出あり", F(BLACK, 46), NAVY)], h=96, bg=YEL)))

NEXT_HEAD = fit(shadowed(headline("来週末は", "バド2連続！", seed=5, size=120)))
EV1 = fit(event_card("11/14(土) バドミントン", (46, 150, 70), "15:00-17:00", "まもり山テラス", "ラケット貸出あり"))
EV2 = fit(event_card("11/15(日) バドミントン", (46, 150, 70), "13:00-15:00", "代々木の杜", "JR代々木駅から徒歩5分", "ラケット貸出あり"))
CTA = fit(shadowed(pill([text_img("LINEで『初参加ガイド』を受け取ろう", F(BLACK, 48), WHITE)], h=104, bg=LINE_GREEN)))
SUB_CTA = fit(shadowed(pill([text_img("プロフィールのリンクから｜保存してね", F(BOLD, 40), WHITE)], h=84, bg=(20, 42, 92, 230))))


def qa(c, t, q, a, extra=None):
    place(c, q, W / 2, 380, appear(t, 0.0), slide=-300)
    place(c, a, W / 2, 620, appear(t, 0.7), slide=300)
    if extra: extra(c, t)


def main():
    s0 = clip_frames(A, 5, 2.8); s1 = clip_frames(B, 12, 4.0); s2 = clip_frames(A, 25, 4.0)
    s3 = clip_frames(B, 35, 4.0); s4 = clip_frames(A, 45, 3.6); s5 = clip_frames(B, 50, 4.6)
    pick = lambda fr: (lambda k: fr[min(k, len(fr) - 1)])
    segs = [
        (2.8, pick(s0), lambda c, t: (place(c, HOOK1, W / 2, 470, appear(t, 0.0), slide=-300),
                                      place(c, HOOK2, W / 2, 620, appear(t, 0.35), slide=300),
                                      place(c, HOOK3, W / 2, 900, appear(t, 0.9)))),
        (4.0, pick(s1), lambda c, t: qa(c, t, Q1, A1)),
        (4.0, pick(s2), lambda c, t: qa(c, t, Q2, A2, lambda c, t: place(c, A2B, W / 2, 860, appear(t, 1.3)))),
        (4.0, pick(s3), lambda c, t: qa(c, t, Q3, A3, lambda c, t: (place(c, RECEIPT, W / 2, 860, appear(t, 1.2)),
                                                                     place(c, A3B, W / 2, 1520, appear(t, 1.8))))),
        (3.6, pick(s4), lambda c, t: qa(c, t, Q4, A4, lambda c, t: place(c, A4B, W / 2, 860, appear(t, 1.2)))),
        (4.6, pick(s5), lambda c, t: (place(c, NEXT_HEAD, W / 2, 300, appear(t, 0.0), slide=-300),
                                      place(c, EV1, W / 2, 620, appear(t, 0.4)),
                                      place(c, EV2, W / 2, 960, appear(t, 0.7)),
                                      place(c, CTA, W / 2, 1330, appear(t, 1.3)),
                                      place(c, SUB_CTA, W / 2, 1470, appear(t, 1.6)))),
    ]
    out = os.path.join(OUTD, "1106_リール_1人参加QA.mp4")
    proc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                             "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", "-movflags", "+faststart", out],
                            stdin=subprocess.PIPE)
    last = None
    for d, bgf, ov in segs:
        for k in range(int(d * FPS)):
            t = k / FPS; bg = bgf(k)
            if bg.size != (W, H): bg = bg.resize((W, H), Image.BICUBIC)
            c = tone(bg, 0.32); ov(c, t); fr = c.convert("RGB")
            if last is not None and t < .25: fr = Image.blend(last, fr, t / .25)
            proc.stdin.write(fr.tobytes()); cur = fr
        last = cur
    proc.stdin.close(); proc.wait(); print(out)


if __name__ == "__main__":
    main()
