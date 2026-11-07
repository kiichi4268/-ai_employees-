"""11/9(月) カルーセル「11/3 卓球 開催しました」8枚（Drive に当日写真なし → AI 画像と過去写真を使い、注記を入れる）
テーマ案：A 開催報告＋次の卓球11/23（採用）／B 卓球の日の流れ（例）／C 卓球はじめての人へ
使い方: python3 studio/make_c1109.py → studio/out/c1109/ と content/instagram/media/ に JPG"""
import os, shutil
from make_c1105 import *  # helpers & SRC（c1105 も作り直されるが無害）

OUT3 = os.path.join(D, "out", "c1109"); os.makedirs(OUT3, exist_ok=True)
MEDIA = os.path.join(D, "..", "content", "instagram", "media")
BLUE = (21, 101, 192)


def save3(c, n):
    page_no(c, n)
    p = os.path.join(OUT3, f"2026-11-09_carousel_{n:02d}.jpg"); c.convert("RGB").save(p, quality=93)
    shutil.copy(p, MEDIA); return p


def note(c, text, y=1190):
    put(c, fit(text_img(text, F(BOLD, 30), WHITE)), W / 2, y)


AI = "※画像はイメージです"
PAST = "※写真は過去の開催時のものです"

# 1 表紙（AI 画像）
c = bg("tt", blur=6, dark=0.40)
put(c, fit(shadowed(pill([text_img("11/3(火・祝)", F(BLACK, 60), NAVY)], h=104))), W / 2, 230)
put(c, fit(shadowed(headline("卓球", "開催しました！", seed=3, size=120))), W / 2, 390)
put(c, fit(shadowed(yellow_band("ご参加ありがとう！", size=130, seed=7))), W / 2, 680)
put(c, fit(shadowed(pill([text_img("次の卓球と11月の日程 →", F(BLACK, 48), WHITE)], h=100, bg=TEAL))), W / 2, 930)
note(c, AI); save3(c, 1)

# 2 会場
c = bg("gym"); head(c, "卓球", "＠大久保プラザ", seed=4)
put(c, card(["11/3(火・祝) 12:20-15:20", "大久保駅・新大久保駅すぐ"], title="開催しました", color=BLUE), W / 2, 360)
put(c, fit(shadowed(yellow_band("ありがとうございました！", size=86, seed=5))), W / 2, 860)
note(c, PAST, 1100); save3(c, 2)

# 3 当日の流れ（例）
c = bg("tt"); head(c, "卓球の日は", "こんな流れ（例）", seed=5)
y = 330
for i, (t, s) in enumerate([("受付", "参加受付証を見せて参加費を払う"), ("ストレッチ・基礎練習", "体をほぐしてから"),
                            ("シャッフルゲーム", "メンバーを入れ替えて試合"), ("片付け → 解散", "終わったらそのまま解散")]):
    r = step_row(i + 1, t, s, color=BLUE); put(c, r, W / 2, y); y += r.height - 20
note(c, AI, 1205); save3(c, 3)

# 4 持ち物
c = bg("gym2"); head(c, "持ち物は", "これだけ", seed=6)
put(c, card(["着替え", "体育館シューズ", "飲み物"], title="持ち物", color=TEAL), W / 2, 340)
put(c, fit(shadowed(pill([text_img("卓球・バドはラケット貸出あり", F(BLACK, 52), NAVY)], h=110, bg=YEL))), W / 2, 860)
note(c, PAST, 1100); save3(c, 4)

# 5 参加者
c = bg("bad"); head(c, "どんな人が", "来ている？", seed=7)
y = 340
for i, (t, s) in enumerate([("20〜40代の社会人", "仕事帰り・休日に体を動かしたい人"), ("ほとんどが1人参加", "1人でも浮きません"),
                            ("初心者7割・経験者3割くらい", "上手さより楽しさ重視")]):
    r = step_row(i + 1, t, s); put(c, r, W / 2, y); y += r.height + 14
note(c, PAST, 1205); save3(c, 5)

# 6 次の卓球
c = bg("tt"); head(c, "次の卓球は", "11/23(月・祝)", seed=8)
put(c, card(["11/23(月・祝) 12:20-15:20", "大久保プラザ", "大久保駅・新大久保駅すぐ"], title="卓球", color=BLUE), W / 2, 360)
put(c, fit(shadowed(yellow_band("連休に体を動かそう！", size=90, seed=9))), W / 2, 900)
note(c, AI, 1100); save3(c, 6)

# 7 11月後半
c = bg("gym"); head(c, "11月後半の", "開催", seed=9)
y = 310
for dt, tm, vn, col in [("11/14(土)", "15:00-17:00", "バド＠まもり山テラス", (17, 151, 65)), ("11/15(日)", "13:00-15:00", "バド＠代々木の杜", (17, 151, 65)),
                        ("11/21(土)", "11:45-13:45", "バレー＠中野", ORANGE), ("11/22(日)", "17:00-19:00", "野球＠芝公園", BLUE),
                        ("11/23(月・祝)", "11:45〜", "バレー＠中野・卓球＠大久保", ORANGE), ("11/26(木)", "18:00-21:00", "バド＠まもり山テラス", (17, 151, 65)),
                        ("11/28(土)", "13:00-15:00", "バド＠渋谷", (17, 151, 65)), ("11/29(日)", "18:00-21:00", "バド＠巣鴨体育館", (17, 151, 65))]:
    r = step_row("●", f"{dt}  {tm}", vn, color=col); r = r.resize((int(r.width * .66), int(r.height * .66)), Image.LANCZOS)
    put(c, r, W / 2, y); y += r.height - 46
note(c, PAST, 1205); save3(c, 7)

# 8 参加方法（CTA）
c = bg("fut", dark=0.45); head(c, "参加方法は", "かんたん3ステップ", seed=11, y=100)
y = 300
for i, (t, s) in enumerate([("公式LINEに登録", "プロフィールのリンクから"), ("イベントカレンダーから予約", "参加フォームで申し込み"),
                            ("合言葉をLINEに送る", "「参加受付証」が届きます")]):
    r = step_row(i + 1, t, s, color=LINE_GREEN); put(c, r, W / 2, y); y += r.height - 40
put(c, fit(shadowed(pill([text_img("参加費 1,500円（当日 現金・PayPay）", F(BLACK, 46), NAVY)], h=100))), W / 2, y + 20)
put(c, fit(shadowed(yellow_band("まだまだ募集中！", size=86, seed=12))), W / 2, y + 150)
save3(c, 8)
print("ok", OUT3)
