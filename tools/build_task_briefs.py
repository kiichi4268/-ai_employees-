"""仕事ごとの短い指示書（作業カード）を作る（11/18 加藤さん：指示書を社員1人・作業1つに分け、その回に要る分だけ読む。質は変えない）。
teams/〇〇担当.md（全員分・約7万字）の代わりに、その仕事に関わる社員だけ、しかも中身のある所
（役割・作業手順・3点セット・この役割の投稿運用・NG例→OK例・身につけた型）だけを入れる。
省くのは全員同じ文（基盤マスタープロンプト・ペルソナ・連携先）と、出力の書式・必須思想・連携フロー（どの仕事でも同じ・判断には使わない）。
元の指示書は消さない。迷ったら元の指示書（ai_employees/0*/*.md）を開く。
使い方: python3 tools/build_task_briefs.py → ai_employees/tasks/*.md
"""
import glob, os, re
A = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ai_employees")
KEEP = ("## 🧑‍💼 役割と専門性", "## 🛠", "## 🧰", "## 🚦 【この役割", "## 🚫")

# 仕事 → 担当 → 社員の番号
TASKS = {
    "日次ストーリー": {  # 毎晩23:55：明日の 10:00・19:00
        "調べる": [3, 4, 27, 28, 31],
        "作る": [8, 9, 10, 18, 19, 21, 22, 33],
        "確かめる": [15, 16, 17, 24, 30],
    },
    "リール・カルーセル制作": {  # 月・水21:00
        "調べる": [3, 4, 5],
        "作る": [6, 7, 8, 9, 10, 11, 12, 13, 19, 20, 21, 22, 23, 33],
        "確かめる": [14, 15, 16, 17, 30],
    },
    "週次PDCA": {  # 日曜21:00
        "調べる": [1, 2, 3, 4, 5, 26, 27, 28, 31],
        "作る": [6, 7],
        "確かめる": [25, 29, 30, 32],
    },
}


def files_by_no():
    m = {}
    for f in glob.glob(os.path.join(A, "0*", "*.md")):
        s = open(f, encoding="utf-8").read()
        n = re.search(r"No\.(\d+)", s)
        if n: m[int(n.group(1))] = (f, s)
    return m


def keep_parts(s):
    parts = re.split(r"(?m)^(?=## )", s)
    return "\n".join(p.strip().replace("## ", "### ", 1) for p in parts if p.startswith(KEEP))


def common():
    s = open(os.path.join(A, "07_management/supervisor.md"), encoding="utf-8").read()
    i, j = s.find("## 📌"), s.find("## 🏛")
    return s[i:j].strip()


def build():
    os.makedirs(os.path.join(A, "tasks"), exist_ok=True)
    m = files_by_no(); com = common()
    for task, teams in TASKS.items():
        for team, nos in teams.items():
            out = [f"# {task}｜{team}担当（{len(nos)}人）— tools/build_task_briefs.py で自動作成。直すのは元の指示書",
                   "読むのはこの1枚だけ。足りない時だけ元の指示書（各社員の見出しの下のパス）を開く。食い違ったら CLAUDE.md・「加藤からの修正・決定」シートが正しい。", "",
                   com, ""]
            for n in nos:
                f, s = m[n]
                title = s.splitlines()[0].lstrip("# ").strip()
                out += ["---", f"## No.{n:02d} {title}", f"元：{os.path.relpath(f, os.path.dirname(A))}", "", keep_parts(s), ""]
            p = os.path.join(A, "tasks", f"{task}_{team}.md")
            open(p, "w", encoding="utf-8").write("\n".join(out))
            print(os.path.basename(p), os.path.getsize(p))


if __name__ == "__main__":
    build()
