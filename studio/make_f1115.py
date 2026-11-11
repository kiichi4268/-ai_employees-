"""11/15(日) 開催日の朝のフィード「今日開催・まだ参加者募集中！」1枚 1080x1350（人が写らない背景）
使い方: cd studio && python3 make_f1114.py"""
import os, shutil
from make_c1105 import *

MEDIA = os.path.join(D, "..", "content", "instagram", "media"); GREEN = (17, 151, 65)
c = bg("floor", blur=2, dark=0.42)
put(c, fit(shadowed(pill([text_img("今日 11/15(日)", F(BLACK, 64), WHITE)], h=112, bg=RED))), W / 2, 120)
put(c, fit(shadowed(headline("バドミントン", "開催します", seed=3, size=120))), W / 2, 270)
put(c, fit(shadowed(yellow_band("まだ参加者募集中！", size=120, seed=7))), W / 2, 540)
put(c, card(["13:00-15:00", "代々木の杜", "JR代々木駅から徒歩5分"], title="11/15(日) バドミントン", color=GREEN, fs=50, gap=14), W / 2, 730)
put(c, fit(shadowed(pill([text_img("1人参加・初心者歓迎／ラケット貸出あり", F(BLACK, 44), NAVY)], h=96, bg=YEL))), W / 2, 1135)
h = text_img("@macachette_sports", F(BOLD, 34), WHITE); c.alpha_composite(h, (40, H - h.height - 40))
from tools.craft import finish
p = os.path.join(D, "out", "2026-11-15_feed_01.jpg"); finish(c.convert("RGB"), seed=15).save(p, quality=93); shutil.copy(p, MEDIA); print("ok", p)
