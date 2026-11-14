"""顔だけを隠す（11/14 加藤さん「ボケはそんなに必要ない。顔が見えない形に」）。

写真全体はくっきりのまま、人の頭のあたりだけをモザイクにする。
1) OpenCV の顔検出（正面・横顔）と人の検出（HOG）で自動
2) 取りこぼしは MANUAL に手で頭の枠を足す（出す前に必ず目で確認する）
使い方: python3 tools/anonymize.py 入力.jpg 出力.jpg
"""
import sys, cv2, numpy as np

MANUAL = {}  # ファイル名: [(x, y, w, h), ...]（元画像の座標）


def _pix(img, x, y, w, h, block=None):
    H, W = img.shape[:2]
    x0, y0, x1, y1 = max(0, x), max(0, y), min(W, x + w), min(H, y + h)
    if x1 <= x0 or y1 <= y0: return
    roi = img[y0:y1, x0:x1]
    b = block or max(6, min(roi.shape[:2]) // 4)
    small = cv2.resize(roi, (max(1, roi.shape[1] // b), max(1, roi.shape[0] // b)), interpolation=cv2.INTER_LINEAR)
    img[y0:y1, x0:x1] = cv2.resize(small, (x1 - x0, y1 - y0), interpolation=cv2.INTER_NEAREST)


def heads(img):
    g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY); boxes = []
    for name in ("haarcascade_frontalface_default.xml", "haarcascade_profileface.xml"):
        cc = cv2.CascadeClassifier(cv2.data.haarcascades + name)
        for (x, y, w, h) in cc.detectMultiScale(g, 1.08, 4, minSize=(14, 14)):
            boxes.append((x - w // 3, y - h // 3, int(w * 1.66), int(h * 1.66)))
    hog = cv2.HOGDescriptor(); hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
    for scale_img, s in ((img, 1.0), (cv2.resize(img, None, fx=2, fy=2), 0.5)):
        rects, _ = hog.detectMultiScale(scale_img, winStride=(8, 8), padding=(8, 8), scale=1.05)
        for (x, y, w, h) in rects:
            x, y, w, h = int(x * s), int(y * s), int(w * s), int(h * s)
            boxes.append((x + w // 5, y, int(w * 0.6), int(h * 0.3)))  # 人の枠の上30%＝頭のあたり
    return boxes


def anonymize(path_in, path_out, extra=()):
    img = cv2.imread(path_in)
    for b in list(heads(img)) + list(extra) + MANUAL.get(path_in.split("/")[-1], []):
        _pix(img, *b)
    cv2.imwrite(path_out, img, [cv2.IMWRITE_JPEG_QUALITY, 92])
    return path_out


if __name__ == "__main__":
    anonymize(sys.argv[1], sys.argv[2])
