"""11/12(木) 保存狙いカルーセル「あなたに合う種目は？」8枚 1080x1350
テーマ案：A あなたに合う種目は？（4種目の選び方・採用：保存されやすい診断＋日程）／B 種目ごとの持ち物チェック／C はじめてでも楽しめる理由5つ
背景は人が写らない court・ceiling・floor（ぼかし2）を主役にし、人が写る写真は使わない（顔の写り込みゼロ）。
使い方: cd studio && python3 make_c1112.py → studio/out/c1112/ と content/instagram/media/ に JPG"""
import os, shutil
from make_c1105 import *  # helpers & SRC

OUT4 = os.path.join(D, "out", "c1112"); os.makedirs(OUT4, exist_ok=True)
MEDIA = os.path.join(D, "..", "content", "instagram", "media")
GREEN = (17, 151, 65); BLUE = (21, 101, 192)


def save4(c, n):
    page_no(c, n)
    p = os.path.join(OUT4, f"2026-11-12_carousel_{n:02d}.jpg"); c.convert("RGB").save(p, quality=93)
    shutil.copy(p, MEDIA); return p


def clear(key, dark=0.45):
    return bg(key, blur=2, dark=dark)


def sport_page(n, key, name, color, catch, fits, dates, extra):
    c = clear(key)
    put(c, fit(shadowed(pill([text_img(name, F(BLACK, 66), WHITE)], h=100, bg=color))), W / 2, 40)
    put(c, fit(shadowed(yellow_band(catch, size=80, seed=n))), W / 2, 160)
    a = card(fits, title="こんな人に向いています", color=color, fs=46, gap=12, pad=34); put(c, a, W / 2, 290)
    b = card(dates + [extra], title="11月の開催", color=NAVY, fs=40, gap=8, pad=28)
    put(c, b, W / 2, min(290 + a.height + 10, H - 110 - b.height))
    save4(c, n)


# 1 表紙
c = clear("court", dark=0.40)
put(c, fit(shadowed(pill([text_img("保存して、選ぶときに見返してね", F(BLACK, 44), WHITE)], h=88, bg=RED))), W / 2, 200)
put(c, fit(shadowed(headline("あなたに合う", "種目は？", seed=3, size=124))), W / 2, 340)
put(c, fit(shadowed(yellow_band("4種目の選び方", size=140, seed=7))), W / 2, 640)
put(c, fit(shadowed(pill([text_img("バド・バレー・卓球・野球", F(BLACK, 50), NAVY)], h=104))), W / 2, 900)
put(c, fit(shadowed(pill([text_img("初心者7割・経験者3割くらい", F(BOLD, 42), WHITE)], h=88, bg=(20, 42, 92, 225)))), W / 2, 1040)
save4(c, 1)

# 2 3つの質問で選ぶ
c = clear("floor")
head(c, "3つの質問で", "かんたんに選べます", seed=4)
y = 330
for i, (q, a, col) in enumerate([("みんなで声をかけ合いたい？", "→ バレー・野球", ORANGE),
                                 ("外で思いきり体を動かしたい？", "→ 野球", BLUE),
                                 ("道具を使って1対1で楽しみたい？", "→ バドミントン・卓球", GREEN)]):
    r = step_row(i + 1, q, a, color=col); put(c, r, W / 2, y); y += r.height + 16
put(c, fit(shadowed(pill([text_img("迷ったら、気になった日程で選んでOK", F(BLACK, 46), NAVY)], h=100, bg=YEL))), W / 2, y + 30)
save4(c, 2)

# 3〜6 種目ごと
sport_page(3, "court", "バドミントン", GREEN, "いちばん気軽に始めやすい",
           ["ラケットを振るのが初めての人", "ラケットの貸出あり"],
           ["11/14(土) 15:00-17:00 まもりやまテラス", "11/15(日) 13:00-15:00 代々木の杜", "11/26(木) 18:00-21:00 まもりやまテラス",
            "11/28(土) 13:00-15:00 本町コミュニティセンター", "11/29(日) 18:00-21:00 巣鴨体育館"], "どの会場も駅から徒歩15分以内")
sport_page(4, "ceiling", "バレーボール", ORANGE, "チームで声をかけ合える",
           ["みんなで盛り上がりたい人", "ボールをつなぐのが好きな人", "学生のころ以来の人も"],
           ["11/21(土) 11:45-13:45", "11/23(月・祝) 11:45-13:45", "中野区中部スポーツ・コミュニティプラザ"], "新中野駅（4番出口）から徒歩9分")
sport_page(5, "floor", "卓球", BLUE, "じっくり1対1で楽しめる",
           ["激しすぎない運動がいい人", "ラリーを続けるのが好きな人", "ラケットの貸出あり"],
           ["11/23(月・祝) 12:20-15:20", "大久保プラザ"], "大久保駅・新大久保駅すぐ")
sport_page(6, "court", "野球", BLUE, "外で思いきり体を動かせる",
           ["外でのびのび動きたい人", "チームで試合を楽しみたい人", "久しぶりに野球をしたい人"],
           ["11/22(日) 17:00-19:00", "芝公園"], "詳しい場所はDMでお気軽にどうぞ")

# 7 どの種目も同じ
c = clear("ceiling")
head(c, "どの種目も", "ここは同じ", seed=8)
y = 330
for i, (t, s) in enumerate([("ほとんどが1人参加", "20〜40代の社会人が中心"), ("初心者7割・経験者3割くらい", "上手さより楽しさ"),
                            ("当日の流れ（例）", "受付 → ストレッチ・基礎練習 → シャッフルゲーム → 片付け → 解散"),
                            ("参加費 1,500円", "当日、現金またはPayPay")]):
    r = step_row(i + 1, t, s); put(c, r, W / 2, y); y += r.height + 12
save4(c, 7)

# 8 CTA
c = clear("floor", dark=0.5)
head(c, "気になる種目が", "見つかったら", seed=11, y=90)
y = 320
for i, (t, s) in enumerate([("プロフィールのリンクから", "公式LINEに登録"), ("イベントカレンダーから予約", "参加フォームで申し込み"),
                            ("合言葉をLINEに送る", "「参加受付証」が届きます")]):
    r = step_row(i + 1, t, s, color=LINE_GREEN); put(c, r, W / 2, y); y += r.height - 10
put(c, fit(shadowed(yellow_band("まだまだ募集中！", size=90, seed=12))), W / 2, 950)
put(c, fit(shadowed(pill([text_img("保存して、選ぶときに見返してね", F(BLACK, 42), WHITE)], h=84, bg=RED))), W / 2, 1150)
save4(c, 8)
print("ok", OUT4)
