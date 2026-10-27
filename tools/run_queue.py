#!/usr/bin/env python3
"""自動投稿キュー：配信管理表で ready の投稿を、予定時刻に各SNSの公式APIで送る（GitHub Actions から定期実行）。

使い方:
  python3 tools/run_queue.py                         # いまの時刻で実行（DRY_RUN=1 が既定。送らずに予定だけ表示）
  DRY_RUN=0 python3 tools/run_queue.py               # 本番（実際に送信し、配信管理表に書き戻す）
  python3 tools/run_queue.py --now 2026-10-26T12:05  # 時刻を指定して動作確認（日本時間）
  python3 tools/run_queue.py --self-test             # 通信なしで動作確認
  python3 tools/run_queue.py --check                 # 鍵・配信管理表が使えるかを読み取りだけで確認（何も送らない）
  python3 tools/run_queue.py --test-post threads     # 接続テストとして1件だけ実際に投稿する（下の TEST_TARGETS）

送る条件（すべて満たすものだけ）:
  - auto_posts.json / wordpress_posts.json の status が ready
  - 配信管理表の status が ready（人が hold・skipped にしたものは送らない）
  - scheduled_at が「いま」から30分前〜いまの間（30分以上過ぎたものは expired にして送らない）
X は API が有料のため手動予約（x_reserve_posts.md）にしており、ここでは絶対に送らない。

送る前に配信管理表を posting にして二重投稿を防ぎ、成功したら posted・posted_at・投稿URL、
失敗したら failed・エラー内容を書き戻して ChatWork に通知する（rate_limit・server は3回まで再送）。

鍵は環境変数（GitHub Secrets、手元では .env）だけで渡す:
  GOOGLE_SERVICE_ACCOUNT_JSON  配信管理表の読み書き（サービスアカウントのJSON全文）。ないときは sheet_seed.json を読むだけ
  THREADS_ACCESS_TOKEN / PINTEREST_ACCESS_TOKEN / WORDPRESS_TOKEN / CHATWORK_API_TOKEN
  INSTAGRAM_ACCESS_TOKEN・INSTAGRAM_USER_ID（tools/get_tokens.py instagram で取得。Facebook ページのトークン）
"""

import argparse
import base64
import datetime
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import build_ai_employees as base  # noqa: E402
import chatwork_notify  # noqa: E402

JST = datetime.timezone(datetime.timedelta(hours=9))
WINDOW = datetime.timedelta(minutes=30)
MAX_ATTEMPTS = chatwork_notify.MAX_ATTEMPTS
RETRY_WAIT_SEC = [30, 60]  # rate_limit・server のときの再送までの待ち時間（Actions の中で待つ）
NEVER_SEND = {key for key, _, _ in base.RESERVE_CHANNELS}  # X（手動予約）
SHEET = base.INTEGRATIONS["sheets"]
THREADS_API = "https://graph.threads.net/v1.0"
PINTEREST_API = "https://api.pinterest.com/v5"
META_VERSION = "v23.0"
META_API = f"https://graph.facebook.com/{META_VERSION}"
META_UPLOAD = f"https://rupload.facebook.com/ig-api-upload/{META_VERSION}"
WORDPRESS_SITE_API = base.INTEGRATIONS["wordpress"]["api"].rsplit("/posts", 1)[0]


class ApiError(Exception):
    def __init__(self, http_status, message, code=""):
        super().__init__(f"HTTP {http_status} {message}")
        self.http_status, self.message, self.code = http_status, message, code


# ---------------------------------------------------------------------------
# 通信（テストでは差し替える）
# ---------------------------------------------------------------------------
def http(method, url, *, params=None, form=None, body=None, headers=None, raw=None):
    if params:
        url += ("&" if "?" in url else "?") + urllib.parse.urlencode(params)
    headers = dict(headers or {})
    data = raw
    if form is not None:
        data = urllib.parse.urlencode(form).encode()
        headers["Content-Type"] = "application/x-www-form-urlencoded"
    elif body is not None:
        data = json.dumps(body).encode()
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=60) as res:
            text = res.read().decode() or "{}"
    except urllib.error.HTTPError as e:
        detail = e.read().decode(errors="replace")
        try:
            err = json.loads(detail)
            err = err.get("error", err)
            message = err.get("message") or err.get("error_description") or detail if isinstance(err, dict) else str(err)
            code = str(err.get("code", "")) if isinstance(err, dict) else ""
        except ValueError:
            message, code = detail[:300], ""
        raise ApiError(e.code, chatwork_notify.mask(str(message)), code) from None
    except (urllib.error.URLError, TimeoutError) as e:
        raise ApiError(0, f"connection error: {e}") from None
    return json.loads(text) if text.strip().startswith(("{", "[")) else {"text": text}


def need(name):
    value = os.environ.get(name)
    if not value:
        raise ApiError(401, f"{name} が設定されていません（GitHub Secrets または .env）", "missing_token")
    return value


# ---------------------------------------------------------------------------
# 配信管理表
# ---------------------------------------------------------------------------
class GoogleSheet:
    """サービスアカウントで配信管理表を読み書きする（Sheets API v4）。"""

    def __init__(self, info):
        self.info = info
        self.token = None
        self.base_url = f"https://sheets.googleapis.com/v4/spreadsheets/{SHEET['spreadsheet_id']}/values/"

    def _token(self):
        if self.token:
            return self.token
        from cryptography.hazmat.primitives import hashes, serialization
        from cryptography.hazmat.primitives.asymmetric import padding

        def b64(data):
            return base64.urlsafe_b64encode(data).rstrip(b"=").decode()
        now = int(time.time())
        claims = {"iss": self.info["client_email"], "scope": "https://www.googleapis.com/auth/spreadsheets",
                  "aud": self.info["token_uri"], "iat": now, "exp": now + 3600}
        signing_input = f"{b64(json.dumps({'alg': 'RS256', 'typ': 'JWT'}).encode())}.{b64(json.dumps(claims).encode())}"
        key = serialization.load_pem_private_key(self.info["private_key"].encode(), password=None)
        signature = key.sign(signing_input.encode(), padding.PKCS1v15(), hashes.SHA256())
        res = http("POST", self.info["token_uri"], form={
            "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
            "assertion": f"{signing_input}.{b64(signature)}"})
        self.token = res["access_token"]
        return self.token

    def _range(self, a1):
        return urllib.parse.quote(f"{SHEET['sheet']}!{a1}", safe="")

    def read(self):
        res = http("GET", self.base_url + self._range("A1:F1000"),
                   headers={"Authorization": f"Bearer {self._token()}"})
        values = res.get("values", [])
        if not values or values[0][:6] != base.SHEET_COLUMNS:
            raise ApiError(400, f"配信管理表の1行目が {base.SHEET_COLUMNS} ではない（列がずれている。invalid）", "sheet")
        return {i: (row + [""] * 6)[:6] for i, row in enumerate(values[1:], 2)}

    def write(self, row, status, posted_at="", log=""):
        http("PUT", self.base_url + self._range(f"D{row}:F{row}"), params={"valueInputOption": "RAW"},
             body={"values": [[status, posted_at, log[:500]]]},
             headers={"Authorization": f"Bearer {self._token()}"})


class SeedSheet:
    """サービスアカウントがないときの代わり：sheet_seed.json を読むだけ（書き込みは表示のみ）。"""

    def __init__(self, folder):
        values = json.loads((folder / "sheet_seed.json").read_text(encoding="utf-8"))["values"]
        self.rows = {i: (row + [""] * 6)[:6] for i, row in enumerate(values, 2)}
        self.writes = []

    def read(self):
        return self.rows

    def write(self, row, status, posted_at="", log=""):
        self.writes.append((row, status, posted_at, log))
        self.rows[row][3:6] = [status, posted_at, log]


# ---------------------------------------------------------------------------
# 各SNSへの送信（成功したら投稿URLを返す）
# ---------------------------------------------------------------------------
def post_threads(p, folder):
    token = need("THREADS_ACCESS_TOKEN")
    if p["media"]:
        raise ApiError(400, "Threads の画像・動画投稿は公開URLが必要なため未対応。media を外すか手動で投稿する", "media")
    reply_to, first = None, None
    for text in [p["text"]] + list(p.get("thread") or []):
        params = {"media_type": "TEXT", "text": text, "access_token": token}
        if reply_to:
            params["reply_to_id"] = reply_to
        container = http("POST", f"{THREADS_API}/me/threads", params=params)["id"]
        reply_to = http("POST", f"{THREADS_API}/me/threads_publish",
                        params={"creation_id": container, "access_token": token})["id"]
        first = first or reply_to
    return http("GET", f"{THREADS_API}/{first}", params={"fields": "permalink", "access_token": token}).get("permalink", first)


def multipart(fields, file_name, file_bytes):
    boundary = uuid.uuid4().hex
    parts = [f'--{boundary}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode()
             for k, v in fields.items()]
    parts.append(f'--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="{file_name}"\r\n'
                 f"Content-Type: application/octet-stream\r\n\r\n".encode() + file_bytes + b"\r\n")
    return b"".join(parts) + f"--{boundary}--\r\n".encode(), f"multipart/form-data; boundary={boundary}"


def post_pinterest(p, folder, poll_sec=10, poll_max=60):
    auth = {"Authorization": f"Bearer {need('PINTEREST_ACCESS_TOKEN')}"}
    boards = http("GET", f"{PINTEREST_API}/boards", params={"page_size": 100}, headers=auth).get("items", [])
    board = next((b for b in boards if b.get("name") == p["board"]), None)
    if not board:
        raise ApiError(400, f"Pinterest にボード「{p['board']}」がありません（invalid board）", "board")
    item = p["media"][0]
    path = folder / "media" / item["file"]
    if not path.exists():
        raise ApiError(400, f"media file {item['file']} が content/<年-月>/media/ にありません", "media")
    pin = {"board_id": board["id"], "title": p["title"], "description": p["text"], "link": p["link"]}
    if item["type"] == "video":
        reg = http("POST", f"{PINTEREST_API}/media", body={"media_type": "video"}, headers=auth)
        data, ctype = multipart(reg["upload_parameters"], item["file"], path.read_bytes())
        http("POST", reg["upload_url"], raw=data, headers={"Content-Type": ctype})
        for _ in range(poll_max):
            state = http("GET", f"{PINTEREST_API}/media/{reg['media_id']}", headers=auth).get("status")
            if state == "succeeded":
                break
            if state == "failed":
                raise ApiError(400, f"Pinterest の動画処理に失敗（media {item['file']}）", "media")
            time.sleep(poll_sec)
        else:
            raise ApiError(504, "Pinterest の動画処理が時間内に終わらない（timeout）", "media")
        pin["media_source"] = {"source_type": "video_id", "media_id": reg["media_id"], "cover_image_key_frame_time": 1}
    else:
        pin["media_source"] = {"source_type": "image_base64", "content_type": "image/png" if path.suffix == ".png"
                               else "image/jpeg", "data": base64.b64encode(path.read_bytes()).decode()}
    res = http("POST", f"{PINTEREST_API}/pins", body=pin, headers=auth)
    return f"https://www.pinterest.com/pin/{res['id']}/"


def post_wordpress(p, folder):
    auth = {"Authorization": f"Bearer {need('WORDPRESS_TOKEN')}"}
    api = p["endpoint"].rsplit("/posts", 1)[0]

    def term_ids(kind, names):
        ids = []
        for name in names:
            found = http("GET", f"{api}/{kind}", params={"search": name, "per_page": 100}, headers=auth)
            match = [t["id"] for t in found if t.get("name") == name] if isinstance(found, list) else []
            if not match:
                raise ApiError(400, f"WordPress に {kind}「{name}」がありません（作ってから ready に戻す。invalid）", "term")
            ids.append(match[0])
        return ids

    if http("GET", p["endpoint"], params={"slug": p["slug"], "status": "publish,future,draft"}, headers=auth):
        raise ApiError(409, f"同じ slug（{p['slug']}）の記事がすでにある（duplicate）", "duplicate")
    at = datetime.datetime.fromisoformat(p["scheduled_at"]).astimezone(datetime.timezone.utc)
    res = http("POST", p["endpoint"], headers=auth, body={
        "title": p["title"], "content": p["content_html"], "excerpt": p["excerpt"], "slug": p["slug"],
        "status": p["wp_status"], "date_gmt": at.strftime("%Y-%m-%dT%H:%M:%S"),
        "categories": term_ids("categories", p["categories"]), "tags": term_ids("tags", p["tags"])})
    return res.get("link", str(res.get("id", "")))


def wordpress_media_url(path):
    """画像のストーリーズ用：画像を WordPress のメディアに上げて公開URLを得る（Instagram は画像を公開URLで受け取るため）。"""
    ctype = "image/png" if path.suffix == ".png" else "image/jpeg"
    res = http("POST", f"{WORDPRESS_SITE_API}/media", raw=path.read_bytes(), headers={
        "Authorization": f"Bearer {need('WORDPRESS_TOKEN')}", "Content-Type": ctype,
        "Content-Disposition": f'attachment; filename="{path.name}"'})
    return res["source_url"]


def post_instagram(p, folder, poll_sec=10, poll_max=60):
    """リール・ストーリーズ：コンテナを作る ➔ 動画は rupload に直接アップロード ➔ 処理完了を待つ ➔ 公開する。"""
    token, ig = need("INSTAGRAM_ACCESS_TOKEN"), need("INSTAGRAM_USER_ID")
    item = p["media"][0]
    path = folder / "media" / item["file"]
    if not path.exists():
        raise ApiError(400, f"media file {item['file']} が content/<年-月>/media/ にありません", "media")
    params = {"access_token": token,
              "media_type": "REELS" if p["platform"] == "instagram_reel" else "STORIES"}
    if p["platform"] == "instagram_reel":
        params.update(caption=p["text"], share_to_feed="true")
    if item["type"] == "video":
        params["upload_type"] = "resumable"
        container = http("POST", f"{META_API}/{ig}/media", params=params)["id"]
        data = path.read_bytes()
        http("POST", f"{META_UPLOAD}/{container}", raw=data, headers={
            "Authorization": f"OAuth {token}", "offset": "0", "file_size": str(len(data))})
    else:
        params["image_url"] = wordpress_media_url(path)
        container = http("POST", f"{META_API}/{ig}/media", params=params)["id"]
    for _ in range(poll_max):
        state = http("GET", f"{META_API}/{container}", params={"fields": "status_code", "access_token": token})
        if state.get("status_code") == "FINISHED":
            break
        if state.get("status_code") in ("ERROR", "EXPIRED"):
            raise ApiError(400, f"Instagram の動画・画像処理に失敗（media {item['file']}・{state.get('status_code')}）", "media")
        time.sleep(poll_sec)
    else:
        raise ApiError(504, "Instagram の動画処理が時間内に終わらない（timeout）", "media")
    media_id = http("POST", f"{META_API}/{ig}/media_publish",
                    params={"creation_id": container, "access_token": token})["id"]
    return http("GET", f"{META_API}/{media_id}", params={"fields": "permalink", "access_token": token}).get(
        "permalink", media_id)


POSTERS = {"threads": post_threads, "pinterest": post_pinterest, "wordpress": post_wordpress,
           "instagram_reel": post_instagram, "instagram_story": post_instagram}
# 媒体ごとに必要な鍵。未設定なら送らずに module_missing と記録する（failed の通知を毎回出さないため）
REQUIRED = {"threads": ["THREADS_ACCESS_TOKEN"], "pinterest": ["PINTEREST_ACCESS_TOKEN"],
            "wordpress": ["WORDPRESS_TOKEN"], "instagram_reel": ["INSTAGRAM_ACCESS_TOKEN", "INSTAGRAM_USER_ID"],
            "instagram_story": ["INSTAGRAM_ACCESS_TOKEN", "INSTAGRAM_USER_ID"]}
# まだ送信を作っていない媒体（トークン取得後に追加する）。配信管理表に module_missing と記録する
NOT_YET = {"tiktok": "TikTok（審査とアクセストークン待ち）", "youtube_shorts": "YouTube Shorts（更新用トークン待ち）"}


# ---------------------------------------------------------------------------
# 本体
# ---------------------------------------------------------------------------
def load_posts(folder):
    posts = []
    for name in ("auto_posts.json", "wordpress_posts.json"):
        path = folder / name
        if path.exists():
            posts += json.loads(path.read_text(encoding="utf-8"))
    return sorted(posts, key=lambda p: (p["scheduled_at"], p["id"]))


def notify(p, err, attempt, dry):
    log = {"post_id": p["id"], "platform": p["platform"], "scheduled_at": p["scheduled_at"], "attempt": attempt,
           "error": {"http_status": err.http_status, "code": err.code, "message": err.message},
           "post": {"text": p.get("text", p.get("title", "")), "media": p.get("media", []), "cta_url": p.get("cta_url", "")}}
    msg = chatwork_notify.build_message(log, chatwork_notify.room_id())
    token = os.environ.get("CHATWORK_API_TOKEN")
    if dry or not token:
        print(f"  ChatWork（{'DRY_RUN のため送らない' if dry else 'CHATWORK_API_TOKEN がないため送れない'}）: {msg['body'][:80]}…")
        return msg
    try:
        chatwork_notify.send(msg, token)
    except Exception as e:  # 通知の失敗で投稿キューを止めない
        print(f"  ChatWork への通知に失敗: {chatwork_notify.mask(str(e))}")
    return msg


def send_with_retry(p, folder, sleep=time.sleep):
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            return POSTERS[p["platform"]](p, folder), None, attempt
        except ApiError as err:
            cls = chatwork_notify.classify({"error": {"http_status": err.http_status, "code": err.code,
                                                      "message": err.message}})
            if cls not in ("rate_limit", "server") or attempt == MAX_ATTEMPTS:
                return None, err, attempt
            sleep(RETRY_WAIT_SEC[attempt - 1])


def run(folder, now, sheet, dry, sleep=time.sleep):
    rows = sheet.read()
    summary = {"sent": [], "failed": [], "expired": [], "missing": [], "planned": [], "warnings": []}
    for row, v in rows.items():
        if v[3] == "posting":  # 前回の実行が送信中に止まった。送れたか分からないので自動では送り直さない
            summary["warnings"].append(v[0])
            print(f"! {v[0]}: {row} 行目が posting のまま。SNS に投稿されたか確認し、posted か ready に手で直す")
    for p in load_posts(folder):
        row = p.get("sheet_row")
        current = rows.get(row)
        if p["platform"] in NEVER_SEND or p["status"] != "ready":
            continue
        if not current or current[0] != p["id"]:
            print(f"! {p['id']}: 配信管理表の {row} 行目の id が一致しないため送らない（{current[0] if current else '空'}）")
            summary["warnings"].append(p["id"])
            continue
        if current[3] != "ready":
            continue
        at = datetime.datetime.fromisoformat(p["scheduled_at"])
        if at > now:
            continue
        stamp = now.isoformat(timespec="seconds")
        if now - at > WINDOW:
            summary["expired"].append(p["id"])
            print(f"- {p['id']}: 予定 {at:%m/%d %H:%M} を30分以上過ぎたため expired")
            if not dry:
                sheet.write(row, "expired", "", f"{stamp} 予定時刻を30分以上過ぎたため送らなかった")
            continue
        if p["platform"] in NOT_YET:
            summary["missing"].append(p["id"])
            print(f"- {p['id']}: {NOT_YET[p['platform']]} の送信はまだ作っていないため module_missing")
            if not dry:
                sheet.write(row, "module_missing", "", f"{stamp} {NOT_YET[p['platform']]}")
            continue
        absent = [n for n in REQUIRED.get(p["platform"], []) if not os.environ.get(n)]
        if p["platform"] == "instagram_story" and p["media"][0]["type"] == "image" and not os.environ.get("WORDPRESS_TOKEN"):
            absent.append("WORDPRESS_TOKEN（画像の公開URL用）")
        if absent:
            summary["missing"].append(p["id"])
            print(f"- {p['id']}: 鍵が未設定（{', '.join(absent)}）のため送らない")
            if not dry:
                sheet.write(row, "module_missing", "", f"{stamp} 鍵が未設定：{', '.join(absent)}")
            continue
        if dry:
            summary["planned"].append(p["id"])
            print(f"○ {p['id']}: DRY_RUN のため送らない（本番なら {p['platform']} に送信）")
            continue
        sheet.write(row, "posting", "", f"{stamp} 送信中")  # 二重投稿を防ぐため、送る前に印を付ける
        url, err, attempt = send_with_retry(p, folder, sleep)
        if err is None:
            sheet.write(row, "posted", datetime.datetime.now(JST).isoformat(timespec="seconds"), url)
            summary["sent"].append(p["id"])
            print(f"✓ {p['id']}: 送信成功 {url}")
        else:
            sheet.write(row, "failed", "", f"{stamp} {err}")
            notify(p, err, attempt, dry)
            summary["failed"].append(p["id"])
            print(f"✗ {p['id']}: 送信失敗 {err}")
    return summary


def make_sheet(folder, dry):
    raw = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
    if raw:
        try:
            info = json.loads(raw)
            missing = [k for k in ("client_email", "private_key", "token_uri") if not info.get(k)]
        except ValueError:
            info, missing = None, ["JSONとして読めない"]
        if missing:
            sys.exit(f"GOOGLE_SERVICE_ACCOUNT_JSON が正しくありません（{', '.join(missing)}）。"
                     "ダウンロードした JSON ファイルの中身を丸ごと Secrets に貼り直してください")
        return GoogleSheet(info)
    if not dry:
        sys.exit("本番（DRY_RUN=0）には GOOGLE_SERVICE_ACCOUNT_JSON が必要です（配信管理表に書き戻せないため止めます）")
    print("（GOOGLE_SERVICE_ACCOUNT_JSON がないため、配信管理表の代わりに sheet_seed.json を読みます）")
    return SeedSheet(folder)


# ---------------------------------------------------------------------------
# 鍵の確認（読み取りだけ。何も投稿・書き込みしない）
# ---------------------------------------------------------------------------
CHECKS = [
    # (表示名, 必要な環境変数, 確認のための GET)
    ("配信管理表", ["GOOGLE_SERVICE_ACCOUNT_JSON"], None),
    ("Threads", ["THREADS_ACCESS_TOKEN"], lambda: http("GET", f"{THREADS_API}/me", params={
        "fields": "username", "access_token": os.environ["THREADS_ACCESS_TOKEN"]}).get("username")),
    ("Pinterest", ["PINTEREST_ACCESS_TOKEN"], lambda: http("GET", f"{PINTEREST_API}/user_account", headers={
        "Authorization": f"Bearer {os.environ['PINTEREST_ACCESS_TOKEN']}"}).get("username")),
    ("WordPress", ["WORDPRESS_TOKEN"], lambda: http("GET", f"{WORDPRESS_SITE_API}/users/me", headers={
        "Authorization": f"Bearer {os.environ['WORDPRESS_TOKEN']}"}).get("name")),
    ("Instagram", ["INSTAGRAM_ACCESS_TOKEN", "INSTAGRAM_USER_ID"], lambda: http(
        "GET", f"{META_API}/{os.environ['INSTAGRAM_USER_ID']}", params={
            "fields": "username", "access_token": os.environ["INSTAGRAM_ACCESS_TOKEN"]}).get("username")),
    ("ChatWork", ["CHATWORK_API_TOKEN"], lambda: http("GET", "https://api.chatwork.com/v2/me", headers={
        "X-ChatWorkToken": os.environ["CHATWORK_API_TOKEN"]}).get("name")),
]


def check(folder):
    """鍵ごとに OK／未設定／NG を表示する。未設定は「その媒体はまだ使わない」なのでエラーにしない。"""
    ng = 0
    for label, names, probe in CHECKS:
        absent = [n for n in names if not os.environ.get(n)]
        if absent:
            what = "本番（DRY_RUN=0）は動かない" if probe is None else "この媒体は送らずに module_missing と記録する"
            print(f"－ {label}: 未設定（{', '.join(absent)}）。{what}")
            continue
        try:
            if probe is None:
                rows = make_sheet(folder, dry=False).read()
                result = f"{len(rows)}行を読み込み、1行目の列もOK"
            else:
                result = probe()
            print(f"✓ {label}: OK（{result}）")
        except ApiError as err:
            ng += 1
            print(f"✗ {label}: NG {err}")
    return ng


# ---------------------------------------------------------------------------
# 接続テスト投稿（配信管理表は使わない。1件だけ実際に送り、あとで人が消す）
# ---------------------------------------------------------------------------
TEST_TEXT = "【接続テスト】Macachette Sports の自動投稿の接続テストです。確認後に削除します。"
TEST_TARGETS = {
    "chatwork": "ChatWork のルームにテストメッセージを送る（いちばん安全。最初にこれを試す）",
    "wordpress": "WordPress に「下書き」を1件作る（公開されない）",
    "threads": "Threads に文章だけのテスト投稿を1件公開する（確認後に Threads のアプリで削除）",
    "pinterest": "Pinterest にテストのピンを1件作る（--file に画像が必要。確認後に削除）",
    "instagram": "Instagram ストーリーズにテストを1件出す（--file に画像か動画が必要。24時間で消える）",
}


def test_post(target, file=None):
    if target == "chatwork":
        msg = {"room_id": chatwork_notify.room_id(), "body": f"[info][title]接続テスト[/title]{TEST_TEXT}[/info]"}
        chatwork_notify.send(msg, need("CHATWORK_API_TOKEN"))
        return f"ルーム {msg['room_id']} に送信"
    if target == "wordpress":
        res = http("POST", f"{WORDPRESS_SITE_API}/posts", headers={"Authorization": f"Bearer {need('WORDPRESS_TOKEN')}"},
                   body={"title": "【接続テスト】自動投稿の確認", "content": f"<p>{TEST_TEXT}</p>", "status": "draft"})
        return f"下書き ID {res.get('id')}（WordPress の「投稿 ➔ 下書き」から削除）"
    if target == "threads":
        return post_threads({"text": TEST_TEXT, "media": [], "thread": []}, None)
    if not file or not Path(file).exists():
        raise ApiError(400, f"{target} のテストには --file で画像（または動画）を指定してください", "media")
    path = Path(file).resolve()
    folder = path.parent.parent  # 送信側は <folder>/media/<file> を読むため、一時的に合わせる
    media = [{"type": "video" if path.suffix.lower() in (".mp4", ".mov") else "image", "file": path.name}]
    if path.parent.name != "media":
        raise ApiError(400, "テスト用のファイルは content/<年-月>/media/ に置いてから指定してください", "media")
    if target == "pinterest":
        posts = load_posts(ROOT / "content" / sorted(d.name for d in (ROOT / "content").iterdir() if d.is_dir())[-1])
        board = next(p["board"] for p in posts if p["platform"] == "pinterest")
        return post_pinterest({"board": board, "media": media, "title": "【接続テスト】", "text": TEST_TEXT,
                               "link": base.LINK["line"]}, folder)
    return post_instagram({"platform": "instagram_story", "text": "", "media": media}, folder)


# ---------------------------------------------------------------------------
# 通信なしの動作確認
# ---------------------------------------------------------------------------
def self_test():
    global http
    real_http = http
    folder = ROOT / "content" / "2026-10"
    calls = []

    def fake(method, url, **kw):
        calls.append((method, url))
        if fake.fail:
            raise ApiError(*fake.fail)
        if url.endswith("/me/threads"):
            return {"id": "c1"}
        if url.endswith("/threads_publish"):
            return {"id": "t1"}
        return {"permalink": "https://www.threads.net/@macachette/post/t1"}

    def scenario(now, dry=False, fail=None, extra=None):
        calls.clear()
        fake.fail = fail
        sheet = SeedSheet(folder)
        for v in sheet.rows.values():  # 実際の配信管理表と同じく、10/24 以前は expired 済みにする
            if v[2] < "2026-10-25":
                v[3] = "expired"
        if extra:
            sheet.rows.update(extra)
        summary = run(folder, datetime.datetime.fromisoformat(now), sheet, dry, sleep=lambda s: None)
        return summary, sheet

    os.environ.update(THREADS_ACCESS_TOKEN="test-token", CHATWORK_API_TOKEN="")
    http = fake
    try:
        s, sheet = scenario("2026-10-26T12:05:00+09:00")
        assert s["sent"] == ["2026-10-26-threads-01"], s
        assert [w[1] for w in sheet.writes] == ["posting", "posted"], sheet.writes
        assert sheet.writes[1][3].startswith("https://www.threads.net/"), sheet.writes
        assert not any("api.x.com" in u or "twitter" in u for _, u in calls)
        assert "2026-10-26-tiktok-01" not in s["missing"]  # hold の動画は送らない・触らない

        s, sheet = scenario("2026-10-26T12:05:00+09:00", dry=True)
        assert s["planned"] == ["2026-10-26-threads-01"] and not sheet.writes and not calls

        s, sheet = scenario("2026-10-26T12:05:00+09:00", fail=(400, "Text is too long", "100"))
        assert s["failed"] == ["2026-10-26-threads-01"] and sheet.writes[-1][1] == "failed", sheet.writes

        s, sheet = scenario("2026-10-26T12:05:00+09:00", fail=(503, "Service Unavailable"))
        assert s["failed"] and len([c for c in calls if c[1].endswith("/me/threads")]) == MAX_ATTEMPTS

        s, sheet = scenario("2026-10-26T13:00:00+09:00")
        assert s["expired"] == ["2026-10-26-threads-01"] and [w[1] for w in sheet.writes] == ["expired"] and not calls

        s, _ = scenario("2026-10-26T11:59:00+09:00")
        assert not any(s.values()), s

        rows = SeedSheet(folder).rows
        x_row = next(r for r, v in rows.items() if v[1] == "x")
        s, sheet = scenario("2026-10-26T07:35:00+09:00", extra={x_row: rows[x_row][:3] + ["ready", "", ""]})
        assert not calls and not sheet.writes, "X は配信管理表が ready でも送らない"
    finally:
        http = real_http
    print("self-test: 送信成功・DRY_RUN・失敗通知・再送3回・期限切れ・予定前・X除外 すべて想定どおり")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("ym", nargs="?", help="対象の年-月（省略時は今月）")
    parser.add_argument("--now", help="この時刻として実行する（例 2026-10-26T12:05。日本時間）")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--check", action="store_true", help="鍵と配信管理表を読み取りだけで確認する")
    parser.add_argument("--test-post", choices=sorted(TEST_TARGETS), help="接続テストとして1件だけ実際に投稿する")
    parser.add_argument("--file", help="--test-post pinterest / instagram で使う画像・動画（content/<年-月>/media/ に置く）")
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    chatwork_notify.load_env()
    dry = os.environ.get("DRY_RUN", "1") != "0"
    now = datetime.datetime.fromisoformat(args.now) if args.now else datetime.datetime.now(JST)
    now = now if now.tzinfo else now.replace(tzinfo=JST)
    folder = ROOT / "content" / (args.ym or f"{now:%Y-%m}")
    if not folder.exists():
        sys.exit(f"{folder} がありません")
    if args.check:
        sys.exit(1 if check(folder) else 0)
    if args.test_post:
        print(f"接続テスト：{TEST_TARGETS[args.test_post]}")
        try:
            print(f"✓ {args.test_post}: 成功 {test_post(args.test_post, args.file)}")
        except ApiError as err:
            sys.exit(f"✗ {args.test_post}: 失敗 {err}")
        return
    print(f"投稿キュー {now:%Y-%m-%d %H:%M}（{'DRY_RUN：送信しない' if dry else '本番：送信する'}）")
    try:
        summary = run(folder, now, make_sheet(folder, dry), dry)
    except ApiError as err:  # 配信管理表が読めない・書けないときは何も送らずに止め、ChatWork に知らせる
        notify({"id": "配信管理表", "platform": "sheets", "scheduled_at": now.isoformat()}, err, MAX_ATTEMPTS, dry)
        sys.exit(f"配信管理表にアクセスできないため止めました：{err}")
    print("結果: " + "、".join(f"{k} {len(v)}件" for k, v in summary.items()))
    if summary["failed"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
