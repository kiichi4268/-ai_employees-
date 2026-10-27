# 🤖 Macachette Sports × 沢田流SNS自動化AI組織（28人体制）

「フロント拡散媒体（X / Threads / TikTok / YouTube Shorts）」から「本陣（Instagram / YouTube / note）」、そして「クローズド教育（公式LINE ➔ 予約フォーム）」へ、集客・教育・成約を毎日まわし続けるための、28人のAI社員プロンプト集と実行手順書です。

---

## 1. 前提（全AI社員の共通ヘッダーに組み込み済み）

### コンセプト
| 項目 | 内容 |
|---|---|
| 商材 | 社会人スポーツ・交流イベント（Macachette Sports）／公式LINE経由のコミュニティ参加・企画案内 |
| 誰が | BAR Macachette系列が運営する「Macachette Sports」（とSNS自動化を統括するAI社員組織） |
| 誰に | 都内在住・在勤の20〜30代社会人（特に初心者・運動不足に悩むお一人様参加希望者） |
| 提供価値 | 用具レンタルあり・初心者歓迎・参加者の8割が一人参加という「浮かない・温かい・安心感のある」スポーツ交流の場 |
| ゴール | 運動不足や休日の所在なさを解消し、新しい仲間とリフレッシュできる生活習慣へ（公式LINE／予約フォームから継続参加・ファン化） |

### 実運用リンク（全AI社員のCTAに埋め込み済み）
| 名称 | URL | 使いどころ |
|---|---|---|
| 公式LINE登録 | https://lin.ee/VwtzoAm | すべての投稿の最終CTA（初参加ガイド・先行案内） |
| 予約フォーム | https://docs.google.com/forms/d/e/1FAIpQLSfXFehVXHLflywFL5NLtyz55OS_n9y50wC4itvNUK2fXKr7kQ/viewform | 日程が決まった人への申込導線（LINE配信・告知・リマインド） |
| note（オープン教育） | https://note.com/gifted_canna4865 | 長文で不安を解消したい人向け |
| Instagram（本陣） | https://www.instagram.com/macachette_sports | フロント拡散からの送り先 |
| アプリ（App Store） | https://itunes.apple.com/app/id1544827472 | アプリでの参加・連絡を案内するときだけ |

### 連携先（自動投稿・通知の接続先。投稿本文のCTAには使わない）
| 連携先 | URL | API・設定 | メモ |
|---|---|---|---|
| WordPress（ブログ） | https://sportsbackstage1.wordpress.com | `POST https://public-api.wordpress.com/wp/v2/sites/sportsbackstage1.wordpress.com/posts` | WordPress.com のサイト。初期記事 `/2026/09/04/hello-world/` は公開前に削除する |
| ChatWork（投稿失敗の通知先） | https://www.chatwork.com/#!rid363171715 | `POST https://api.chatwork.com/v2/rooms/363171715/messages` | ルームID `363171715`（環境変数 `CHATWORK_ROOM_ID` で上書き可）。APIトークンは `CHATWORK_API_TOKEN` だけで渡す |
| Pinterest | https://jp.pinterest.com/ | Make の Pinterest 接続 | ボードは接続時に選ぶ |
| Twitch（ライブ配信） | https://www.twitch.tv/ | https://www.twitch.tv/settings/profile | 公開チャンネルURL（`https://www.twitch.tv/<ユーザー名>`）が決まるまで投稿のCTAには使わない |

連携先は `tools/build_ai_employees.py` の `INTEGRATIONS` で管理しています。APIトークン・パスワードは書かず、`.env`（`.env.example` をコピー。git には入りません）か Make の接続設定で管理します。

- X / Threads / LINE配信 / note は本文にURLを直接書きます。Instagram / TikTok はキャプション内のURLがタップできないため「プロフィールのリンクから」で案内し、プロフィールに公式LINEのURLを置きます。

### 投稿運用の切り分け（手動投稿 vs 手動予約 vs 自動投稿）
| 投稿方法 | 媒体 | 誰が投稿するか | AI社員の出力形式 |
|---|---|---|---|
| 手動予約 | X（旧Twitter） | AI が本文・画像を完成させ、人が X の予約投稿機能で予約（X API は有料のため自動投稿しない） | 自動投稿用JSONで作り、`x_reserve_posts.md`（予約日時・コピペ用本文・添付画像・チェックリスト）に変換 |
| 手動投稿 | Instagram（フィード／カルーセル／リール／ストーリーズ）・公式LINE（配信・オファー）・note・YouTube（長尺） | 人がデザイン・クローズド教育・記事品質を確認して投稿・配信 | 手動投稿用フォーマット（コピペ用本文＋投稿前チェックリスト） |
| 自動投稿 | Threads・TikTok・YouTube Shorts・Pinterest | GitHub Actions ＋ Python が各SNSの無料の公式APIで投稿まで完結 | 自動投稿用JSON（ツールがそのまま読み取って送信できる形式。動画・画像には `video_specs` 付き） |
| 自動投稿 | WordPress（ブログ） | WordPress REST API／Make連携で予約公開 | WordPress投稿用JSON（`title`・`content_html`・`categories`・`tags`・`slug`） |

- 自動投稿用JSONの `status` は `"draft"`（作成時）➔ `"ready"`（品質確認AIがPassしたものだけ）➔ 自動化ツールが送信。【要確認】が残るものは `"hold"` のまま止まります。**自動化ツールは `"ready"` だけを送信する設定にしてください。**
- 各フォーマットの中身は、各AI社員ファイルの【投稿運用ルール】にあります。
- **費用は0円で運用します。** X API は2026年から無料枠がなく従量課金（リンク付き投稿は1件約0.20ドル）のため、X は自動投稿せず手動予約にしています。自動投稿する媒体（Threads・YouTube・TikTok・Pinterest・WordPress）の公式APIと、GitHub Actions（非公開リポジトリは月2,000分まで無料）、Google スプレッドシート、ChatWork はすべて無料の範囲に収まります。
- WordPress記事は、ブログ記事作成をキャプション作成AI、カテゴリ・タグ・CTAの方針（プロモーション統括）をCTA・導線設計AIが担当します。

### 今月のイベントスケジュール（2026年10月）
| 日付 | 時間 | 種目 | 会場 | 参加費 | 持ち物 | 定員 | レンタル |
|---|---|---|---|---|---|---|---|
| 10/22(木) | 18:00-21:00 | 🏸 バドミントン | まもり山 | 1,500円（税込） | 動きやすい服装、室内シューズ、タオル、飲み物 | 15名 | ラケット無料レンタルあり（ラケットは手ぶらでOK） |
| 10/24(土) | 14:00-16:00 | ⚽ フットサル | 新宿中央公園 | 1,800円（税込） | 動きやすい服装、運動靴（スパイク不可）、タオル、飲み物 | 20名 | ボール・ビブス完備（シューズのみご持参） |
| 10/31(土) | 11:45-13:45 | 🏐 バレーボール | 中野区中部コミュニティプラザ | 1,500円（税込） | 動きやすい服装、室内シューズ、タオル、飲み物 | 18名 | なし（体育館シューズのみご持参） |

### ファネル
```text
【集客】X / Threads / TikTok / YouTube Shorts   … 毎日投稿で認知を取る
   │  CTA：「プロフィールを見てね」「Instagramで当日の雰囲気を見てね」
   ▼
【オープン教育】Instagram / YouTube / note       … 雰囲気・実績・参加の流れで信頼をつくる
   │  CTA：「プロフィールのリンクから公式LINEで“初参加ガイド”を受け取ってね」
   ▼
【クローズド教育・販売】公式LINE ➔ 予約フォーム … 特典・日程の先行案内・個別質問で申込へ
   │
   ▼
【継続参加・ファン化】参加後のお礼配信・次回案内・口コミ（コメント／ストーリーズ）
```

### マスター思想（5原則）
1. **集客 ➔ 教育 ➔ 販売**：すべての成果物に「ファネル位置」を明示する
2. **インプット2：アウトプット8**：すぐ使える成果物＋仮説＋検証指標でPDCAを速く回す
3. **ターゲットの痛み**：「一人で浮きそう」「ガチ勢が怖い」「準備が面倒」「サードプレイスがない」を言い当てる
4. **投稿ロジック**：冒頭3秒フック ➔ 共感 ➔ 解決 ➔ 保存トリガー ➔ CTA（Canva / CapCutで再現できる指示）
5. **NG**：AI特有の過剰表現・ガチすぎる専門用語・根拠のない数字は禁止。「〜だよ」「〜しよう」の温かい話し言葉

> 共通ヘッダーは `tools/build_ai_employees.py` で一元管理しています。直したら `python3 tools/build_ai_employees.py` を実行すれば28人全員に反映されます。
>
> | 変えたいもの | 編集する場所 |
> |---|---|
> | 思想・コンセプト・ペルソナ・数字（おひとり様参加率など） | `COMMON_HEADER` |
> | 公式LINE・予約フォームなどのURL | `LINKS` |
> | WordPress・ChatWork・Pinterest・Twitch の接続先 | `INTEGRATIONS` |
> | 今月のイベントスケジュール | `EVENT_YEAR` / `EVENT_MONTH` / `EVENTS` |
> | 手動投稿／自動投稿の媒体 | `MANUAL_CHANNELS` / `AUTO_CHANNELS` |
> | 各AI社員の役割・手順・出力フォーマット | `EMPLOYEES` |
>
> スクリプトは、日付と曜日がずれていたり、どれかのファイルにリンクが入っていなかったり、自動投稿用JSONのサンプルが壊れていたりするとエラーで止まります。

---

## 2. フォルダ構造とAI社員一覧

```text
.
├── README.md                           # 本手順書
├── tools/build_ai_employees.py         # 28人分の .md を生成するスクリプト（共通ヘッダー・リンク・イベント情報の一元管理）
├── tools/build_content.py              # 月ごとの毎日投稿コンテンツを生成・検証するスクリプト
├── tools/chatwork_notify.py            # 自動投稿の失敗をChatWorkに通知するメッセージを作る（送信・トークン確認も可）
├── tools/build_make.py                 # Make に読み込む Blueprint と設定ファイルを生成する
├── make/                               # Make 用 Blueprint（01 投稿キュー／02 失敗通知／03 Twitch告知／04 WordPress）と config.json
├── content/2026-10/                    # 10月（10/18〜10/31）の本番用コンテンツ
│   ├── source.py                       #   企画・台本・キャプションの元データ（ここを編集する）
│   ├── auto_posts.json                 #   自動投稿用JSON（Threads / TikTok / Shorts / Pinterest）→ 自動化ツールへ
│   ├── x_reserve_posts.md              #   X予約投稿用フォーマット（人が X の予約投稿機能で予約する）
│   ├── wordpress_posts.json            #   WordPress投稿用JSON（ブログ記事）→ Make の WordPress シナリオへ
│   ├── media_status.json               #   素材連携の完了状況（書き出した動画を "ready": true で書き込む）
│   ├── sheet_rows.json                 #   配信管理表の行番号（id ➔ 行。一度決まったら変えない）
│   ├── sheet_seed.csv / .json          #   配信管理表の初期データ（A〜F列・71行）
│   ├── manual_posts.md                 #   手動投稿用フォーマット（Instagram / LINE / note / YouTube長尺）
│   ├── calendar.md                     #   日別の企画・台本・配信カレンダー
│   └── qc_report.md                    #   品質確認の判定と自動検証の結果
├── examples/2026-10_chain_test.md     # 10月スケジュールでの連係テスト出力（企画立案 ➔ 台本 ➔ キャプション）
├── examples/chatwork_error_logs.json  # ChatWork通知のテスト用エラーログ（6分類）
├── _source/                            # アップロードされた元の定義ファイル（参照用）
└── ai_employees/                       # 28人のAI社員定義ファイル
    ├── 01_research/                    # 【リサーチ・分析系】
    │   ├── market_research.md          # 1. 市場調査AI
    │   ├── competitor_research.md      # 2. 競合調査AI
    │   ├── post_collection.md          # 3. 投稿収集AI
    │   ├── trend_research.md           # 4. トレンド調査AI
    │   └── audience_analysis.md        # 5. 視聴者分析AI
    ├── 02_planning/                    # 【企画・設計系】
    │   ├── idea_generation.md          # 6. 企画立案AI
    │   ├── theme_selection.md          # 7. テーマ選定AI
    │   ├── structure_design.md         # 8. 構成設計AI
    │   └── funnel_architect.md         # 9. CTA・導線設計AI
    ├── 03_content_creation/            # 【制作・ライティング系】
    │   ├── hook_creator.md             # 10. フック作成AI
    │   ├── script_writer.md            # 11. 台本作成AI
    │   ├── title_writer.md             # 12. タイトル作成AI
    │   └── caption_writer.md           # 13. キャプション作成AI
    ├── 04_review_quality/              # 【品質・校正系】
    │   ├── script_reviewer.md          # 14. 台本レビューAI
    │   ├── fact_checker.md             # 15. 事実確認AI
    │   ├── expression_checker.md       # 16. 表現チェックAI
    │   └── quality_controller.md       # 17. 品質確認AI
    ├── 05_visual_production/           # 【ビジュアル・動画制作系】
    │   ├── material_collector.md       # 18. 素材収集AI
    │   ├── image_generator.md          # 19. 画像生成AI
    │   ├── infographic_creator.md      # 20. 図解作成AI
    │   ├── subtitle_creator.md         # 21. 字幕作成AI
    │   ├── video_editor.md             # 22. 動画編集AI
    │   └── audio_adjuster.md           # 23. 音声調整AI
    └── 06_operations_analytics/        # 【運用・分析・改善系】
        ├── posting_manager.md          # 24. 投稿管理AI
        ├── progress_manager.md         # 25. 進行管理AI
        ├── comment_analyzer.md         # 26. コメント分析AI
        ├── numeric_analyst.md          # 27. 数値分析AI
        └── improvement_proposal.md     # 28. 改善提案AI
```

各ファイルは同じ構成です：**共通ヘッダー（マスター思想・コンセプト・ペルソナ）➔ 役割と専門性 ➔ 役割別の必須思想 ➔ 連携フロー（受け取るもの／渡す相手）➔ 作業手順 ➔ 出力フォーマット（3部構成）➔ NG例／OK例**。

---

## 3. セットアップ（初回のみ・約30分）

1. **AI社員を「席」に座らせる**
   - Claudeのプロジェクト（またはカスタムGPT等）を、よく使うAI社員ごとに作り、該当 `.md` の全文を「プロジェクトの指示（システムプロンプト）」に貼り付けます。
   - 全員分つくるのが大変なら、まずは **毎日使う8人**（フック作成・台本作成・キャプション作成・表現チェック・事実確認・品質確認・字幕作成・投稿管理）から始めます。
   - 1つの会話で複数の社員を使う場合は「以下の定義で〇〇AIとして動いて」と、`.md` の中身を貼ってから依頼します。
2. **イベント情報（正）を1か所にまとめる**
   - 日時・曜日・会場・参加費（税込）・持ち物・定員・レンタル用具・申込URLを、Googleスプレッドシートなどで「正」の表として管理します。事実確認AIは必ずこの表と突き合わせます。
3. **導線を用意する**
   - Instagram（https://www.instagram.com/macachette_sports）のプロフィールに公式LINE（https://lin.ee/VwtzoAm）を設定します。TikTok・X・Threadsのプロフィールにも同じURLを置きます。
   - LINE登録特典を1つ決めます（例：「はじめての参加ガイド（当日の流れ・持ち物・服装）」「一人参加さんの不安Q&A」「次回イベントの先行案内」）。
   - 公式LINEの自動応答（友だち追加時のあいさつ）に特典と予約フォーム（https://docs.google.com/forms/d/e/1FAIpQLSfXFehVXHLflywFL5NLtyz55OS_n9y50wC4itvNUK2fXKr7kQ/viewform）を入れておきます。文面はCTA・導線設計AIに作らせます。
4. **素材を集める**
   - 実際の会場・受付・レンタル用具・参加者の笑顔の写真と動画を撮りためます（**参加者が写るものは必ず掲載許可を取る**）。
5. **自動投稿ツールをつなぐ**（Threads・TikTok・YouTube Shorts・Pinterest・WordPress）
   - X は自動投稿しません。`x_reserve_posts.md` を見て、前日までに X の予約投稿機能で予約し、配信管理表の status を `manual` ➔ `manual_posted` に変えます。
   - Make／Zapier／Python連携などで、自動投稿用JSONの配列を受け取り、`status` が `"ready"` のものだけを `scheduled_at` の時刻に `platform` へ送信するシナリオを作ります。
   - 動画（TikTok・Shorts・Pinterest）は `media.file` のファイル名で保存先（Googleドライブなど）から取得します。Pinterest は `link`（リンク先）と `board`（ボード名）も渡します。
   - WordPress は `wordpress_posts.json` を読み、`title`・`content_html`・`excerpt`・`slug`・`wp_status`・`scheduled_at`（公開日時）を、各記事の `endpoint`（`https://public-api.wordpress.com/wp/v2/sites/sportsbackstage1.wordpress.com/posts`、WordPress.com の REST API）に渡します。認証は WordPress.com の OAuth2 です。Make の WordPress モジュールはサイト側にプラグインが必要なため、プラグインを入れられないプランでは Make の HTTP モジュール（OAuth2 接続）から送ります。`categories`・`tags` は名前で入っているので、Make 側でIDに変換します（存在しない名前は作らずにエラーにする）。
   - 送信結果（成功・失敗・投稿URL）を配信管理表に書き戻すようにします。
   - **失敗したとき**は、エラーログを品質確認AI（または `tools/chatwork_notify.py`）に渡し、ChatWork に通知します（「9. 投稿失敗時のChatWork通知」）。
   - **動画・画像の自動生成**（任意）：CapCut／Remotion／Canva などに、投稿の `video_specs`（テロップ・背景素材・読み上げテキスト・BGM）を渡して動画を作ります。書き出しが終わったら `media_status.json` に `"<ファイル名>": {"ready": true}` を書き込みます。
6. **数値記録シートを作る**
   - 下の「7. KPI」の項目を列にしたシートを用意します（数値分析AIにそのまま貼れる形）。

---

## 4. 毎日の運用フロー（フロント毎日投稿 ➔ Instagram・LINEへの導線）

### 4-1. 1本のコンテンツが流れる順番
```text
［リサーチ］トレンド調査・投稿収集・視聴者分析（週1でまとめて、日々は差分だけ）
   ▼
［企画］企画立案 ➔ テーマ選定 ➔ 構成設計 ＋ CTA・導線設計
   ▼
［制作］フック作成 ➔ 台本作成 ➔ タイトル作成 ➔ キャプション作成
   ▼
［品質］台本レビュー ➔ 表現チェック ➔ 事実確認
   ▼
［ビジュアル］素材収集 ➔ 画像生成／図解作成 ➔ 字幕作成 ➔ 音声調整 ➔ 動画編集
   ▼
［最終ゲート］品質確認（5大要素スコア20点以上でPass）
   ▼
［運用］投稿管理 ➔ （24h・72h後）コメント分析・数値分析 ➔ 改善提案 ➔ 企画へ戻る
                   全工程を 進行管理AI が監視
```

### 4-2. 1日のタイムテーブル（例）
| 時間 | 担当AI社員 | やること | 成果物 |
|---|---|---|---|
| 朝（15分） | 進行管理AI | ストック日数・今日の投稿・遅れの確認 | 今日のタスク表 |
| 朝（15分） | トレンド調査AI | 今日使える音源・形式・ワードの差分チェック | トレンドメモ |
| 午前（60分） | フック作成AI ➔ 台本作成AI ➔ 台本レビューAI | 翌日以降のショート動画台本を1〜2本 | 添削済み台本 |
| 午前（30分） | キャプション作成AI ➔ タイトル作成AI | 【自動】Threads・TikTok・Shortsの投稿文 ／【手動予約】Xの投稿文 ／【手動】Instagram・LINE・noteの本文 | 自動投稿用JSON（draft）＋手動投稿用フォーマット |
| 昼（30分） | 表現チェックAI ➔ 事実確認AI ➔ 品質確認AI | 原稿のチェックと最終判定 | 【自動】Passしたものを `ready` に ／【手動】Passした原稿とチェックリスト |
| 午後（60〜90分） | 素材収集AI ➔ 字幕作成AI ➔ 音声調整AI ➔ 動画編集AI／画像生成AI | 動画・カルーセルの制作（指示書どおりにCapCut・Canvaで作業）。自動投稿用の動画はJSONの `media.file` と同じファイル名で書き出す | 完成データ |
| 夕方（15分） | 投稿管理AI | 【自動】`ready` のJSONを自動化ツールのキューへ渡す ／【手動】人の投稿予定とリンク動作の確認 | 配信管理表（投稿方法の列つき） |
| 夕方〜夜（人の作業・20分） | 運営スタッフ | 【手動】チェックリストを見ながらInstagram投稿・LINE配信・note公開 ／【手動予約】翌日分の X を予約 | 投稿済みの更新 |
| 夜（15分） | 投稿管理AI ➔ コメント分析AI | 【自動】送信結果（失敗の再送・手動切り替え）の確認 ／ 前日投稿のコメント・DMへの返信文づくり | 送信ログ・返信文・不安TOP5 |

### 4-3. 媒体別の投稿リズム（初期値・数値を見て調整）
| 媒体 | 投稿方法 | ファネル | 頻度 | 中身 | CTA |
|---|---|---|---|---|---|
| X（手動予約）／ Threads（自動） | 手動予約／自動 | 集客 | 毎日1〜3投稿 | 一人参加あるある・運動不足の共感・当日の小ネタ | プロフィール／Instagramへ |
| TikTok / YouTube Shorts | 自動 | 集客 | 毎日1本 | 冒頭3秒フック＋会場の笑顔ダイジェスト（20〜30秒） | プロフィール／Instagramへ |
| Pinterest | 自動 | 集客 | 毎日1本（ショート動画を転用） | 「一人参加」「初心者」「持ち物」など検索されやすいテーマ | ピンのリンク先（予約フォーム） |
| WordPress（ブログ） | 自動 | オープン教育 | 月1〜2本 | 月間の日程・当日の流れ・持ち物（検索で見つけた人向け） | 予約フォーム／公式LINEへ |
| Instagram（リール・カルーセル） | 手動 | オープン教育 | 週4〜5本 | 参加の流れ・持ち物・参加者の声・初心者Q&A（保存される情報） | 公式LINE（特典）へ |
| Instagram（ストーリーズ） | 手動 | オープン教育 | 毎日 | 準備の様子・当日のライブ感・質問箱・リマインド | 公式LINE／予約フォームへ |
| YouTube（長尺）／note | 手動 | オープン教育 | 週1〜月2 | 「はじめての人ガイド」「1日の様子まるごと」など深い安心材料 | 公式LINEへ |
| 公式LINE | 手動 | クローズド教育・販売 | 週1〜2配信 | 次回イベントの先行案内・残り枠・不安Q&A・参加後のお礼 | 予約フォームへ |

### 4-4. AI社員への依頼テンプレ（コピペ用）
```text
【依頼】{AI社員名}として、以下の条件で出力してください。
・媒体：{例：Instagramリール}
・ファネル位置：{集客／オープン教育／クローズド教育・販売}
・今回のゴール（1つ）：{例：公式LINE登録}
・狙うPain：{一人で浮きそう／ガチ勢が怖い／準備が面倒／サードプレイスがない}
・前工程の成果物：{前のAI社員の出力を貼る}
・イベント情報（正）：{日時・会場・参加費・持ち物・申込URL など}
```
前のAI社員の出力をそのまま次のAI社員へ貼ってつないでいくのが基本です（各ファイルの「連携フロー」に、受け取るものと渡す相手が書いてあります）。

---

## 5. 月間イベントスケジュールの運用（毎月25日〜末日）

毎日の投稿とイベント告知を途切れさせないために、**翌月1か月分の日程を毎月25日〜末日にまとめてAIへ渡します**。

1. **スクリプトを更新する**：`tools/build_ai_employees.py` の `EVENT_YEAR` / `EVENT_MONTH` / `EVENTS` を翌月分に書き換え、`python3 tools/build_ai_employees.py` を実行してコミットします（曜日の間違いはここでエラーになります）。
2. **企画立案AIに渡す**：次の形式で翌月の日程を貼ります。企画立案AIが、開催日から逆算して「どの週に・どの媒体で・何を出すか」を割り振ります。
   ```text
   【翌月イベントスケジュール】{年}年{月}月
   ・{月}/{日}({曜}) {開始}-{終了} {絵文字}{種目}＠{会場}
   ・…（翌月の開催分をすべて）
   【共通情報】参加費：／持ち物：／定員：／レンタル用具：
   【予約フォーム】（変更があれば）
   【今月の重点】（例：初参加の女性を増やしたい、バレーの集客が弱い）
   ```
3. **投稿管理AIに渡す**：同じ日程と企画立案AIの割り振り表を貼ります。投稿管理AIが、フロント拡散 ➔ Instagram ➔ 公式LINE ➔ 予約フォームの1か月分の配信カレンダーを作ります。
4. **逆算のルール**（両AI社員の定義に組み込み済み）：月初にラインナップ発表 ➔ 14〜8日前に種目別の認知 ➔ 7日前に告知 ➔ 3日前に残り枠のリマインド ➔ 前日に最終案内 ➔ 当日にストーリーズ ➔ 翌日にレポートと次回案内。開催日が近いイベントのLINE配信は1通にまとめます（週2通まで）。

5. **1か月分のコンテンツを生成する**：企画立案AI ➔ 台本作成AI ➔ キャプション作成AI ➔ 品質確認AI の出力を `content/<年-月>/source.py` にまとめ、次を実行します。
   ```bash
   python3 tools/build_content.py 2026-10
   ```
   `auto_posts.json`・`manual_posts.md`・`calendar.md`・`qc_report.md` が書き出されます。次のどれかに当てはまると、エラーで止まって何も書き出しません。
   - JSONとして読み込めない
   - 文字数の上限を超えている（X：全角140字・URLは1つ23字換算／Threads：500字／TikTok：2,200字／Shorts：タイトル100字）
   - 実運用リンクにないURLがある、またはTikTok・Shorts・Instagramの本文にURLがある
   - 日付・曜日・時間・会場・参加費・定員がイベント情報と違う
   - 告知の投稿が開催後になっている
   - `ready` の投稿に【要確認】が残っている
6. **`hold` を `ready` にする**：自動投稿のうち、次の2つは `hold` で止めてあります。
   - **TikTok・Shorts・Pinterest（素材連携で自動昇格）**：動画ファイル（`media.file` の名前）の素材がそろうと `video_ready=True` になり、再生成のときに自動で `ready` に上がります。`video_ready=True` になる条件は次のどれか1つです。
     - `media_status.json` に `{"2026-10-19_V02.mp4": {"ready": true}}` のように書き込まれている（自動生成ツールや Make が書き込む）
     - `content/2026-10/media/` にそのファイルが置かれている
     - `source.py` の VIDEOS に `video_ready=True` と書いてある
   - **開催レポート**：素材がそろっても自動では上がりません。開催後に様子を確認し、【開催後に記入】を埋めて `source.py` の `hold_reason` を消してから再生成します。

10月分の本番用コンテンツは `content/2026-10/`、詳細が確定する前の連係テストは `examples/2026-10_chain_test.md` にあります。

## 6. PDCAサイクル（週次・月次）

### 毎週（例：月曜朝・60分）
1. **数値分析AI**：先週の数字をシートから貼り、媒体別KPI・ファネル転換率・上位/下位3投稿を出す
2. **コメント分析AI**：先週のコメント・DMを貼り、頻出の不安TOP5を出す
3. **改善提案AI**：上の2つを渡し、KPT（Keep／Problem／Try）を作る（Tryは最大3つ、担当・期限・検証指標・合格ライン付き）
4. **視聴者分析AI・トレンド調査AI・投稿収集AI**：今週のネタの材料をまとめる
5. **企画立案AI ➔ テーマ選定AI**：Tryを反映した今週の企画10本 ➔ 上位テーマを選ぶ
6. **進行管理AI ➔ 投稿管理AI**：今週の制作タスクと投稿カレンダーを確定する

### 毎月（月末・90分）
- **市場調査AI・競合調査AI**：季節要因・競合の動きを確認し、来月の勝ち筋を出す
- **CTA・導線設計AI**：プロフィール文・LINE特典・自動応答文を数字に合わせて見直す
- **25日〜末日**：翌月のイベントスケジュールを `EVENTS` に反映して再生成し、企画立案AI・投稿管理AIへ渡す（「5. 月間イベントスケジュールの運用」）
- 共通ヘッダーの数字（おひとり様参加率など）が変わっていれば `tools/build_ai_employees.py` を更新して再生成する

---

## 7. KPI（数値分析AIに渡す項目）

| ファネル | 指標 | 計算式 | 見るポイント |
|---|---|---|---|
| 集客 | インプレッション／リーチ | 各媒体のインサイト | フックが機能しているか |
| 集客 | 3秒視聴率・平均視聴維持率 | 動画インサイト | 冒頭3秒と構成のテンポ |
| オープン教育 | 保存率 | 保存数 ÷ リーチ | 保存トリガーが効いているか |
| オープン教育 | プロフィール遷移率 | プロフィールアクセス ÷ リーチ | 投稿CTAの強さ |
| クローズド教育 | LINE登録率 | LINE新規登録 ÷ プロフィールアクセス（またはリンクタップ） | プロフィール文・特典の魅力 |
| 販売 | 予約率 | 予約数 ÷ LINE新規登録 | LINE配信・案内のわかりやすさ |
| ファン化 | リピート率 | 2回目以降の参加者 ÷ 参加者 | 当日の体験・参加後フォロー |

> 目標値はアカウントの規模で大きく変わるため、最初の2〜4週間で現状値を測り、改善提案AIのTryで「前週比どれだけ上げるか」を合格ラインとして決めていきます。

---

## 8. 運用ルール（必ず守ること）
- **事実の正しさ**：日時・会場・参加費・「8割」などの数字は、必ずイベント情報（正）と運営の実績に基づくこと。事実確認AIを通らない原稿は投稿しない。
- **リンクの正しさ**：CTAのURLは「実運用リンク」の表のものだけを使う。投稿前に投稿管理AIの確認フローで、すべてのリンクが開けるかを確かめる。
- **肖像権・掲載許可**：参加者が写る写真・動画は、掲載許可を取ったものだけを使う。
- **音源の権利**：各プラットフォームで商用利用できる音源だけを使う。
- **AIっぽさの排除**：投稿前に必ず表現チェックAIを通し、「〜の世界へようこそ」「革命的な」などのNG表現を残さない。
- **手動投稿媒体（Instagram・公式LINE・note・YouTube長尺）**：品質確認AIでPassになっても、投稿・配信するのは人。手動投稿用フォーマットのチェックリストをすべて埋めてから投稿する。
- **手動予約媒体（X）**：自動投稿ツールは X を送らない。人が `x_reserve_posts.md` のチェックリストを埋めてから予約する。
- **自動投稿媒体（Threads・TikTok・YouTube Shorts・Pinterest）**：人の目を通らずに公開されるため、品質確認AIのPassで `"ready"` になったものだけを自動化ツールが送信する。`"draft"`・`"hold"` は絶対に送信しない。送信に失敗したものは投稿管理AIが原因を記録し、再送するか手動投稿に切り替える。
- **フォーマットを崩さない**：自動投稿用JSONは、キー名や構造を人の手で変えない（自動化ツールが読めなくなる）。直すときは `text`・`thread`・`title` の中身だけを直す。

## 9. 投稿失敗時のChatWork通知

自動投稿ツール（Make など）でAPIエラーが起きたら、品質確認AIが原因を分類して「AIによる修正案」をつけ、ChatWork の指定ルームに通知します。仕様の全文は `ai_employees/04_review_quality/quality_controller.md` の【投稿失敗時のエラーハンドリングとChatWork通知】にあります。

**流れ**
1. Make のエラーハンドラー（Error handler ルート）で、失敗した投稿のエラーログを作る（`post_id`・`platform`・`scheduled_at`・`attempt`・`error`・`post`）。
2. 品質確認AIのプロンプトにエラーログを渡し、通知JSON（`room_id`・`body`・`error_class`・`retry`・`fixed_post`）を作ってもらう。AIを使わない場合は `tools/chatwork_notify.py` が分類ごとの定型の修正案で同じ形の通知を作る。
3. ChatWork API（`POST https://api.chatwork.com/v2/rooms/{room_id}/messages`、ヘッダー `X-ChatWorkToken`、フォームの `body`）に送る。
4. `retry.auto` が `true`（`rate_limit`・`server`）なら、`retry.after_minutes` 後に自動で再送する（最大3回）。それ以外は、通知を見た運営・投稿管理AIが対応する。

**原因の分類**
| 分類 | 例 | 自動リトライ | 次の対応 |
|---|---|---|---|
| `auth` | HTTP 401/403、トークン切れ | なし | Make の接続を再認証してから手動で再送 |
| `rate_limit` | HTTP 429 | あり（15分間隔・最大3回） | 時間をあけて自動で再送 |
| `content` | HTTP 400/422、文字数オーバー・重複投稿 | なし | AIの修正案（`fixed_post`）で直し、品質確認AIが再チェックしてから再送 |
| `media` | 動画が見つからない・形式が合わない | なし | 素材を書き出し直して `media_status.json` を更新 |
| `server` | HTTP 5xx・タイムアウト | あり（5分 ➔ 15分 ➔ 60分） | 自動で再送 |
| `unknown` | 上記以外 | なし | `hold` に戻してエラーログを確認 |

**スクリプトでの使い方**
```bash
python3 tools/chatwork_notify.py error_log.json          # 通知内容を表示するだけ（送信しない）
cp .env.example .env   # 初回だけ。.env の CHATWORK_API_TOKEN= にトークンを入れる（git には入らない）
python3 tools/chatwork_notify.py error_log.json --send   # ルーム 363171715 に送信
python3 tools/chatwork_notify.py --self-test              # 6分類のテスト（examples/chatwork_error_logs.json）
```

**守ること**
- 通知先ルームは https://www.chatwork.com/#!rid363171715（ルームID `363171715`）。別のルームに送るときは環境変数 `CHATWORK_ROOM_ID` で上書きする。
- ChatWork の APIトークンは Make の接続設定か環境変数 `CHATWORK_API_TOKEN`（`.env`）で管理し、リポジトリ・プロンプト・JSONには書かない。エラーログに混ざったトークンやパスワードは、通知の前に伏せ字（`****`）にする（`tools/chatwork_notify.py` は自動で伏せる）。
- `fixed_post` はそのまま再送しない。品質確認AIの再チェックでPassになってから `ready` に戻す。
- 同じ投稿の同じエラーは1回だけ通知し、10分以内に5件以上失敗したら1通にまとめる（Make 側で設定）。

## 10. 予定時刻を過ぎた投稿の扱い（運用開始日・停止明けのガイドライン）

運用を始めた日や、自動投稿ツールが止まっていたあとは、`scheduled_at` を過ぎた `ready` の投稿が残ります。告知の時期がずれると「明日やるよ」が当日に出るなど、事実と食い違うおそれがあるため、**過ぎた投稿はそのまま自動で送らず**、次のルールで扱います。

**自動投稿ツール（Make など）の設定**
- `scheduled_at` を過ぎて30分以内なら、そのまま送信する。
- 30分を超えて過ぎたものは自動では送らず、配信管理表に「期限切れ」と記録して ChatWork に1通まとめて知らせる。

**期限切れになった投稿の判断（投稿管理AI・運営）**
| 状況 | 対応 |
|---|---|
| その日のうちで、本文の内容がまだ正しい（「今日」「明日」などの表現が今の時点でも合っている） | **手動投稿でカバー**：`auto_posts.json` の `text` をコピーして、運営が手で投稿する。投稿後、配信管理表を「手動で投稿済み」にする |
| 翌日以降に出しても内容が正しく、開催開始より前に出せる | **繰り延べ**：`source.py` の日時を翌日以降の空いている時間に変えて再生成する（同じ媒体の投稿と重ならない時間にする）。告知が開催開始より後になる場合は、検証でエラーになって止まる |
| 「明日」「今日」など日付に依存していて、もう合わない／開催が終わった | **見送り**：投稿しない。配信管理表に「見送り」と理由を書く |

**2026/10/18（運用開始日）の適用**
| 投稿 | 予定 | 対応 |
|---|---|---|
| X `2026-10-18-x-01`（今週は2つやるよ） | 07:30（過ぎている） | 当日中は内容が正しいので、**手動投稿でカバー**（夕方までに運営がコピペで投稿）。間に合わなければ見送り（10/19 07:30 の X が同じイベントを告知するため） |
| Threads `2026-10-18-threads-01`（今週は2つ） | 12:00（過ぎている） | 同上。**当日中に手動投稿でカバー** |
| TikTok・YouTube Shorts・Pinterest（V01） | 12:00／18:00／20:00 | もともと `hold`（動画の書き出し待ち）。今日中に書き出せなければ見送り |
| Instagram ストーリーズ・公式LINE・Instagram カルーセル | 19:00／20:00／21:00 | 手動投稿の予定どおり |

## 11. 自動投稿ツールの稼働設定（ステップ5）のチェックリスト

Make を例にした接続の順番です。上から順に設定し、最後にテスト投稿で確認します。

**A. 事前準備**
- [ ] WordPress.com の初期記事（`/2026/09/04/hello-world/`）を削除し、カテゴリ「イベント案内」とタグ（`wordpress_posts.json` の `tags`）を作っておく
- [ ] Instagram・TikTok・X・Threads のプロフィールに公式LINE（https://lin.ee/VwtzoAm）を設定する
- [ ] `.env.example` を `.env` にコピーし、`CHATWORK_API_TOKEN` を入れる（ChatWork の「サービス連携 ➔ APIトークン」で発行）
- [ ] 動画・画像の保存先（Googleドライブのフォルダなど）を決め、`media.file` のファイル名で置くルールを共有する

**B. Make の接続（Connections）**
| 接続 | 使う投稿 | 確認すること |
|---|---|---|
| Threads | `"threads"` | Instagram と同じ Meta アカウントで認可されているか |
| TikTok | `"tiktok"` | 動画の直接投稿の権限があるか |
| YouTube | `"youtube_shorts"` | 投稿先チャンネルが正しいか |
| Pinterest | `"pinterest"` | `board` と同じ名前のボードがあるか |
| WordPress.com（HTTP・OAuth2） | `wordpress_posts.json` | `endpoint` に送れるか（`wp_status: "draft"` でテスト） |
| ChatWork | 失敗通知 | ルーム 363171715 にテストメッセージが届くか |

**C. シナリオ（Scenarios）**
1. **投稿キュー**（15分ごとに実行）：`auto_posts.json` と `wordpress_posts.json` を読み込む（GitHub の raw URL、またはGoogleドライブに置いたコピー）。次のすべてに当てはまるものだけを送る。
   - `status` が `"ready"`
   - `scheduled_at` が今から30分前〜今の間
   - まだ送っていない（配信管理表に記録がない）
2. **媒体ごとの送信**：Router で `platform` ごとに分け、各媒体のモジュールに `text`・`title`・`media`・`link`・`board` を渡す。WordPress は HTTP モジュールで `endpoint` に POST する。
3. **結果の記録**：成功したら投稿URLを、失敗したらエラー内容を、配信管理表に書き戻す。
4. **エラーハンドラー**：各送信モジュールに Error handler を付け、エラーログ（`post_id`・`platform`・`scheduled_at`・`attempt`・`error`・`post`）を作る。品質確認AIの通知仕様（または `tools/chatwork_notify.py`）で通知を作り、ChatWork に送る。`retry.auto` が `true` のときだけ `retry.after_minutes` 後に再送する。
5. **期限切れ**：`scheduled_at` を30分以上過ぎた `ready` は送らず、「期限切れ」として記録し、ChatWork に1通まとめて知らせる（「10. 予定時刻を過ぎた投稿の扱い」）。
6. **素材連携**（任意）：動画の書き出しが終わったら `media_status.json` に `"ready": true` を書き込み、`python3 tools/build_content.py 2026-10` を実行して JSON を作り直す。

**D. 稼働前のテスト**
- [ ] `python3 tools/build_content.py 2026-10` と `python3 tools/chatwork_notify.py --self-test` が通る
- [ ] Threads にテスト投稿を1件だけ流し、送信 ➔ 配信管理表への記録まで確認する
- [ ] わざと失敗する投稿（例：上限を超える長文）を1件流し、ChatWork のルームに通知が届くか確認する
- [ ] WordPress に `wp_status: "draft"` で1件送り、見出し・表・リンクの表示を確認してから `"future"` に戻す

## 12. Make 稼働設定（ステップ5）：Blueprint・配信管理表・ChatWork

`python3 tools/build_make.py 2026-10` で `make/` に Blueprint と `config.json` が作られます（APIトークンは含みません。含まれていたら生成が止まります）。

### 12-1. 設定値
| 項目 | 値 |
|---|---|
| Make | eu1.make.com／チーム「My Team」 |
| 投稿データ | `https://raw.githubusercontent.com/kiichi4268/-ai_employees-/main/content/2026-10/auto_posts.json`（WordPress は `wordpress_posts.json`） |
| キャッシュ回避 | 取得のたびに `?t={{formatDate(now; "x")}}`（ミリ秒のUNIX時刻）を付け、`Cache-Control: no-cache` を送る |
| 配信管理表 | スプレッドシート `1m7VCzodX8U3xzuTzFYOXQX8IWfExvXXvo6T3Xq3Gstk` のシート「配信管理表」 |
| 配信管理表の列 | A `id`／B `platform`／C `scheduled_at`／D `status`／E `posted_at`／F `log`（G列以降は人が使う欄：配信日・配信内容・対象者・媒体・ステータス・担当者・備考） |
| ChatWork | ルーム 363171715（https://www.chatwork.com/#!rid363171715）。トークンは `.env` の `CHATWORK_API_TOKEN` と、Make の「HTTP ➔ API key」接続（ヘッダー `X-ChatWorkToken`）にだけ入れる |

**配信管理表の `status`**
| 値 | 意味 |
|---|---|
| `ready` | 送信待ち |
| `hold` | 保留中（`log` に理由） |
| `posted` | 送信成功（`posted_at` に日時、`log` に投稿URL） |
| `failed` | 送信失敗（ChatWork に通知済み） |
| `retrying` | 自動リトライ待ち（rate_limit・server） |
| `expired` | 予定時刻を30分以上過ぎたため送らなかった |
| `manual_posted` | 運営が手動で投稿した |
| `skipped` | 見送り |
| `module_missing` | Make にその媒体の投稿モジュールがまだない |

### 12-2. 配信管理表の準備（初回だけ）
1. シート「配信管理表」の1行目を、A〜F列 `id, platform, scheduled_at, status, posted_at, log` にする（今ある見出し「配信日〜備考」は G〜M列に移す）。
2. `content/2026-10/sheet_seed.csv` の2行目以降（71行）を A2 から貼り付ける。各投稿の行番号は `auto_posts.json` の `sheet_row` と一致していて、Make はこの行番号で結果を書き戻す。
3. 投稿を作り直して新しい id が増えたときは、`sheet_rows.json` で決まった行番号のところに追記する（既存の行番号は変わらない）。

### 12-3. Make への読み込み
各シナリオで「…」➔「Import Blueprint」から `make/0*.blueprint.json` を読み込み、接続を選びます。

| シナリオ | 動き | 選ぶ接続 | 稼働設定 |
|---|---|---|---|
| 01 投稿キュー | 15分ごとに `auto_posts.json` を取得し、`ready` で予定時刻が直近15分以内の投稿を媒体ごとに振り分け、配信管理表に書き戻す | Google（配信管理表） | 15分ごと |
| 02 投稿失敗の ChatWork 通知 | Webhook でエラーログを受け、原因の分類と修正案をつけて ChatWork に通知し、配信管理表を `failed`／`retrying` にする | HTTP API key（ChatWork）、Google | 即時（Webhook） |
| 03 Twitch 配信開始 | Twitch EventSub の確認（challenge）に答え、`stream.online` を受けたら「ライブ配信スタート！」の告知を配信管理表に記録する | Google | 即時（Webhook） |
| 04 WordPress 記事 | 15分ごとに `wordpress_posts.json` を取得し、予定時刻の記事を WordPress.com に送り、結果を書き戻す。失敗したら ChatWork に通知 | WordPress.com（HTTP・OAuth2）、HTTP API key（ChatWork）、Google | 15分ごと |

**読み込んだあとに必要な作業**
- **01・03 の各ルート**：X・Threads・TikTok・YouTube・Pinterest の投稿モジュールを、配信管理表を書き換えるモジュールの前に追加する。各SNSの接続はアカウントのログインが必要なので、Make の画面で作る。そのうえで、書き戻しの値を `status=posted`・`posted_at={{now}}`・`log=投稿URL` に変える。追加するまでは `module_missing` と記録され、誤って `posted` にはならない。
- **投稿モジュールのエラーハンドラー**：HTTP モジュールで 02 の Webhook URL にエラーログを POST する。中身は `post_id`・`platform`・`scheduled_at`・`sheet_row`・`attempt`・`error`・`post`・`retry_auto`。
- **Twitch**：EventSub の `stream.online` 購読を作り、callback に 03 の Webhook URL を登録する。Twitch の署名（`Twitch-Eventsub-Message-Signature`）は Make の標準フィルターでは確かめられない。そのため、配信者ID（`event.broadcaster_user_id`）の一致もフィルターに足しておく。
- **ChatWork のトークン確認**：`python3 tools/chatwork_notify.py --check` で、メッセージを送らずに確認できる。

## 13. GitHub Actions で自動投稿する（費用0円）

`tools/run_queue.py` が、配信管理表で `ready` の投稿を予定時刻に各SNSの公式APIで送ります。`.github/workflows/post.yml` が日本時間 10:00／12:00／18:00／20:00／21:00 の2分後と17分後にだけ動かします（月300分ほど。非公開リポジトリの無料枠2,000分に収まります）。

| 媒体 | 送信 | 必要な Secrets |
|---|---|---|
| Threads | ✅（文章のみ。`thread` は返信でつなぐ） | `THREADS_ACCESS_TOKEN` |
| Pinterest | ✅（動画・画像。ボードは `board` の名前で探す） | `PINTEREST_ACCESS_TOKEN` |
| WordPress | ✅（カテゴリ・タグは名前でIDに変換。同じ slug があれば送らない） | `WORDPRESS_TOKEN` |
| Instagram リール | ✅（TikTok・Shorts の動画を転用。動画は Meta に直接アップロード） | `INSTAGRAM_ACCESS_TOKEN`・`INSTAGRAM_USER_ID` |
| Instagram ストーリーズ | ✅ スタンプなしの画像・動画だけ（画像は WordPress のメディアに上げた公開URLを使う）。リンク・質問スタンプ付き、シェア、実況は手動のまま | 上と同じ＋画像のときは `WORDPRESS_TOKEN` |
| TikTok・YouTube Shorts | まだ作っていない（`module_missing` と記録） | トークン取得後に追加 |
| X | **送らない**（手動予約。`x_reserve_posts.md`） | なし |
| 配信管理表・ChatWork | 送信結果の書き戻し・失敗通知 | `GOOGLE_SERVICE_ACCOUNT_JSON`・`CHATWORK_API_TOKEN` |

**まとめて設定する（おすすめ）**：ご本人のPCで、リポジトリ直下から1回実行するだけです。
```bash
cp .env.example .env    # 集めた鍵（Client ID・Secret、Meta のトークン、Pinterest・ChatWork のトークン）を入れる
python3 tools/setup_all.py --google-json ~/Downloads/サービスアカウント.json --upload
```
足りないトークンの取得（WordPress・Threads はブラウザで「許可」を1回）➔ 読み取りだけの確認 ➔ GitHub Secrets への登録（gh CLI。値は画面に出ない）まで行います。✗ が1つでもあれば Secrets には登録しません。gh CLI がないときは `--upload` を外すと、登録する7つを `.secrets.upload.env` に書き出します（画面から登録したら消す）。

**動かし方（1つずつ行う場合）**
1. トークンをご自身のPCで取得する：`python3 tools/get_tokens.py wordpress`（`youtube`／`tiktok`／`threads` も同じ）。ブラウザで「許可」を押すと `.env` に保存されます。Instagram は `python3 tools/get_tokens.py instagram`（`.env` の `META_APP_ID`・`META_APP_SECRET`・`META_ACCESS_TOKEN` から、期限なしのページトークンと Instagram のIDを作ります。ブラウザ操作は不要）。
2. GitHub の **Settings ➔ Secrets and variables ➔ Actions** に、上の表の Secrets を同じ名前で登録する（チャットには貼らない）。サービスアカウントのメールアドレスを、配信管理表の「共有」に編集者で追加する。
3. **Actions ➔ post-queue ➔ Run workflow** を `dry_run=1` で実行する（何も送られません）。最初に `--check` が鍵ごとに ✓ OK／－ 未設定／✗ NG を表示し、続けて送る予定の投稿を表示します。✗ があれば、その鍵を作り直して Secrets を更新します。
4. 問題なければ、**Variables** に `QUEUE_ENABLED=true`（定期実行を開始）と `DRY_RUN=0`（本番送信）を追加する。止めたいときは `QUEUE_ENABLED` を消すだけです。

- 送る前に配信管理表を `posting` にして二重投稿を防ぎます。成功すると `posted`・`posted_at`・投稿URL、失敗すると `failed`・エラー内容を書き戻し、ChatWork に通知します（`rate_limit`・`server` は3回まで再送）。
- 予定時刻を30分以上過ぎた `ready` は送らずに `expired` にします。鍵が未設定の媒体は送らずに `module_missing` と記録します。
- `posting` のまま残った行（送信中に止まった）は自動では送り直しません。SNS を見て `posted` か `ready` に手で直します。
- 配信管理表の1行目が `id, platform, scheduled_at, status, posted_at, log` でないとき・読めないときは、何も送らずに止まり ChatWork に知らせます。
- 配信管理表の行番号：2〜72行目は10月の初期分、73〜77行目は自動化した Instagram（リール4件・ストーリーズ1件）。行番号は `sheet_rows.json` で固定し、あとから足した投稿は末尾に追加します。
- 手元での確認：`python3 tools/run_queue.py --self-test`、`python3 tools/run_queue.py --now 2026-10-26T12:05`（`DRY_RUN=1` が既定）。
