"""11/26(木) 12:00 保存狙いカルーセル「初参加の持ち物チェック」8枚 1080x1350
テーマ案：A 仕事帰りのバド 当日の動き方（例）／B 初参加の持ち物チェック（採用：見返す情報＝保存）／C 11月後半の会場アクセスまとめ
K3（カルーセルの閲覧が落ちた）：11/21 は20:07公開でリーチ16、11/16 は19:00で62 → 今回は昼12:00に出して比べる。
使い方: cd studio && python3 make_c1126.py"""
import os, shutil, json
from make_c1105 import *

OUT7 = os.path.join(D, "out", "c1126"); os.makedirs(OUT7, exist_ok=True)
MEDIA = os.path.join(D, "..", "content", "instagram", "media"); GRN = (17, 151, 65)
DAY = "2026-11-26"


def save7(c, n):
    page_no(c, n); p = os.path.join(OUT7, f"{DAY}_carousel_{n:02d}.jpg"); c.convert("RGB").save(p, quality=93); shutil.copy(p, MEDIA)


def clear(key, dark=0.45): return bg(key, blur=2, dark=dark)


c = clear("court", .40)
put(c, fit(shadowed(pill([text_img("保存して、当日の朝に見返してね", F(BLACK, 44), WHITE)], h=88, bg=RED))), W / 2, 200)
put(c, fit(shadowed(headline("初参加の", "持ち物チェック", seed=3, size=116))), W / 2, 340)
put(c, fit(shadowed(yellow_band("これだけでOK", size=124, seed=7))), W / 2, 650)
put(c, fit(shadowed(pill([text_img("体育館の種目（バド・バレー・卓球）", F(BLACK, 44), NAVY)], h=96))), W / 2, 900)
save7(c, 1)

c = clear("floor"); head(c, "必ず持っていく", "3つ", seed=4)
y = 330
for i, (t, s) in enumerate([("着替え", "動きやすい服"), ("体育館シューズ", "室内用の運動靴"), ("飲み物", "水やスポーツドリンク")]):
    r = step_row(i + 1, t, s, color=TEAL); put(c, r, W / 2, y); y += r.height + 14
save7(c, 2)

c = clear("ceiling"); head(c, "あると便利", "（例）", seed=5)
put(c, card(["タオル", "着替えを入れる袋", "髪をまとめるゴム"], title="あると便利（例）", color=NAVY), W / 2, 330)
save7(c, 3)

c = clear("court"); head(c, "ラケットは", "持っていなくてOK", seed=6)
put(c, fit(shadowed(pill([text_img("バドミントン・卓球はラケット貸出あり", F(BLACK, 50), NAVY)], h=110, bg=YEL))), W / 2, 420)
put(c, card(["自分のラケットがなくても", "そのまま参加できます"], color=GRN, fs=50), W / 2, 600)
save7(c, 4)

c = clear("floor"); head(c, "お金は", "これだけ", seed=7)
put(c, card(["参加費 1,500円", "当日、現金またはPayPay"], title="参加費", color=RED, fs=60), W / 2, 380)
save7(c, 5)

c = clear("ceiling"); head(c, "会場に着いたら", "受付だけ", seed=8)
y = 360
for i, (t, s) in enumerate([("参加受付証を見せる", "LINE に届いた画面でOK"), ("参加費を払う", "1,500円（現金またはPayPay）")]):
    r = step_row(i + 1, t, s, color=TEAL); put(c, r, W / 2, y); y += r.height + 14
save7(c, 6)

c = clear("court"); head(c, "当日は", "こんな流れ（例）", seed=9)
y = 330
for i, (t, s) in enumerate([("受付", "参加受付証を見せて参加費を払う"), ("ストレッチ・基礎練習", "体をほぐしてから"),
                            ("シャッフルゲーム", "メンバーを入れ替えて試合"), ("片付け → 解散", "終わったらそのまま解散")]):
    r = step_row(i + 1, t, s, color=GRN); put(c, r, W / 2, y); y += r.height - 20
save7(c, 7)

c = bg("fut", dark=0.45); head(c, "今週のバドは", "3回", seed=11, y=90)
y = 290
for dt, tm, vn in [("11/26(木)", "18:00-21:00", "まもりやまテラス（新代田駅 徒歩約5分）"), ("11/28(土)", "13:00-15:00", "渋谷区本町コミュニティセンター（初台駅 徒歩約13分）"),
                   ("11/29(日)", "18:00-21:00", "巣鴨体育館（巣鴨駅・大塚駅 徒歩約10分）")]:
    r = step_row("●", f"{dt}  {tm}", vn, color=GRN); r = r.resize((int(r.width * .8), int(r.height * .8)), Image.LANCZOS); put(c, r, W / 2, y); y += r.height - 10
put(c, fit(shadowed(pill([text_img("参加費 1,500円（当日 現金・PayPay）", F(BLACK, 46), NAVY)], h=100))), W / 2, y + 20)
put(c, fit(shadowed(yellow_band("予約は公式LINEから", size=80, seed=12))), W / 2, y + 150)
save7(c, 8)

cap = ("保存しておくと、当日の朝に見返せます📌\n\n初参加の持ち物チェック（体育館の種目）\n"
       "・必ず：着替え・体育館シューズ・飲み物\n・バドミントン・卓球はラケット貸出あり\n・お金は参加費1,500円だけ（当日、現金またはPayPay）\n\n"
       "会場では参加受付証を見せて参加費を払うだけ。当日は 受付 → ストレッチ・基礎練習 → シャッフルゲーム（試合）→ 片付け → 解散（例）。\n\n"
       "今週のバドミントン\n・11/26(木) 18:00-21:00 まもりやまテラス（京王井の頭線 新代田駅から徒歩約5分）\n"
       "・11/28(土) 13:00-15:00 渋谷区本町コミュニティセンター（京王新線 初台駅から徒歩約13分）\n"
       "・11/29(日) 18:00-21:00 巣鴨体育館（JR巣鴨駅・大塚駅から徒歩約10分）\n\n"
       "予約はプロフィールのリンクから公式LINEへ（LINEで @827lnqaq を検索でもOK）\nわからないことはDMでお気軽にどうぞ\n\n"
       "#社会人スポーツ #社会人サークル #バドミントン #持ち物 #初参加 #1人参加 #初心者歓迎 #東京スポーツ #マカシェットスポーツ")
json.dump({"id": f"{DAY}-carousel-01", "type": "carousel", "scheduled_at": f"{DAY}T12:00:00+09:00", "caption": cap,
           "media": [f"{DAY}_carousel_{n:02d}.jpg" for n in range(1, 9)],
           "note": "保存狙いカルーセル「初参加の持ち物チェック」。studio/make_c1126.py。K3：昼12:00に出して 11/21（20:07・リーチ16）と比べる。背景は人が写らない court・ceiling・floor。参加費は5・8枚目。今週のカルーセル2本目"},
          open(os.path.join(D, "..", "content", "instagram", "posts", f"{DAY}-carousel-01.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("ok")
