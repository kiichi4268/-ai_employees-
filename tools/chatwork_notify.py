#!/usr/bin/env python3
"""自動投稿の失敗を ChatWork に通知するメッセージを作る（品質確認AIのエラーハンドリング仕様の実装）。

使い方:
  python3 tools/chatwork_notify.py error_log.json            # 通知メッセージを表示するだけ（送信しない）
  python3 tools/chatwork_notify.py error_log.json --send     # ChatWork API に送信する
  python3 tools/chatwork_notify.py --self-test               # examples/chatwork_error_logs.json で動作確認
  python3 tools/chatwork_notify.py --check                   # トークンが有効か確認する（GET /v2/me。メッセージは送らない）

エラーログは Make などの自動投稿ツールから渡される JSON（1件のオブジェクト、または配列）。
"ai_fix" に品質確認AIが作った修正案テキストが入っていればそれを使い、なければ分類ごとの定型の修正案を入れる。
送信には環境変数 CHATWORK_API_TOKEN が必要（リポジトリ直下の .env に書いてもよい。.env は git に入らない）。
ルームIDは環境変数 CHATWORK_ROOM_ID ➔ .env ➔ build_ai_employees.py の INTEGRATIONS の順で決まる。
トークンはコード・JSON・プロンプトに書かないこと（.env.example を参照）。
"""

import json
import os
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import build_ai_employees as base  # noqa: E402
from build_content import LIMITS, PLATFORM_LABELS, x_weighted_length  # noqa: E402

CLASSES = {key: dict(cause=cause, action=action, retry=retry) for key, _, cause, action, retry in base.ERROR_CLASSES}
RETRY_MINUTES = {"rate_limit": [15, 15, 15], "server": [5, 15, 60]}
MAX_ATTEMPTS = 3
SECRET_RE = re.compile(
    r"(?i)(bearer\s+|token[\"'=:\s]+|x-chatworktoken[\"'=:\s]+|password[\"'=:\s]+|secret[\"'=:\s]+)[^\s\"',]+")


def load_env(path: Path = ROOT / ".env") -> None:
    """リポジトリ直下の .env（KEY=VALUE）を、まだ設定されていない環境変数として読み込む。"""
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip("\"'"))


def room_id() -> str:
    return os.environ.get("CHATWORK_ROOM_ID") or base.INTEGRATIONS["chatwork"]["room_id"]


def mask(text: str) -> str:
    """エラーログに混ざったトークン・パスワードを伏せ字にする。"""
    return SECRET_RE.sub(lambda m: m.group(1) + "****", text)


def classify(log: dict) -> str:
    err = log.get("error", {})
    status = err.get("http_status")
    message = f"{err.get('code', '')} {err.get('message', '')}".lower()
    if status in (401, 403) or re.search(r"unauthori[sz]ed|forbidden|token|permission|auth", message):
        return "auth"
    if status == 429 or re.search(r"rate.?limit|too many requests", message):
        return "rate_limit"
    if re.search(r"media|video|image|file|upload|duration|resolution", message) and status != 500:
        return "media"
    if status in (400, 422) or re.search(r"too long|shorter|invalid|duplicate|length", message):
        return "content"
    if (isinstance(status, int) and status >= 500) or re.search(r"timeout|timed out|connection|unavailable", message):
        return "server"
    return "unknown"


def default_fix(log: dict, error_class: str) -> str:
    """ai_fix がないときの定型の修正案。"""
    post = log.get("post", {})
    platform = log.get("platform", "")
    text = post.get("text", "")
    if error_class == "content":
        if platform == "x":
            n = x_weighted_length(text)
            return f"本文が X の上限を超えている可能性（現在 {n}/280）。前置きの1文を削り、全角140字以内に収めて再チェックする"
        if platform in LIMITS:
            return f"本文・タイトルが {PLATFORM_LABELS.get(platform, platform)} のルールに合っていない可能性（本文 {len(text)}/{LIMITS[platform]}字）。エラーメッセージの指摘箇所を直して再チェックする"
        return "エラーメッセージの指摘箇所（文字数・形式・重複）を直して再チェックする"
    if error_class == "media":
        files = ", ".join(m.get("file", "") for m in post.get("media", [])) or "（指定なし）"
        return f"素材 {files} が見つからない、または形式・サイズ・長さが合っていない。書き出し直して media_status.json を更新する"
    if error_class == "auth":
        return "Make の接続（コネクション）を開き、該当SNSのアカウントで再認証する"
    return CLASSES[error_class]["action"]


def build_message(log: dict, room_id: str) -> dict:
    error_class = classify(log)
    info = CLASSES[error_class]
    attempt = int(log.get("attempt", 1))
    auto_retry = info["retry"] and attempt < MAX_ATTEMPTS
    after = RETRY_MINUTES[error_class][attempt - 1] if auto_retry else None
    fix = mask(log.get("ai_fix") or default_fix(log, error_class))
    err = log.get("error", {})
    platform = PLATFORM_LABELS.get(log.get("platform", ""), log.get("platform", ""))
    when = log.get("scheduled_at", "")[:16].replace("T", " ")
    retry_line = (f"あり（{after}分後に再送・{attempt}/{MAX_ATTEMPTS}回目の失敗）" if auto_retry
                  else "なし" + ("（3回失敗したため停止。hold に戻しました）" if info["retry"] else ""))
    body = (f"[info][title]【投稿失敗】{platform} {when}（{log.get('post_id', '')}）[/title]"
            f"■ エラー：HTTP {err.get('http_status', '-')} {mask(str(err.get('message', '')))}\n"
            f"■ 原因（{error_class}）：{info['cause']}\n"
            f"■ AIの修正案：{fix}\n"
            f"■ 次の対応：{info['action']}\n"
            f"■ 自動リトライ：{retry_line}[/info]")
    fixed = log.get("ai_fixed_post") if error_class == "content" else None
    return {"room_id": room_id, "body": body, "error_class": error_class,
            "retry": {"auto": auto_retry, "after_minutes": after, "max_attempts": MAX_ATTEMPTS},
            "fixed_post": fixed}


def send(message: dict, token: str) -> dict:
    url = f"https://api.chatwork.com/v2/rooms/{urllib.parse.quote(str(message['room_id']), safe='')}/messages"
    data = urllib.parse.urlencode({"body": message["body"]}).encode()
    req = urllib.request.Request(url, data=data, headers={"X-ChatWorkToken": token}, method="POST")
    with urllib.request.urlopen(req, timeout=15) as res:
        return json.loads(res.read().decode())


def check_token() -> None:
    """トークンが有効か、ルームに参加しているかを確認する（読み取りだけ。メッセージは送らない）。"""
    load_env()
    token = os.environ.get("CHATWORK_API_TOKEN")
    if not token:
        sys.exit("CHATWORK_API_TOKEN を環境変数（または .env）で指定してください")
    headers = {"X-ChatWorkToken": token}
    for path in ("/v2/me", f"/v2/rooms/{urllib.parse.quote(room_id(), safe='')}"):
        req = urllib.request.Request("https://api.chatwork.com" + path, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as res:
            data = json.loads(res.read().decode())
        print(f"OK {path}: {data.get('name', '')}")


def self_test() -> None:
    samples = json.loads((ROOT / "examples" / "chatwork_error_logs.json").read_text(encoding="utf-8"))
    for sample in samples:
        msg = build_message(sample["log"], base.INTEGRATIONS["chatwork"]["room_id"])
        assert msg["room_id"] == "363171715"
        assert msg["error_class"] == sample["expect"], (sample["log"]["post_id"], msg["error_class"])
        assert msg["body"].startswith("[info][title]【投稿失敗】") and msg["body"].endswith("[/info]")
        assert "abcd1234secret" not in json.dumps(msg, ensure_ascii=False)
        json.loads(json.dumps(msg, ensure_ascii=False))
        print(f"OK {sample['log']['post_id']}: {msg['error_class']}（自動リトライ {msg['retry']['auto']}）")
    print(f"self-test: {len(samples)}件すべて想定どおり")


def main() -> None:
    args = sys.argv[1:]
    if args == ["--self-test"]:
        return self_test()
    if args == ["--check"]:
        return check_token()
    if not args:
        sys.exit(__doc__)
    logs = json.loads(Path(args[0]).read_text(encoding="utf-8"))
    logs = logs if isinstance(logs, list) else [logs]
    load_env()
    messages = [build_message(log, room_id()) for log in logs]
    if "--send" in args:
        token = os.environ.get("CHATWORK_API_TOKEN")
        if not token:
            sys.exit("CHATWORK_API_TOKEN を環境変数（または .env）で指定してください")
        for msg in messages:
            print(send(msg, token))
    else:
        print(json.dumps(messages if len(messages) > 1 else messages[0], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
