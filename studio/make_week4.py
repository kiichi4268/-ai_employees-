"""4週目（11/23〜11/29）ストーリー：週の予約は 8:00・12:00 の各3本（画像→動画→画像。③は QR と ID）。
- 10:00・19:00 は毎晩の日次PDCAのあと DAILY に書いて1日分ずつ作る（11/13 加藤さん）。
- 8:00＝開催の案内（今日・今週）／12:00＝安心材料（1人参加・初心者7割・ラケット貸出・当日の流れ）。
- 背景は人がプレーしている実写（顔は頭だけモザイク・または全体ぼかし）。過去写真の注記は入れない（11/19 加藤さん）。参加費は画像内。
使い方: cd studio && python3 make_week4.py --base ／ python3 make_week4.py --daily 1124
"""
import os, sys, shutil
import make_week3 as w3
from make_week3 import (w1, event_card, card_lines, make_image, make_video, add_music, music_for, qr_line, people_bg,
                        montage, full_bleed, collage, FB, CL, MV, GREEN, ORANGE, BLUE, MEDIA, POSTS, D, as_video)

OUT = os.path.join(D, "out", "week4"); os.makedirs(OUT, exist_ok=True)
FEE = "参加費1,500円（当日）"

VB23 = event_card("バレーボール", ORANGE, "11/23(月祝)", "11:45-13:45", "中野区中部スポーツ・コミュニティプラザ", "新中野駅（4番出口）から徒歩9分")
TT23 = event_card("卓球", BLUE, "11/23(月祝)", "12:20-15:20", "大久保プラザ", "大久保駅・新大久保駅すぐ")
BD26 = event_card("バドミントン", GREEN, "11/26(木)", "18:00-21:00", "まもりやまテラス", "京王井の頭線 新代田駅から徒歩約5分")
BD28 = event_card("バドミントン", GREEN, "11/28(土)", "13:00-15:00", "渋谷区本町コミュニティセンター", "京王新線 初台駅から徒歩約13分")
BD29 = event_card("バドミントン", GREEN, "11/29(日)", "18:00-21:00", "巣鴨体育館", "JR巣鴨駅・大塚駅から徒歩約10分")

# (日, 8:00 画像, 8:00 動画, 8:00 ③, 12:00 画像, 12:00 動画, 12:00 ③)
WEEK = [
 ("1123", dict(h1="今日は", h2="バレーと卓球", blocks=[VB23, TT23], bg="ceiling"),
  dict(src="ceiling", h1="今日", h2="祝日2種目", lines=["バレー 11:45〜 新中野", "卓球 12:20〜 大久保"]),
  ("今日の", "予約は", FEE),
  dict(h1="1人で", h2="来ていい？", blocks=[card_lines(["ほとんどが1人参加", "初心者7割・経験者3割くらい", "卓球はラケット貸出あり", FEE])], bg="floor"),
  dict(src="floor", h1="1人参加が", h2="ほとんど", lines=["初心者7割・経験者3割くらい", "まだ参加枠あります"]),
  ("1人でも", "公式LINEから", FEE)),
 ("1124", dict(h1="今週は", h2="バド3回", blocks=[BD26], bg="court"),
  dict(src="court", h1="今週", h2="バドミントン", lines=["木 18:00 新代田", "土 13:00 初台・日 18:00 巣鴨"]),
  ("今週の", "予約は", FEE),
  dict(h1="バドは", h2="初めてでも", blocks=[card_lines(["初心者7割・経験者3割くらい", "ラケット貸出あり", "上手さより楽しさ", FEE])], bg="floor"),
  dict(src="floor", h1="初めてでも", h2="大丈夫", lines=["ラケット貸出あり", "初心者7割・経験者3割くらい"]),
  ("まずは", "公式LINEへ", FEE)),
 ("1125", dict(h1="明日の夜は", h2="バドミントン", blocks=[BD26], bg="court"),
  dict(src="court", h1="明日 18:00", h2="バド", lines=["まもりやまテラス", "新代田駅から徒歩約5分"]),
  ("明日の", "予約は", FEE),
  dict(h1="持ち物は", h2="少なめ", blocks=[card_lines(["着替え・体育館シューズ・飲み物", "ラケットは貸出あり", FEE + "・現金またはPayPay"])], bg="ceiling"),
  dict(src="ceiling", h1="持ち物", h2="これだけ", lines=["着替え・シューズ・飲み物", "ラケット貸出あり"]),
  ("仕事帰りに", "公式LINEから", FEE)),
 ("1126", dict(h1="今日の夜は", h2="バドミントン", blocks=[BD26], bg="court"),
  dict(src="court", h1="今日 18:00", h2="バド", lines=["まだ参加枠あります", "新代田駅から徒歩約5分"]),
  ("今日の", "予約は", FEE),
  dict(h1="仕事帰りに", h2="1人で", blocks=[card_lines(["ほとんどが1人参加", "20〜40代の社会人が中心", "ラケット貸出あり", FEE])], bg="floor"),
  dict(src="floor", h1="仕事帰りに", h2="体を動かす", lines=["ほとんどが1人参加", "ラケット貸出あり"]),
  ("今日の予約も", "公式LINEから", FEE)),
 ("1127", dict(h1="週末は", h2="バド2回", blocks=[BD28, BD29], bg="ceiling"),
  dict(src="ceiling", h1="週末", h2="バドミントン", lines=["土 13:00 初台", "日 18:00 巣鴨"]),
  ("週末の", "予約は", FEE),
  dict(h1="当日の流れ", h2="（例）", blocks=[card_lines(["受付 → ストレッチ・基礎練習", "→ シャッフルゲーム（試合）", "→ 片付け → 解散", FEE])], bg="floor"),
  dict(src="floor", h1="当日の流れ", h2="（例）", lines=["受付 → 基礎練習", "→ シャッフルゲーム → 解散"]),
  ("週末の予定は", "公式LINEから", FEE)),
 ("1128", dict(h1="今日は", h2="バドミントン", blocks=[BD28], bg="court"),
  dict(src="court", h1="今日 13:00", h2="バド", lines=["渋谷区本町コミュニティセンター", "初台駅から徒歩約13分"]),
  ("今日の", "予約は", FEE),
  dict(h1="明日も", h2="バドミントン", blocks=[BD29], bg="ceiling"),
  dict(src="ceiling", h1="明日 18:00", h2="巣鴨", lines=["巣鴨駅・大塚駅から徒歩約10分", "ラケット貸出あり"]),
  ("明日の", "予約は", FEE)),
 ("1129", dict(h1="今日の夜は", h2="バドミントン", blocks=[BD29], bg="court"),
  dict(src="court", h1="今日 18:00", h2="巣鴨", lines=["まだ参加枠あります", "巣鴨駅・大塚駅から徒歩約10分"]),
  ("今日の", "予約は", FEE),
  dict(h1="日曜の夜、", h2="1人で", blocks=[card_lines(["ほとんどが1人参加", "初心者7割・経験者3割くらい", "ラケット貸出あり", FEE])], bg="floor"),
  dict(src="floor", h1="日曜の夜に", h2="いい汗を", lines=["初心者7割・経験者3割くらい", "ラケット貸出あり"]),
  ("今夜の予約も", "公式LINEから", FEE)),
]
# その日の②の背景（人がプレーしている実写）：8:00, 12:00
BASE_BG = {"1123": ("play_vb", "play_vb2"), "1124": ("b14_court", "b14_wide"), "1125": ("b14_wide", "play_bad"),
           "1126": ("play_bad", "b14_court"), "1127": ("b14_court", "play_bad"), "1128": ("b14_wide", "b14_court"), "1129": ("play_bad", "b14_wide")}
DAILY = {
 # 11/23(月祝・バレー11:45／卓球12:20)：10:00＝今日のお昼2種目／19:00＝次は木曜 11/26 バド（仕事帰り）
 "1123": {
  "1000": (FB("play_vb", "今日 11/23(月祝)", ["お昼から、", "2種目。"], ["バレー 11:45 新中野駅4番出口 徒歩9分", "卓球 12:20 大久保駅・新大久保駅すぐ", "参加費1,500円（当日）"], mark="今日", seed=231),
           MV(["play_vb", "play_vb2", "play_vb"], "お昼から、2種目。", ["バレー 11:45・卓球 12:20", "まだ参加枠あります"]), "今日の予約はLINEから・参加費1,500円（当日）"),
  "1900": (FB("play_bad", "次は 11/26(木) 18:00-21:00", ["木曜18時、", "バド。"], ["まもりやまテラス 新代田駅 徒歩約5分", "ラケット貸出あり・仕事帰りに", "参加費1,500円（当日）"], mark="次", seed=232),
           MV(["play_bad", "b14_court", "play_bad"], "木曜18時、バド。", ["新代田駅 徒歩約5分", "ラケット貸出あり"]), "木曜の予約はLINEから・参加費1,500円（当日）"),
 },
 "1124": {
  "1000": (FB("b14_court", "今週 11/26(木)・28(土)・29(日)", ["今週は、", "バド3回。"], ["木 18:00 新代田駅 徒歩約5分", "土 13:00 初台・日 18:00 巣鴨", "参加費1,500円（当日）"], mark="今週", seed=241),
           MV(["b14_court", "play_bad", "b14_wide"], "今週は、バド3回。", ["木・土・日", "ラケット貸出あり"]), "今週の予約はLINEから・参加費1,500円（当日）"),
  "1500": (FB("play_bad", "休憩のあとに、ひと息", ["1人で", "来ていい？"], ["ほとんどが1人参加", "初心者7割・経験者3割くらい", "参加費1,500円（当日）"], mark="Q", seed=242),
           MV(["play_bad", "b14_wide", "play_bad"], "1人で来ていい？", ["ほとんどが1人参加", "ラケット貸出あり"]), "1人でも予約はLINEから・参加費1,500円（当日）"),
  "1900": (FB("b14_wide", "あさって 11/26(木) 18:00-21:00", ["木曜は、", "仕事帰りにバド。"], ["まもりやまテラス 新代田駅 徒歩約5分", "着替え・体育館シューズ・飲み物だけ", "参加費1,500円（当日）"], mark="木", seed=243),
           MV(["b14_wide", "play_bad", "b14_court"], "木曜は、仕事帰りにバド。", ["18:00 新代田駅 徒歩約5分", "まだ参加枠あります"]), "木曜の予約はLINEから・参加費1,500円（当日）"),
 },
 "1125": {
  "1000": (FB("play_bad", "明日 11/26(木) 18:00-21:00", ["明日18時、", "バド。"], ["まもりやまテラス 新代田駅 徒歩約5分", "ラケット貸出あり", "参加費1,500円（当日）"], mark="明日", seed=251),
           MV(["play_bad", "b14_court", "play_bad"], "明日18時、バド。", ["新代田駅 徒歩約5分", "まだ参加枠あります"]), "明日の予約はLINEから・参加費1,500円（当日）"),
  "1500": (FB("b14_wide", "休憩のあとに、ひと息", ["持ち物、", "なにがいる？"], ["着替え・体育館シューズ・飲み物", "ラケットは貸出あり", "参加費1,500円（当日）"], mark="Q", seed=252),
           MV(["b14_wide", "play_bad", "b14_court"], "持ち物、なにがいる？", ["着替え・シューズ・飲み物", "ラケット貸出あり"]), "持ち物が分かったら予約はLINEから・参加費1,500円（当日）"),
  "1900": (FB("b14_court", "バドに参加した人の声（つなげーとのレビューより）", ["「在宅勤務で鈍った", "身体解すのに", "バドミントンは", "丁度よかったです」"], ["明日 11/26(木) 18:00 新代田駅 徒歩約5分", "ほとんどが1人参加", "参加費1,500円（当日）"], mark="声", seed=253),
           MV(["b14_court", "play_bad", "b14_wide"], "明日は、仕事帰りにバド。", ["18:00 まもりやまテラス", "ほとんどが1人参加"]), "明日の予約はLINEから・参加費1,500円（当日）"),
 },
}
# 11/25 の夜から：新しい並べ方（上の札と矢印なし・見出し＋1行＋値段の3つまで）と K7（QR は 8:00・19:00 だけ。ほかの③は質問の答えか次の開催）
QR_SLOTS = ("0800", "1900")
def FB3(key, lines, line, mark=None, seed=1):
    return (full_bleed, dict(key=key, kicker=None, lines=lines, chips=[line, FEE], mark=mark, seed=seed, brand=False))
DAILY["1126"] = {
  "1000": (FB3("play_bad", ["今日18時、", "バドどうですか？"], "まもりやまテラス 新代田駅 徒歩約5分", mark="今日", seed=261),
           MV(["play_bad", "b14_court", "play_bad"], "今日18時、バド。", ["新代田駅 徒歩約5分", "まだ参加枠あります"]),
           FB3("floor", ["1人で行っても", "大丈夫？"], "ほとんどが1人参加です", mark="1人", seed=264)),
  "1500": (FB3("b14_wide", ["仕事終わりに、", "体動かしません？"], "今日18:00 着替え・シューズ・飲み物だけ", mark="体", seed=262),
           MV(["b14_wide", "play_bad", "b14_court"], "仕事終わりに、バド。", ["ラケット貸出あり", "初心者7割・経験者3割くらい"]),
           FB3("ceiling", ["週末も、", "バド2回。"], "土13:00 初台・日18:00 巣鴨", mark="週末", seed=265)),
  "1900": (FB3("b14_court", ["疲れたら、", "休んで大丈夫。"], "次は 11/28(土) 13:00 初台駅 徒歩約13分", mark="休んで", seed=263),
           MV(["b14_court", "play_bad", "b14_wide"], "週末は、バド2回。", ["土 13:00 初台", "日 18:00 巣鴨"]), "週末の予約はLINEから・参加費1,500円（当日）"),
}
# 12:00 の③（金曜に QR で作った分）を 11/26〜29 は QR なしに作り直す（K7）
NOON3 = {"1126": FB3("floor", ["今日の夜、", "1人でもどうぞ。"], "18:00 まもりやまテラス", mark="1人", seed=266),
         "1127": FB3("ceiling", ["週末の流れは", "こんな感じ（例）"], "受付→基礎練習→試合→片付け", mark="流れ", seed=267),
         "1128": FB3("ceiling", ["明日の夜も", "バドあります。"], "日18:00 巣鴨駅・大塚駅 徒歩約10分", mark="明日", seed=268),
         "1129": FB3("floor", ["日曜の夜、", "1人でもどうぞ。"], "初心者7割・経験者3割くらい", mark="1人", seed=269)}
EXP_NOTE = {"1125": "実験:D-1125（改善2個・5日周期の2日目）①15:00 は質問の見出しを続ける（持ち物）②19:00 で参加者の声の見出しを3晩ぶりに戻して、11/22〜24 の普通の見出しと比べる", "1124": "実験:D-1124（改善1個・5日周期の1日目）①15:00 の枠を新しく出す（休憩明け向け・1人参加の不安に答える）。10:00・19:00 は前の日の型（短い見出し・①②の言葉をそろえる）のまま", "1123": "実験:D-1123（改善5個）①見出し1行8文字前後を続ける ②①と②の動画の1行目を同じ言葉に（style.md・K1）③19時は次の開催（木曜バド）を仕事帰り向けに ④19時の声の見出しはもう1晩休んで比べる ⑤ラケット貸出をチップに"}
EXP_NOTE["1126"] = "実験:D-1126（改善3個・5日周期の3日目）①新しい並べ方（上の札・矢印なし、見出し＋1行＋値段）②話しかける見出し（加藤さんの言葉「疲れたら休んで大丈夫」）③K7：QR は 19:00 だけ、10:00・15:00 の③は質問の答え・次の開催"


def post(day, tm, k, name, note):
    import json
    pid = f"2026-11-{day[2:]}-story-{tm}-{k}"
    json.dump({"id": pid, "type": "story", "scheduled_at": f"2026-11-{day[2:]}T{tm[:2]}:{tm[2:]}:00+09:00", "caption": "",
               "media": [name], "note": note}, open(os.path.join(POSTS, pid + ".json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)


if __name__ == "__main__":
    args = sys.argv[1:]
    mode = "daily" if "--daily" in args else "base"
    if "--noon" in args:  # 12:00 の③だけ QR なしに作り直す（K7）
        for day in [a for a in args if not a.startswith("--")]:
            dd = os.path.join(OUT, day); os.makedirs(dd, exist_ok=True); p3 = os.path.join(dd, f"{day}_1200_3.jpg")
            NOON3[day][0](**NOON3[day][1]).save(p3, quality=93)
            shutil.copy(p3, os.path.join(MEDIA, f"2026-11-{day[2:]}_story_1200_3.jpg")); print("noon3", day)
        sys.exit(0)
    only = [a for a in args if not a.startswith("--")]
    days = [w[0] for w in WEEK]
    for day in (only or days):
        dd = os.path.join(OUT, day); os.makedirs(dd, exist_ok=True); files = []
        if mode == "base":
            _, img8, vid8, l8, img12, vid12, l12 = next(w for w in WEEK if w[0] == day)
            for tm, img, vid, line in (("0800", img8, vid8, l8), ("1200", img12, vid12, l12)):
                p1, p2, p3 = (os.path.join(dd, f"{day}_{tm}_{n}.{e}") for n, e in ((1, "jpg"), (2, "mp4"), (3, "jpg")))
                k = BASE_BG[day][0 if tm == "0800" else 1]
                make_image(dict(img, bg=k), p1); make_video(dict(vid, src=k, blur=1), p2)
                _n, _s = music_for(tm, day); add_music(p2, _n, start=_s)
                qr_line(*line, p3)
                files += [(tm, 1, p1), (tm, 2, p2), (tm, 3, p3)]
        else:
            for tm, (a, b, sub) in DAILY[day].items():
                p1, p2, p3 = (os.path.join(dd, f"{day}_{tm}_{k}.{e}") for k, e in ((1, "jpg"), (2, "mp4"), (3, "jpg")))
                a[0](**a[1]).save(p1, quality=93)
                if b[0] == "montage": montage(path=p2, **b[1])
                else: make_video(as_video(b, "court"), p2)
                _n, _s = music_for(tm, day); add_music(p2, _n, start=_s)
                if isinstance(sub, tuple): sub[0](**sub[1]).save(p3, quality=93)  # K7：QR なしの③
                else: qr_line("予約は", "公式LINEから", sub, p3, bg="floor")
                files += [(tm, 1, p1), (tm, 2, p2), (tm, 3, p3)]
        for tm, k, p in files:
            name = f"2026-11-{day[2:]}_story_{tm}_{k}" + os.path.splitext(p)[1]
            shutil.copy(p, os.path.join(MEDIA, name))
            post(day, tm, k, name, f"4週目ストーリー {day[:2]}/{day[2:]} {tm[:2]}:{tm[2:]} の{k}本目。studio/make_week4.py（③は経路つき QR・ID、参加費は画像内）。改善:K-003 {EXP_NOTE.get(day, '')}".strip())
        print("done", day, len(files), flush=True)
