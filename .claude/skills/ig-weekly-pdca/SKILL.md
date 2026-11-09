---
name: ig-weekly-pdca
description: Instagram の週次PDCA（リサーチ・コメント数・改善の判定と次の改善1つ）と月曜レポートを行う。「週のふりかえり」「週次PDCA」と言われたとき、毎週日曜21:00の予約で使う。
---
# 週次PDCA＋月曜のレポート
1. ai_employees/PDCA.md を読み、PIPELINE.md「B. 週1のリサーチ」の順に回す（各段は CARDS.md の担当カードだけ）。調べものは PIPELINE.md「週次リサーチの調べもの」（Web検索2〜3回まで）。
2. 数字は data/insights/（`git fetch origin main` は GitHub アクセス1回）と「参加申込（自動）」タブ。無ければ「数字なし」。推測しない。コメント本文は保存しない。
3. C・A：「Instagram改善ログ」で判定日が来た改善を判定（続ける／やめる／もう一週）。続けるものは tools/build_ai_employees.py の TOOLKIT に足して `python3 tools/build_ai_employees.py`。
4. P：一番落ちている段に効く改善を1つ決めて Instagram改善ログに1行（動いている改善は2つまで）。「Instagram週次結果」に要点（週目標 V〜Y列の達成率、保存・滞留・ホーム率の週の動き）。改善は PDCA.md の早見表から。data/insights/online_followers.csv を見て、ストーリーの時刻を変えたほうがよければ加藤さんに提案（勝手に変えない）。
5. 月曜18:00ごろに出すレポートカルーセル（土日の開催分）を ig-production と同じ手順で作る。
5.5 31 逆張り発想：いつもと逆の切り口を3つ（決まりの範囲で）。月に1つは Instagram改善ログに入れる。29 管理数値で週の予定／投稿／失敗／達成率を報告の1行目に。
6. `--self-test`・`--check` → 30 監督の関所（PIPELINE.md 6.5）→ コミット（担当ログ）→ 未 push のコミットもまとめて push → PR を作る（GitHub の create_pull_request：base `main`・head `claude/awesome-tesla-dbf5p1`。もう開いている PR があれば作らずにそのリンクを使う）→ 加藤さんには「このリンクを開いて Merge を押すだけ」と PR のリンクを送る（月曜の投稿より前）。報告は3行まで。

## 作業の終わり（11/9 仕組み化）
- 作業の最後に、未 push のコミットが残っていれば必ず push する（停止フックが知らせる）。GitHub アクセスの数に入れる（普段1日3回・最大4回、5回はしない）。超えてしまうときは push せず、次の予約の回に回すと報告に書く。
- その日の GitHub アクセスの回数は「加藤からの修正・決定」ではなく報告の最後に「GitHub：本日◯回目」と書いて数える。
