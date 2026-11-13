---
name: ig-weekly-stories
description: Instagram の翌週（月〜日）のストーリー下書きを作って PR 用に push する。「来週のストーリー作って」「ストーリーの下書き」と言われたとき、毎週金曜21:30の予約で使う。
---
# 翌週のストーリー（締め：金曜23:50）
1. CLAUDE.md・ai_employees/PDCA.md、シート「大元の配信先」の「Instagram改善ログ」（動いている改善）・「加藤からの修正・決定」・「イベント状況」を読む（シートが優先）。
2. ai_employees/PIPELINE.md「A. 制作」の順に回す（各段は ai_employees/CARDS.md の担当カードだけ）。デザインは PIPELINE.md「デザインの決まり」。
3. `bash studio/setup_studio.sh`（素材が無ければ加藤さんに素材パックを頼み、AI画像で進める）。studio/make_week2.py をコピーして SLOTS を書き換える。自動は朝8:00・昼12:00の各3本（③は kind="line"）。**10:00・19:00 はここでは作らない**（11/13 加藤さん：毎晩の日次PDCAのあと1日分ずつ作る）。週のまとめは 8:00・12:00 だけ（`python3 make_week3.py --base`、翌週は make_week4.py にコピー）。夜の自動投稿は作らない。代わりに **夜の手動用セット**（11/12 加藤さん）：studio/make_night.py の NIGHTS を翌週の7晩分に書き換えて実行し、out/night を zip にして加藤さんに渡す（ダークなエディトリアル画像＋リンクスタンプの文言＋公式LINEのURL。A 夜の本音Q&A／B 本質／C 予約の案内を日替わり。事実だけ・特典やUTAGEの話は入れない）。ストーリー③には公式LINEの QR（studio/assets/line_qr.png）と ID @827lnqaq を入れ、「スクショ → LINEのQRコードリーダー → 画像から読み込む」と添える。改善を入れた下書きは note に `改善:K-00X`。
4. 顔は強くぼかし、全画像をサムネイルで目視。投稿済みの古い下書き・media を消す。`python3 tools/ig_queue.py --self-test` と `--check`。
5. 30 監督の関所（PIPELINE.md 6.5。夜の分は作らない）→ コミット（担当ログ）→ push → PR を作る（GitHub の create_pull_request：base `main`・head `claude/awesome-tesla-dbf5p1`。もう開いている PR があれば作らずにそのリンクを使う）→ **30 監督がOKなら Claude が merge_pull_request で Merge する**（先に承認・11/10。差し戻しが多くなったら案2に戻す）→ 加藤さんに「Merge しました」と PR のリンク・中身・投稿日時を送る（月曜8:00より前）。「加藤からの修正・決定」に1行。報告は短く。鍵の値は出さない。

## 作業の終わり（11/9 仕組み化）
- **GitHub は1日2回まで**（11/11 加藤さん）：①朝8:00の回（数字の読み込み＋残りの push）②夜の制作の回（この手順：push → PR → Merge をひと続きで1回と数える）。この2回以外では GitHub に触らない。
- 報告の最後に「GitHub：本日◯回目（2回まで）」と書いて数える。
