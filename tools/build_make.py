#!/usr/bin/env python3
"""Make（make.com）に読み込むシナリオの Blueprint と設定ファイルを生成する。

使い方: python3 tools/build_make.py 2026-10

make/ フォルダに次のファイルを書き出す（APIトークンは含めない）。
  - config.json                     接続先・スプレッドシート・キャッシュ回避などの設定一覧
  - 01_post_queue.blueprint.json    X / Threads / TikTok / Shorts / Pinterest の投稿キュー（15分ごと）
  - 02_failure_notify.blueprint.json 投稿失敗の ChatWork 通知（Webhook で受ける）
  - 03_twitch_live.blueprint.json   Twitch の配信開始で X / Threads に告知（EventSub Webhook）
  - 04_wordpress_queue.blueprint.json WordPress 記事の予約投稿（15分ごと）

ChatWork の APIトークンは Make の「HTTP ➔ API key」接続に入れ、Blueprint には書かない。
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import build_ai_employees as base  # noqa: E402

SHEETS = base.INTEGRATIONS["sheets"]
CHATWORK = base.INTEGRATIONS["chatwork"]
COL = {name: str(i) for i, name in enumerate(base.SHEET_COLUMNS)}  # 列番号（A=0）
INTERVAL_MIN = 15
CACHE_BUSTER = {"name": "t", "value": '{{formatDate(now; "x")}}'}  # ミリ秒のUNIX時刻
# 投稿キュー（01）のルート：platform ➔ (表示名, 追加する投稿モジュール)
# Make に公式の投稿モジュールがない X・Threads・TikTok・Instagramストーリーズは Zernio（make-nodes-late）を使う
ROUTES = {
    # X は Zernio を使わず、HTTP モジュールで X API v2 に直接投稿する（無料枠の範囲で運用）
    "x": ("X", "HTTP「Make a request」で X API に直接投稿（画像あり：先に POST https://api.x.com/2/media/upload で media_id を取得 ➔ POST https://api.x.com/2/tweets に text・media.media_ids を送る。認証は X の OAuth 2.0 接続（tweet.write・media.write）。無料枠の投稿上限を超えない）"),
    "threads": ("Threads", "Zernio「Add a Threads Post」(make-nodes-late:addThreadsPost)"),
    "linkedin": ("LinkedIn", "LinkedIn「Create a Company Text Post」(linkedin:CreateTextShare)"),
    "tiktok": ("TikTok", "Zernio「Add a Post to Tiktok」(make-nodes-late:addTiktokPost)"),
    "youtube_shorts": ("YouTube Shorts", "YouTube「Upload a Video」(youtube:uploadVideo)"),
    "instagram_story": ("Instagram ストーリーズ", "Zernio「Add a Story to Instagram」(make-nodes-late:addInstagramStory)"),
    "instagram_reel": ("Instagram リール", "Instagram for Business「Create a reel post」(instagram-business:CreateAReelPost)"),
    "pinterest": ("Pinterest", "Zernio「Upload a Video Pin」(make-nodes-late:addPinterestVideoPin)"),
}
# API がなく自動投稿できない媒体（ルートは作り、配信管理表に「手動」と記録する）
MANUAL_ROUTES = {"note": "note（無料・有料）は投稿APIがないため手動で投稿する。投稿したら status を manual_posted にする"}

# 投稿失敗の分類（build_ai_employees.ERROR_CLASSES と同じ）を Make の switch() で表す
STATUS_TO_CLASS = [(401, "auth"), (403, "auth"), (429, "rate_limit"), (400, "content"), (422, "content"),
                   (500, "server"), (502, "server"), (503, "server"), (504, "server")]
CLASS_INFO = {key: (cause, action) for key, _, cause, action, _ in base.ERROR_CLASSES}


def raw_url(ym, name):
    return f"{base.INTEGRATIONS['github_raw']['url']}{ym}/{name}"


def switch_expr(status_ref, pick):
    pairs = "; ".join(f'{code}; "{pick(cls)}"' for code, cls in STATUS_TO_CLASS)
    return f'{{{{switch({status_ref}; {pairs}; "{pick("unknown")}")}}}}'


def http_get(mid, url):
    return {"id": mid, "module": "http:MakeRequest", "version": 4,
            "parameters": {"authenticationType": "noAuth"},
            "mapper": {"url": url, "method": "get", "queryParameters": [CACHE_BUSTER],
                       "headers": [{"name": "Cache-Control", "value": "no-cache"}], "parseResponse": True},
            "metadata": {"designer": {"x": 0, "y": 0},
                         "note": "キャッシュ回避のため ?t=<ミリ秒> を毎回付ける"}}


def iterator(mid, array_ref):
    return {"id": mid, "module": "builtin:BasicFeeder", "version": 1, "mapper": {"array": array_ref},
            "metadata": {"designer": {"x": 300, "y": 0}}}


def window_filter(item, extra=(), name=""):
    """iterator（item）の次のモジュールに付けるフィルター。フィルターはそのモジュールの実行前に評価される。"""
    at = f"{{{{{item}.scheduled_at}}}}"
    return {"name": name or f"ready かつ 予定時刻が直近{INTERVAL_MIN}分以内",
            "conditions": [[
                {"a": f"{{{{{item}.status}}}}", "o": "text:equal", "b": "ready"},
                {"a": at, "o": "date:lessorequal", "b": "{{now}}"},
                {"a": at, "o": "date:greater", "b": f"{{{{addMinutes(now; -{INTERVAL_MIN})}}}}"},
                *extra]]}


def sheet_update(mid, row_ref, status, posted_at, log, x=900):
    return {"id": mid, "module": "google-sheets:updateRow", "version": 2,
            "parameters": {"__IMTCONN__": None},
            "mapper": {"mode": "map", "spreadsheetId": SHEETS["spreadsheet_id"], "sheetId": SHEETS["sheet"],
                       "rowNumber": row_ref, "tableFirstRow": "A1:Z1",
                       "values": {COL["status"]: status, COL["posted_at"]: posted_at, COL["log"]: log}},
            "metadata": {"designer": {"x": x, "y": 0}}}


def chatwork_post(mid, body):
    return {"id": mid, "module": "http:MakeRequest", "version": 4,
            "parameters": {"authenticationType": "apiKeyConnection", "apiKeyAccount": None},
            "mapper": {"url": CHATWORK["api"], "method": "post", "contentType": "urlEncoded",
                       "urlEncodedBodyContent": [{"name": "body", "value": body}], "parseResponse": True},
            "metadata": {"designer": {"x": 600, "y": 0},
                         "note": "接続は「HTTP ➔ API key」：ヘッダー名 X-ChatWorkToken、値に .env の CHATWORK_API_TOKEN"}}


def failure_body(prefix):
    """ChatWork 通知の本文（prefix は失敗情報を持つモジュールの参照）。"""
    status = f"{prefix}.error.http_status"
    return ("[info][title]【投稿失敗】{{" + prefix + ".platform}} {{" + prefix + ".scheduled_at}}"
            "（{{" + prefix + ".post_id}}）[/title]"
            "■ エラー：HTTP {{" + status + "}} {{" + prefix + ".error.message}}\n"
            "■ 原因（" + switch_expr(status, lambda c: c) + "）：" + switch_expr(status, lambda c: CLASS_INFO[c][0]) + "\n"
            "■ AIの修正案：{{ifempty(" + prefix + ".ai_fix; \"品質確認AIの分類表（ai_employees/04_review_quality/quality_controller.md）で確認\")}}\n"
            "■ 次の対応：" + switch_expr(status, lambda c: CLASS_INFO[c][1]) + "[/info]")


def post_queue(ym):
    routes = []
    for n, (key, (label, module)) in enumerate(ROUTES.items()):
        routes.append({"flow": [dict(
            sheet_update(10 + n, "{{2.sheet_row}}", "module_missing", "",
                         f"{label}：この前に {module} を追加し、成功時は status=posted・posted_at={{{{now}}}}・log=投稿URL にする"),
            filter=window_filter(2, [{"a": "{{2.platform}}", "o": "text:equal", "b": key}],
                                 f"platform = {key}・ready・予定時刻が直近{INTERVAL_MIN}分以内"))]})
    for n, (key, note) in enumerate(MANUAL_ROUTES.items()):
        routes.append({"flow": [dict(
            sheet_update(30 + n, "{{2.sheet_row}}", "skipped", "", note),
            filter=window_filter(2, [{"a": "{{2.platform}}", "o": "text:equal", "b": key}],
                                 f"platform = {key}（手動）"))]})
    return {"name": "01 投稿キュー（X / Threads / LinkedIn / TikTok / Shorts / Instagram / Pinterest / note）",
            "flow": [http_get(1, raw_url(ym, "auto_posts.json")),
                     iterator(2, "{{1.data}}"),
                     {"id": 3, "module": "builtin:BasicRouter", "version": 1, "routes": routes,
                      "metadata": {"designer": {"x": 600, "y": 0}}}],
            "metadata": {"version": 1, "instant": False,
                         "scenario": {"roundtrips": 1, "maxErrors": 3, "autoCommit": True, "sequential": True}}}


def failure_notify():
    return {"name": "02 投稿失敗の ChatWork 通知",
            "flow": [{"id": 1, "module": "gateway:CustomWebHook", "version": 1,
                      "parameters": {"hook": None, "maxResults": 1},
                      "metadata": {"designer": {"x": 0, "y": 0},
                                   "note": "各投稿モジュールのエラーハンドラーから、エラーログ（post_id・platform・scheduled_at・sheet_row・attempt・error・post・retry_auto）をこのURLにPOSTする。retry_auto は rate_limit・server で3回未満なら true"}},
                     chatwork_post(2, failure_body("1")),
                     sheet_update(3, "{{1.sheet_row}}",
                                  '{{if(1.retry_auto; "retrying"; "failed")}}',
                                  "", "HTTP {{1.error.http_status}} {{1.error.message}}（{{1.attempt}}回目）"),
                     {"id": 4, "module": "gateway:WebhookRespond", "version": 1,
                      "mapper": {"status": "200", "body": "ok", "headers": []},
                      "metadata": {"designer": {"x": 1200, "y": 0}}}],
            "metadata": {"version": 1, "instant": True,
                         "scenario": {"roundtrips": 1, "maxErrors": 3, "autoCommit": True, "sequential": False}}}


def twitch_live():
    text = base.TWITCH_LIVE_TEXT.format(login="{{1.event.broadcaster_user_login}}", form=base.LINK["form"])
    routes = [
        {"flow": [{"id": 3, "module": "gateway:WebhookRespond", "version": 1,
                   "mapper": {"status": "200", "body": "{{1.challenge}}",
                              "headers": [{"key": "Content-Type", "value": "text/plain"}]},
                   "filter": {"name": "EventSub の確認（challenge）",
                              "conditions": [[{"a": "{{1.challenge}}", "o": "exist"}]]},
                   "metadata": {"designer": {"x": 600, "y": -150}}}]},
        {"flow": [{"id": 4, "module": "gateway:WebhookRespond", "version": 1,
                   "mapper": {"status": "204", "body": "", "headers": []},
                   "filter": {"name": "配信開始（stream.online）",
                              "conditions": [[{"a": "{{1.subscription.type}}", "o": "text:equal", "b": "stream.online"}]]},
                   "metadata": {"designer": {"x": 600, "y": 150}}},
                  {"id": 5, "module": "google-sheets:addRow", "version": 2,
                   "parameters": {"__IMTCONN__": None},
                   "mapper": {"mode": "map", "spreadsheetId": SHEETS["spreadsheet_id"], "sheetId": SHEETS["sheet"],
                              "tableFirstRow": "A1:Z1", "includesHeaders": True,
                              "values": {COL["id"]: '{{"live-" + formatDate(now; "YYYYMMDDHHmm")}}',
                                         COL["platform"]: "x / threads",
                                         COL["scheduled_at"]: "{{formatDate(now; \"YYYY-MM-DDTHH:mm:ssZ\")}}",
                                         COL["status"]: "module_missing", COL["posted_at"]: "",
                                         COL["log"]: text}},
                   "metadata": {"designer": {"x": 900, "y": 150},
                                "note": "この後に X・Threads の投稿モジュールを追加し、本文に log と同じ文面（TWITCH_LIVE_TEXT）を入れる"}}]},
    ]
    return {"name": "03 Twitch 配信開始 ➔ X / Threads 告知",
            "flow": [{"id": 1, "module": "gateway:CustomWebHook", "version": 1,
                      "parameters": {"hook": None, "maxResults": 1},
                      "metadata": {"designer": {"x": 0, "y": 0},
                                   "note": "Twitch EventSub（stream.online）の callback にこのURLを登録する"}},
                     {"id": 2, "module": "builtin:BasicRouter", "version": 1, "routes": routes,
                      "metadata": {"designer": {"x": 300, "y": 0}}}],
            "metadata": {"version": 1, "instant": True,
                         "scenario": {"roundtrips": 1, "maxErrors": 3, "autoCommit": True, "sequential": False}}}


def wordpress_queue(ym):
    send = {"id": 3, "module": "http:MakeRequest", "version": 4,
            "parameters": {"authenticationType": "oAuth", "oAuthAccount": None},
            "mapper": {"url": "{{2.endpoint}}", "method": "post", "contentType": "urlEncoded",
                       "urlEncodedBodyContent": [
                           {"name": "title", "value": "{{2.title}}"},
                           {"name": "content", "value": "{{2.content_html}}"},
                           {"name": "excerpt", "value": "{{2.excerpt}}"},
                           {"name": "slug", "value": "{{2.slug}}"},
                           {"name": "status", "value": "{{2.wp_status}}"},
                           {"name": "date", "value": "{{2.scheduled_at}}"}],
                       "parseResponse": True},
            "filter": window_filter(2),
            "metadata": {"designer": {"x": 600, "y": 0},
                         "note": "接続は WordPress.com の OAuth2（public-api.wordpress.com）。categories・tags は名前で入っているので、使う場合はIDに変換してから送る"},
            "onerror": [
                chatwork_post(30, "[info][title]【投稿失敗】WordPress {{2.scheduled_at}}（{{2.id}}）[/title]"
                                  "■ エラー：HTTP {{3.statusCode}} {{3.data.message}}\n"
                                  "■ 次の対応：WordPress.com の接続（OAuth2）と記事の内容を確認して再送する[/info]"),
                sheet_update(31, "{{2.sheet_row}}", "failed", "", "HTTP {{3.statusCode}} {{3.data.message}}", x=900),
                {"id": 32, "module": "builtin:Ignore", "version": 1, "metadata": {"designer": {"x": 1200, "y": 150}}}]}
    return {"name": "04 WordPress 記事の予約投稿",
            "flow": [http_get(1, raw_url(ym, "wordpress_posts.json")),
                     iterator(2, "{{1.data}}"),
                     send,
                     sheet_update(4, "{{2.sheet_row}}", "posted", "{{now}}", "{{3.data.link}}")],
            "metadata": {"version": 1, "instant": False,
                         "scenario": {"roundtrips": 1, "maxErrors": 3, "autoCommit": True, "sequential": True}}}


def config(ym):
    return {
        "make": {"zone": "eu1.make.com", "team": "My Team", "schedule_interval_minutes": INTERVAL_MIN},
        "sources": {name: raw_url(ym, name) + '?t={{formatDate(now; "x")}}'
                    for name in ("auto_posts.json", "wordpress_posts.json")},
        "cache_buster": "取得URLに ?t={{formatDate(now; \"x\")}}（ミリ秒のUNIX時刻）を付け、Cache-Control: no-cache を送る",
        "sheet": {"spreadsheet_id": SHEETS["spreadsheet_id"], "sheet": SHEETS["sheet"], "url": SHEETS["url"],
                  "columns": base.SHEET_COLUMNS, "statuses": dict(base.SHEET_STATUSES),
                  "seed": f"content/{ym}/sheet_seed.json"},
        "chatwork": {"room_id": CHATWORK["room_id"], "room_url": CHATWORK["url"], "api": CHATWORK["api"],
                     "token": "環境変数 CHATWORK_API_TOKEN（.env）／Make の HTTP API key 接続。ここには書かない"},
        "wordpress": {"site": base.INTEGRATIONS["wordpress"]["url"], "api": base.INTEGRATIONS["wordpress"]["api"]},
        "twitch": {"event": "stream.online", "post_text": base.TWITCH_LIVE_TEXT.format(
            login="{{broadcaster_user_login}}", form=base.LINK["form"])},
        "blueprints": [f"make/{n}" for n in BLUEPRINTS],
    }


BLUEPRINTS = {
    "01_post_queue.blueprint.json": post_queue,
    "02_failure_notify.blueprint.json": lambda ym: failure_notify(),
    "03_twitch_live.blueprint.json": lambda ym: twitch_live(),
    "04_wordpress_queue.blueprint.json": wordpress_queue,
}


def main():
    ym = sys.argv[1] if len(sys.argv) > 1 else f"{base.EVENT_YEAR}-{base.EVENT_MONTH:02d}"
    out = ROOT / "make"
    out.mkdir(exist_ok=True)
    files = {name: build(ym) for name, build in BLUEPRINTS.items()}
    files["config.json"] = config(ym)
    token = (ROOT / ".env").read_text(encoding="utf-8") if (ROOT / ".env").exists() else ""
    secret = next((line.split("=", 1)[1].strip() for line in token.splitlines()
                   if line.startswith("CHATWORK_API_TOKEN=")), "")
    for name, data in files.items():
        text = json.dumps(data, ensure_ascii=False, indent=2)
        json.loads(text)
        assert not secret or secret not in text, f"{name} にAPIトークンが入っている"
        (out / name).write_text(text + "\n", encoding="utf-8")
        print(f"make/{name}")


if __name__ == "__main__":
    main()
