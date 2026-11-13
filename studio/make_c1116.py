"""11/16(月) カルーセル「11/14・15 バドミントン 開催しました」8枚（レポート・当日写真を待たず AI 画像＋注記：11/10 加藤さん）
テーマ案：A 2日連続の開催報告＋今週末の3連続（採用：レポートから次の予定へつなげる）／B バドの日の流れ（例）／C 次のバド 11/26・28・29
参加人数・盛り上がりなど見ていないことは書かない。参加費は画像に書く（11/13）。
使い方: cd studio && python3 make_c1116.py"""
import os, shutil, json
from make_c1105 import *

OUT3 = os.path.join(D, "out", "c1116"); os.makedirs(OUT3, exist_ok=True)
MEDIA = os.path.join(D, "..", "content", "instagram", "media")
BLUE = (21, 101, 192); GRN = (17, 151, 65)
AI = "※画像はイメージです"; PAST = "※写真は過去の開催時のものです"


def save3(c, n):
    page_no(c, n)
    p = os.path.join(OUT3, f"2026-11-16_carousel_{n:02d}.jpg"); c.convert("RGB").save(p, quality=93)
    shutil.copy(p, MEDIA); return p


def note(c, text, y=1190):
    put(c, fit(text_img(text, F(BOLD, 30), WHITE)), W / 2, y)


# 1 表紙
c = bg("bad", blur=6, dark=0.40)
put(c, fit(shadowed(pill([text_img("11/14(土)・11/15(日)", F(BLACK, 60), NAVY)], h=104))), W / 2, 230)
put(c, fit(shadowed(headline("バドミントン", "2日連続 開催しました", seed=3, size=110))), W / 2, 400)
put(c, fit(shadowed(yellow_band("ご参加ありがとう！", size=130, seed=7))), W / 2, 690)
put(c, fit(shadowed(pill([text_img("今週末は3連続開催 →", F(BLACK, 48), WHITE)], h=100, bg=TEAL))), W / 2, 930)
note(c, PAST); save3(c, 1)

# 2 会場
c = bg("gym"); head(c, "2つの会場で", "開催しました", seed=4)
put(c, card(["11/14(土) 15:00-17:00", "まもりやまテラス", "新代田駅から徒歩約5分"], title="1日目", color=GRN, fs=46), W / 2, 280)
put(c, card(["11/15(日) 13:00-15:00", "代々木の杜", "JR代々木駅から徒歩5分"], title="2日目", color=GRN, fs=46), W / 2, 740)
note(c, PAST, 1180); save3(c, 2)

# 3 当日の流れ（例）
c = bg("bad"); head(c, "バドの日は", "こんな流れ（例）", seed=5)
y = 330
for i, (t, s) in enumerate([("受付", "参加受付証を見せて参加費を払う"), ("ストレッチ・基礎練習", "体をほぐしてから"),
                            ("シャッフルゲーム", "メンバーを入れ替えて試合"), ("片付け → 解散", "終わったらそのまま解散")]):
    r = step_row(i + 1, t, s, color=GRN); put(c, r, W / 2, y); y += r.height - 20
note(c, PAST, 1205); save3(c, 3)

# 4 持ち物
c = bg("gym2"); head(c, "持ち物は", "これだけ", seed=6)
put(c, card(["着替え", "体育館シューズ", "飲み物"], title="持ち物", color=TEAL), W / 2, 340)
put(c, fit(shadowed(pill([text_img("バドミントン・卓球はラケット貸出あり", F(BLACK, 50), NAVY)], h=110, bg=YEL))), W / 2, 860)
note(c, PAST, 1100); save3(c, 4)

# 5 どんな人が
c = bg("bad"); head(c, "どんな人が", "来ている？", seed=7)
y = 340
for i, (t, s) in enumerate([("20〜40代の社会人", "仕事帰り・休日に体を動かしたい人"), ("ほとんどが1人参加", "1人で申し込んでOK"),
                            ("初心者7割・経験者3割くらい", "久しぶりの人も")]):
    r = step_row(i + 1, t, s); put(c, r, W / 2, y); y += r.height + 14
note(c, PAST, 1205); save3(c, 5)

# 6 今週末の3連続
c = bg("gym"); head(c, "今週末は", "3連続開催", seed=8)
y = 330
for dt, tm, vn, col in [("11/21(土)", "11:45-13:45", "バレー＠中野（新中野駅 徒歩9分）", ORANGE),
                        ("11/22(日)", "17:00-19:00", "野球＠芝公園野球場（芝公園駅 徒歩約2分）", BLUE),
                        ("11/23(月・祝)", "11:45-13:45", "バレー＠中野", ORANGE), ("11/23(月・祝)", "12:20-15:20", "卓球＠大久保プラザ", BLUE)]:
    r = step_row("●", f"{dt}  {tm}", vn, color=col); r = r.resize((int(r.width * .8), int(r.height * .8)), Image.LANCZOS)
    put(c, r, W / 2, y); y += r.height - 20
note(c, PAST, 1205); save3(c, 6)

# 7 次のバド
c = bg("bad"); head(c, "次のバドは", "11/26(木)から", seed=9)
y = 330
for dt, tm, vn in [("11/26(木)", "18:00-21:00", "まもりやまテラス（新代田駅 徒歩約5分）"), ("11/28(土)", "13:00-15:00", "渋谷区本町コミュニティセンター（初台駅 徒歩約13分）"),
                   ("11/29(日)", "18:00-21:00", "巣鴨体育館（巣鴨駅・大塚駅 徒歩約10分）")]:
    r = step_row("●", f"{dt}  {tm}", vn, color=GRN); r = r.resize((int(r.width * .8), int(r.height * .8)), Image.LANCZOS)
    put(c, r, W / 2, y); y += r.height - 10
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

cap = ("11/14(土)・11/15(日) バドミントン、2日連続で開催しました🏸\nご参加いただいたみなさん、ありがとうございました！\n\n"
       "今週末は3連続開催\n・11/21(土) 11:45-13:45 バレーボール＠中野区中部スポーツ・コミュニティプラザ（丸ノ内線 新中野駅4番出口から徒歩9分）\n"
       "・11/22(日) 17:00-19:00 野球＠芝公園野球場（都営三田線 芝公園駅から徒歩約2分）\n"
       "・11/23(月祝) 11:45-13:45 バレーボール＠中野区中部スポーツ・コミュニティプラザ／12:20-15:20 卓球＠大久保プラザ（大久保駅・新大久保駅すぐ）\n\n"
       "次のバドミントンは 11/26(木)・11/28(土)・11/29(日)\n\nほとんどが1人参加で、初心者7割・経験者3割くらいです。\n"
       "参加費1,500円（当日、現金またはPayPay）\n予約はプロフィールのリンクから公式LINEへ\nわからないことはDMでお気軽にどうぞ\n\n※写真は過去の開催時のものです\n\n"
       "#社会人スポーツ #社会人サークル #バドミントン #バドミントンサークル #1人参加 #初心者歓迎 #東京スポーツ #マカシェットスポーツ")
json.dump({"id": "2026-11-16-carousel-01", "type": "carousel", "scheduled_at": "2026-11-16T19:00:00+09:00", "caption": cap,
           "media": [f"2026-11-16_carousel_{n:02d}.jpg" for n in range(1, 9)],
           "note": "レポートカルーセル（11/14・15 バド）。studio/make_c1116.py。過去写真（注記あり）。参加費は8枚目に記載（11/13）"},
          open(os.path.join(D, "..", "content", "instagram", "posts", "2026-11-16-carousel-01.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("ok", OUT3)
