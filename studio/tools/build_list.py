import asyncio, os
from playwright.async_api import async_playwright

OUT = os.path.join(os.path.dirname(__file__), "out")
os.makedirs(OUT, exist_ok=True)

SPORT = {
    "バド":  ("バドミントン", "#F2994A", "#fff"),
    "バレー": ("バレー",     "#F2C94C", "#3a2a00"),
    "卓球":  ("卓球",       "#EB5757", "#fff"),
    "野球":  ("野球",       "#27AE60", "#fff"),
}
EVENTS = [
    ("11/1", "日", "バレー", "18:00-21:00", "巣鴨体育館"),
    ("11/1", "日", "バド", "19:00-22:00", "目黒区民センター"),
    ("11/3", "火・祝", "卓球", "12:20-15:20", "大久保プラザ"),
    ("11/7", "土", "バド", "15:00-17:00", "まもり山テラス"),
    ("11/15", "日", "バド", "13:00-15:00", "代々木の杜"),
    ("11/21", "土", "バレー", "11:45-13:45", "中野区中部コミュニティプラザ"),
    ("11/22", "日", "野球", "17:00-19:00", "芝公園"),
    ("11/23", "月・祝", "バレー", "11:45-13:45", "中野区中部コミュニティプラザ"),
    ("11/23", "月・祝", "卓球", "12:20-15:20", "大久保プラザ"),
    ("11/26", "木", "バド", "18:00-21:00", "まもり山テラス"),
    ("11/28", "土", "バド", "13:00-15:00", "渋谷区本町コミュニティ"),
    ("11/29", "日", "バド", "18:00-21:00", "巣鴨体育館"),
]

BASE_CSS = """
*{margin:0;padding:0;box-sizing:border-box}
body{width:1080px;height:1350px;overflow:hidden;font-family:'Noto Sans CJK JP';color:#123a6b;
 background:linear-gradient(170deg,#2f86d9 0%,#5aa9ea 45%,#a8d5f6 100%);position:relative}
.cloud{position:absolute;border-radius:50%;background:#fff;filter:blur(40px);opacity:.55}
.panel{position:absolute;left:60px;right:60px;top:60px;bottom:60px;border-radius:44px;
 background:rgba(255,255,255,.18);border:2px solid rgba(255,255,255,.7);
 box-shadow:0 20px 60px rgba(10,50,110,.18);padding:56px 56px 40px}
.brand{font-family:'Noto Serif CJK JP';letter-spacing:.35em;color:#fff;font-size:24px;text-align:center;opacity:.95}
h1{font-family:'Noto Serif CJK JP';font-weight:900;color:#fff;text-align:center;font-size:68px;margin-top:14px;
 text-shadow:0 3px 14px rgba(10,50,110,.35)}
.sub{color:#fff;text-align:center;font-size:28px;margin-top:10px;font-weight:700;letter-spacing:.06em}
.line{height:2px;background:rgba(255,255,255,.8);margin:26px 40px}
.foot{position:absolute;left:0;right:0;bottom:30px;text-align:center;color:#fff;font-family:'Noto Serif CJK JP';
 font-size:24px;letter-spacing:.12em}
.tag{display:inline-block;border-radius:999px;font-weight:900;font-size:24px;padding:6px 0;width:170px;text-align:center}
"""
CLOUDS = """
<div class="cloud" style="width:520px;height:260px;left:-120px;top:120px"></div>
<div class="cloud" style="width:600px;height:300px;right:-160px;top:620px"></div>
<div class="cloud" style="width:480px;height:240px;left:120px;bottom:-60px"></div>
"""

def tag(k):
    name, bg, fg = SPORT[k]
    return f'<span class="tag" style="background:{bg};color:{fg}">{name}</span>'

def page(body, extra_css=""):
    return f"<html><head><meta charset='utf-8'><style>{BASE_CSS}{extra_css}</style></head><body>{CLOUDS}<div class='panel'>{body}</div><div class='foot'>@macachette_sports</div></body></html>"

# --- slide 2: full list
rows = ""
for d, w, s, t, v in EVENTS:
    holiday = "祝" in w
    wcol = "#d64545" if (holiday or w == "日") else ("#2f6fd1" if w == "土" else "#123a6b")
    rows += f"""<div class="row"><div class="date">{d}<span style="color:{wcol}">({w})</span></div>
    {tag(s)}<div class="info"><div class="time">{t}</div><div class="venue">{v}</div></div></div>"""
list_css = """
.panel{padding:40px 48px 40px}
.rows{margin-top:0;display:flex;flex-direction:column;gap:7px}
.row{display:flex;align-items:center;gap:20px;background:rgba(255,255,255,.92);border-radius:18px;padding:6px 22px;height:70px}
.date{width:230px;font-weight:900;font-size:34px;white-space:nowrap}
.date span{font-size:22px;margin-left:4px}
.info{display:flex;flex-direction:column;flex:1;min-width:0;line-height:1.15}
.time{font-weight:900;font-size:27px;white-space:nowrap}
.venue{font-size:21px;font-weight:700;color:#3d5f88;white-space:nowrap}
h1{font-size:62px;margin-top:6px}
"""
s2 = page(f"""<div class="brand">MACACHETTE_SPORTS</div><h1>11月の開催日程</h1>
<div class="sub">全12回｜一人参加・初心者歓迎</div><div class="line" style="margin:16px 40px 16px"></div>
<div class="rows">{rows}</div>""", list_css)

# --- slide 3: by sport
def blk(k):
    evs = [e for e in EVENTS if e[2] == k]
    items = "".join(f"<li><b>{d}({w})</b> {t}<br><span>{v}</span></li>" for d, w, s, t, v in evs)
    name, bg, fg = SPORT[k]
    return f"""<div class="blk"><div class="bh" style="background:{bg};color:{fg}">{name}<small>{len(evs)}回</small></div><ul>{items}</ul></div>"""
sport_css = """
.grid{display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-top:4px}
.col{display:flex;flex-direction:column;gap:20px}
.col:first-child .blk{height:100%}
.col:first-child li{padding:22px 0;font-size:26px}
.blk{background:rgba(255,255,255,.92);border-radius:24px;overflow:hidden}
.bh{font-weight:900;font-size:34px;padding:14px 24px;display:flex;justify-content:space-between;align-items:baseline}
.bh small{font-size:24px}
ul{list-style:none;padding:12px 24px 18px}
li{font-size:24px;line-height:1.35;padding:8px 0;border-bottom:1px dashed #c9d8ea}
li:last-child{border-bottom:none}
li span{font-size:20px;color:#3d5f88;font-weight:700}
"""
s3 = page(f"""<div class="brand">MACACHETTE_SPORTS</div><h1>種目別でチェック</h1>
<div class="sub">気になる種目の日程を保存しておこう</div><div class="line"></div>
<div class="grid"><div class="col">{blk("バド")}</div><div class="col">{blk("バレー")}{blk("卓球")}{blk("野球")}</div></div>""", sport_css)

# --- slide 4: how to join
howto_css = """
.card{background:rgba(255,255,255,.93);border-radius:26px;padding:32px 38px;margin-top:26px}
.card h3{font-size:30px;font-weight:900;color:#1f6fd1;margin-bottom:8px}
.card p{font-size:31px;font-weight:700;line-height:1.5}
.cta{margin-top:44px;background:#06C755;color:#fff;border-radius:999px;text-align:center;font-size:36px;font-weight:900;padding:24px 10px;
 box-shadow:0 10px 24px rgba(0,90,40,.25)}
.small{color:#fff;text-align:center;font-size:24px;margin-top:16px;font-weight:700}
"""
s4 = page("""<div class="brand">MACACHETTE_SPORTS</div><h1>参加のしかた</h1>
<div class="sub">はじめての方も、ひとりでも大丈夫</div><div class="line"></div>
<div class="card"><h3>参加費</h3><p>1,500円<br>当日、現金またはPayPay</p></div>
<div class="card"><h3>持ち物</h3><p>着替え・体育館シューズ<br>（バドミントンはラケット貸出あり）</p></div>
<div class="card"><h3>雰囲気</h3><p>参加者の多くが一人参加・初心者<br>上手さより楽しさ重視です</p></div>
<div class="cta">予約は公式LINEの「EVENT」から</div>
<div class="small">プロフィールのリンクからLINEへ｜ご不明点はDMでどうぞ</div>""", howto_css)

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])
        pg = await b.new_page(viewport={"width": 1080, "height": 1350})
        for name, html in [("02_日程一覧", s2), ("03_種目別", s3), ("04_参加のしかた", s4)]:
            await pg.set_content(html)
            await pg.wait_for_timeout(300)
            await pg.screenshot(path=f"{OUT}/1031_11月一覧_{name}.png")
        await b.close()

asyncio.run(main())
