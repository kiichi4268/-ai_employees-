"""11月スケジュール リール（実写・顔ぼかし・参加方法なし）"""
import subprocess, os
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps

D = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(D, "out", "1031_11月スケジュール_リール_v3.mp4")
W, H, FPS = 1080, 1920, 30
BLACK = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts", "NotoSansCJK-Black.ttc")
BOLD = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts", "NotoSansCJK-Bold.ttc")
FRONT = cv2.CascadeClassifier(os.path.join(D, "models", "haar.xml"))
PROF = cv2.CascadeClassifier(os.path.join(D, "models", "haar_profile.xml"))

# ---------- face hiding ----------
def detect(img_rgb, min_px=14):
    g = cv2.cvtColor(np.array(img_rgb), cv2.COLOR_RGB2GRAY)
    g = cv2.equalizeHist(g)
    boxes = []
    for c in (FRONT, PROF):
        for (x, y, w, h) in c.detectMultiScale(g, 1.08, 4, minSize=(min_px, min_px)):
            boxes.append((x, y, w, h))
    gf = cv2.flip(g, 1)
    for (x, y, w, h) in PROF.detectMultiScale(gf, 1.08, 4, minSize=(min_px, min_px)):
        boxes.append((g.shape[1] - x - w, y, w, h))
    return boxes

def pixelate(img, boxes, pad=0.45):
    img = img.copy()
    for (x, y, w, h) in boxes:
        x0, y0 = int(x - w * pad), int(y - h * pad)
        x1, y1 = int(x + w * (1 + pad)), int(y + h * (1 + pad))
        x0, y0 = max(0, x0), max(0, y0); x1, y1 = min(img.width, x1), min(img.height, y1)
        if x1 - x0 < 2 or y1 - y0 < 2: continue
        reg = img.crop((x0, y0, x1, y1))
        n = max(2, (x1 - x0) // 10)
        reg = reg.resize((max(1, (x1 - x0) // n), max(1, (y1 - y0) // n)), Image.BILINEAR).resize((x1 - x0, y1 - y0), Image.NEAREST)
        img.paste(reg, (x0, y0))
    return img

# ---------- sources ----------
class Photo:
    def __init__(self, img, extra_boxes=(), focus=(0.5, 0.5), blur=0):
        img = ImageOps.exif_transpose(img).convert("RGB")
        img = pixelate(img, list(extra_boxes), pad=0.35)
        r = max(W * 1.1 / img.width, H * 1.1 / img.height)
        self.im = img.resize((int(img.width * r), int(img.height * r)), Image.LANCZOS)
        if blur: self.im = self.im.filter(ImageFilter.GaussianBlur(blur))
        self.focus = focus
    def frame(self, t, d):
        im = self.im; z = 1 + 0.06 * (t / d)
        cw, ch = W * 1.1 / z, H * 1.1 / z
        cw, ch = min(cw * im.width / (W * 1.1), im.width), min(ch * im.height / (H * 1.1), im.height)
        cx, cy = self.focus[0] * im.width, self.focus[1] * im.height
        x0 = min(max(cx - cw / 2, 0), im.width - cw); y0 = min(max(cy - ch / 2, 0), im.height - ch)
        return im.crop((int(x0), int(y0), int(x0 + cw), int(y0 + ch))).resize((W, H), Image.BILINEAR)

class Clip:
    SW_, SH_ = 360, 640
    def __init__(self, path, start, dur):
        w, h = self.SW_, self.SH_
        cmd = ["ffmpeg", "-v", "error", "-ss", str(start), "-i", path, "-t", str(dur), "-vf",
               f"fps={FPS},scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h}",
               "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
        raw = subprocess.run(cmd, capture_output=True).stdout
        n = len(raw) // (w * h * 3)
        self.frames = []
        for i in range(n):
            fr = Image.frombuffer("RGB", (w, h), raw[i * w * h * 3:(i + 1) * w * h * 3]).copy()
            self.frames.append(fr.filter(ImageFilter.GaussianBlur(4.6)))
        self.pos = 0
    def frame(self, t, d):
        f = self.frames[min(self.pos, len(self.frames) - 1)]; self.pos += 1
        return f.resize((W, H), Image.BICUBIC)

def darken(f, a):
    return Image.blend(f, Image.new("RGB", (W, H), (10, 22, 52)), a) if a else f

# ---------- captions ----------
def cap(main, sub=None, tag=None, size=88):
    im = Image.new("RGBA", (W, 420), (0, 0, 0, 0)); d = ImageDraw.Draw(im); y = 80
    if tag:
        f = ImageFont.truetype(BLACK, 38); tw = d.textlength(tag, font=f)
        d.rectangle(((W - tw) / 2 - 24, 24, (W + tw) / 2 + 24, 84), fill=(226, 38, 38))
        d.text((W / 2, 54), tag, font=f, fill="white", anchor="mm"); y = 108
    f = ImageFont.truetype(BLACK, size)
    while d.textlength(main, font=f) > W - 70:
        size -= 4; f = ImageFont.truetype(BLACK, size)
    d.text((W / 2 + 4, y + 8 + size / 2), main, font=f, fill=(0, 0, 0, 170), anchor="mm", stroke_width=11, stroke_fill=(0, 0, 0, 170))
    d.text((W / 2, y + size / 2), main, font=f, fill=(78, 170, 255), anchor="mm", stroke_width=10, stroke_fill="white")
    if sub:
        fs = ImageFont.truetype(BOLD, 44)
        d.text((W / 2 + 2, y + size + 66), sub, font=fs, fill=(0, 0, 0, 160), anchor="mm")
        d.text((W / 2, y + size + 64), sub, font=fs, fill="white", anchor="mm")
    return im

def put(frame, c, t, y):
    p = min(1.0, t / 0.3); s = 0.85 + 0.15 * (p * p * (3 - 2 * p))
    cc = c.resize((int(W * s), int(420 * s)), Image.LANCZOS)
    if p < 1: cc.putalpha(cc.split()[3].point(lambda v: int(v * p)))
    frame.paste(cc, ((W - cc.width) // 2, y + (420 - cc.height) // 2), cc)

GRAD = Image.new("RGBA", (W, H), (0, 0, 0, 0)); gd = ImageDraw.Draw(GRAD)
for yy in range(900, H): gd.line([(0, yy), (W, yy)], fill=(8, 18, 45, int(235 * (yy - 900) / (H - 900))))

# ---------- calendar card ----------
cal = Image.open(os.path.join(D, "cal", "cal11_fixed.png")).convert("RGB"); SW, SH = cal.size
calbig = cal.resize((SW * 2, SH * 2), Image.LANCZOS)
CX, CY, CW, CH = 90, 470, 900, 1350
cmask = Image.new("L", (CW, CH), 0); ImageDraw.Draw(cmask).rounded_rectangle((0, 0, CW, CH), 26, fill=255)
SHADOW = Image.new("RGBA", (W, H), (0, 0, 0, 0))
ImageDraw.Draw(SHADOW).rounded_rectangle((CX - 6, CY + 10, CX + CW + 6, CY + CH + 22), 32, fill=(0, 0, 0, 150))
SHADOW = SHADOW.filter(ImageFilter.GaussianBlur(16))
def card(f, cam):
    cx, cy, w = cam; h = w * 1.5
    cx = min(max(cx, w / 2), SW - w / 2); cy = min(max(cy, h / 2), SH - h / 2)
    view = calbig.crop(tuple(int(v * 2) for v in (cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2))).resize((CW, CH), Image.LANCZOS)
    f = Image.alpha_composite(f.convert("RGBA"), SHADOW).convert("RGB")
    ImageDraw.Draw(f).rounded_rectangle((CX - 6, CY - 6, CX + CW + 6, CY + CH + 6), 32, fill="white")
    f.paste(view, (CX, CY), cmask); return f

def ease(t): return t * t * (3 - 2 * t)
FULL = (SW / 2, SH / 2, SW)
BAD, VOL, TAK = (280, 700, 560), (512, 700, 560), (744, 700, 560)

def photo_seg(src, c):
    def fn(t, d):
        f = darken(src.frame(t, d), 0.08)
        f = Image.alpha_composite(f.convert("RGBA"), GRAD).convert("RGB")
        put(f, c, t, 1330); return f
    return fn

def cal_seg(src, a, b, c):
    def fn(t, d):
        f = darken(src.frame(t, d), 0.5)
        p = ease(min(1.0, t / 0.7))
        cam = tuple(a[k] + (b[k] - a[k]) * p for k in range(3))
        cam = (cam[0], cam[1], cam[2] * (1 - 0.012 * max(0, t - 0.7)))
        f = card(f, cam); put(f, c, t, 20); return f
    return fn

# ---------- material ----------
C = os.path.join(D, "clips")
clipA1 = Clip(os.path.join(C, "96bd7101d80345dea32585cc72954439.MOV"), 10, 2.7)
clipA2 = Clip(os.path.join(C, "96bd7101d80345dea32585cc72954439.MOV"), 13, 3.1)
clipB1 = Clip(os.path.join(C, "29da73e9795845e4aea114b14fb8c95c.MOV"), 20, 1.9)
clipB2 = Clip(os.path.join(C, "29da73e9795845e4aea114b14fb8c95c.MOV"), 22, 3.5)
clipA3 = Clip(os.path.join(C, "96bd7101d80345dea32585cc72954439.MOV"), 30, 3.3)
gym = Photo(Image.open(os.path.join(D, "photos", "IMG_3560.jpg")), focus=(0.5, 0.55), blur=5)
tt_src = Image.open(os.path.join(D, "mat", "Gemini_Generated_Image_159bg159bg159bg1.jpeg")).convert("RGB").crop((54, 420, 458, 866))
tt = Photo(tt_src, extra_boxes=[(97, 102, 52, 62), (211, 78, 28, 30), (287, 108, 40, 40)], focus=(0.45, 0.5))
base = Photo(Image.open(os.path.join(C, "IMG_4049.JPG")), extra_boxes=[(440, 356, 64, 64), (1130, 276, 110, 130), (590, 432, 34, 34)], focus=(0.62, 0.5))

SEGS = [
    (2.6, photo_seg(clipA1, cap("11月の予定、もう決めた？", "社会人スポーツイベント 全12回", size=92))),
    (3.0, cal_seg(clipA2, FULL, FULL, cap("11月のスポーツイベント", "初心者・1人参加 大歓迎"))),
    (1.8, photo_seg(clipB1, cap("バドミントン", "11月は6回開催！", size=96))),
    (3.4, cal_seg(clipB2, FULL, BAD, cap("バドミントン 6回", "目黒・まもり山・代々木・渋谷・巣鴨"))),
    (1.8, photo_seg(gym, cap("バレーボール", "11月は3回開催！", size=96))),
    (3.2, cal_seg(gym, BAD, VOL, cap("バレーボール 3回", "巣鴨体育館・中野区中部コミュニティプラザ"))),
    (1.6, photo_seg(tt, cap("卓球", "11/3・11/23 大久保プラザ", size=96))),
    (1.6, photo_seg(base, cap("野球", "11/22 芝公園", size=96))),
    (3.2, cal_seg(base, VOL, TAK, cap("卓球・野球 3回", "大久保プラザ・芝公園"))),
    (3.2, cal_seg(clipA3, TAK, FULL, cap("保存して予定に入れよう！", "@macachette_sports", tag="保存推奨"))),
]
XF = 0.3
proc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                         "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
                         "-pix_fmt", "yuv420p", "-movflags", "+faststart", OUT], stdin=subprocess.PIPE)
last = None
for i, (d, fn) in enumerate(SEGS):
    for k in range(int(d * FPS)):
        t = k / FPS; fr = fn(t, d)
        if last is not None and t < XF:
            fr = Image.blend(last, fr, t / XF)
        proc.stdin.write(fr.tobytes())
        cur = fr
    last = cur
proc.stdin.close(); proc.wait()
print("done", OUT, sum(d for d, _ in SEGS))
