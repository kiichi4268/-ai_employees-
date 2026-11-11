"""「人が手で作った」質感を足す仕上げ道具（HUMAN_CRAFT.md・デザインの戒律）。

AIが作ったと一目で分かる「つるっとした均一さ」を消すために、最後の仕上げで使う。
  from tools.craft import finish, tilt, misprint
  img = finish(img)                 # 紙の質感＋フィルムの粒子＋ほんの少しの周辺減光（毎回これを最後に）
  sticker = tilt(sticker, -2.5)     # 帯・ラベルをわずかに傾ける（完全な水平・左右対称を崩す）
  title = misprint(title, (3, 2))   # 印刷の版ずれ（文字の影を少しずらす）
すべて numpy・Pillow だけ。乱数は seed で固定でき、同じ投稿は同じ見た目に作り直せる。
"""
import numpy as np
from PIL import Image, ImageFilter


def grain(img, amount=0.045, seed=1):
    """フィルムの粒子。明るい所は控えめ、暗い所は少し強め（実際のフィルムに近い）。"""
    a = np.asarray(img.convert("RGB"), dtype=np.float32) / 255
    rng = np.random.default_rng(seed)
    n = rng.normal(0, 1, a.shape[:2])[..., None]
    n = np.asarray(Image.fromarray(((n[..., 0] * 40 + 128).clip(0, 255)).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.6)),
                   dtype=np.float32)[..., None] / 255 - 0.5
    lum = a.mean(axis=2, keepdims=True)
    out = a + n * amount * 2 * (1.2 - lum)
    return Image.fromarray((out.clip(0, 1) * 255).astype(np.uint8))


def paper(img, strength=0.06, seed=2):
    """紙の繊維のような、ゆるいムラ。真っ平らな塗りをなくす。"""
    w, h = img.size
    rng = np.random.default_rng(seed)
    small = rng.normal(0, 1, (h // 24 + 1, w // 24 + 1)).astype(np.float32)
    m = Image.fromarray(((small * 30 + 128).clip(0, 255)).astype(np.uint8)).resize((w, h), Image.BICUBIC)
    m = np.asarray(m.filter(ImageFilter.GaussianBlur(8)), dtype=np.float32)[..., None] / 255 - 0.5
    a = np.asarray(img.convert("RGB"), dtype=np.float32) / 255
    return Image.fromarray(((a + m * strength * 2).clip(0, 1) * 255).astype(np.uint8))


def vignette(img, strength=0.18):
    """周辺をほんの少し落とす（レンズの自然な減光）。"""
    w, h = img.size
    y, x = np.ogrid[-1:1:complex(0, h), -1:1:complex(0, w)]
    v = 1 - strength * np.clip((x ** 2 + y ** 2) / 2, 0, 1)
    a = np.asarray(img.convert("RGB"), dtype=np.float32) * v[..., None]
    return Image.fromarray(a.clip(0, 255).astype(np.uint8))


def finish(img, seed=1):
    """仕上げのセット（紙→粒子→周辺減光）。完成画像を保存する直前に1回だけ通す。"""
    mode = img.mode
    out = vignette(grain(paper(img.convert("RGB"), seed=seed + 1), seed=seed))
    return out.convert("RGBA") if mode == "RGBA" else out


def tilt(part, deg=-2.0):
    """帯・ラベル・写真の切り抜きを、わずかに傾ける（−4〜4度まで。やりすぎない）。"""
    return part.rotate(deg, resample=Image.BICUBIC, expand=True)


def misprint(part, offset=(3, 2), color=(255, 92, 70, 150)):
    """印刷の版ずれ：形をずらした色の影を、元の後ろに敷く（リソグラフ風）。"""
    part = part.convert("RGBA")
    shadow = Image.new("RGBA", part.size, color)
    shadow.putalpha(part.getchannel("A").point(lambda v: v * color[3] // 255))
    out = Image.new("RGBA", (part.width + abs(offset[0]), part.height + abs(offset[1])), (0, 0, 0, 0))
    out.alpha_composite(shadow, (max(0, offset[0]), max(0, offset[1])))
    out.alpha_composite(part, (max(0, -offset[0]), max(0, -offset[1])))
    return out


if __name__ == "__main__":
    im = Image.new("RGB", (540, 675), (24, 160, 178))
    out = finish(im)
    a = np.asarray(out, dtype=np.float32)
    assert out.size == im.size and a.std() > 1.0, "質感が足されていない"
    t = tilt(Image.new("RGBA", (200, 60), (255, 236, 30, 255)), -3)
    assert t.width > 200
    mp = misprint(Image.new("RGBA", (100, 40), (20, 42, 92, 255)))
    assert mp.size == (103, 42)
    print("craft self-test ok：仕上げ・傾き・版ずれ")
