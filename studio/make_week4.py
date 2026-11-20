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
DAILY = {}
EXP_NOTE = {}


def post(day, tm, k, name, note):
    import json
    pid = f"2026-11-{day[2:]}-story-{tm}-{k}"
    json.dump({"id": pid, "type": "story", "scheduled_at": f"2026-11-{day[2:]}T{tm[:2]}:{tm[2:]}:00+09:00", "caption": "",
               "media": [name], "note": note}, open(os.path.join(POSTS, pid + ".json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)


if __name__ == "__main__":
    args = sys.argv[1:]
    mode = "daily" if "--daily" in args else "base"
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
                qr_line("予約は", "公式LINEから", sub, p3, bg="floor")
                files += [(tm, 1, p1), (tm, 2, p2), (tm, 3, p3)]
        for tm, k, p in files:
            name = f"2026-11-{day[2:]}_story_{tm}_{k}" + os.path.splitext(p)[1]
            shutil.copy(p, os.path.join(MEDIA, name))
            post(day, tm, k, name, f"4週目ストーリー {day[:2]}/{day[2:]} {tm[:2]}:{tm[2:]} の{k}本目。studio/make_week4.py（③は経路つき QR・ID、参加費は画像内）。改善:K-003 {EXP_NOTE.get(day, '')}".strip())
        print("done", day, len(files), flush=True)
