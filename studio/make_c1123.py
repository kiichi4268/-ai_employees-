"""11/23(月祝) 18:00 カルーセル「11/21 バレー・11/22 野球 開催しました」8枚（レポート）
テーマ案：A 週末2種目の開催報告＋次の予定（採用：レポートから今週のバドと12月のバレー・野球へつなげる）／B バレーの日の流れ（例）／C 12月の野球・バレー先取り
参加人数・盛り上がりなど見ていないことは書かない。参加費は画像に書く（11/13）。過去写真の注記は入れない（11/19）。顔は処理済みの bg を使う。
使い方: cd studio && python3 make_c1123.py"""
import os, shutil, json
from make_c1105 import *
import make_week1 as _w1
from tools import people_bg
people_bg.register(_w1)

OUT6 = os.path.join(D, "out", "c1123"); os.makedirs(OUT6, exist_ok=True)
MEDIA = os.path.join(D, "..", "content", "instagram", "media")
BLUE = (21, 101, 192); GRN = (17, 151, 65)
DAY = "2026-11-23"


def save6(c, n):
    page_no(c, n)
    p = os.path.join(OUT6, f"{DAY}_carousel_{n:02d}.jpg"); c.convert("RGB").save(p, quality=93)
    shutil.copy(p, MEDIA); return p


def small(r, k=.8):
    return r.resize((int(r.width * k), int(r.height * k)), Image.LANCZOS)


# 1 表紙
c = bg("play_vb", blur=0, dark=0.45)
put(c, fit(shadowed(pill([text_img("11/21(土)・11/22(日)", F(BLACK, 60), NAVY)], h=104))), W / 2, 230)
put(c, fit(shadowed(headline("バレーと野球", "開催しました", seed=3, size=110))), W / 2, 400)
put(c, fit(shadowed(yellow_band("ご参加ありがとう！", size=130, seed=7))), W / 2, 690)
put(c, fit(shadowed(pill([text_img("次の開催はこちら →", F(BLACK, 48), WHITE)], h=100, bg=TEAL))), W / 2, 930)
save6(c, 1)

# 2 会場
c = bg("play_bb", blur=0, dark=0.55); head(c, "週末は", "2つの種目で", seed=4)
put(c, card(["11/21(土) 11:45-13:45", "中野区中部スポーツ・コミュニティプラザ", "新中野駅（4番出口）から徒歩9分"], title="バレーボール", color=ORANGE, fs=44), W / 2, 280)
put(c, card(["11/22(日) 17:00-19:00", "芝公園野球場", "芝公園駅から徒歩約2分"], title="野球", color=BLUE, fs=44), W / 2, 760)
save6(c, 2)

# 3 当日の流れ（例）
c = bg("ceiling"); head(c, "当日は", "こんな流れ（例）", seed=5)
y = 330
for i, (t, s) in enumerate([("受付", "参加受付証を見せて参加費を払う"), ("ストレッチ・基礎練習", "体をほぐしてから"),
                            ("シャッフルゲーム", "メンバーを入れ替えて試合"), ("片付け → 解散", "終わったらそのまま解散")]):
    r = step_row(i + 1, t, s, color=ORANGE); put(c, r, W / 2, y); y += r.height - 20
save6(c, 3)

# 4 どんな人が
c = bg("floor"); head(c, "どんな人が", "来ている？", seed=7)
y = 340
for i, (t, s) in enumerate([("20〜40代の社会人", "仕事帰り・休日に体を動かしたい人"), ("ほとんどが1人参加", "1人で申し込んでOK"),
                            ("初心者7割・経験者3割くらい", "久しぶりの人も")]):
    r = step_row(i + 1, t, s); put(c, r, W / 2, y); y += r.height + 14
save6(c, 4)

# 5 今週のバド
c = bg("play_bad", blur=0, dark=0.55); head(c, "今週は", "バドミントン3回", seed=8)
y = 330
for dt, tm, vn in [("11/26(木)", "18:00-21:00", "まもりやまテラス（新代田駅 徒歩約5分）"), ("11/28(土)", "13:00-15:00", "渋谷区本町コミュニティセンター（初台駅 徒歩約13分）"),
                   ("11/29(日)", "18:00-21:00", "巣鴨体育館（巣鴨駅・大塚駅 徒歩約10分）")]:
    r = small(step_row("●", f"{dt}  {tm}", vn, color=GRN)); put(c, r, W / 2, y); y += r.height - 10
put(c, fit(shadowed(pill([text_img("ラケット貸出あり", F(BLACK, 50), NAVY)], h=100, bg=YEL))), W / 2, y + 30)
save6(c, 5)

# 6 次のバレー・野球（12月）
c = bg("play_vb2", blur=0, dark=0.55); head(c, "次のバレー・野球は", "12月です", seed=9)
y = 340
for dt, tm, vn, col in [("12/26(土)", "11:45-13:45", "バレー＠中野区中部コミュニティプラザ", ORANGE),
                        ("12/30(水)", "12:00-14:00", "野球＠麻布運動場（広尾駅1番出口 徒歩約7〜10分）", BLUE)]:
    r = small(step_row("●", f"{dt}  {tm}", vn, color=col), .85); put(c, r, W / 2, y); y += r.height + 10
save6(c, 6)

# 7 持ち物（体育館の種目）
c = bg("court"); head(c, "体育館の種目の", "持ち物", seed=6)
put(c, card(["着替え", "体育館シューズ", "飲み物"], title="持ち物", color=TEAL), W / 2, 340)
put(c, fit(shadowed(pill([text_img("バドミントン・卓球はラケット貸出あり", F(BLACK, 50), NAVY)], h=110, bg=YEL))), W / 2, 860)
save6(c, 7)

# 8 参加方法（CTA）
c = bg("fut", dark=0.45); head(c, "参加方法は", "かんたん3ステップ", seed=11, y=100)
y = 300
for i, (t, s) in enumerate([("公式LINEに登録", "プロフィールのリンクから"), ("イベントカレンダーから予約", "参加フォームで申し込み"),
                            ("合言葉をLINEに送る", "「参加受付証」が届きます")]):
    r = step_row(i + 1, t, s, color=LINE_GREEN); put(c, r, W / 2, y); y += r.height - 40
put(c, fit(shadowed(pill([text_img("参加費 1,500円（当日 現金・PayPay）", F(BLACK, 46), NAVY)], h=100))), W / 2, y + 20)
put(c, fit(shadowed(yellow_band("まだまだ募集中！", size=86, seed=12))), W / 2, y + 150)
save6(c, 8)

cap = ("保存しておくと、次に申し込む前に見返せます📌\n\n"
       "11/21(土) バレーボール、11/22(日) 野球を開催しました🏐⚾\nご参加いただいたみなさん、ありがとうございました！\n\n"
       "・ほとんどが1人参加\n・初心者7割・経験者3割くらい\n・当日は 受付 → ストレッチ・基礎練習 → シャッフルゲーム（試合）→ 片付け → 解散（例）\n\n"
       "今週はバドミントン3回\n・11/26(木) 18:00-21:00 まもりやまテラス（京王井の頭線 新代田駅から徒歩約5分）\n"
       "・11/28(土) 13:00-15:00 渋谷区本町コミュニティセンター（京王新線 初台駅から徒歩約13分）\n"
       "・11/29(日) 18:00-21:00 巣鴨体育館（JR巣鴨駅・大塚駅から徒歩約10分）\n\n"
       "次のバレーは 12/26(土)、野球は 12/30(水)\n\n"
       "参加費1,500円（当日、現金またはPayPay）\n予約はプロフィールのリンクから公式LINEへ（LINEで @827lnqaq を検索でもOK）\nわからないことはDMでお気軽にどうぞ\n\n"
       "#社会人スポーツ #社会人サークル #バレーボール #社会人バレー #草野球 #バドミントン #1人参加 #初心者歓迎 #東京スポーツ #マカシェットスポーツ")
json.dump({"id": f"{DAY}-carousel-01", "type": "carousel", "scheduled_at": f"{DAY}T18:00:00+09:00", "caption": cap,
           "media": [f"{DAY}_carousel_{n:02d}.jpg" for n in range(1, 9)],
           "note": "レポートカルーセル（11/21 バレー・11/22 野球）。studio/make_c1123.py。過去写真（顔は処理済み・注記なし 11/19）。参加費は8枚目に記載（11/13）。キャプション1行目＝保存の一言（11/21）"},
          open(os.path.join(D, "..", "content", "instagram", "posts", f"{DAY}-carousel-01.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("ok", OUT6)
