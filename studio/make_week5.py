"""5週目（11/30〜12/6）ストーリー 8:00・12:00 の各3本（画像→動画→画像）。11/27 金曜21:30 の回。
- 新しい並べ方（上の札・矢印なし・見出し＋1行＋値段）を 8:00・12:00 にも広げる（11/26〜 で閲覧が落ちなかったため）
- K7（IG_IMPROVE A）：11/30〜12/6 は QR を 10:00・12:00 だけ → 8:00 の③は QR なし（次の開催・質問の答え）、12:00 の③は QR
- 背景は人がプレーする実写（顔が分からない形・全体ぼかし／頭モザイク済み）。10:00・15:00・19:00 は毎晩1日分ずつ（make_week4 と同じ形で別に作る）
使い方: cd studio && python3 make_week5.py [1130 ...]
"""
import os, sys, shutil, json
from make_week4 import FB3, MV, FEE, montage, make_video, as_video, add_music, music_for, qr_line, MEDIA, POSTS, D

OUT = os.path.join(D, "out", "week5"); os.makedirs(OUT, exist_ok=True)
Q = "予約はLINEから・参加費1,500円（当日）"
W = {
 "1130": {"0800": (FB3("b26_court", ["今週末は、", "バドと卓球。"], "土19:00 目黒・日12:20 大久保", mark="今週末", seed=301),
                   MV(["b26_wide", "b26_court", "b26_net"], "今週末、2種目。", ["土 19:00 バド 目黒駅 徒歩10分", "日 12:20 卓球 大久保駅すぐ"]),
                   FB3("ceiling", ["12月は、", "10回あります。"], "最初は 12/5(土) バドミントン", mark="10回", seed=302)),
          "1200": (FB3("floor", ["1人で行くの、", "ちょっと不安？"], "ほとんどが1人参加です", mark="1人", seed=303),
                   MV(["b26_wide", "b26_court", "b26_net"], "ほとんど1人参加。", ["初心者7割・経験者3割くらい", "疲れたら休んでOK"]), "今週末の" + Q)},
 "1201": {"0800": (FB3("b26_wide", ["12月、", "始まりました。"], "最初は 12/5(土) 19:00 バドミントン", mark="12月", seed=311),
                   MV(["b26_court", "b26_wide", "b26_net"], "12月も、体動かそう。", ["12/5(土) 19:00 目黒", "12/6(日) 12:20 大久保"]),
                   FB3("b26_net", ["土曜の夜、", "目黒でバド。"], "19:00-22:00 目黒駅から徒歩10分", mark="目黒", seed=312)),
          "1200": (FB3("b26_rackets", ["ラケット、", "持ってなくてOK。"], "バドミントン・卓球は貸出あり", mark="OK", seed=313),
                   MV(["b26_rackets", "b26_shuttle", "b26_wide"], "道具は、貸出あり。", ["着替え・シューズ・飲み物だけ", "まだ参加枠あります"]), Q)},
 "1202": {"0800": (FB3("b26_court", ["今週末、", "どっちに行く？"], "土 19:00 バド・日 12:20 卓球", mark="どっち", seed=321),
                   MV(["b26_wide", "b26_court", "b26_net"], "土はバド、日は卓球。", ["土 19:00 目黒駅 徒歩10分", "日 12:20 大久保駅すぐ"]),
                   FB3("floor", ["初めての種目でも", "大丈夫？"], "初心者7割・経験者3割くらいです", mark="大丈夫", seed=322)),
          "1200": (FB3("b26_shuttle", ["持ち物は、", "3つだけ。"], "着替え・体育館シューズ・飲み物", mark="3つ", seed=323),
                   MV(["b26_shuttle", "b26_rackets", "b26_wide"], "持ち物は、3つだけ。", ["着替え・シューズ・飲み物", "ラケット貸出あり"]), Q)},
 "1203": {"0800": (FB3("tt", ["卓球は、", "日曜のお昼。"], "12/6(日) 12:20 大久保プラザ", mark="卓球", seed=331),
                   MV(["tt", "play_gym", "tt"], "日曜のお昼に、卓球。", ["12:20-15:20 大久保プラザ", "大久保駅・新大久保駅すぐ"]),
                   FB3("ceiling", ["土曜の夜は、", "バドもあります。"], "12/5(土) 19:00 目黒駅 徒歩10分", mark="バド", seed=332)),
          "1200": (FB3("floor", ["当日の流れ", "（例）"], "受付→基礎練習→試合→片付け", mark="流れ", seed=333),
                   MV(["b26_wide", "b26_court", "b26_net"], "当日の流れ（例）", ["受付 → ストレッチ・基礎練習", "→ シャッフルゲーム → 解散"]), Q)},
 "1204": {"0800": (FB3("b26_court", ["明日の夜は、", "バドミントン。"], "12/5(土) 19:00 目黒区民センター", mark="明日", seed=341),
                   MV(["b26_wide", "b26_court", "b26_net"], "明日の夜、バド。", ["19:00-22:00 目黒駅 徒歩10分", "まだ参加枠あります"]),
                   FB3("b26_rackets", ["ラケットは、", "貸出あり。"], "手ぶらに近い形で来られます", mark="貸出", seed=342)),
          "1200": (FB3("b26_wide", ["仕事のあと、", "体動かしません？"], "初心者7割・経験者3割くらい", mark="体", seed=343),
                   MV(["b26_net", "b26_wide", "b26_court"], "金曜の次は、土曜の夜。", ["12/5 19:00 目黒", "12/6 12:20 大久保"]), "明日の" + Q)},
 "1205": {"0800": (FB3("b26_court", ["今日の夜は、", "バドミントン。"], "19:00-22:00 目黒駅から徒歩10分", mark="今日", seed=351),
                   MV(["b26_wide", "b26_court", "b26_net"], "今日19時、バド。", ["目黒区民センター", "まだ参加枠あります"]),
                   FB3("floor", ["明日のお昼は、", "卓球です。"], "12/6(日) 12:20 大久保駅すぐ", mark="卓球", seed=352)),
          "1200": (FB3("b26_wide", ["疲れたら、", "休んで大丈夫。"], "ほとんどが1人参加です", mark="休んで", seed=353),
                   MV(["b26_court", "b26_net", "b26_wide"], "今日の夜、目黒で。", ["19:00-22:00", "ラケット貸出あり"]), "今日の" + Q)},
 "1206": {"0800": (FB3("tt", ["今日のお昼は、", "卓球。"], "12:20-15:20 大久保プラザ", mark="今日", seed=361),
                   MV(["tt", "play_gym", "tt"], "今日12時20分、卓球。", ["大久保駅・新大久保駅すぐ", "まだ参加枠あります"]),
                   FB3("ceiling", ["次の週末は、", "バド2回。"], "12/12(土) 15:00・12/13(日) 18:00", mark="バド", seed=362)),
          "1200": (FB3("tt", ["卓球、", "久しぶりでも。"], "ラケット貸出あり・初心者7割くらい", mark="久しぶり", seed=363),
                   MV(["tt", "play_gym", "tt"], "久しぶりでも、大丈夫。", ["ラケット貸出あり", "疲れたら休んでOK"]), "今日の" + Q)},
}


def post(day, tm, k, name):
    mm, dd = ("11", day[2:]) if day.startswith("11") else ("12", day[2:])
    pid = f"2026-{mm}-{dd}-story-{tm}-{k}"
    note = f"5週目ストーリー {mm}/{dd} {tm[:2]}:{tm[2:]} の{k}本目。studio/make_week5.py（新しい並べ方・K7：QR は 12:00 だけ／8:00 の③は QR なし・参加費は画像内）。改善:K-003"
    json.dump({"id": pid, "type": "story", "scheduled_at": f"2026-{mm}-{dd}T{tm[:2]}:{tm[2:]}:00+09:00", "caption": "", "media": [name], "note": note},
              open(os.path.join(POSTS, pid + ".json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    return mm, dd


if __name__ == "__main__":
    for day in (sys.argv[1:] or list(W)):
        dd_ = os.path.join(OUT, day); os.makedirs(dd_, exist_ok=True)
        for tm, (a, b, c) in W[day].items():
            p1, p2, p3 = (os.path.join(dd_, f"{day}_{tm}_{k}.{e}") for k, e in ((1, "jpg"), (2, "mp4"), (3, "jpg")))
            a[0](**a[1]).save(p1, quality=93)
            montage(path=p2, **b[1]); n, s = music_for(tm, day); add_music(p2, n, start=s)
            if isinstance(c, tuple): c[0](**c[1]).save(p3, quality=93)
            else: qr_line("予約は", "公式LINEから", c, p3, bg="floor")
            for k, p in ((1, p1), (2, p2), (3, p3)):
                mm = "11" if day.startswith("11") else "12"
                name = f"2026-{mm}-{day[2:]}_story_{tm}_{k}" + os.path.splitext(p)[1]
                shutil.copy(p, os.path.join(MEDIA, name)); post(day, tm, k, name)
        print("done", day, flush=True)
