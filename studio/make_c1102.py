"""11/2 カルーセル「11/1 開催ありがとう」8枚（当日写真なし→過去写真を使用・注記あり）"""
import os
from make_c1105 import *  # helpers & SRC (re-renders c1105, harmless)
OUT2 = os.path.join(D, "out", "c1102"); os.makedirs(OUT2, exist_ok=True)
def save2(c, n):
    page_no(c, n); p = os.path.join(OUT2, f"1102_カルーセル_{n:02d}.png"); c.convert("RGB").save(p, quality=95); return p
def note(c, y=1190):
    put(c, fit(text_img("※写真は過去の開催時のものです", F(BOLD, 30), WHITE)), W / 2, y)
def sched(rows, color):
    out = []
    for dt, tm, vn in rows:
        out.append(step_row("•", dt + "  " + tm, vn, color=color))
    return out

# 1 cover
c = bg("bad", blur=6, dark=0.38)
put(c, fit(shadowed(pill([text_img("11/1(日)", F(BLACK, 60), NAVY)], h=104))), W / 2, 230)
put(c, fit(shadowed(headline("バレー＆バド", "開催しました！", seed=3, size=110))), W / 2, 380)
put(c, fit(shadowed(yellow_band("ご参加ありがとう！", size=130, seed=7))), W / 2, 680)
put(c, fit(shadowed(pill([text_img("次の開催日もまとめました →", F(BLACK, 48), WHITE)], h=100, bg=TEAL))), W / 2, 930)
note(c); save2(c, 1)

# 2 volleyball
c = bg("gym"); head(c, "バレーボール", "＠巣鴨体育館", seed=4)
put(c, card(["11/1(日) 18:00-21:00", "JR巣鴨駅・大塚駅から", "徒歩約10分"], title="開催しました", color=ORANGE), W / 2, 360)
put(c, fit(shadowed(yellow_band("ありがとうございました！", size=86, seed=5))), W / 2, 900)
note(c, 1100); save2(c, 2)

# 3 badminton
c = bg("gym2"); head(c, "バドミントン", "＠目黒区民センター", seed=5)
put(c, card(["11/1(日) 19:00-22:00", "JR・東急 目黒駅から", "徒歩10分"], title="開催しました", color=(17, 151, 65)), W / 2, 360)
put(c, fit(shadowed(yellow_band("ありがとうございました！", size=86, seed=6))), W / 2, 900)
note(c, 1100); save2(c, 3)

# 4 vibe
c = bg("fut"); head(c, "こんな雰囲気で", "開催しています", seed=6)
y = 330
for i, (t, s) in enumerate([("1人参加OK", "ほとんどの方が1人で参加"), ("初心者歓迎", "経験・レベルは問いません"),
                            ("シャッフルゲーム", "メンバーを入れ替えて楽しむ"), ("終わったら解散", "気軽に参加できます")]):
    r = step_row(i + 1, t, s); put(c, r, W / 2, y); y += r.height + 14
save2(c, 4)

# 5 next badminton
c = bg("bad"); head(c, "次のバドミントン", "11月はあと5回", seed=7)
y = 270
for dt, tm, vn in [("11/14(土)", "15:00-17:00", "まもり山テラス"), ("11/15(日)", "13:00-15:00", "代々木の杜"),
                   ("11/26(木)", "18:00-21:00", "まもり山テラス"), ("11/28(土)", "13:00-15:00", "渋谷区本町コミュニティ"),
                   ("11/29(日)", "18:00-21:00", "巣鴨体育館")]:
    r = step_row("●", f"{dt}  {tm}", vn, color=(17, 151, 65)); r = r.resize((int(r.width * .88), int(r.height * .88)), Image.LANCZOS)
    put(c, r, W / 2, y); y += r.height - 40
save2(c, 5)

# 6 next volleyball
c = bg("gym"); head(c, "次のバレーボール", "11月はあと2回", seed=8)
y = 360
for dt, tm, vn in [("11/21(土)", "11:45-13:45", "中野区中部コミュニティプラザ"), ("11/23(月・祝)", "11:45-13:45", "中野区中部コミュニティプラザ")]:
    r = step_row("●", f"{dt}  {tm}", vn, color=ORANGE); put(c, r, W / 2, y); y += r.height + 16
put(c, fit(shadowed(yellow_band("連休も体を動かそう！", size=90, seed=9))), W / 2, y + 60)
save2(c, 6)

# 7 tt / baseball
c = bg("base"); head(c, "卓球・野球", "もあります", seed=9)
y = 360
for dt, tm, vn, col in [("11/22(日)", "17:00-19:00", "野球＠芝公園", BLUE := (21, 101, 192)), ("11/23(月・祝)", "12:20-15:20", "卓球＠大久保プラザ", (21, 101, 192))]:
    r = step_row("●", f"{dt}  {tm}", vn, color=col); put(c, r, W / 2, y); y += r.height + 16
put(c, fit(shadowed(pill([text_img("野球・卓球も初心者OK", F(BLACK, 52), NAVY)], h=110, bg=YEL))), W / 2, y + 60)
save2(c, 7)

# 8 CTA
c = bg("fut", dark=0.45); head(c, "参加方法は", "かんたん3ステップ", seed=11, y=100)
y = 300
for i, (t, s) in enumerate([("公式LINEに登録", "プロフィールのリンクから"), ("参加フォームで申し込み", "LINEメニュー「イベントカレンダーから予約」"),
                            ("合言葉をLINEに送る", "「参加受付証」が届きます")]):
    r = step_row(i + 1, t, s, color=LINE_GREEN); put(c, r, W / 2, y); y += r.height - 40
put(c, fit(shadowed(pill([text_img("参加費 1,500円（現金・PayPay）", F(BLACK, 48), NAVY)], h=100))), W / 2, y + 20)
put(c, fit(shadowed(yellow_band("まだまだ募集中！", size=86, seed=12))), W / 2, y + 150)
save2(c, 8)
print("ok")
