"""3週目（11/16〜11/22）ストーリー 1日10本（11/10 加藤さん：8:00×3・10:00×2・12:00×3・19:00×2）。全部自動投稿。
- ③（8:00・12:00）は公式LINEの QR と ID（@827lnqaq）入り（11/12 加藤さん）。
- 10:00・19:00 は画像2枚。組み方は studio/tools/editorial.py（上下分割・罫線リスト）＝中央の白いカードをやめる（11/12 デザインを上げる）。
- 週のテーマ（企画シート PLANNING.md）：だれ＝「行ってみたいが1人だと不安な社会人」、動かす数字＝リンクタップ（週26）。
  11/21 バレー・11/22 野球・11/23 バレー＋卓球の3連続を、1日1つの不安に答えながら予約へ。
使い方: cd studio && python3 make_week3.py → out/week3/ と content/instagram（media・posts）
"""
import os, json, shutil
from PIL import Image, ImageDraw
import make_week1 as w1
from make_week1 import card_lines, event_card, make_image, make_video, GREEN, ORANGE, TEAL, LINE_GREEN, D
from tools.editorial import split_story, list_ruled, CREAM, INK
from tools.craft import finish

OUT = os.path.join(D, "out", "week3"); os.makedirs(OUT, exist_ok=True)
ROOT = os.path.dirname(D); MEDIA = os.path.join(ROOT, "content", "instagram", "media"); POSTS = os.path.join(ROOT, "content", "instagram", "posts")
BLUE = (21, 101, 192)
QR = Image.open(os.path.join(D, "assets", "line_qr.png")).convert("RGBA")

VB21 = event_card("バレーボール", ORANGE, "11/21(土)", "11:45-13:45", "中野区中部スポーツ・コミュニティプラザ", "新中野駅（4番出口）から徒歩9分")
BB22 = event_card("野球", BLUE, "11/22(日)", "17:00-19:00", "芝公園野球場", "都営三田線 芝公園駅から徒歩約2分")
VB23 = event_card("バレーボール", ORANGE, "11/23(月祝)", "11:45-13:45", "中野区中部スポーツ・コミュニティプラザ")
TT23 = event_card("卓球", BLUE, "11/23(月祝)", "12:20-15:20", "大久保プラザ", "大久保駅・新大久保駅すぐ")


def qr_line(head1, head2, sub, path, bg="ceiling"):
    """③：公式LINEの QR と ID。見ている本人はカメラで読めないので、スクショ→画像から読み込む手順を添える。"""
    c = w1.still_bg(bg, dark=0.55)
    w1.place(c, w1.hl(head1, head2, seed=5, size=110), w1.W / 2, 200)
    if sub: w1.place(c, w1.fit(w1.shadowed(w1.pill([w1.text_img(sub, w1.F(w1.BLACK, 44), w1.NAVY)], h=86))), w1.W / 2, 470)
    panel = Image.new("RGBA", (760, 820), (255, 255, 255, 250)); d = ImageDraw.Draw(panel)
    q = QR.resize((440, 440)); panel.alpha_composite(q, (160, 40))
    for i, (t, f, col) in enumerate([("LINEで @827lnqaq を検索", w1.F(w1.BLACK, 46), LINE_GREEN),
                                     ("または この画面をスクショ →", w1.F(w1.BOLD, 34), w1.NAVY),
                                     ("LINEの「QRコードリーダー」→", w1.F(w1.BOLD, 34), w1.NAVY),
                                     ("「画像から読み込む」", w1.F(w1.BOLD, 34), w1.NAVY)]):
        ti = w1.text_img(t, f, col); panel.alpha_composite(ti, ((760 - ti.width) // 2, 510 + i * 72 + (10 if i else 0)))
    w1.place(c, w1.shadowed(panel), w1.W / 2, 600)
    w1.foot(c); finish(c.convert("RGB"), seed=7).save(path, quality=93)


def two(day, tm, a, b):
    """10:00・19:00 の画像2枚（editorial）。a, b は (関数, 引数) 。"""
    out = []
    for k, (fn, kw) in enumerate((a, b), 1):
        p = os.path.join(OUT, day, f"{day}_{tm}_{k}.jpg"); fn(**kw).save(p, quality=93); out.append(p)
    return out


def S(top, kicker, lines, foot, accent=ORANGE, seed=1):
    return (split_story, dict(top_img=w1.SRC[top], kicker=kicker, headline_lines=lines, foot=foot, accent=accent, seed=seed))


def L(title, items, accent=ORANGE, seed=1):
    def mk(**kw):  # 1350の組みを縦長の紙の真ん中に置く（下が空きすぎないように）
        body = list_ruled(size=(1080, 1350), **kw)
        c = Image.new("RGB", (1080, 1920), CREAM); c.paste(body, (0, 285)); return c
    return (mk, dict(title=title, items=items, accent=accent, seed=seed))


WEEK = [
 ("1116", dict(h1="今週末は", h2="3連続開催", blocks=[VB21, BB22], bg="ceiling"),
  dict(src="ceiling", h1="11/21〜23", h2="3連続", lines=["土 バレー　日 野球", "月祝 バレー・卓球"]),
  ("今週末の", "予約は", "11/21〜23 受付中"),
  S("ceiling", "今週の予定", ["土・日・月祝、", "3日続けて。"], "11/21 バレー　11/22 野球　11/23 バレー・卓球", ORANGE, 11),
  L("1人で来る人へ", [("ほとんどが1人参加", "1人で申し込んでOK"), ("初心者7割・経験者3割くらい", ""), ("参加費1,500円", "当日 現金・PayPay")], ORANGE, 12),
  dict(h1="1人で", h2="行っていい？", blocks=[card_lines(["来る人のほとんどが1人参加", "初心者7割・経験者3割くらい"])], bg="floor"),
  dict(src="clipB", ss=24, h1="1人でも", h2="大丈夫", lines=["ほとんどが1人参加", "上手さより楽しさ"]),
  ("まずは", "公式LINEへ", "わからないことはDMでも"),
  S("floor", "仕事帰りに", ["週末の予定、", "1つ入れておく。"], "11/21(土) 11:45 バレーボール", ORANGE, 13),
  S("court", "予約はここから", ["公式LINEの", "カレンダーから。"], "LINEで @827lnqaq を検索", ORANGE, 14)),
 ("1117", dict(h1="今週末は", h2="3連続開催", blocks=[VB23, TT23], bg="ceiling"),
  dict(src="court", h1="11/23", h2="祝日は2種目", lines=["バレー 11:45〜", "卓球 12:20〜"]),
  ("祝日の", "予約は", "11/23 バレー・卓球"),
  S("ceiling", "持ち物は少なめ", ["着替えと", "体育館シューズ。"], "あとは飲み物だけ", ORANGE, 21),
  L("当日の流れ（例）", [("受付", "参加受付証を見せて参加費を払う"), ("ストレッチ・基礎練習", ""), ("シャッフルゲーム", "メンバーを入れ替えて試合"), ("片付け → 解散", "")], TEAL, 22),
  dict(h1="バレーは", h2="久しぶりでも", blocks=[card_lines(["学生のころ以来の人も", "初心者7割・経験者3割くらい"])], bg="floor"),
  dict(src="floor", h1="バレーボール", h2="11/21・23", lines=["11:45-13:45", "新中野駅から徒歩9分"]),
  ("バレーの", "予約は", "11/21・23 受付中"),
  S("floor", "11/21(土)・11/23(月祝)", ["バレーボール、", "2回あります。"], "中野区中部スポーツ・コミュニティプラザ", ORANGE, 23),
  S("court", "予約はここから", ["プロフィールの", "リンクから。"], "またはLINEで @827lnqaq", ORANGE, 24)),
 ("1118", dict(h1="野球", h2="やってみない？", blocks=[BB22], bg="court"),
  dict(src="court", h1="11/22(日)", h2="野球", lines=["17:00-19:00", "芝公園野球場"]),
  ("野球の", "予約は", "11/22 17:00〜"),
  S("court", "11/22(日) 17:00", ["野球、", "久しぶりにやる？"], "芝公園駅から徒歩約2分", BLUE, 31),
  L("こんな人に", [("外でのびのび動きたい", ""), ("チームで試合を楽しみたい", ""), ("久しぶりに野球をしたい", "")], BLUE, 32),
  dict(h1="何人で", h2="行けばいい？", blocks=[card_lines(["1人でOK", "来る人のほとんどが1人参加"])], bg="floor"),
  dict(src="clipB", ss=30, h1="ほとんど", h2="1人参加", lines=["1人で申し込んでOK", "初心者7割くらい"]),
  ("1人でも", "公式LINEへ", "予約はカレンダーから"),
  S("ceiling", "今週の予定", ["土・日・月祝、", "3日続けて。"], "どれか1日だけでもOK", ORANGE, 33),
  S("court", "予約はここから", ["公式LINEの", "カレンダーから。"], "LINEで @827lnqaq を検索", BLUE, 34)),
 ("1119", dict(h1="今週末は", h2="3連続開催", blocks=[VB21, BB22], bg="ceiling"),
  dict(src="ceiling", h1="どれか1日", h2="だけでも", lines=["11/21 バレー　11/22 野球", "11/23 バレー・卓球"]),
  ("今週末の", "予約は", "11/21〜23 受付中"),
  S("floor", "参加費", ["1,500円。", "当日払い。"], "現金またはPayPay", ORANGE, 41),
  L("申し込みは", [("プロフィールのリンク", "または LINE で @827lnqaq"), ("公式LINEを友だち追加", ""), ("カレンダーから予約", "合言葉を送ると参加受付証")], LINE_GREEN, 42),
  dict(h1="下手でも", h2="平気？", blocks=[card_lines(["初心者7割・経験者3割くらい", "上手さより楽しさ"])], bg="floor"),
  dict(src="clipA", ss=20, h1="ラケットは", h2="貸出あり", lines=["卓球・バドミントン", "卓球は11/23 大久保プラザ"]),
  ("気になったら", "公式LINEへ", "わからないことはDMでも"),
  S("ceiling", "明後日から", ["週末は", "3連続です。"], "11/21(土) 11:45 バレーボール", ORANGE, 43),
  S("court", "予約はここから", ["プロフィールの", "リンクから。"], "またはLINEで @827lnqaq", ORANGE, 44)),
 ("1120", dict(h1="明日は", h2="バレーボール", blocks=[VB21], bg="floor"),
  dict(src="floor", h1="明日 11:45", h2="バレー", lines=["中野区中部", "スポーツ・コミュニティプラザ"]),
  ("明日の", "予約は", "11/21(土) 11:45〜"),
  S("floor", "明日 11/21(土)", ["11:45から、", "バレーボール。"], "新中野駅（4番出口）から徒歩9分", ORANGE, 51),
  L("明日の持ち物", [("着替え", ""), ("体育館シューズ", ""), ("飲み物", ""), ("参加費1,500円", "当日 現金・PayPay")], ORANGE, 52),
  dict(h1="当日の", h2="受付は簡単", blocks=[card_lines(["参加受付証を見せる", "参加費を払う", "それだけでOK"])], bg="floor"),
  dict(src="ceiling", h1="受付は", h2="これだけ", lines=["参加受付証を見せる", "参加費を払う"]),
  ("明日の", "予約は", "公式LINEから"),
  S("ceiling", "今週末", ["土・日・月祝、", "まだ参加枠あります。"], "11/21 バレー　11/22 野球　11/23 バレー・卓球", ORANGE, 53),
  S("court", "予約はここから", ["公式LINEの", "カレンダーから。"], "LINEで @827lnqaq を検索", ORANGE, 54)),
 ("1121", dict(h1="今日は", h2="バレーボール", blocks=[VB21], bg="floor"),
  dict(src="floor", h1="今日 11:45", h2="バレー", lines=["まだ参加枠あります", "新中野駅から徒歩9分"]),
  ("今日・明日の", "予約は", "公式LINEから"),
  S("floor", "今日 11/21(土)", ["11:45から、", "バレーボール。"], "まだ参加枠あります", ORANGE, 61),
  S("court", "明日 11/22(日)", ["17:00から、", "野球。"], "芝公園野球場（芝公園駅から徒歩約2分）", BLUE, 62),
  dict(h1="明日は", h2="野球", blocks=[BB22], bg="court"),
  dict(src="court", h1="明日 17:00", h2="野球", lines=["芝公園野球場", "芝公園駅から徒歩約2分"]),
  ("明日の", "予約は", "11/22(日) 17:00〜"),
  S("court", "明日 11/22(日)", ["野球、", "まだ参加枠あります。"], "17:00-19:00 芝公園野球場", BLUE, 63),
  S("ceiling", "予約はここから", ["プロフィールの", "リンクから。"], "またはLINEで @827lnqaq", BLUE, 64)),
 ("1122", dict(h1="今日は", h2="野球", blocks=[BB22], bg="court"),
  dict(src="court", h1="今日 17:00", h2="野球", lines=["芝公園野球場", "まだ参加枠あります"]),
  ("今日の", "予約は", "11/22(日) 17:00〜"),
  S("court", "今日 11/22(日)", ["17:00から、", "野球。"], "芝公園駅から徒歩約2分", BLUE, 71),
  S("floor", "明日 11/23(月祝)", ["バレーと卓球、", "2つあります。"], "バレー 11:45 中野／卓球 12:20 大久保", ORANGE, 72),
  dict(h1="明日は", h2="祝日2種目", blocks=[VB23, TT23], bg="ceiling"),
  dict(src="ceiling", h1="明日", h2="バレー・卓球", lines=["バレー 11:45〜 中野", "卓球 12:20〜 大久保"]),
  ("明日の", "予約は", "11/23(月祝)"),
  S("ceiling", "明日 11/23(月祝)", ["祝日も、", "体を動かそう。"], "卓球はラケット貸出あり", BLUE, 73),
  S("court", "予約はここから", ["公式LINEの", "カレンダーから。"], "LINEで @827lnqaq を検索", ORANGE, 74)),
]


def post(day, tm, k, name, note):
    pid = f"2026-11-{day[2:]}-story-{tm}-{k}"
    json.dump({"id": pid, "type": "story", "scheduled_at": f"2026-11-{day[2:]}T{tm[:2]}:{tm[2:]}:00+09:00", "caption": "",
               "media": [name], "note": note}, open(os.path.join(POSTS, pid + ".json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)


if __name__ == "__main__":
    import sys
    only = sys.argv[1:]
    for day, img8, vid8, l8, i10a, i10b, img12, vid12, l12, i19a, i19b in WEEK:
        if only and day not in only: continue
        dd = os.path.join(OUT, day); os.makedirs(dd, exist_ok=True)
        files = []
        for tm, img, vid, line in (("0800", img8, vid8, l8), ("1200", img12, vid12, l12)):
            p1, p2, p3 = (os.path.join(dd, f"{day}_{tm}_{n}.{e}") for n, e in ((1, "jpg"), (2, "mp4"), (3, "jpg")))
            make_image(dict(img), p1); make_video(dict(vid), p2)
            qr_line(*line, p3)
            files += [(tm, 1, p1), (tm, 2, p2), (tm, 3, p3)]
        for tm, (a, b) in (("1000", (i10a, i10b)), ("1900", (i19a, i19b))):
            for k, p in enumerate(two(day, tm, a, b), 1): files.append((tm, k, p))
        for tm, k, p in files:
            name = f"2026-11-{day[2:]}_story_{tm}_{k}" + os.path.splitext(p)[1]
            shutil.copy(p, os.path.join(MEDIA, name))
            post(day, tm, k, name, f"3週目ストーリー {day[:2]}/{day[2:]} {tm[:2]}:{tm[2:]} の{k}本目。studio/make_week3.py（③はQR・ID、10時・19時は editorial）。改善:K-003")
        print("done", day, len(files), flush=True)
