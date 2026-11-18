"""11/21(土) 保存狙いカルーセル「参加者の声でわかった 初参加の安心5つ」8枚 1080x1350（C3 不安 → 安心）
テーマ案：A 参加者の声でわかった安心5つ（採用：11/18 加藤さんのレビュー取り込み・VOICES.md）／B 初参加の持ち物チェック／C 種目別 はじめての1日（例）
声は言葉を変えず・名前なし・どの開催かを書き・「つなげーとのレビューより」を添える（ai_employees/VOICES.md）。背景は人が写らない court・ceiling・floor。
使い方: cd studio && python3 make_c1121.py → studio/out/c1121/ と content/instagram/media/ に JPG"""
import os, shutil
from make_c1105 import *  # helpers & SRC

OUT5 = os.path.join(D, "out", "c1121"); os.makedirs(OUT5, exist_ok=True)
MEDIA = os.path.join(D, "..", "content", "instagram", "media")
GREEN = (17, 151, 65); BLUE = (21, 101, 192)
SRCNOTE = "つなげーとのレビューより"


def save5(c, n):
    page_no(c, n)
    p = os.path.join(OUT5, f"2026-11-21_carousel_{n:02d}.jpg"); c.convert("RGB").save(p, quality=93)
    shutil.copy(p, MEDIA); return p


def clear(key, dark=0.45):
    return bg(key, blur=2, dark=dark)


def voice_page(n, key, worry, quote, when, fact_title, facts, color):
    c = clear(key)
    put(c, fit(shadowed(pill([text_img(f"不安{n - 2}　{worry}", F(BLACK, 50), WHITE)], h=96, bg=color))), W / 2, 50)
    q = card(quote, title=f"参加した人の声（{when}）", color=NAVY, fs=44, gap=10, pad=36)
    put(c, q, W / 2, 190)
    put(c, fit(pill([text_img(f"※{SRCNOTE}", F(BOLD, 30), WHITE)], h=60, bg=(20, 42, 92, 200))), W / 2, 190 + q.height + 8)
    a = card(facts, title=fact_title, color=color, fs=46, gap=12, pad=34)
    put(c, a, W / 2, min(190 + q.height + 90, H - 110 - a.height))
    save5(c, n)


# 1 表紙
c = clear("court", dark=0.40)
put(c, fit(shadowed(pill([text_img("保存して、申し込む前に見返してね", F(BLACK, 44), WHITE)], h=88, bg=RED))), W / 2, 200)
put(c, fit(shadowed(headline("参加者の声で", "わかった", seed=3, size=116))), W / 2, 340)
put(c, fit(shadowed(yellow_band("初参加の安心5つ", size=124, seed=7))), W / 2, 650)
put(c, fit(shadowed(pill([text_img(SRCNOTE, F(BLACK, 46), NAVY)], h=100))), W / 2, 900)
put(c, fit(shadowed(pill([text_img("ほとんどが1人参加・初心者7割くらい", F(BOLD, 42), WHITE)], h=88, bg=(20, 42, 92, 225)))), W / 2, 1040)
save5(c, 1)

# 2 もう一つの表紙（一覧）
c = clear("floor")
head(c, "不安だったこと", "→ 実際はこう", seed=4)
lst = card(["1 1人で浮かない？", "　→ 同じように1人の人がいる", "2 雰囲気が合うか心配", "　→ 内輪ノリなし・優しい声かけ",
            "3 初心者でついていける？", "　→ ルールやコツを教えてもらえる", "4 人が多くて待つ？", "　→ 待つ時間が少ない", "5 運動不足でも大丈夫？", "　→ ちょうどいい運動に"],
           title="参加した人の声から", color=TEAL, fs=42, gap=6, pad=30)
put(c, lst, W / 2, 300)
save5(c, 2)

# 3〜7 声と事実
voice_page(3, "court", "1人で浮かない？",
           ["初めての参加でしたが、同じように", "1人の参加の方がいて、初心者ですが", "上級者の方とも一緒にダブルス", "できたりして楽しかったです！"],
           "8/15 バド・代々木の杜", "実際は", ["ほとんどが1人参加", "20〜40代の社会人が中心"], TEAL)
voice_page(4, "ceiling", "雰囲気が合うか心配",
           ["初参加でドキドキでしたが、", "内輪ノリとかチャラい感じもなく", "安心しました", "むしろ優しく声かけてくださる", "方ばかりでした！"],
           "9/26 バド・代々木", "実際は", ["上手さより楽しさ", "運営：BARマカシェット"], ORANGE)
voice_page(5, "floor", "初心者でついていける？",
           ["初心者ですが、ルールやコツなど", "教えてくださる人が多くて", "楽しかったです！ありがとうございました。"],
           "8/22 バド・代々木の杜", "実際は", ["初心者7割・経験者3割くらい", "バド・卓球はラケット貸出あり"], GREEN)
voice_page(6, "court", "人が多くて待つ？",
           ["回転率も良かったので人数は", "多かったですが、待つ時間も", "あまりなく最後までずっと", "楽しめました"],
           "7/19 バド・代々木", "当日の流れ（例）", ["受付 → ストレッチ・基礎練習", "→ シャッフルゲーム → 片付け → 解散"], BLUE)
voice_page(7, "ceiling", "運動不足でも大丈夫？",
           ["在宅勤務で鈍った身体解すのに", "バドミントンは丁度よかったです"],
           "8/15 バド・代々木の杜", "持ち物", ["着替え・体育館シューズ・飲み物", "参加費1,500円（当日、現金またはPayPay）"], TEAL)

# 8 まとめ・次の開催・CTA
c = clear("floor", dark=0.5)
head(c, "次の開催", "1人でどうぞ", seed=11, y=50)
b = card(["11/23(月祝) バレー 11:45-13:45 中野区中部スポーツ・コミュニティプラザ", "　新中野駅（4番出口）から徒歩9分",
          "11/23(月祝) 卓球 12:20-15:20 大久保プラザ", "　大久保駅・新大久保駅すぐ",
          "11/26(木) バド 18:00-21:00 まもりやまテラス", "　新代田駅から徒歩約5分",
          "11/28(土) バド 13:00-15:00 渋谷区本町コミュニティセンター", "　初台駅から徒歩約13分",
          "11/29(日) バド 18:00-21:00 巣鴨体育館", "　巣鴨駅・大塚駅から徒歩約10分"],
         title="11月のこれから", color=NAVY, fs=31, gap=4, pad=24)
put(c, b, W / 2, 250)
put(c, fit(shadowed(pill([text_img("参加費1,500円（当日、現金またはPayPay）", F(BLACK, 42), NAVY)], h=90, bg=YEL))), W / 2, 250 + b.height + 24)
put(c, fit(shadowed(pill([text_img("予約はプロフィールのリンクから公式LINEへ", F(BLACK, 44), WHITE)], h=96, bg=LINE_GREEN))), W / 2, 250 + b.height + 132)
save5(c, 8)
print("ok", OUT5)
