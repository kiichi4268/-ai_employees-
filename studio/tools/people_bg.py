"""背景を「人がプレーしている実写」にする部品（11/14 加藤さん「背景をやっている人に」）。

写真は 1080×1920 に合わせてから全体をぼかし、顔が分からない形にして make_week1 の SRC に入れる（CLEAR_BG 扱い＝追加のぼかしは弱め）。
過去の写真なので、画像・動画の下に「※写真は過去の開催時のものです」を入れる（add_note_img / add_note_video）。
"""
import os, subprocess
from PIL import Image, ImageOps, ImageFilter, ImageDraw

D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PHOTOS = {  # キー: (ファイル, ぼかし)。顔が近い写真ほど強く
    "play_bad": ("IMG_3754.jpg", 7), "play_gym": ("IMG_3560.jpg", 6), "play_bb": ("S__66338826_0.jpg", 7),
    "play_vb": ("vb_play.jpg", 10), "play_vb2": ("vb_sugamo_people.jpg", 8),
    # 11/14 加藤さん「ボケはそんなに必要ない。顔が見えない形で」→ 顔だけモザイク（tools/anonymize.py・手で全員の頭を確認）・写真はくっきり
    "b14_wide": ("anon_b1114_IMG_4801.jpg", 0), "b14_court": ("anon_b1114_IMG_4807.jpg", 0),
}
NOTE = "※写真は過去の開催時のものです"
FONT = os.path.join(D, "fonts", "NotoSansCJK-Bold.ttc")


BG = os.path.join(os.path.dirname(D), "content", "instagram", "media", "bg")  # 顔の処理済み（ぼかし・顔だけモザイク）。新しい作業場でも使える（11/15）


def processed(key):
    """元の写真が作業場に無いとき（毎回新しい会話の予約）は、処理済みの content/instagram/media/bg/{key}.jpg を使う。"""
    p = os.path.join(BG, key + ".jpg")
    return ImageOps.exif_transpose(Image.open(p)).convert("RGB") if os.path.exists(p) else None


def register(w1):
    for key, (fn, r) in PHOTOS.items():
        p = os.path.join(D, "photos", fn)
        if os.path.exists(p):
            im = ImageOps.exif_transpose(Image.open(p)).convert("RGB")
            im = w1.cover(im).filter(ImageFilter.GaussianBlur(r))
        else:
            im = processed(key)
            if im is None: continue
            im = w1.cover(im)
        w1.SRC[key] = im; w1.CLEAR_BG.add(key)


def add_note_img(path, y=1745):
    from PIL import ImageFont
    im = Image.open(path).convert("RGB"); d = ImageDraw.Draw(im); f = ImageFont.truetype(FONT, 30)
    w = d.textlength(NOTE, font=f); d.text(((im.width - w) / 2, y), NOTE, font=f, fill=(255, 255, 255), stroke_width=3, stroke_fill=(20, 42, 92))
    im.save(path, quality=93)


def add_note_video(path, y=1745):
    tmp = path + ".note.mp4"
    vf = f"drawtext=fontfile={FONT}:text='{NOTE}':fontsize=30:fontcolor=white:borderw=3:bordercolor=0x142a5c:x=(w-text_w)/2:y={y}"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", path, "-vf", vf, "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
                    "-pix_fmt", "yuv420p", "-c:a", "copy", "-movflags", "+faststart", tmp], check=True)
    os.replace(tmp, path)
