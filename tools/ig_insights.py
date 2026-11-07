#!/usr/bin/env python3
"""Instagram の数字（インサイト）を毎晩取り、data/insights/ の CSV に残す。あわせて鍵が生きているかを確かめる。

GitHub Actions（.github/workflows/ig_insights.yml）から毎晩 23:50 に動く。Claude のコネクタは使わない
（投稿と同じ GitHub Secrets の鍵で、Instagram の公式APIを直接呼ぶ。だから設定し直しが要らない）。

使い方:
  python3 tools/ig_insights.py                 # 直近3日分のアカウントの数字と、直近14日の投稿・今出ているストーリーの数字を取る
  python3 tools/ig_insights.py --days 7        # アカウントの数字を7日分取り直す（数字は最大48時間遅れて確定するため）
  python3 tools/ig_insights.py --token-only    # 鍵の確認だけ
  python3 tools/ig_insights.py --self-test     # 通信なしの動作確認

出力（同じ日・同じ投稿の行は上書き。消えたストーリーの行は残る）:
  data/insights/account_daily.csv   日付ごと：閲覧・リーチ・反応・保存・シェア・リンクタップ・フォロワー数など
  data/insights/media.csv           投稿ごと：種類・投稿日時・閲覧・リーチ・保存・シェア・いいね・コメント など
  ※ストーリーの数字は出てから24時間しか取れない。毎晩23:50に取れば、その日の8:00・12:00・夜の分がすべて間に合う。

鍵（環境変数・GitHub Secrets）: INSTAGRAM_ACCESS_TOKEN・INSTAGRAM_USER_ID（必須）、CHATWORK_API_TOKEN（通知）、
  META_APP_ID・META_APP_SECRET（任意。入れると鍵の有効期限・データ利用期限まで確かめられる）
DRY_RUN=1 のときは ChatWork に送らず、CSV も書かない（画面に出すだけ）。
"""

import argparse
import csv
import datetime
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import chatwork_notify  # noqa: E402
import run_queue as q  # noqa: E402

JST = q.JST
OUT = ROOT / "data" / "insights"
ACCOUNT_METRICS = ["views", "reach", "accounts_engaged", "total_interactions", "likes", "comments",
                   "saves", "shares", "replies", "profile_links_taps", "profile_views"]
MEDIA_METRICS = {  # 種類ごとに取れる数字（取れないものは空欄になるだけで止まらない）
    "FEED": ["views", "reach", "saved", "shares", "likes", "comments", "total_interactions", "profile_visits", "follows"],
    "REELS": ["views", "reach", "saved", "shares", "likes", "comments", "total_interactions",
              "ig_reels_avg_watch_time", "ig_reels_video_view_total_time"],  # 滞留（平均視聴ミリ秒）
    "STORY": ["views", "reach", "replies", "shares", "total_interactions", "profile_visits", "follows"],
}
ACCOUNT_COLS = ["date", "followers"] + ACCOUNT_METRICS + ["reach_follower", "reach_non_follower", "home_rate", "fetched_at"]
MEDIA_COLS = ["id", "kind", "posted_at", "permalink", "caption_head"] + sorted(
    {m for ms in MEDIA_METRICS.values() for m in ms}) + ["fetched_at"]
WARN_DAYS = 14  # 鍵の期限がこれより近づいたら知らせる


def api(path, **params):
    params["access_token"] = q.need("INSTAGRAM_ACCESS_TOKEN")
    return q.http("GET", f"{q.META_API}/{path}", params=params)


def tell(text, dry):
    token = os.environ.get("CHATWORK_API_TOKEN")
    if dry or not token:
        print(f"  ChatWork（{'DRY_RUN のため送らない' if dry else '鍵がないため送らない'}）:\n{text}")
        return
    try:
        chatwork_notify.send({"room_id": chatwork_notify.room_id(), "body": text}, token)
    except Exception as e:  # 通知の失敗で止めない
        print(f"  ChatWork への通知に失敗: {chatwork_notify.mask(str(e))}")


# ---------------------------------------------------------------------------
# 鍵の確認（設定し直しを防ぐ：切れる前に知らせる）
# ---------------------------------------------------------------------------
FIX_STEPS = ("直し方（5分）：Mac で `python3 tools/get_tokens.py instagram` を実行 ➔ 表示された INSTAGRAM_ACCESS_TOKEN を "
             "GitHub の Settings ➔ Secrets and variables ➔ Actions で上書き（チャットには貼らない）。"
             "META_ACCESS_TOKEN が切れている場合は、先に Meta のグラフAPIエクスプローラで取り直して .env に入れる。")


def check_token(now):
    """鍵が使えるか・期限はいつかを調べる。戻り値：(ok, 知らせる文 or None, 画面用の文)"""
    ig = q.need("INSTAGRAM_USER_ID")
    try:
        me = api(ig, fields="username,followers_count")
    except q.ApiError as err:
        if err.code == "missing_token":
            return False, None, f"✗ 鍵が未登録: {err.message}"
        bad = err.code == "190" or err.http_status in (400, 401)
        head = "鍵が使えなくなっています" if bad else "Instagram に接続できませんでした"
        return False, (f"[info][title]【Instagram】{head}（自動投稿・数字の取得が止まります）[/title]"
                       f"{err}\n{FIX_STEPS if bad else '一時的な障害の可能性。次の回で自動的に再確認します。'}[/info]"), f"✗ {head}: {err}"
    line = f"✓ 鍵 OK（@{me.get('username', '?')}・フォロワー {me.get('followers_count', '?')}）"
    app_id, app_secret = os.environ.get("META_APP_ID"), os.environ.get("META_APP_SECRET")
    if not (app_id and app_secret):
        return True, None, line + "（期限の確認は META_APP_ID・META_APP_SECRET を入れると有効）"
    try:
        info = q.http("GET", f"{q.META_API}/debug_token", params={
            "input_token": q.need("INSTAGRAM_ACCESS_TOKEN"), "access_token": f"{app_id}|{app_secret}"}).get("data", {})
    except q.ApiError as err:
        return True, None, line + f"（期限は確認できず: {err}）"
    warn = []
    for key, label in (("expires_at", "鍵の有効期限"), ("data_access_expires_at", "データ利用の期限")):
        ts = int(info.get(key) or 0)
        if ts == 0:
            line += f"／{label}: なし"
            continue
        left = (datetime.datetime.fromtimestamp(ts, JST) - now).days
        line += f"／{label}: あと{left}日"
        if left <= WARN_DAYS:
            warn.append(f"{label}まで あと{left}日（{datetime.datetime.fromtimestamp(ts, JST):%m/%d}）")
    if not info.get("is_valid", True):
        warn.append("鍵が無効と判定されました")
    msg = (f"[info][title]【Instagram】鍵の期限が近づいています[/title]" + "\n".join(warn) + f"\n{FIX_STEPS}[/info]") if warn else None
    return True, msg, line


# ---------------------------------------------------------------------------
# 数字を取る
# ---------------------------------------------------------------------------
def totals(metrics, since, until):
    """アカウントの数字（metric_type=total_value）。まとめて1回で聞き、だめなら1つずつ聞く。取れないものは ''。"""
    ig = q.need("INSTAGRAM_USER_ID")
    base = dict(period="day", metric_type="total_value", since=int(since.timestamp()), until=int(until.timestamp()))

    def parse(res):
        out = {}
        for d in res.get("data", []):
            tv = d.get("total_value") or {}
            if "value" in tv:
                out[d.get("name")] = tv["value"]
        return out
    try:
        got = parse(api(f"{ig}/insights", metric=",".join(metrics), **base))
        return {m: got.get(m, "") for m in metrics}
    except q.ApiError:
        pass
    out = {}
    for m in metrics:
        try:
            out[m] = parse(api(f"{ig}/insights", metric=m, **base)).get(m, "")
        except q.ApiError as err:
            print(f"  - {m}: 取れず（{err.message[:80]}）")
            out[m] = ""
    return out


def home_rate(since, until):
    """ホーム率：その日のリーチのうちフォロワーの割合（follow_type の内訳）。取れなければ空欄。"""
    ig = q.need("INSTAGRAM_USER_ID")
    try:
        res = api(f"{ig}/insights", metric="reach", period="day", metric_type="total_value", breakdown="follow_type",
                  since=int(since.timestamp()), until=int(until.timestamp()))
    except q.ApiError:
        return {}
    got = {}
    for d in res.get("data", []):
        for b in (d.get("total_value") or {}).get("breakdowns", []):
            for r in b.get("results", []):
                got[(r.get("dimension_values") or [""])[0].upper()] = r.get("value", 0)
    f, n = got.get("FOLLOWER"), got.get("NON_FOLLOWER")
    if f is None or n is None or f + n == 0:
        return {}
    return {"reach_follower": f, "reach_non_follower": n, "home_rate": round(f / (f + n), 3)}


def online_followers():
    """フォロワーがよく見ている時間帯（0〜23時の人数）。ストーリーの時刻を決める材料。取れなければ空。"""
    try:
        res = api(f"{q.need('INSTAGRAM_USER_ID')}/insights", metric="online_followers", period="lifetime")
    except q.ApiError:
        return []
    vals = ((res.get("data") or [{}])[0].get("values") or [{}])[0].get("value") or {}
    return [{"hour": f"{int(h):02d}", "followers": v} for h, v in sorted(vals.items(), key=lambda x: int(x[0]))]


def account_rows(now, days):
    rows = []
    today = now.astimezone(JST).date()
    followers = ""
    try:
        followers = api(q.need("INSTAGRAM_USER_ID"), fields="followers_count").get("followers_count", "")
    except q.ApiError as err:
        print(f"  - followers_count: 取れず（{err.message[:80]}）")
    for i in range(days):
        day = today - datetime.timedelta(days=i)
        since = datetime.datetime.combine(day, datetime.time(0, 0), JST)
        until = min(since + datetime.timedelta(days=1), now)
        row = {"date": day.isoformat(), "followers": followers if i == 0 else None, "fetched_at": f"{now:%Y-%m-%d %H:%M}"}
        row.update(totals(ACCOUNT_METRICS, since, until))
        row.update(home_rate(since, until))
        rows.append(row)
    return rows


def media_insights(mid, kind):
    metrics = MEDIA_METRICS[kind]

    def parse(res):
        return {d.get("name"): ((d.get("values") or [{}])[0].get("value", "")) for d in res.get("data", [])}
    try:  # まとめて1回
        got = parse(api(f"{mid}/insights", metric=",".join(metrics)))
        return {m: got.get(m, "") for m in metrics}
    except q.ApiError:
        pass
    out = {}
    for m in metrics:  # だめなら1つずつ（1つ取れなくても他は取れる）
        try:
            out[m] = parse(api(f"{mid}/insights", metric=m)).get(m, "")
        except q.ApiError:
            out[m] = ""
    return out


def media_rows(now, recent_days=14):
    ig = q.need("INSTAGRAM_USER_ID")
    items = []
    feed = api(f"{ig}/media", fields="id,media_type,media_product_type,timestamp,caption,permalink", limit=30)
    for x in feed.get("data", []):
        posted = datetime.datetime.strptime(x["timestamp"], "%Y-%m-%dT%H:%M:%S%z")
        if now - posted <= datetime.timedelta(days=recent_days):
            kind = "REELS" if x.get("media_product_type") == "REELS" else "FEED"
            items.append((x, kind, f"{kind.lower()}:{x.get('media_type', '').lower()}"))
    for x in api(f"{ig}/stories", fields="id,media_type,timestamp,permalink").get("data", []):
        items.append((x, "STORY", "story"))
    rows = []
    for x, kind, label in items:
        posted = datetime.datetime.strptime(x["timestamp"], "%Y-%m-%dT%H:%M:%S%z").astimezone(JST)
        row = {"id": x["id"], "kind": label, "posted_at": f"{posted:%Y-%m-%d %H:%M}", "permalink": x.get("permalink", ""),
               "caption_head": (x.get("caption") or "").replace("\n", " ")[:30], "fetched_at": f"{now:%Y-%m-%d %H:%M}"}
        row.update(media_insights(x["id"], kind))
        rows.append(row)
    return rows


# ---------------------------------------------------------------------------
# CSV（同じキーの行は上書き。空欄では上書きしない）
# ---------------------------------------------------------------------------
def upsert(path, cols, key, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    old = {}
    if path.exists():
        with path.open(encoding="utf-8") as f:
            for r in csv.DictReader(f):
                old[r[key]] = r
    for r in rows:
        cur = old.get(r[key], {})
        for c in cols:
            v = r.get(c)
            if v not in (None, ""):
                cur[c] = v
        cur[key] = r[key]
        old[r[key]] = cur
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        for k in sorted(old):
            w.writerow({c: old[k].get(c, "") for c in cols})


def summary_text(now, acc, media):
    today = acc[0] if acc else {}
    stories = [m for m in media if m["kind"] == "story" and m["posted_at"].startswith(f"{now:%Y-%m-%d}")]
    best = sorted([m for m in media if m["kind"] != "story" and str(m.get("saved", "")).isdigit()],
                  key=lambda m: -int(m["saved"]))[:3]
    lines = [f"閲覧 {today.get('views', '?')}／リーチ {today.get('reach', '?')}／リンクタップ {today.get('profile_links_taps', '?')}"
             f"／保存 {today.get('saves', '?')}／フォロワー {today.get('followers', '?')}"]
    if stories:
        lines.append("ストーリー（時刻：閲覧）：" + "、".join(f"{s['posted_at'][11:]} {s.get('views', '?')}" for s in sorted(stories, key=lambda s: s["posted_at"])))
    if best:
        lines.append("保存が多い投稿（14日）：" + "、".join(f"{b['caption_head'][:12]}… {b['saved']}" for b in best))
    lines.append("※数字は最大48時間遅れて確定します（毎晩3日分を取り直します）")
    return f"[info][title]【Instagram】今日の数字 {now:%m/%d}[/title]" + "\n".join(lines) + "[/info]"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=3)
    ap.add_argument("--token-only", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--now")
    args = ap.parse_args()
    if args.self_test:
        return self_test()
    dry = os.environ.get("DRY_RUN", "0") != "0"
    now = datetime.datetime.fromisoformat(args.now) if args.now else datetime.datetime.now(JST)
    now = now if now.tzinfo else now.replace(tzinfo=JST)
    ok, alert, line = check_token(now)
    print(line)
    if alert:
        tell(alert, dry)
    if not ok:
        sys.exit(1)
    if args.token_only:
        return
    acc = account_rows(now, args.days)
    media = media_rows(now)
    print(f"アカウント {len(acc)}日分・投稿 {len(media)}件")
    if acc and all(acc[0].get(m) in ("", None) for m in ACCOUNT_METRICS):
        tell("[info][title]【Instagram】数字が1つも取れませんでした[/title]鍵に instagram_manage_insights の権限が無い可能性があります。"
             "Meta のグラフAPIエクスプローラで instagram_manage_insights にチェックを入れて META_ACCESS_TOKEN を取り直し、"
             "`python3 tools/get_tokens.py instagram` ➔ GitHub Secrets を上書きしてください（フォロワー100人未満の数字・48時間以内の数字は空のことがあります）。[/info]", dry)
    if not dry:
        upsert(OUT / "account_daily.csv", ACCOUNT_COLS, "date", acc)
        upsert(OUT / "media.csv", MEDIA_COLS, "id", media)
        hours = online_followers()
        if hours:
            upsert(OUT / "online_followers.csv", ["hour", "followers", "fetched_at"], "hour",
                   [dict(h, fetched_at=f"{now:%Y-%m-%d %H:%M}") for h in hours])
    tell(summary_text(now, acc, media), dry)


# ---------------------------------------------------------------------------
# 通信なしの動作確認
# ---------------------------------------------------------------------------
def self_test():
    import tempfile
    global OUT
    real = (OUT, q.http)
    OUT = Path(tempfile.mkdtemp())
    os.environ.setdefault("INSTAGRAM_ACCESS_TOKEN", "test")
    os.environ.setdefault("INSTAGRAM_USER_ID", "1")
    now = datetime.datetime(2026, 11, 10, 23, 50, tzinfo=JST)
    calls = []

    def fake(method, url, params=None, **kw):
        calls.append(url)
        if url.endswith("/debug_token"):
            return {"data": {"is_valid": True, "expires_at": 0, "data_access_expires_at": int((now + datetime.timedelta(days=10)).timestamp())}}
        if url.endswith("/1") or url.endswith("/1?"):
            return {"username": "macachette_sports", "followers_count": 300}
        if url.endswith("/1/insights"):
            if "replies" in params["metric"].split(","):
                raise q.ApiError(400, "not supported", "100")
            return {"data": [{"name": m, "total_value": {"value": 10}} for m in params["metric"].split(",")]}
        if url.endswith("/1/media"):
            return {"data": [{"id": "r1", "media_type": "VIDEO", "media_product_type": "REELS", "timestamp": "2026-11-06T12:05:00+0000", "caption": "1人参加Q&A"},
                             {"id": "old", "media_type": "IMAGE", "media_product_type": "FEED", "timestamp": "2026-10-01T00:00:00+0000"}]}
        if url.endswith("/1/stories"):
            return {"data": [{"id": "s1", "media_type": "IMAGE", "timestamp": "2026-11-09T23:05:00+0000"}]}
        if url.endswith("/insights"):
            return {"data": [{"name": m, "values": [{"value": 5}]} for m in params["metric"].split(",")]}
        raise AssertionError(url)
    q.http = fake
    try:
        ok, alert, line = check_token(now)
        assert ok and line.startswith("✓"), line
        os.environ["META_APP_ID"], os.environ["META_APP_SECRET"] = "a", "b"
        ok, alert, line = check_token(now)
        assert alert and "データ利用の期限" in alert, alert  # 10日前なので知らせる
        acc = account_rows(now, 2)
        assert acc[0]["views"] == 10 and acc[0]["replies"] == "" and acc[0]["followers"] == 300, acc[0]
        media = media_rows(now)
        assert [m["id"] for m in media] == ["r1", "s1"], media  # 14日より前の投稿は取らない
        assert media[1]["kind"] == "story" and media[1]["views"] == 5
        upsert(OUT / "a.csv", ACCOUNT_COLS, "date", acc)
        upsert(OUT / "a.csv", ACCOUNT_COLS, "date", [{"date": acc[0]["date"], "views": 99, "reach": ""}])
        rows = list(csv.DictReader((OUT / "a.csv").open(encoding="utf-8")))
        r = [x for x in rows if x["date"] == acc[0]["date"]][0]
        assert r["views"] == "99" and r["reach"] == "10", r  # 空欄では上書きしない
        assert "ストーリー" in summary_text(now, acc, media)

        def broken(method, url, params=None, **kw):
            raise q.ApiError(400, "Error validating access token", "190")
        q.http = broken
        ok, alert, line = check_token(now)
        assert not ok and "鍵が使えなくなっています" in alert and "get_tokens.py" in alert
        print("self-test OK")
    finally:
        OUT, q.http = real
        os.environ.pop("META_APP_ID", None)
        os.environ.pop("META_APP_SECRET", None)


if __name__ == "__main__":
    main()
