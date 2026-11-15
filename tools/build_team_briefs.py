"""33人の指示書を、3つの担当ごとの短いまとめにする（11/15 加藤さん：使う量を減らす・質は落とさない）。
指示書の大部分（基盤マスタープロンプト・ペルソナ・連携先など）は33人とも同じなので、共通の決まりは1回だけ、
各社員の「役割と専門性」から下（その社員だけの部分）はそのまま全部入れる。指示書を直したらこれを動かし直す。
使い方: python3 tools/build_team_briefs.py → ai_employees/teams/*.md
"""
import os, re
A = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ai_employees")
TEAMS = {
    "調べる担当": ["01_research/" + f for f in ("market_research", "competitor_research", "post_collection", "trend_research", "audience_analysis")]
               + ["06_operations_analytics/comment_analyzer", "06_operations_analytics/numeric_analyst", "06_operations_analytics/improvement_proposal", "07_management/contrarian_ideas"],
    "作る担当": ["02_planning/" + f for f in ("idea_generation", "theme_selection", "structure_design", "funnel_architect")]
              + ["03_content_creation/" + f for f in ("hook_creator", "script_writer", "title_writer", "caption_writer")]
              + ["05_visual_production/" + f for f in ("material_collector", "image_generator", "infographic_creator", "subtitle_creator", "video_editor", "audio_adjuster", "music_composer")],
    "確かめる担当": ["04_review_quality/" + f for f in ("script_reviewer", "fact_checker", "expression_checker", "quality_controller")]
                + ["06_operations_analytics/posting_manager", "06_operations_analytics/progress_manager", "07_management/management_metrics", "07_management/supervisor", "07_management/posting_doctor"],
}
MARK = "## 🧑‍💼 役割と専門性"


def sec(s, start, end):
    i = s.find(start); j = s.find(end, i + 1) if i >= 0 else -1
    return s[i:j].strip() if i >= 0 else ""


def build():
    os.makedirs(os.path.join(A, "teams"), exist_ok=True)
    first = open(os.path.join(A, "07_management/supervisor.md"), encoding="utf-8").read()
    common = sec(first, "## 📌", "## 🏆") + "\n\n" + sec(first, "## 🏆", "## 🏛")
    for team, files in TEAMS.items():
        out = [f"# {team}（{len(files)}人）の指示書まとめ — tools/build_team_briefs.py で自動作成。直すのは元の指示書のほう",
               "", "33人共通の決まり（全員の指示書に同じ文がある所は1回だけ載せる。食い違ったら CLAUDE.md・「加藤からの修正・決定」シートが正しい）", "", common, "",
               "全員共通の考え方（基盤マスタープロンプト・ペルソナ・投稿運用ルール）は 33人とも同じ文。必要なときだけ ai_employees/07_management/supervisor.md の「🏛」〜「役割と専門性」の前を読む。", ""]
        for f in files:
            s = open(os.path.join(A, f + ".md"), encoding="utf-8").read()
            title = s.splitlines()[0].lstrip("# ").strip()
            no = re.search(r"No\.\d+[^\n]*", s)
            out += ["---", f"## {title}（{no.group(0) if no else ''}）", f"元の指示書：ai_employees/{f}.md", "", s[s.find(MARK):].replace(MARK, "### 役割と専門性") if MARK in s else "", ""]
        p = os.path.join(A, "teams", team + ".md")
        open(p, "w", encoding="utf-8").write("\n".join(out))
        print(p, os.path.getsize(p))


if __name__ == "__main__":
    build()
