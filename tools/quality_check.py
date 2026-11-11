"""下書きの品質を点数にする（監督AI No.30・品質管理部 No.14〜17 が使う）。

CLAUDE.md の絶対ルールと投稿の型に、全部の下書きを機械的に当てて 100点満点で採点する。
減点ごとに「どの社員の担当か」を出すので、いちばん点を落としている社員から直せる。

使い方:
  python3 tools/quality_check.py            # 全部の下書き
  python3 tools/quality_check.py --since 2026-11-11   # その日以降に出るものだけ
  python3 tools/quality_check.py --self-test
終了コード: 重大な減点（絶対ルール違反）があれば 1。
"""
import argparse, datetime, glob, json, os, re, sys
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POSTS = os.path.join(ROOT, "content", "instagram", "posts")
MEDIA = os.path.join(ROOT, "content", "instagram", "media")

# 会場 → CLAUDE.md の表にあるアクセス（キャプションに会場名が出たら、駅か「DM」があるかを見る）
VENUES = {
    "まもりやまテラス": "新代田", "代々木の杜": "代々木駅", "中部スポーツ・コミュニティプラザ": "新中野",
    "大久保プラザ": "大久保駅", "本町コミュニティセンター": "初台", "巣鴨体育館": "巣鴨駅", "目黒区民センター": "目黒駅",
}
NG = {  # 言葉 → 理由（CLAUDE.md の NG・表記ルール）
    "一律": "参加費に「一律」とは書かない", "ガチ": "ガチ感の表現", "上級者向け": "初心者お断りに見える",
    "経験者限定": "初心者お断りに見える", "出会い": "出会いを連想させる", "ナンパ": "ナンパを連想させる",
    "合コン": "出会いを連想させる", "残り": "残り人数は書かない（「まだまだ募集中！」）", "あと◯": "残り人数は書かない",
    "初心者8割": "表記は「初心者7割・経験者3割くらい」", "初心者6割": "表記は「初心者7割・経験者3割くらい」",
    "いかがでしたか": "AIっぽい言い回し", "ぜひぜひ": "AIっぽい言い回し", "〜しませんか？✨": "AIっぽい言い回し",
}
# AIっぽい言い回し（HUMAN_CRAFT.md の戒律2。1つ −3。「詳しくはDMでお気軽にどうぞ」は決まりの文なので対象外）
AI_PHRASES = ["いかがでしたか", "ぜひ", "素敵な", "充実した", "最高の", "楽しいひととき", "ではないでしょうか",
              "魅力", "ワクワク", "特別な", "盛りだくさん", "心を込めて", "大切な時間", "新しい自分", "一歩を踏み出"]
SIZES = {"carousel": (1080, 1350), "feed": (1080, 1350), "story": (1080, 1920), "reel": (1080, 1920)}

# 減点の担当（ai_employees の No.）
OWNER = {"human": "13 キャプション・16 表現チェック", "caption": "13 キャプション", "ng": "16 表現チェック", "fact": "15 事実確認", "cta": "09 CTA・導線",
         "size": "17 品質確認", "media": "24 投稿管理", "hashtag": "13 キャプション", "note": "25 進行管理",
         "time": "25 進行管理"}


def check_post(p, media_dir=MEDIA):
    """1つの下書きを採点する。返り値: (点数, [(減点, 重大か, 担当, 理由)])"""
    issues = []
    def minus(pt, owner, why, severe=False): issues.append((pt, severe, OWNER[owner], why))
    cap = p.get("caption", "") or ""
    t = p.get("type")
    # 絶対ルール（重大）
    if re.search(r"https?://|lin\.ee|fanme\.link", cap): minus(30, "ng", "本文にURL（プロフィールのリンクへ誘導する）", True)
    for w, why in NG.items():
        if w in cap and not (w == "残り" and "残りわずか" not in cap and re.search(r"残り\s*\d", cap) is None):
            minus(20, "ng", f"「{w}」：{why}", True)
    if "1500円" in cap or "1,500 円" in cap: minus(5, "fact", "参加費の表記は「1,500円」")
    if "当日の流れ" in cap and "（例）" not in cap and "(例)" not in cap: minus(15, "fact", "当日の流れは必ず「（例）」として書く", True)
    if "当日の流れ" in cap and re.search(r"\d{1,2}:\d{2}\s*(受付|ストレッチ|試合|片付け)", cap): minus(15, "fact", "当日の流れに時間を書かない", True)
    for v, st in VENUES.items():
        if v in cap and st not in cap and "DM" not in cap: minus(8, "fact", f"会場「{v}」にアクセス（{st}…）がない")
    if "芝公園" in cap and re.search(r"芝公園駅から徒歩", cap): minus(5, "fact", "芝公園は会場未確定（要確認）。アクセスは書かずDMへ")
    if "写真" in cap and "過去" not in cap and "イメージ" not in cap and t in ("carousel", "feed"):
        pass
    # 型（キャプションがある種類）
    if t in ("carousel", "feed", "reel"):
        if not cap.strip(): minus(40, "caption", "キャプションが空", True)
        else:
            if "公式LINE" not in cap: minus(15, "cta", "CTA（プロフィールのリンクから公式LINEへ）がない")
            if "1,500円" not in cap and t != "reel": minus(5, "fact", "参加費（1,500円・当日 現金またはPayPay）がない")
            tags = re.findall(r"#\S+", cap)
            if len(tags) > 15: minus(5, "hashtag", f"ハッシュタグが多すぎる（{len(tags)}個。15個まで）")
            if len(tags) < 3: minus(3, "hashtag", "ハッシュタグが少ない（3個以上）")
            if len(cap) > 2200: minus(30, "caption", "キャプションが2,200字を超える（Instagram の上限）", True)
            first = cap.strip().splitlines()[0]
            if len(first) > 40: minus(3, "caption", "1行目が長い（40字まで。最初の1行で中身が分かるように）")
    # 人間らしさ（HUMAN_CRAFT.md）
    for w in AI_PHRASES:
        if w in cap: minus(3, "human", f"AIっぽい言い回し「{w}」→ 自分の言葉・具体的な場面に言い換える")
    emo = len(re.findall(r"[\U0001F300-\U0001FAFF\u2600-\u27BF]", cap))
    if emo > 5: minus(3, "human", f"絵文字が多い（{emo}個。5個まで）")
    bullets = sum(1 for l in cap.splitlines() if l.strip().startswith(("・", "-", "✅", "✔")))
    if bullets > 6: minus(3, "human", f"箇条書きが多い（{bullets}行。6行まで。文章で語る）")
    if not p.get("note"): minus(2, "note", "note（どのスクリプトで作ったか・改善ID）がない")
    # 素材
    try:
        from PIL import Image
    except ImportError:
        Image = None
    for m in p.get("media", []):
        path = os.path.join(media_dir, m)
        if not os.path.exists(path): minus(40, "media", f"素材がない：{m}", True); continue
        if Image and m.lower().endswith((".jpg", ".jpeg", ".png")) and t in SIZES:
            w, h = Image.open(path).size
            if (w, h) != SIZES[t]: minus(10, "size", f"{m} の大きさ {w}×{h}（{t} は {SIZES[t][0]}×{SIZES[t][1]}）")
    return max(0, 100 - sum(i[0] for i in issues)), issues


def load(since=None):
    out = []
    for f in sorted(glob.glob(os.path.join(POSTS, "*.json"))):
        p = json.load(open(f, encoding="utf-8"))
        if since and p.get("scheduled_at", "")[:10] < since: continue
        out.append(p)
    return out


def report(posts):
    scores, owners, severe = [], Counter(), 0
    lines = []
    for p in posts:
        s, iss = check_post(p); scores.append(s)
        for pt, sv, ow, why in iss:
            owners[ow] += pt; severe += sv
            lines.append(f"  -{pt:>2} {'【重大】' if sv else ''}{p['id']}：{why}（担当 {ow}）")
    avg = sum(scores) / len(scores) if scores else 0
    print(f"品質チェック：下書き {len(posts)}件・平均 {avg:.1f}点・重大 {severe}件")
    print("\n".join(lines) if lines else "  減点なし")
    if owners:
        print("減点の多い担当：" + "／".join(f"{o} -{n}" for o, n in owners.most_common(3)))
    return avg, severe


def self_test():
    import tempfile
    from PIL import Image
    d = tempfile.mkdtemp(); Image.new("RGB", (1080, 1350)).save(os.path.join(d, "a.jpg"))
    good = {"id": "g", "type": "feed", "media": ["a.jpg"], "note": "x",
            "caption": "今日 11/14(土) バド開催\n📍まもりやまテラス（新代田駅から徒歩約5分）\n参加費1,500円\nプロフィールのリンクから公式LINEへ\n#a #b #c"}
    s, iss = check_post(good, d); assert s == 100, iss
    bad = dict(good, caption="残り3名！参加費は一律1500円 https://lin.ee/x 当日の流れ 13:00 受付", media=["none.jpg"])
    s, iss = check_post(bad, d); assert s == 0 and sum(i[1] for i in iss) >= 4, iss
    small = dict(good); Image.new("RGB", (800, 800)).save(os.path.join(d, "b.jpg")); small["media"] = ["b.jpg"]
    s, iss = check_post(small, d); assert s == 90, iss
    ai = dict(good, caption=good["caption"] + "\nぜひ素敵な時間を！")
    s, iss = check_post(ai, d); assert s == 94, iss
    print("self-test: 良い下書き100点・違反だらけ0点・大きさ違い90点・AIっぽい言い回し94点 すべて想定どおり")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--since"); ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test: self_test(); sys.exit(0)
    avg, severe = report(load(a.since))
    sys.exit(1 if severe else 0)
