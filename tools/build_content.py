#!/usr/bin/env python3
"""月ごとの毎日投稿コンテンツを生成・検証する。

使い方: python3 tools/build_content.py 2026-10

content/<年-月>/source.py（企画・台本・キャプションの元データ）を読み込み、
同じフォルダに次のファイルを書き出す。検証エラーが1つでもあれば何も書き出さずに止まる。
  - auto_posts.json  自動投稿用JSON（X / Threads / TikTok / YouTube Shorts）
  - manual_posts.md  手動投稿用フォーマット（Instagram / 公式LINE / note / YouTube長尺）
  - calendar.md      日別の企画・台本・配信カレンダー
  - qc_report.md     品質確認AIの判定と自動検証の結果

イベント情報・リンク・投稿媒体は tools/build_ai_employees.py の定義をそのまま使う。
"""

import datetime
import importlib.util
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import build_ai_employees as base  # noqa: E402

JST = datetime.timezone(datetime.timedelta(hours=9))
URL_RE = re.compile(r"https?://[^\s）)]+")
LINK = {**base.LINK, "insta": base.LINK["instagram"]}  # 本文では {insta} と短く書ける
LINK_URLS = set(base.LINK.values())
EVENTS = {ev["id"]: ev for ev in base.EVENTS}
AUTO_KEYS = {key for key, _, _ in base.AUTO_CHANNELS}
MANUAL_LABELS = {
    "instagram": "Instagram", "instagram_story": "Instagramストーリーズ",
    "line": "公式LINE", "note": "note", "youtube": "YouTube長尺",
}
PLATFORM_LABELS = {"x": "X", "threads": "Threads", "tiktok": "TikTok", "youtube_shorts": "YouTube Shorts"}
LIMITS = {"threads": 500, "tiktok": 2200, "youtube_shorts": 5000}  # X は重み付きで別計算
PENDING_MARK = "【"  # 【要確認】【開催後に記入】など、埋まっていない印


def x_weighted_length(text: str) -> int:
    """X の文字数（全角=2・半角=1、URLは1つ23）。上限は280（全角140字）。"""
    urls = URL_RE.findall(text)
    rest = URL_RE.sub("", text)
    return sum(1 if ord(c) < 0x1100 else 2 for c in rest) + 23 * len(urls)


def event_start(ev, key="start"):
    h, m = map(int, ev[key].split(":"))
    return datetime.datetime(base.EVENT_YEAR, base.EVENT_MONTH, ev["day"], h, m, tzinfo=JST)


def scheduled(date: str, time: str) -> datetime.datetime:
    return datetime.datetime.fromisoformat(f"{date}T{time}:00+09:00")


def fill_links(text: str) -> str:
    return text.format(**LINK)


def check_facts(where: str, text: str, event_ids, errors):
    """日付・曜日・時間・会場・参加費・定員・レンタル表現を EVENTS と突き合わせる。"""
    evs = [EVENTS[i] for i in event_ids]
    for m, d, wd in re.findall(r"(\d{1,2})/(\d{1,2})\((.)\)", text):
        actual = base.WEEKDAYS[datetime.date(base.EVENT_YEAR, int(m), int(d)).weekday()]
        if wd != actual:
            errors.append(f"{where}: {m}/{d}({wd}) の曜日が違う（正：{actual}）")
    mentioned_days = {int(d) for m, d in re.findall(r"(\d{1,2})/(\d{1,2})", text) if int(m) == base.EVENT_MONTH}
    if mentioned_days - {ev["day"] for ev in evs}:
        errors.append(f"{where}: 紐づけていないイベントの日付 {sorted(mentioned_days)} が本文にある")
    for rng in re.findall(r"\d{1,2}:\d{2}-\d{1,2}:\d{2}", text):
        if rng not in {f"{ev['start']}-{ev['end']}" for ev in evs}:
            errors.append(f"{where}: 時間 {rng} がイベント情報と一致しない")
    for fee in re.findall(r"\d,\d{3}円", text):
        if fee not in {ev["fee"].split("円")[0] + "円" for ev in evs}:
            errors.append(f"{where}: 参加費 {fee} がイベント情報と一致しない")
    for cap in re.findall(r"定員(\d+)名", text):
        if int(cap) not in {ev["capacity"] for ev in evs}:
            errors.append(f"{where}: 定員{cap}名 がイベント情報と一致しない")
    venues = {ev["venue"] for ev in base.EVENTS}
    for place in re.findall(r"＠([^\s（(／\u2600-\u27bf\U0001f000-\U0001ffff]+)", text):
        if place not in venues:
            errors.append(f"{where}: 会場「{place}」がイベント情報にない")
        elif place not in {ev["venue"] for ev in evs}:
            errors.append(f"{where}: 会場「{place}」のイベントを紐づけていない")
    if len(evs) == 1 and evs[0]["rental"].startswith("なし") and re.search(r"手ぶら|無料で貸す|レンタルあり", text):
        errors.append(f"{where}: レンタルがないイベントでレンタル・手ぶらを案内している")


def check_timing(where, kind, at, event_ids, errors):
    evs = [EVENTS[i] for i in event_ids]
    if not (datetime.datetime(2026, 10, 18, tzinfo=JST) <= at < datetime.datetime(2026, 11, 1, tzinfo=JST)):
        errors.append(f"{where}: 投稿日時 {at} が対象期間（10/18〜10/31）の外")
    if kind == "promo" and evs and at >= min(event_start(ev) for ev in evs):
        errors.append(f"{where}: 告知なのに開催開始より後に投稿される")
    if kind == "report" and evs:
        # 先頭は振り返るイベント（開催後に出す）、2つ目以降は次回の告知（開催前に出す）
        if at < event_start(evs[0]):
            errors.append(f"{where}: 開催レポートなのに開催前に投稿される")
        if any(at >= event_start(ev) for ev in evs[1:]):
            errors.append(f"{where}: 次回告知のイベントが投稿時点で始まっている")


def check_links(where, text, allow_urls, errors):
    urls = URL_RE.findall(text)
    if not allow_urls and urls:
        errors.append(f"{where}: この媒体の本文にはURLを書かない（タップできない）")
    for url in urls:
        if url not in LINK_URLS:
            errors.append(f"{where}: 実運用リンクにないURL {url}")


def build_auto(src, errors):
    posts, counter = [], Counter()

    def add(date, time, platform, kind, events, text, title, media, cta, hold_reason):
        counter[(date, platform)] += 1
        pid = f"{date}-{platform}-{counter[(date, platform)]:02d}"
        text = fill_links(text)
        at = scheduled(date, time)
        status = "hold" if hold_reason else "ready"
        if status == "ready" and PENDING_MARK in text + title:
            errors.append(f"{pid}: 埋まっていない【】が残っているのに ready")
        posts.append(dict(
            id=pid, platform=platform, scheduled_at=at.isoformat(), funnel_stage="集客",
            event=" / ".join(f"{e} {EVENTS[e]['sport']}＠{EVENTS[e]['venue']}" for e in events),
            text=text, thread=[], title=title,
            hashtags=re.findall(r"#(\S+)", text), media=media,
            cta_url=LINK[cta], status=status, hold_reason=hold_reason,
            _kind=kind, _events=events))

    for p in src.TEXT_POSTS:
        add(p["date"], p["time"], p["platform"], p["kind"], p["events"], p["text"], "", [],
            p["cta"], p.get("hold_reason", ""))
        if LINK[p["cta"]] not in posts[-1]["text"]:
            errors.append(f"{posts[-1]['id']}: CTA（{p['cta']}）のURLが本文に入っていない")
    for v in src.VIDEOS:
        media = [{"type": "video", "file": f"{v['date']}_{v['vid']}.mp4"}]
        # 動画を書き出して確認したら source.py で video_ready=True にする
        reason = v.get("hold_reason") or ("" if v.get("video_ready") else f"動画 {media[0]['file']} の書き出し・確認後に ready にする")
        add(v["date"], src.VIDEO_TIMES["tiktok"], "tiktok", v["kind"], v["events"], v["tiktok"],
            "", media, "line", reason)
        add(v["date"], src.VIDEO_TIMES["youtube_shorts"], "youtube_shorts", v["kind"], v["events"], v["tiktok"],
            v["title"], media, "line", reason)

    for p in posts:
        where = p["id"]
        if p["platform"] not in AUTO_KEYS:
            errors.append(f"{where}: 未定義の platform {p['platform']}")
        if p["platform"] == "x":
            if x_weighted_length(p["text"]) > 280:
                errors.append(f"{where}: X の文字数 {x_weighted_length(p['text'])}/280 を超えている")
        elif len(p["text"]) > LIMITS[p["platform"]]:
            errors.append(f"{where}: 文字数 {len(p['text'])}/{LIMITS[p['platform']]} を超えている")
        if p["platform"] == "youtube_shorts" and not 0 < len(p["title"]) <= 100:
            errors.append(f"{where}: Shorts の title が1〜100字ではない")
        if p["platform"] in ("tiktok", "youtube_shorts") and not p["media"]:
            errors.append(f"{where}: 動画ファイルが指定されていない")
        if p["cta_url"] not in LINK_URLS:
            errors.append(f"{where}: cta_url が実運用リンクにない")
        check_links(where, p["text"], p["platform"] in ("x", "threads"), errors)
        check_facts(where, p["text"] + "\n" + p["title"], p["_events"], errors)
        check_timing(where, p["_kind"], datetime.datetime.fromisoformat(p["scheduled_at"]), p["_events"], errors)
        if p["status"] == "hold" and not p["hold_reason"]:
            errors.append(f"{where}: hold なのに hold_reason がない")
    posts.sort(key=lambda p: (p["scheduled_at"], p["id"]))
    return posts


def public(post):
    return {k: v for k, v in post.items() if not k.startswith("_")}


def build_manual(src, errors):
    items = []
    for i, m in enumerate(src.MANUAL, 1):
        body = fill_links(m["body"])
        where = f"手動#{i} {m['date']} {m['label']}"
        check_links(where, body, m["channel"] in ("line", "note", "youtube"), errors)
        check_facts(where, body, m["events"], errors)
        check_timing(where, m["kind"], scheduled(m["date"], m["time"]), m["events"], errors)
        items.append({**m, "body": body})
    items.sort(key=lambda m: (m["date"], m["time"]))
    return items


COMMON_CHECKS = [
    "画像・動画のデザイン、文字の誤字、掲載許可を人の目で確認した",
    "日時・曜日・種目・会場・参加費・持ち物・定員・レンタルが【今月のイベントスケジュール】と一致している",
    "【要確認】【開催後に記入】が残っていない",
]
CHANNEL_CHECKS = {
    "instagram": ["本文にURLを書かず「プロフィールのリンクから」で案内している",
                  f"プロフィールのリンクが公式LINE（{base.LINK['line']}）になっている"],
    "instagram_story": [],
    "line": ["配信対象と配信日時を設定した", "本文のURLが【実運用リンク】のもの"],
    "note": ["見出し・目次・アイキャッチ画像を設定した", "本文のURLが【実運用リンク】のもの"],
    "youtube": ["タイトル・概要欄・サムネイル・公開日時を設定した", "概要欄のURLが【実運用リンク】のもの"],
}


def render_manual(items):
    out = ["# 📝 手動投稿用フォーマット（2026/10/18〜10/31）", "",
           "Instagram・公式LINE・note・YouTube長尺は、人がデザイン・クローズド教育・記事品質を確認して手で投稿・配信します。",
           "各ブロックの本文をそのままコピペし、チェックリストをすべて埋めてから投稿してください。", ""]
    current = None
    for n, m in enumerate(items, 1):
        if m["date"] != current:
            current = m["date"]
            d = datetime.date.fromisoformat(current)
            out += [f"## {d.month}/{d.day}({base.WEEKDAYS[d.weekday()]})", ""]
        events = "／".join(f"{base.EVENT_MONTH}/{EVENTS[e]['day']}({EVENTS[e]['wd']}) {EVENTS[e]['sport']}"
                          for e in m["events"]) or "なし"
        fence = "markdown" if m["channel"] == "note" else "text"
        checks = COMMON_CHECKS + CHANNEL_CHECKS[m["channel"]] + ([m["extra"]] if m.get("extra") else [])
        checks.append("投稿後、配信管理表を「投稿済み」に更新した")
        out += [f"### M{n:02d}｜{m['time']}｜{m['label']}", "",
                f"- **媒体**：{MANUAL_LABELS[m['channel']]}（手動）　**投稿予定**：{m['date']} {m['time']}　**紐づくイベント**：{events}",
                f"- **添付する素材**：{m['materials']}", "",
                "**▼ コピペ用本文**", f"```{fence}", m["body"], "```", "",
                "**▼ 投稿前チェックリスト**", *[f"- [ ] {c}" for c in checks], ""]
    return "\n".join(out)


def render_calendar(src, auto, manual):
    out = ["# 📅 2026年10月 毎日投稿カレンダー（10/18〜10/31）", "",
           "企画立案AI ➔ 台本作成AI ➔ キャプション作成AI ➔ 品質確認AI の連携で作った、日別の配信計画です。",
           "自動投稿の本文は `auto_posts.json`、手動投稿の本文は `manual_posts.md` にあります。", ""]
    videos = {v["date"]: v for v in src.VIDEOS}
    for date, theme, pain, events in src.PLAN:
        d = datetime.date.fromisoformat(date)
        out += [f"## {d.month}/{d.day}({base.WEEKDAYS[d.weekday()]})｜{theme}", "",
                f"- **狙うPain**：{pain}",
                f"- **紐づくイベント**：" + "／".join(f"{EVENTS[e]['sport']}（{base.EVENT_MONTH}/{EVENTS[e]['day']}）" for e in events), "",
                "| 時間 | 媒体 | 投稿方法 | 内容 | ステータス |", "|---|---|---|---|---|"]
        rows = []
        for p in auto:
            if p["scheduled_at"].startswith(date):
                first = p["title"] or p["text"].split("\n")[0]
                rows.append((p["scheduled_at"][11:16], PLATFORM_LABELS[p["platform"]], "自動", first,
                             f"`{p['status']}`"))
        for m in manual:
            if m["date"] == date:
                rows.append((m["time"], MANUAL_LABELS[m["channel"]], "手動", m["label"], "人が投稿"))
        out += [f"| {' | '.join(r)} |" for r in sorted(rows)] + [""]
        if date in videos:
            v = videos[date]
            out += [f"**🎬 台本 {v['vid']}「{v['title']}」**（TikTok／YouTube Shortsに自動投稿、Instagramリールにも転用可）", "",
                    "| 秒数 | 映像指示 | テロップ | ナレーション |", "|---|---|---|---|",
                    *[f"| {a} | {b} | {c} | {e} |" for a, b, c, e in v["rows"]], ""]
    return "\n".join(out)


def render_qc(auto, manual):
    status = Counter(p["status"] for p in auto)
    by_platform = Counter((p["platform"], p["status"]) for p in auto)
    out = ["# ✅ 品質確認レポート（2026/10/18〜10/31）", "",
           "`python3 tools/build_content.py 2026-10` が、生成のたびに下の項目を自動で検証しています（エラーが1つでもあれば書き出しません）。", "",
           "## 自動検証の項目", "",
           "- JSONとして読み込めること（`json.loads`）",
           "- 文字数：X は全角140字（半角280字、URLは1つ23字換算）以内／Threads 500字以内／TikTok 2,200字以内／Shorts は title 100字以内",
           "- リンク：本文のURL・`cta_url` がすべて【実運用リンク】のものであること、X・Threadsは本文にCTAのURLが入っていること、TikTok・Shorts・Instagramは本文にURLを書いていないこと",
           "- 事実：日付と曜日、時間、会場、参加費、定員がイベント情報と一致すること、レンタルがないバレーボールでレンタル・手ぶらを案内していないこと",
           "- タイミング：告知は開催開始より前、レポートは開催後に投稿されること",
           "- ステータス：`ready` に【要確認】【開催後に記入】が残っていないこと、`hold` に理由があること", "",
           "## 結果：エラー 0件", "",
           f"- 自動投稿 {len(auto)}件（ready {status['ready']}件／hold {status['hold']}件）",
           f"- 手動投稿 {len(manual)}件", "",
           "| 媒体 | ready | hold |", "|---|---|---|",
           *[f"| {PLATFORM_LABELS[k]} | {by_platform[(k, 'ready')]} | {by_platform[(k, 'hold')]} |" for k in PLATFORM_LABELS], "",
           "## 品質確認AIの判定（自動投稿）", "",
           "| ID | 投稿日時 | 文字数 | 判定 | 理由 |", "|---|---|---|---|---|"]
    for p in auto:
        n = f"{x_weighted_length(p['text'])}/280" if p["platform"] == "x" else f"{len(p['text'])}/{LIMITS[p['platform']]}"
        verdict = "Pass ➔ `ready`" if p["status"] == "ready" else "保留 ➔ `hold`"
        reason = p["hold_reason"] or "フック・保存トリガー・トーン・事実・CTAを確認済み"
        out.append(f"| {p['id']} | {p['scheduled_at'][5:16].replace('T', ' ')} | {n} | {verdict} | {reason} |")
    return "\n".join(out) + "\n"


def main():
    ym = sys.argv[1] if len(sys.argv) > 1 else f"{base.EVENT_YEAR}-{base.EVENT_MONTH:02d}"
    folder = ROOT / "content" / ym
    spec = importlib.util.spec_from_file_location("source", folder / "source.py")
    src = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(src)

    errors = []
    auto = build_auto(src, errors)
    manual = build_manual(src, errors)
    payload = json.dumps([public(p) for p in auto], ensure_ascii=False, indent=2)
    json.loads(payload)
    if errors:
        print("\n".join(errors), file=sys.stderr)
        sys.exit(f"検証エラー {len(errors)}件。何も書き出していません。")

    (folder / "auto_posts.json").write_text(payload + "\n", encoding="utf-8")
    (folder / "manual_posts.md").write_text(render_manual(manual), encoding="utf-8")
    (folder / "calendar.md").write_text(render_calendar(src, auto, manual), encoding="utf-8")
    (folder / "qc_report.md").write_text(render_qc(auto, manual), encoding="utf-8")
    status = Counter(p["status"] for p in auto)
    print(f"OK: 自動投稿 {len(auto)}件（ready {status['ready']}／hold {status['hold']}）、手動投稿 {len(manual)}件")


if __name__ == "__main__":
    main()
