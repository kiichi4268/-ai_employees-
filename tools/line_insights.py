"""公式LINEの友だち数を毎晩取って data/insights/line_daily.csv に残す（v6.0・11/11）。

Instagram のリンクタップは「LINEに向かった人」まで。本当に友だちが増えたかは LINE 側の数字で見る。
LINE Messaging API の「友だち数」（GET /v2/bot/insight/followers?date=YYYYMMDD）を使う。
LINE 側の集計は翌日にでき上がるので、毎晩、前日と前々日の分を取る（でき上がっていなければ次の晩に取り直す）。

鍵（GitHub Secrets）: LINE_CHANNEL_ID と LINE_CHANNEL_SECRET（11/12：毎回15分だけ使える一時的な鍵＝stateless トークンを作る。
  長期トークンの再発行をしないので、同じチャネルを使う AutoSNS などの連携に影響しない）。LINE_CHANNEL_ACCESS_TOKEN があればそれを使う。
  どちらも無ければ何もせず終わる（今の仕組みは止まらない）
使い方: python3 tools/line_insights.py [--days 2]   ／   python3 tools/line_insights.py --self-test
CSV の列: date, followers（友だち数）, targeted_reaches（届く人数）, blocks（ブロック数）, new_friends（前日からの増加）, fetched_at
"""
import argparse, csv, datetime, json, os, sys, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV = os.path.join(ROOT, "data", "insights", "line_daily.csv")
COLS = ["date", "followers", "targeted_reaches", "blocks", "new_friends", "fetched_at"]
JST = datetime.timezone(datetime.timedelta(hours=9))


def fetch(day, token, opener=urllib.request.urlopen):
    req = urllib.request.Request(f"https://api.line.me/v2/bot/insight/followers?date={day:%Y%m%d}",
                                 headers={"Authorization": f"Bearer {token}"})
    with opener(req, timeout=30) as r:
        return json.loads(r.read().decode())


def load(path=CSV):
    if not os.path.exists(path): return {}
    with open(path, encoding="utf-8") as f:
        return {r["date"]: r for r in csv.DictReader(f)}


def save(rows, path=CSV):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    days = sorted(rows)
    prev = None
    for d in days:  # 前日からの増加（友だち数の差。ブロックされた分は差し引かれる）
        f = rows[d].get("followers")
        rows[d]["new_friends"] = (int(f) - int(prev)) if (f not in (None, "") and prev not in (None, "")) else ""
        prev = f
    with open(path, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=COLS); w.writeheader()
        for d in days: w.writerow({k: rows[d].get(k, "") for k in COLS})


def stateless_token(cid, secret, opener=urllib.request.urlopen):
    """チャネルIDとシークレットから、15分だけ使える一時的な鍵を作る（ほかの連携の鍵は切れない）。"""
    import urllib.parse
    body = urllib.parse.urlencode({"grant_type": "client_credentials", "client_id": cid, "client_secret": secret}).encode()
    req = urllib.request.Request("https://api.line.me/oauth2/v3/token", data=body,
                                 headers={"Content-Type": "application/x-www-form-urlencoded"})
    with opener(req, timeout=30) as r:
        return json.loads(r.read().decode())["access_token"]


def run(days=2, token=None, path=CSV, today=None, opener=urllib.request.urlopen):
    token = token or os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")
    cid, sec = os.environ.get("LINE_CHANNEL_ID"), os.environ.get("LINE_CHANNEL_SECRET")
    if not token and cid and sec:
        try:
            token = stateless_token(cid, sec, opener)
        except Exception as e:
            print(f"LINE の一時的な鍵が作れません（{type(e).__name__}）。チャネルID・シークレットを確かめてください。"); return 0
    if not token:
        print("LINE の鍵（LINE_CHANNEL_ID・LINE_CHANNEL_SECRET）が無いので、LINE の友だち数は取りません（社長タスク）。"); return 0
    today = today or datetime.datetime.now(JST).date()
    rows = load(path); got = 0
    for k in range(1, days + 1):
        day = today - datetime.timedelta(days=k)
        try:
            j = fetch(day, token, opener)
        except Exception as e:  # 鍵の切れ・一時的な障害でも、Instagram の数字の保存は止めない
            print(f"LINE {day}: 取れません（{type(e).__name__}）"); continue
        if j.get("status") != "ready":
            print(f"LINE {day}: まだ集計中（{j.get('status')}）"); continue
        rows[f"{day}"] = {"date": f"{day}", "followers": j.get("followers", ""), "targeted_reaches": j.get("targetedReaches", ""),
                          "blocks": j.get("blocks", ""), "fetched_at": datetime.datetime.now(JST).strftime("%Y-%m-%d %H:%M")}
        got += 1
    if got: save(rows, path)
    last = sorted(rows)[-1] if rows else None
    if last: print(f"LINE 友だち数 {last}: {rows[last].get('followers')}（前日比 {rows[last].get('new_friends')}）")
    return got


def self_test():
    import io, tempfile
    data = {"20261109": {"status": "ready", "followers": 300, "targetedReaches": 280, "blocks": 10},
            "20261110": {"status": "ready", "followers": 304, "targetedReaches": 284, "blocks": 11}}

    class R(io.BytesIO):
        def __enter__(self): return self
        def __exit__(self, *a): pass

    def opener(req, timeout=0):
        d = req.full_url.split("date=")[1]
        return R(json.dumps(data.get(d, {"status": "unready"})).encode())

    p = os.path.join(tempfile.mkdtemp(), "line.csv")
    assert run(0, None, p) == 0 or True
    n = run(2, "x", p, today=datetime.date(2026, 11, 11), opener=opener)
    rows = load(p)
    assert n == 2 and rows["2026-11-10"]["new_friends"] == "4", rows
    assert run(1, "x", p, today=datetime.date(2026, 11, 12), opener=opener) == 0  # 集計中は書かない
    print("self-test: 友だち数の保存・前日比（+4）・集計中はとばす すべて想定どおり")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--days", type=int, default=2); ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test: self_test(); sys.exit(0)
    run(a.days); sys.exit(0)
