"""11/28(土)・11/29(日) 開催日の朝のフィード「今日開催・まだ参加者募集中！」各1枚 1080x1350（人が写らない背景）
使い方: cd studio && python3 make_f1128.py"""
import os, shutil, json
from make_c1105 import *

MEDIA = os.path.join(D, "..", "content", "instagram", "media")
POSTS = os.path.join(D, "..", "content", "instagram", "posts")
BLUE = (21, 101, 192)
TAGS = "#社会人スポーツ #社会人サークル #1人参加 #初心者歓迎 #東京スポーツ #マカシェットスポーツ"


def feed(day, label, sport_hl, events, chip, key, color, cap_head, cap_events, cap_points, tags, seed):
    c = bg(key, blur=2, dark=0.42)
    put(c, fit(shadowed(pill([text_img(f"今日 {label}", F(BLACK, 64), WHITE)], h=112, bg=RED))), W / 2, 120)
    put(c, fit(shadowed(headline(sport_hl, "開催します", seed=3, size=116))), W / 2, 270)
    put(c, fit(shadowed(yellow_band("まだ参加者募集中！", size=108, seed=7))), W / 2, 500)
    y = 660
    for title, lines, col in events:
        k = card(lines, title=title, color=col, fs=36 if len(events[0][1]) > 3 else 48, gap=6 if len(events[0][1]) > 3 else 10, pad=24 if len(events[0][1]) > 3 else 30); put(c, k, W / 2, y); y += k.height + 12
    put(c, fit(shadowed(pill([text_img(chip, F(BLACK, 42), NAVY)], h=92, bg=YEL))), W / 2, min(y + 14, 1150))
    h = text_img("@macachette_sports", F(BOLD, 34), WHITE); c.alpha_composite(h, (40, H - h.height - 40))
    from tools.craft import finish
    name = f"2026-11-{day}_feed_01.jpg"
    p = os.path.join(D, "out", name); finish(c.convert("RGB"), seed=seed).save(p, quality=93); shutil.copy(p, MEDIA)
    cap = (f"{cap_head}\nまだ参加者募集中！\n\n{cap_events}\n\n" + "\n".join("・" + x for x in cap_points) +
           "\n\n参加費1,500円（当日、現金またはPayPay）\n申し込みはプロフィールのリンクから公式LINEへ\nわからないことはDMでお気軽にどうぞ\n\n" + f"{tags} {TAGS}")
    post = {"id": f"2026-11-{day}-feed-01", "type": "feed", "scheduled_at": f"2026-11-{day}T09:00:00+09:00", "caption": cap,
            "media": [name], "note": "開催日の朝のフィード（studio/make_f1128.py）。人が写らない背景。参加費は画像内（下の黄色）とキャプション"}
    json.dump(post, open(os.path.join(POSTS, f"2026-11-{day}-feed-01.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print("ok", p)


feed("28", "11/28(土)", "バドミントン",
     [("11/28(土) バドミントン", ["13:00-15:00", "渋谷区本町コミュニティセンター", "京王新線 初台駅から徒歩約13分"], (17, 151, 65))],
     "1人参加OK／ラケット貸出／参加費1,500円", "floor", (17, 151, 65),
     "今日 11/28(土) バドミントン開催します🏸", "⏰13:00-15:00\n📍渋谷区本町コミュニティセンター（京王新線 初台駅から徒歩約13分／都営大江戸線 西新宿五丁目駅から徒歩約12分）",
     ["ほとんどが1人参加", "初心者7割・経験者3割くらい", "ラケット貸出あり"], "#バドミントン #バドミントンサークル #初台 #渋谷", 28)
feed("29", "11/29(日)", "バドミントン",
     [("11/29(日) バドミントン", ["18:00-21:00", "巣鴨体育館", "JR巣鴨駅・大塚駅から徒歩約10分"], (17, 151, 65))],
     "1人参加OK／ラケット貸出／参加費1,500円", "ceiling", (17, 151, 65),
     "今日 11/29(日) バドミントン開催します🏸", "⏰18:00-21:00\n📍巣鴨体育館（JR巣鴨駅・大塚駅から徒歩約10分）",
     ["ほとんどが1人参加", "初心者7割・経験者3割くらい", "ラケット貸出あり"], "#バドミントン #バドミントンサークル #巣鴨", 29)
