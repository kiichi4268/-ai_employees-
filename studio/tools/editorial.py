"""エディトリアル（雑誌・ZINE）風の組み方の部品（11/12 加藤さん「デザインと企画を上げる」）。

今までの「中央の白いカード＋帯」の型をやめ、左右どちらかに寄せた大きな文字・細い罫線・余白で組む。
どの組み方も最後に tools/craft の finish を通す。色はブランド3色＋種目色1つまで（PIPELINE.md デザインの決まり）。

  from tools.editorial import poster_big_date, list_ruled, split_story
  img = poster_big_date(bg, "11/21", "SAT", "バレーボール", [...], accent=ORANGE)

組み方：
- poster_big_date：日付をとても大きく左に置くポスター型（開催日フィード・告知）
- list_ruled：細い罫線で区切った番号つきリスト（保存狙いカルーセルの中ページ）
- split_story：上下2分割（上＝写真／背景、下＝無地の色面に文字）の縦長（ストーリー・リール表紙）
"""
from PIL import Image, ImageDraw

try:
    from make_1101 import BLACK, BOLD, F, text_img
except ImportError:  # studio/ の外から呼ばれたとき
    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from make_1101 import BLACK, BOLD, F, text_img
from tools.craft import finish, tilt

NAVY = (20, 42, 92); CREAM = (244, 240, 230); INK = (24, 26, 30); YEL = (255, 236, 30)


def _dark(bg, amount=0.55, color=(14, 18, 30)):
    return Image.blend(bg.convert("RGB"), Image.new("RGB", bg.size, color), amount)


def poster_big_date(bg, date, dow, sport, lines, accent, label="まだ参加枠あります", seed=1, size=(1080, 1350)):
    """左に巨大な日付、右下に情報。中央揃えを使わない。"""
    W, H = size
    c = _dark(bg.resize(size), 0.58).convert("RGBA"); d = ImageDraw.Draw(c)
    x = 80
    d.text((x, 70), "MACACHETTE SPORTS", font=F(BOLD, 30), fill=(200, 200, 196))
    d.line((x, 120, W - 80, 120), fill=(200, 200, 196), width=2)
    big = text_img(date, F(BLACK, 300), CREAM); c.alpha_composite(big, (x - 10, 170))
    dw = text_img(dow, F(BLACK, 70), accent); c.alpha_composite(dw, (x + 6, 170 + big.height + 4))
    sp = text_img(sport, F(BLACK, 96), CREAM); c.alpha_composite(sp, (x, 170 + big.height + dw.height + 40))
    y = 170 + big.height + dw.height + sp.height + 90
    d.line((x, y, x + 140, y), fill=accent, width=8); y += 36
    for ln in lines:
        t = text_img(ln, F(BOLD, 44), CREAM); c.alpha_composite(t, (x, y)); y += t.height + 14
    tag = text_img(label, F(BLACK, 46), INK)
    band = Image.new("RGBA", (tag.width + 44, tag.height + 26), YEL + (255,)); band.alpha_composite(tag, (22, 10))
    band = tilt(band, -2.5); c.alpha_composite(band, (W - band.width - 70, H - band.height - 120))
    d.text((x, H - 80), "@macachette_sports", font=F(BOLD, 30), fill=(200, 200, 196))
    return finish(c.convert("RGB"), seed=seed)


def list_ruled(title, items, accent, page="", seed=1, size=(1080, 1350), paper=CREAM):
    """紙の色の上に、細い罫線と番号で区切ったリスト。1枚4行まで（PATTERNS：5行以上は詰めすぎ）。"""
    assert len(items) <= 4, "1枚4行まで"
    W, H = size
    c = Image.new("RGBA", size, paper + (255,)); d = ImageDraw.Draw(c)
    x = 90
    t = text_img(title, F(BLACK, 88), INK); c.alpha_composite(t, (x, 130))
    d.line((x, 130 + t.height + 30, x + 120, 130 + t.height + 30), fill=accent, width=10)
    y = 130 + t.height + 110
    for i, (head, sub) in enumerate(items, 1):
        d.line((x, y, W - 90, y), fill=(190, 186, 176), width=2)
        n = text_img(f"{i:02d}", F(BLACK, 60), accent); c.alpha_composite(n, (x, y + 30))
        h = text_img(head, F(BLACK, 54), INK); c.alpha_composite(h, (x + 130, y + 30))
        if sub:
            s = text_img(sub, F(BOLD, 34), (90, 92, 98)); c.alpha_composite(s, (x + 132, y + 36 + h.height))
        y += max(170, h.height + (s.height if sub else 0) + 80)
    d.text((x, H - 90), "@macachette_sports", font=F(BOLD, 30), fill=(120, 118, 112))
    if page: d.text((W - 160, H - 90), page, font=F(BOLD, 30), fill=(120, 118, 112))
    return finish(c.convert("RGB"), seed=seed)


def split_story(top_img, kicker, headline_lines, foot, accent, seed=1, size=(1080, 1920)):
    """上60%＝写真（人の写らない背景）、下40%＝無地の色面に左寄せの大きな文字。"""
    W, H = size; top_h = int(H * 0.58)
    c = Image.new("RGBA", size, NAVY + (255,))
    t = top_img.convert("RGB"); r = max(W / t.width, top_h / t.height)
    t = t.resize((int(t.width * r) + 1, int(t.height * r) + 1)); x0 = (t.width - W) // 2; y0 = (t.height - top_h) // 2
    c.paste(t.crop((x0, y0, x0 + W, y0 + top_h)), (0, 0))
    d = ImageDraw.Draw(c); x = 80; y = top_h + 70
    k = text_img(kicker, F(BOLD, 40), accent); c.alpha_composite(k, (x, y)); y += k.height + 30
    for ln in headline_lines:
        h = text_img(ln, F(BLACK, 100), CREAM); c.alpha_composite(h, (x, y)); y += h.height + 12
    y += 30; f = text_img(foot, F(BOLD, 40), CREAM); c.alpha_composite(f, (x, y))
    d.text((x, H - 90), "@macachette_sports", font=F(BOLD, 30), fill=(200, 200, 196))
    return finish(c.convert("RGB"), seed=seed)
