"""夜の手動ストーリー用セット（毎夜3分で出す・11/12 加藤さん「夜間誘導・画像自動生成 v1.0」）。

加藤さんが手動で出す夜のストーリー用に、画像1枚と、コピペ用の文（リンクスタンプの文言・貼るリンク）を1週間分まとめて作る。
- 見た目：夜のダークトーン（チャコール／マットな黒／深いネイビー）、雑誌・ZINE の1ページのような左寄せの組み方、余白、細い罫線、紙と粒子の質感（tools/craft.finish）。
- 下3分の1は空けておく（リンクスタンプを貼る場所）。
- 中身はマカシェットスポーツの事実だけ（CLAUDE.md）。UTAGE・特典の話は出さない（11/11 加藤さん）。
- 日替わり3パターン：A 夜の本音Q&A／B 本質（運動の続け方）／C 予約の案内（次の開催）。

使い方: cd studio && python3 make_night.py → out/night/ に画像と「夜ストーリー_コピペ.txt」。zip にして加藤さんに渡す（自動投稿には入れない）。
"""
import os
from PIL import Image, ImageDraw
from make_1101 import BLACK, BOLD, F, text_img, D
from tools.craft import grain, vignette, tilt

W, H = 1080, 1920
OUT = os.path.join(D, "out", "night_1119"); os.makedirs(OUT, exist_ok=True)
LINE_URL = "https://lin.ee/WIbLPFV"
TONES = {"charcoal": (35, 37, 42), "black": (22, 22, 24), "navy": (18, 26, 46)}
CREAM = (238, 233, 222); MUTE = (150, 150, 146); YEL = (255, 236, 30)

# 1週間分（日付・パターン・色・小見出し・本文の行・下の一言・リンクスタンプの文言）
NIGHTS = [  # 11/19〜11/25（11/13 作成）
    ("11/19", "C", "navy", "今週末の、予定。", ["土・日・月祝、", "3日続けて", "やります。"],
     "11/21 バレー　11/22 野球　11/23 バレー・卓球", "予約は公式LINEから"),
    ("11/20", "C", "black", "明日の、予定。", ["明日 11:45、", "中野で", "バレーボール。"],
     "新中野駅（4番出口）から徒歩9分", "明日の予約は公式LINEから"),
    ("11/21", "C", "charcoal", "明日の、予定。", ["明日 17:00、", "芝公園で", "野球。"],
     "都営三田線 芝公園駅から徒歩約2分", "明日の予約は公式LINEから"),
    ("11/22", "C", "navy", "明日の、予定。", ["祝日の昼、", "バレーと卓球、", "どちらでも。"],
     "バレー 11:45 中野／卓球 12:20 大久保プラザ", "明日の予約は公式LINEから"),
    ("11/23", "A", "charcoal", "夜の、本音。", ["1人で行って、", "浮かないか", "心配な人へ。"],
     "来る人のほとんどが1人参加です。", "公式LINEで日程を見る"),
    ("11/24", "B", "black", "ちょっと、本質。", ["運動不足は、", "気合いより", "予定で直る。"],
     "平日の夜に1つ、体を動かす予定を入れておく。", "公式LINEで次の予定を決める"),
    ("11/25", "C", "navy", "明日の、予定。", ["明日 18:00、", "新代田で", "バドミントン。"],
     "11/26(木) まもりやまテラス（新代田駅 徒歩約5分）", "明日の予約は公式LINEから"),
]


def make(day, pat, tone, kicker, lines, foot, sticker, seed):
    c = Image.new("RGB", (W, H), TONES[tone]); d = ImageDraw.Draw(c)
    x = 96
    # 上：小さな通し番号と日付（雑誌の柱のように）
    d.text((x, 150), f"MACACHETTE SPORTS / {day}", font=F(BOLD, 30), fill=MUTE)
    d.line((x, 205, W - 96, 205), fill=(90, 90, 88), width=2)
    # 小見出し（黄色の短い帯を少しだけ傾ける＝あえての崩し）
    k = text_img(kicker, F(BLACK, 44), (20, 20, 22))
    band = Image.new("RGBA", (k.width + 36, k.height + 22), YEL + (255,)); band.alpha_composite(k, (18, 8))
    band = tilt(band, -2.5); c.paste(band, (x - 6, 300), band)
    # 本文：大きく左寄せ。行ごとにわずかに字間を変えない（均一すぎない程度に行間で調整）
    y = 430
    for i, ln in enumerate(lines):
        t = text_img(ln, F(BLACK, 108), CREAM); c.paste(t, (x, y), t); y += t.height + (26 if i < len(lines) - 1 else 0)
    # 下の一言（事実だけ）と細い罫線
    y += 70; d.line((x, y, x + 120, y), fill=YEL, width=6); y += 40
    f = text_img(foot, F(BOLD, 38), CREAM); c.paste(f, (x, y), f)
    # 下3分の1は何も置かない（リンクスタンプの場所）
    d.text((x, 1780), "@macachette_sports", font=F(BOLD, 30), fill=MUTE)
    out = vignette(grain(c, amount=0.03, seed=seed), strength=0.22)  # 暗い色は紙のムラが目立つので、粒子と周辺減光だけ
    name = f"night_{day.replace('/', '')}_{pat}.jpg"
    out.save(os.path.join(OUT, name), quality=93)
    return name


if __name__ == "__main__":
    rows = []
    for i, (day, pat, tone, kicker, lines, foot, sticker) in enumerate(NIGHTS):
        name = make(day, pat, tone, kicker, lines, foot, sticker, seed=40 + i)
        label = {"A": "夜の本音Q&A", "B": "本質", "C": "予約の案内"}[pat]
        rows.append(f"■ {day}（{label}）{name}\n"
                    f"  画像のメイン：{''.join(lines)}\n  画像のサブ：{foot}\n"
                    f"  リンクスタンプの文言：{sticker}\n  貼るリンク：{LINE_URL}\n"
                    f"  手順（3分）：画像を選ぶ → リンクスタンプ → URLを貼る → 文言を入れる → 下の空いた所に置く → 投稿\n")
    head = ("夜のストーリー（手動用）1週間分。下の空いている所にリンクスタンプを貼るだけで出せます。\n"
            "中身は事実だけ（参加費・会場・アクセスは CLAUDE.md どおり）。特典の話は入れていません。\n\n")
    open(os.path.join(OUT, "夜ストーリー_コピペ.txt"), "w", encoding="utf-8").write(head + "\n".join(rows))
    print("ok", OUT, len(rows))
