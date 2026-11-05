#!/usr/bin/env python3
"""Instagram の承認制投稿キュー（GitHub Actions から1時間ごとに実行する）。

流れ:
  1. Claude が content/instagram/posts/*.json（下書き）と content/instagram/media/（写真・動画）を作り、PR を出す
  2. 人が GitHub で PR を「Merge」する ＝ 承認
  3. main に入った下書きを、予定時刻に GitHub Actions が Instagram に投稿し、ChatWork に結果を知らせる

使い方:
  python3 tools/ig_queue.py --check                  # 下書きの形を確かめる（PR で自動実行。何も送らない）
  python3 tools/ig_queue.py                          # 予定時刻を過ぎた下書きを投稿する（DRY_RUN=1 なら送らない）
  python3 tools/ig_queue.py --now 2026-11-10T21:05   # その時刻として動かす（確認用）
  python3 tools/ig_queue.py --self-test              # 通信なしの動作確認

下書き（1投稿1ファイル）:
  {"id": "2026-11-10-reel-01", "type": "reel", "scheduled_at": "2026-11-10T21:00:00+09:00",
   "caption": "本文（ハッシュタグ込み・2,200字以内）", "media": ["2026-11-10_volley.mp4"], "note": "企画メモ（投稿されない）"}
  type は feed（写真1枚）／carousel（写真・動画2〜10枚）／reel（動画）／story（写真か動画1つ）

同じ投稿を2回出さないよう、投稿前に Instagram 側の最近の投稿を見て、同じキャプション
（ストーリーズは予定時刻以降のもの）があれば送らない。予定時刻から WINDOW を過ぎた下書きは送らずに ChatWork に知らせる。
鍵は環境変数（GitHub Secrets）: INSTAGRAM_ACCESS_TOKEN・INSTAGRAM_USER_ID・WORDPRESS_TOKEN（写真の公開URL用）・CHATWORK_API_TOKEN
"""

import argparse
import datetime
import json
import os
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import chatwork_notify  # noqa: E402
import run_queue as q  # noqa: E402

JST = q.JST
POSTS = ROOT / "content" / "instagram" / "posts"
MEDIA = ROOT / "content" / "instagram" / "media"
WINDOW = datetime.timedelta(hours=2)  # cron の遅れを見込んだ、投稿してよい時間の幅
TYPES = {"feed", "carousel", "reel", "story"}
IMAGE_EXT = {".jpg", ".jpeg"}
VIDEO_EXT = {".mp4", ".mov"}
CAPTION_LIMIT = 2200
HASHTAG_LIMIT = 30


def kind(name):
    return "video" if Path(name).suffix.lower() in VIDEO_EXT else "image"


def load():
    return sorted((json.loads(p.read_text(encoding="utf-8")) | {"_file": p.name} for p in POSTS.glob("*.json")),
                  key=lambda p: (p.get("scheduled_at", ""), p.get("id", "")))


def validate(posts):
    errors, ids = [], set()
    for p in posts:
        where = p.get("_file", "?")
        if p.get("id") in ids:
            errors.append(f"{where}: id {p.get('id')} が重複している")
        ids.add(p.get("id"))
        if p.get("type") not in TYPES:
            errors.append(f"{where}: type は {sorted(TYPES)} のどれか")
            continue
        try:
            at = datetime.datetime.fromisoformat(p["scheduled_at"])
            if at.tzinfo is None:
                errors.append(f"{where}: scheduled_at に +09:00 を付ける")
        except (KeyError, ValueError):
            errors.append(f"{where}: scheduled_at が 2026-11-10T21:00:00+09:00 の形ではない")
        caption = p.get("caption", "")
        if p["type"] != "story" and not caption.strip():
            errors.append(f"{where}: caption が空")
        if len(caption) > CAPTION_LIMIT:
            errors.append(f"{where}: caption が {len(caption)}/{CAPTION_LIMIT} 字")
        if len(re.findall(r"#\S+", caption)) > HASHTAG_LIMIT:
            errors.append(f"{where}: ハッシュタグが{HASHTAG_LIMIT}個を超えている")
        if re.search(r"https?://", caption):
            errors.append(f"{where}: Instagram の本文のURLは押せないので「プロフィールのリンクから」と書く")
        media = p.get("media") or []
        counts = {"feed": (1, 1), "carousel": (2, 10), "reel": (1, 1), "story": (1, 1)}[p["type"]]
        if not counts[0] <= len(media) <= counts[1]:
            errors.append(f"{where}: {p['type']} の media は {counts[0]}〜{counts[1]} 個")
        for name in media:
            ext = Path(name).suffix.lower()
            if not (MEDIA / name).exists():
                errors.append(f"{where}: content/instagram/media/{name} がない")
            if ext not in IMAGE_EXT | VIDEO_EXT:
                errors.append(f"{where}: {name} は JPG か MP4/MOV にする（Instagram は PNG を受け付けない）")
            if p["type"] in ("feed",) and ext not in IMAGE_EXT:
                errors.append(f"{where}: feed は写真（JPG）1枚")
            if p["type"] == "reel" and ext not in VIDEO_EXT:
                errors.append(f"{where}: reel は動画（MP4/MOV）")
    return errors


# ---------------------------------------------------------------------------
# Instagram への送信（q.http を使うのでテストで差し替えられる）
# ---------------------------------------------------------------------------
def container(params, path=None):
    """コンテナを作る。動画は rupload に直接アップロードし、処理が終わるまで待つ。"""
    token, ig = q.need("INSTAGRAM_ACCESS_TOKEN"), q.need("INSTAGRAM_USER_ID")
    params = dict(params, access_token=token)
    if path is not None and kind(path.name) == "video":
        params["upload_type"] = "resumable"
        cid = q.http("POST", f"{q.META_API}/{ig}/media", params=params)["id"]
        data = path.read_bytes()
        q.http("POST", f"{q.META_UPLOAD}/{cid}", raw=data,
               headers={"Authorization": f"OAuth {token}", "offset": "0", "file_size": str(len(data))})
    else:
        if path is not None:
            params["image_url"] = q.wordpress_media_url(path)
        cid = q.http("POST", f"{q.META_API}/{ig}/media", params=params)["id"]
    for _ in range(60):
        state = q.http("GET", f"{q.META_API}/{cid}", params={"fields": "status_code", "access_token": token})
        if state.get("status_code") == "FINISHED":
            return cid
        if state.get("status_code") in ("ERROR", "EXPIRED"):
            raise q.ApiError(400, f"Instagram の写真・動画の処理に失敗（{path.name if path else ''}）", "media")
        time.sleep(container.poll_sec)
    raise q.ApiError(504, "Instagram の処理が時間内に終わらない（timeout）", "media")


container.poll_sec = 10


def publish(p):
    token, ig = q.need("INSTAGRAM_ACCESS_TOKEN"), q.need("INSTAGRAM_USER_ID")
    paths = [MEDIA / name for name in p["media"]]
    caption = p.get("caption", "")
    if p["type"] == "carousel":
        children = [container({"is_carousel_item": "true"} | ({"media_type": "VIDEO"} if kind(x.name) == "video" else {}), x)
                    for x in paths]
        cid = container({"media_type": "CAROUSEL", "children": ",".join(children), "caption": caption})
    elif p["type"] == "reel":
        cid = container({"media_type": "REELS", "caption": caption, "share_to_feed": "true"}, paths[0])
    elif p["type"] == "story":
        cid = container({"media_type": "STORIES"}, paths[0])
    else:
        cid = container({"caption": caption}, paths[0])
    media_id = q.http("POST", f"{q.META_API}/{ig}/media_publish", params={"creation_id": cid, "access_token": token})["id"]
    return q.http("GET", f"{q.META_API}/{media_id}", params={"fields": "permalink", "access_token": token}).get(
        "permalink", media_id)


def already_posted(p):
    """同じ投稿がもう出ているか（キャプション一致。ストーリーズは予定時刻以降に出たものがあるか）。"""
    token, ig = q.need("INSTAGRAM_ACCESS_TOKEN"), q.need("INSTAGRAM_USER_ID")
    at = datetime.datetime.fromisoformat(p["scheduled_at"])
    if p["type"] == "story":
        items = q.http("GET", f"{q.META_API}/{ig}/stories", params={"fields": "timestamp", "access_token": token})
        return any(datetime.datetime.strptime(x["timestamp"], "%Y-%m-%dT%H:%M:%S%z") >= at - datetime.timedelta(minutes=5)
                   for x in items.get("data", []))
    items = q.http("GET", f"{q.META_API}/{ig}/media", params={"fields": "caption", "limit": 25, "access_token": token})
    return any((x.get("caption") or "").strip() == p.get("caption", "").strip() for x in items.get("data", []))


def tell(text, dry):
    token = os.environ.get("CHATWORK_API_TOKEN")
    if dry or not token:
        print(f"  ChatWork（{'DRY_RUN のため送らない' if dry else '鍵がないため送らない'}）: {text.splitlines()[0]}")
        return
    try:
        chatwork_notify.send({"room_id": chatwork_notify.room_id(), "body": text}, token)
    except Exception as e:  # 通知の失敗で投稿を止めない
        print(f"  ChatWork への通知に失敗: {chatwork_notify.mask(str(e))}")


def check_keys():
    """4つの鍵が GitHub Secrets に入っていて、本物として通るかを読み取りだけで確かめる（何も投稿しない）。"""
    ng = 0
    for label, names, probe in q.CHECKS:
        if label not in ("Instagram", "WordPress", "ChatWork"):
            continue
        absent = [n for n in names if not os.environ.get(n)]
        if absent:
            ng += 1
            print(f"✗ 鍵 {label}: 未登録（{', '.join(absent)}）")
            continue
        try:
            print(f"✓ 鍵 {label}: OK（{probe()}）")
        except q.ApiError as err:
            ng += 1
            print(f"✗ 鍵 {label}: NG {chatwork_notify.mask(str(err))}（401・190 なら値の貼り間違いか期限切れ）")
    return ng


def run(now, dry):
    posts = load()
    errors = validate(posts)
    if errors:
        print("\n".join(errors))
        tell("[info][title]【Instagram】下書きの形がおかしいため、今回は送りませんでした[/title]" + "\n".join(errors[:10]) + "[/info]", dry)
        return {"failed": [e for e in errors]}
    summary = {"sent": [], "failed": [], "skipped": [], "expired": [], "planned": []}
    for p in posts:
        at = datetime.datetime.fromisoformat(p["scheduled_at"])
        if at > now:
            continue
        if now - at > WINDOW:
            if now - at <= WINDOW + datetime.timedelta(hours=1):  # 期限切れの知らせは1回だけ
                summary["expired"].append(p["id"])
                tell(f"[info][title]【Instagram】予定時刻を過ぎたため送りませんでした[/title]{p['id']}（予定 {at:%m/%d %H:%M}）[/info]", dry)
            continue
        if dry:
            summary["planned"].append(p["id"])
            print(f"○ {p['id']}: DRY_RUN のため送らない（本番なら {p['type']} を投稿）")
            continue
        try:
            if already_posted(p):
                summary["skipped"].append(p["id"])
                print(f"- {p['id']}: もう投稿されているので送らない")
                continue
            url = publish(p)
            summary["sent"].append(p["id"])
            print(f"✓ {p['id']}: 投稿しました {url}")
            tell(f"[info][title]【Instagram】投稿しました[/title]{p['id']}（{p['type']}）\n{url}[/info]", dry)
        except q.ApiError as err:
            summary["failed"].append(p["id"])
            print(f"✗ {p['id']}: 失敗 {err}")
            msg = chatwork_notify.build_message({
                "post_id": p["id"], "platform": f"instagram_{p['type']}", "scheduled_at": p["scheduled_at"],
                "attempt": chatwork_notify.MAX_ATTEMPTS,
                "error": {"http_status": err.http_status, "code": err.code, "message": err.message},
                "post": {"text": p.get("caption", ""), "media": [{"file": m} for m in p["media"]]}}, chatwork_notify.room_id())
            tell(msg["body"], dry)
    return summary


# ---------------------------------------------------------------------------
# 通信なしの動作確認
# ---------------------------------------------------------------------------
def self_test():
    import tempfile
    global POSTS, MEDIA
    real = (POSTS, MEDIA, q.http, chatwork_notify.send)
    tmp = Path(tempfile.mkdtemp())
    POSTS, MEDIA = tmp / "posts", tmp / "media"
    POSTS.mkdir()
    MEDIA.mkdir()
    for name in ("a.jpg", "b.jpg", "v.mp4"):
        (MEDIA / name).write_bytes(b"x")

    def write(pid, typ, at, media, caption="今週はバレーやるよ🏐 #社会人サークル"):
        (POSTS / f"{pid}.json").write_text(json.dumps(
            {"id": pid, "type": typ, "scheduled_at": at, "caption": caption, "media": media}, ensure_ascii=False))

    write("feed", "feed", "2026-11-10T12:00:00+09:00", ["a.jpg"])
    write("carousel", "carousel", "2026-11-10T12:00:00+09:00", ["a.jpg", "v.mp4"], "カルーセル #一人参加")
    write("reel", "reel", "2026-11-10T12:00:00+09:00", ["v.mp4"], "リール")
    write("story", "story", "2026-11-10T12:00:00+09:00", ["b.jpg"], "")
    write("later", "feed", "2026-11-10T21:00:00+09:00", ["a.jpg"], "夜の投稿")
    write("old", "feed", "2026-11-10T09:00:00+09:00", ["a.jpg"], "朝の投稿")
    calls, sent = [], []
    state = {"posted_captions": [], "stories": []}

    def fake(method, url, **kw):
        params = kw.get("params") or {}
        calls.append((method, url.rsplit("/", 1)[-1], {k: v for k, v in params.items() if k != "access_token"}))
        if url.endswith("/stories"):
            return {"data": state["stories"]}
        if url.endswith("/media") and method == "GET":
            return {"data": [{"caption": c} for c in state["posted_captions"]]}
        if url.endswith("wordpress.com/media"):
            return {"source_url": "https://img/x.jpg"}
        if url.endswith("/media") and method == "POST":
            return {"id": f"C{len(calls)}"}
        if "rupload" in url:
            return {}
        if url.endswith("media_publish"):
            return {"id": "M1"}
        if params.get("fields") == "status_code":
            return {"status_code": "FINISHED"}
        return {"permalink": "https://www.instagram.com/p/x/"}

    q.http = fake
    chatwork_notify.send = lambda msg, token: sent.append(msg["body"])
    container.poll_sec = 0
    os.environ.update(INSTAGRAM_ACCESS_TOKEN="T", INSTAGRAM_USER_ID="1", WORDPRESS_TOKEN="W", CHATWORK_API_TOKEN="c")
    try:
        assert not validate(load()), validate(load())
        s = run(datetime.datetime.fromisoformat("2026-11-10T12:05:00+09:00"), dry=True)
        assert s["planned"] == ["carousel", "feed", "reel", "story"] and not calls, s

        s = run(datetime.datetime.fromisoformat("2026-11-10T12:05:00+09:00"), dry=False)
        assert s["sent"] == ["carousel", "feed", "reel", "story"], s
        assert "old" not in s["expired"]  # 3時間以上前に期限切れを知らせ済み
        types = [c[2].get("media_type") for c in calls if c[0] == "POST" and c[1] == "media"]
        assert types.count("CAROUSEL") == 1 and "REELS" in types and "STORIES" in types and "VIDEO" in types, types
        assert any(c[2].get("is_carousel_item") for c in calls)
        assert len(sent) == 4 and all("投稿しました" in b for b in sent), sent

        calls.clear()
        state["posted_captions"] = ["今週はバレーやるよ🏐 #社会人サークル"]
        state["stories"] = [{"timestamp": "2026-11-10T03:01:00+0000"}]
        s = run(datetime.datetime.fromisoformat("2026-11-10T12:35:00+09:00"), dry=False)
        assert "feed" in s["skipped"] and "story" in s["skipped"], s  # 2回目の実行では同じ投稿を出さない

        s = run(datetime.datetime.fromisoformat("2026-11-10T14:30:00+09:00"), dry=False)
        assert s["expired"] == ["carousel", "feed", "reel", "story"], s

        write("bad", "feed", "2026-11-11T12:00", ["none.png"], "https://lin.ee/x")
        errs = validate(load())
        assert any("+09:00" in e for e in errs) and any("PNG" in e for e in errs) and any("URL" in e for e in errs), errs
    finally:
        POSTS, MEDIA, q.http, chatwork_notify.send = real
    print("self-test: 4種類の投稿・DRY_RUN・二重投稿の防止・期限切れ・下書きの形チェック すべて想定どおり")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true", help="下書きの形だけ確かめる（何も送らない）")
    parser.add_argument("--now", help="この時刻として動かす（例 2026-11-10T21:05。日本時間）")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    posts = load()
    if args.check:
        errors = validate(posts)
        for p in posts:
            print(f"・{p['scheduled_at'][:16].replace('T', ' ')} {p['type']:8} {p['id']}")
        print("\n".join(errors) or f"OK: 下書き {len(posts)}件、形の問題なし")
        sys.exit(1 if errors else 0)
    chatwork_notify.load_env()
    dry = os.environ.get("DRY_RUN", "1") != "0"
    now = datetime.datetime.fromisoformat(args.now) if args.now else datetime.datetime.now(JST)
    now = now if now.tzinfo else now.replace(tzinfo=JST)
    print(f"Instagram キュー {now:%Y-%m-%d %H:%M}（{'DRY_RUN：送信しない' if dry else '本番：送信する'}）")
    bad_keys = check_keys() if dry and os.environ.get("GITHUB_ACTIONS") else 0
    summary = run(now, dry)
    print("結果: " + "、".join(f"{k} {len(v)}件" for k, v in summary.items()))
    if summary.get("failed") or bad_keys:
        sys.exit(1)


if __name__ == "__main__":
    main()
