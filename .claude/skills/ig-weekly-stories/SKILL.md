---
name: ig-weekly-stories
description: Instagram の翌週（月〜日）のストーリー下書きを作って PR 用に push する。「来週のストーリー作って」「ストーリーの下書き」と言われたとき、毎週金曜21:30の予約で使う。
---
# 翌週のストーリー（締め：金曜23:50）
1. CLAUDE.md・ai_employees/PDCA.md、シート「大元の配信先」の「Instagram改善ログ」（動いている改善）・「加藤からの修正・決定」・「イベント状況」を読む（シートが優先）。
2. ai_employees/PIPELINE.md「A. 制作」の順に回す（各段は ai_employees/CARDS.md の担当カードだけ）。デザインは PIPELINE.md「デザインの決まり」。
3. `bash studio/setup_studio.sh`（素材が無ければ加藤さんに素材パックを頼み、AI画像で進める）。studio/make_week2.py をコピーして SLOTS を書き換える。自動は朝8:00・昼12:00の各3本（③は kind="line"）。**11/16の週から** 10:00に2枚・19:00に2枚（画像のみ。10:00＝今日・今週の開催のおさらい、19:00＝次の開催＋公式LINEへ）を足す（1日10本）。夜は作らない。改善を入れた下書きは note に `改善:K-00X`。
4. 顔は強くぼかし、全画像をサムネイルで目視。投稿済みの古い下書き・media を消す。`python3 tools/ig_queue.py --self-test` と `--check`。
5. 30 監督の関所（PIPELINE.md 6.5。夜の分は作らない）→ コミット（担当ログ）→ push（GitHub は普段1日3回・最大4回、5回はしない）→ PR を作る（GitHub の create_pull_request：base `main`・head `claude/awesome-tesla-dbf5p1`。もう開いている PR があれば作らずにそのリンクを使う）→ 加藤さんには「このリンクを開いて Merge を押すだけ」と PR のリンクを送る（月曜8:00より前）。「加藤からの修正・決定」に1行。報告は短く。鍵の値は出さない。

## 作業の終わり（11/9 仕組み化）
- 作業の最後に、未 push のコミットが残っていれば必ず push する（停止フックが知らせる）。GitHub アクセスの数に入れる（普段1日3回・最大4回、5回はしない）。超えてしまうときは push せず、次の予約の回に回すと報告に書く。
- その日の GitHub アクセスの回数は「加藤からの修正・決定」ではなく報告の最後に「GitHub：本日◯回目」と書いて数える。
