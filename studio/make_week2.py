"""2週目（11/9〜11/15）ストーリー63本：各枠 ①画像 ②動画 ③仕掛け。
朝8:00・昼12:00は自動投稿（③は kind="line"＝スタンプなし）。夜（平日・日20:00／金土21:00）は加藤さんが手動でスタンプを付ける。
週のテーマ：「週末バド2連続（11/14・15）に向けて、不安を減らして公式LINEで予約」。
使い方: python3 studio/make_week2.py [1109 ...]  → studio/out/week2/"""
import os, csv, sys
import make_week1 as w1
from make_week1 import (card_lines, event_card, yellow_band, make_image, make_video, make_ix, GREEN, ORANGE, TEAL, LINE_GREEN, D)

OUT = os.path.join(D, "out", "week2"); os.makedirs(OUT, exist_ok=True)

BAD14 = event_card("バドミントン", GREEN, "11/14(土)", "15:00-17:00", "まもり山テラス")
BAD15 = event_card("バドミントン", GREEN, "11/15(日)", "13:00-15:00", "代々木の杜", "JR代々木駅から徒歩5分")
NEXT = card_lines(["11/21(土) バレー 中野", "11/22(日) 野球 芝公園", "11/23(月祝) バレー・卓球", "11/26(木) バド まもり山テラス",
                   "11/28(土) バド 渋谷", "11/29(日) バド 巣鴨"], title="11月の後半", color=ORANGE)
JOIN = card_lines(["① 公式LINEに登録", "② イベントカレンダーから予約", "③ 合言葉をLINEに送る", "④ 参加受付証が届く"], title="申し込みの流れ", color=TEAL)
LINE = lambda h1, h2, sub=None, bg="gym2": dict(kind="line", h1=h1, h2=h2, sub=sub, bg=bg, opts="（自動・スタンプなし）")

SLOTS = [
 # 11/9(月)
 ("1109", "0800", dict(h1="今週末は", h2="バド2連続！", blocks=[BAD14, BAD15], bg="bad"),
  dict(src="clipA", ss=12, h1="今週末は", h2="バドミントン", lines=["11/14(土) まもり山テラス", "11/15(日) 代々木の杜"]),
  LINE("予約は", "公式LINEから", "11/14・15 受付中", bg="bad")),
 ("1109", "1200", dict(h1="1人参加", h2="でも大丈夫？", blocks=[card_lines(["参加者のほとんどが", "1人で参加しています", "初心者7割・経験者3割くらい"])], bg="bad"),
  dict(src="clipB", ss=24, h1="1人でも", h2="浮かない", lines=["ほとんどが1人参加", "上手さより楽しさ重視"]),
  LINE("まずは", "LINEで相談", "わからないことはDMでもOK")),
 ("1109", "2000", dict(h1="バドミントン", h2="経験ある？", blocks=[card_lines(["はじめての方も", "久しぶりの方も歓迎", "ラケット貸出あり"])], bg="bad"),
  dict(src="clipA", ss=20, h1="ラケット", h2="貸出あり", lines=["手ぶらでOK", "初心者さん大歓迎"]),
  dict(kind="poll", h1="バドミントン", h2="経験ある？", opts="投票：ある／はじめて", bg="bad")),
 # 11/10(火)
 ("1110", "0800", dict(h1="今週末の", h2="開催", blocks=[BAD14, BAD15], bg="bad"),
  dict(src="clipB", ss=30, h1="11/14・15", h2="バド2連続", lines=["土 15:00 まもり山テラス", "日 13:00 代々木の杜"]),
  LINE("週末の予定に", "入れよう", "予約は公式LINEから", bg="bad")),
 ("1110", "1200", dict(h1="持ち物", h2="チェック", blocks=[card_lines(["・着替え", "・体育館シューズ", "・飲み物", "（バドはラケット貸出あり）"])], bg="gym"),
  dict(src="gym", h1="これだけ", h2="あればOK", lines=["着替え", "体育館シューズ", "飲み物"]),
  LINE("準備は", "これだけ", "詳しくはDMでお気軽にどうぞ", bg="gym")),
 ("1110", "2000", dict(h1="気になること", h2="ある？", blocks=[card_lines(["1人参加のこと", "レベルのこと", "当日のこと、なんでもどうぞ"])], bg="gym"),
  dict(src="clipA", ss=36, h1="不安は", h2="聞いてOK", lines=["質問にはストーリーで答えます"]),
  dict(kind="question", h1="不安なこと", h2="教えて", sub="なんでも答えます！", bg="gym", opts="質問スタンプ")),
 # 11/11(水)
 ("1111", "0800", dict(h1="今週末は", h2="2日連続！", blocks=[BAD14, BAD15], bg="bad"),
  dict(src="clipA", ss=44, h1="どっちでも", h2="参加OK", lines=["土曜も日曜も開催", "両日の参加も歓迎"]),
  LINE("予約は", "公式LINEから", "11/14・15 バド", bg="bad")),
 ("1111", "1200", dict(h1="当日の流れ", h2="（例）", blocks=[card_lines(["① 受付", "② ストレッチ・基礎練習", "③ シャッフルゲーム（試合）", "④ 片付け → 解散"])], bg="gym"),
  dict(src="clipB", ss=40, h1="当日は", h2="こんな感じ", lines=["受付 → ストレッチ", "シャッフルゲーム", "片付け → 解散"]),
  LINE("流れが分かれば", "安心", "詳しくはDMでお気軽にどうぞ", bg="gym")),
 ("1111", "2000", dict(h1="どっちに", h2="行く？", blocks=[BAD14, BAD15], bg="bad"),
  dict(src="clipB", ss=50, h1="土曜？", h2="日曜？", lines=["11/14(土) 15:00-17:00", "11/15(日) 13:00-15:00"]),
  dict(kind="poll", h1="どっちに", h2="行きたい？", opts="投票：11/14(土)／11/15(日)", bg="bad")),
 # 11/12(木)
 ("1112", "0800", dict(h1="週末まで", h2="あと2日", blocks=[BAD14, BAD15], bg="bad"),
  dict(src="clipA", ss=52, h1="週末は", h2="体を動かそう", lines=["11/14・15 バドミントン", "初心者さん大歓迎"]),
  LINE("予約は", "公式LINEから", "まだ参加枠あります", bg="bad")),
 ("1112", "1200", dict(h1="申し込みは", h2="かんたん", blocks=[JOIN], bg="navy"),
  dict(src="ref", ss=6, h1="申し込みは", h2="かんたん", lines=["予約 → 合言葉 → 受付証"], lower=True),
  LINE("まずは", "LINE登録", "プロフィールのリンクから", bg="navy")),
 ("1112", "2000", dict(h1="どんな人が", h2="参加してる？", blocks=[card_lines(["20〜40代の社会人", "ほとんどが1人参加", "初心者7割・経験者3割くらい"])], bg="gym"),
  dict(src="clipB", ss=56, h1="参加者は", h2="こんな人", lines=["20〜40代の社会人", "ほとんどが1人参加"]),
  dict(kind="quiz", h1="クイズ", sub="初心者の割合は？", opts="クイズ：3割／5割／7割くらい（正解）", bg="gym")),
 # 11/13(金)
 ("1113", "0800", dict(h1="明日は", h2="バドミントン！", blocks=[BAD14, card_lines(["ラケット貸出あり"])], bg="bad"),
  dict(src="clipA", ss=58, h1="明日", h2="バド開催", lines=["11/14(土) 15:00-17:00", "まもり山テラス"]),
  LINE("予約は", "公式LINEから", "明日 11/14(土) 15:00〜", bg="bad")),
 ("1113", "1200", dict(h1="参加費の", h2="こと", blocks=[card_lines(["1,500円", "当日、現金またはPayPay"], title="参加費", color=TEAL)], bg="gym"),
  dict(src="gym2", h1="当日は", h2="受付証を見せるだけ", lines=["参加費1,500円", "現金またはPayPay"]),
  LINE("受付証は", "LINEで届く", "予約は公式LINEから", bg="gym")),
 ("1113", "2100", dict(h1="明日・明後日", h2="バド2連続", blocks=[BAD14, BAD15], bg="bad"),
  dict(src="clipB", ss=20, h1="今週末", h2="バド2連続", lines=["11/14(土) まもり山テラス", "11/15(日) 代々木の杜"]),
  dict(kind="link", h1="申し込みは", h2="公式LINEから", sub="11/14・15 バド受付中", opts="リンク：公式LINE", bg="bad")),
 # 11/14(土) 開催日
 ("1114", "0800", dict(h1="本日", h2="開催！", blocks=[BAD14, yellow_band("まだ参加枠あります", size=80)], bg="bad"),
  dict(src="clipA", ss=12, h1="今日は", h2="バドミントン", lines=["15:00-17:00", "まもり山テラス"]),
  LINE("今日の参加も", "LINEから", "15:00〜 まもり山テラス", bg="bad")),
 ("1114", "1200", dict(h1="手ぶらで", h2="OK！", blocks=[card_lines(["ラケット貸出あり", "着替え・体育館シューズ・飲み物", "があれば大丈夫"])], bg="bad"),
  dict(src="clipB", ss=30, h1="このあと", h2="15:00〜", lines=["まもり山テラス", "初心者さん大歓迎"]),
  LINE("まだ", "間に合います", "予約は公式LINEから", bg="bad")),
 ("1114", "2100", dict(h1="明日も", h2="開催！", blocks=[BAD15, card_lines(["ラケット貸出あり"])], bg="bad"),
  dict(src="clipA", ss=44, h1="明日は", h2="代々木の杜", lines=["11/15(日) 13:00-15:00", "JR代々木駅から徒歩5分"]),
  dict(kind="link", h1="明日の参加は", h2="公式LINEから", sub="11/15(日) 13:00〜", opts="リンク：公式LINE", bg="bad")),
 # 11/15(日) 開催日
 ("1115", "0800", dict(h1="本日", h2="開催！", blocks=[BAD15, yellow_band("まだ参加枠あります", size=80)], bg="bad"),
  dict(src="clipB", ss=40, h1="今日は", h2="バドミントン", lines=["13:00-15:00 代々木の杜", "JR代々木駅から徒歩5分"]),
  LINE("今日の参加も", "LINEから", "13:00〜 代々木の杜", bg="bad")),
 ("1115", "1200", dict(h1="このあと", h2="13:00〜", blocks=[BAD15], bg="bad"),
  dict(src="clipA", ss=52, h1="1人でも", h2="大丈夫", lines=["ほとんどが1人参加", "ラケット貸出あり"]),
  LINE("まだ", "間に合います", "予約は公式LINEから", bg="bad")),
 ("1115", "2000", dict(h1="次の開催は", h2="こちら", blocks=[NEXT], bg="gym2"),
  dict(src="cal", blur=0, focus=(0.5, 0.55), h1="11月後半も", h2="開催します", lines=["保存して予定に入れよう"], lower=True),
  dict(kind="poll", h1="次に行きたい", h2="種目は？", opts="投票：バド／バレー／卓球／野球", bg="gym2")),
]

# ---------- 11/8 作り直し：人が写らないくっきり背景＋リンクタップを増やす③（PIPELINE.md「デザインの決まり」） ----------
BG = {"bad": "court", "gym": "floor", "gym2": "ceiling"}   # 人が写る写真の強いぼかし → 人が写っていない背景
STEP3 = card_lines(["① プロフィールのリンクをタップ", "② 公式LINEを友だち追加", "③ イベントカレンダーから予約"], title="申し込みは3ステップ", color=LINE_GREEN)


def restyle(img, vid, ix):
    img = dict(img, bg=BG.get(img.get("bg", "gym"), img.get("bg", "gym")))
    vid = dict(vid)
    if vid["src"] in BG.values() or vid["src"] in BG:
        vid.update(src=BG.get(vid["src"], vid["src"]), blur=1)
    ix = dict(ix, bg=BG.get(ix.get("bg", "gym2"), ix.get("bg", "gym2")))
    return img, vid, ix


def make_line(spec, path):
    """③（自動・スタンプなし）：リンクタップへの道筋を3ステップで見せる。"""
    c = w1.still_bg(spec.get("bg", "ceiling"), dark=0.5)
    w1.place(c, w1.hl(spec["h1"], spec.get("h2", ""), seed=spec.get("seed", 5), size=120), w1.W / 2, 270)
    if spec.get("sub"):
        w1.place(c, w1.fit(w1.shadowed(w1.pill([w1.text_img(spec["sub"], w1.F(w1.BLACK, 46), w1.NAVY)], h=90))), w1.W / 2, 560)
    w1.place(c, STEP3, w1.W / 2, 720)
    w1.place(c, w1.fit(w1.shadowed(w1.pill([w1.text_img("↖ プロフィールのリンクから", w1.F(w1.BLACK, 52), w1.WHITE)], h=110, bg=LINE_GREEN))), w1.W / 2, 1230)
    w1.foot(c); c.convert("RGB").save(path, quality=93)


if __name__ == "__main__":
    only = sys.argv[1:]
    rows = []
    for day, tm, img, vid, ix in SLOTS:
        if only and day not in only: continue
        if os.environ.get("ONLY_AUTO") and tm not in ("0800", "1200"): continue  # 夜は作らない（11/6 決定）
        dd = os.path.join(OUT, day); os.makedirs(dd, exist_ok=True)
        p1 = os.path.join(dd, f"{day}_{tm}_1.jpg"); p2 = os.path.join(dd, f"{day}_{tm}_2.mp4"); p3 = os.path.join(dd, f"{day}_{tm}_3.jpg")
        img, vid, ix = restyle(img, vid, ix)
        make_image(img, p1); make_video(vid, p2); (make_line if ix["kind"] == "line" else make_ix)(ix, p3)
        rows.append([day, f"{tm[:2]}:{tm[2:]}", os.path.basename(p1), os.path.basename(p2), os.path.basename(p3), ix["opts"]])
        print("done", day, tm, flush=True)
    if not only:
        with open(os.path.join(OUT, "予約一覧.csv"), "w", encoding="utf-8-sig", newline="") as f:
            w = csv.writer(f); w.writerow(["日付", "時間", "1本目（画像）", "2本目（動画）", "3本目（仕掛け）", "3本目に付けるスタンプ"]); w.writerows(rows)
