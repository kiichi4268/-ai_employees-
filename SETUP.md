# 🔰 初期設定ガイド（はじめての人向け）

自動投稿を動かすための「最初の1回だけの準備」です。
**上から順番に、1つずつ進めれば終わります。** わからなくなったら、その手順の番号を Claude に伝えてください。

---

## 0. はじめに読むこと（1分）

### 全体の流れ
```
 ① 準備            ② 鍵を集める         ③ コマンドを1回     ④ GitHub に登録     ⑤ テスト
 パソコンに入れる ➔ 6つのサイトで   ➔ 質問に貼り付ける ➔ 鍵を預ける     ➔ ボタンを押して確認
                   「鍵」をもらう                                              ➔ 完了！
```
- **かかる時間**：2〜3時間くらい（いちばん時間がかかるのは Meta＝Instagram・Threads）
- **お金**：0円（どのサイトも無料の範囲で使います）
- **X（旧Twitter）は自動投稿しません**。`content/<年-月>/x_reserve_posts.md` を見て、X の予約投稿で手で予約します。
- **YouTube Shorts・TikTok は、この初期設定のあとで追加します**（今回は設定しなくてOK）。

### 🔑「鍵」ってなに？
自動投稿のプログラムが、あなたの代わりに各SNSへ投稿するための **合言葉** です。
家の鍵と同じで、**人に渡すと勝手に投稿されてしまいます。**

### ⚠️ 守ってほしいこと 3つ
1. **鍵はチャット（Claude・LINE・メール）に貼らない。** 貼るのは、この手順で出てくる「黒い画面の質問」と「GitHub の Secrets」だけ。
2. **`.env` というファイルは、人に送らない・消さない。** あなたのパソコンにだけ置いておく鍵の保管箱です。
3. **わからない質問は、Enter キーだけ押して飛ばしてOK。** あとで何度でもやり直せます。

---

## 1. 準備（最初の1回だけ・20分）

### 1-1. Python（パイソン）を入れる
プログラムを動かすための道具です。

- **Mac**：入っていることが多いです。下の 1-3 で `python3 --version` と打って、`Python 3.9` 以上の数字が出ればOK。出なければ ↓
- **Windows・Mac 共通**：https://www.python.org/downloads/ を開く ➔ 黄色い「Download Python」ボタン ➔ ダウンロードしたファイルを開いてインストール。
  - **Windows は、最初の画面の「Add python.exe to PATH」に必ずチェック** を入れてから「Install Now」。

### 1-2. このプログラムをパソコンに置く
1. https://github.com/kiichi4268/-ai_employees- を開く（GitHub にログインしておく）
2. 緑色の **「Code」** ボタン ➔ **「Download ZIP」**
3. ダウンロードした ZIP をダブルクリックして開く（Windows は右クリック ➔「すべて展開」）
4. できたフォルダ（`-ai_employees--main`）を **デスクトップ** に移す

### 1-3. 黒い画面（ターミナル）を開いて、フォルダに入る
- **Mac**：
  1. 「アプリケーション ➔ ユーティリティ ➔ ターミナル」を開く
  2. `cd ` と打つ（cd のあとに **半角スペース**）
  3. デスクトップのフォルダを、黒い画面に **ドラッグ＆ドロップ** して Enter
- **Windows**：
  1. デスクトップのフォルダを開く
  2. フォルダの中の何もないところで **右クリック ➔「ターミナルで開く」**

> 💡 このあと、この黒い画面に「コマンド」を打ちます。**この画面は閉じずに置いておいてください。**

---

## 2. 鍵を集める（6つのサイト・1〜2時間）

それぞれのサイトで「鍵」をもらいます。**もらった鍵は、手順3で黒い画面に聞かれたときに貼り付けます。**
（メモ帳に一時的に貼るのはOK。終わったらメモは消してください）

### ✅ ① ChatWork（5分）➔ 投稿に失敗したとき知らせてくれる
1. ChatWork にログイン ➔ 右上の **自分の名前** ➔ **「サービス連携」**
2. 左の **「API トークン」** ➔ パスワードを入れる ➔ 表示された英数字が鍵
- 🔑 もらうもの：**ChatWork の API トークン**
- 会社のプランで「API は管理者の許可が必要」と出たら、管理者に許可してもらう

### ✅ ② Pinterest（10分）
1. https://developers.pinterest.com/ ➔ ログイン ➔ **「My apps」** ➔ アプリを開く（なければ「Connect app」で作る）
2. **「Generate token」**（アクセストークンを作る）で、`boards:read`・`pins:read`・`pins:write`・`user_accounts:read` にチェック ➔ 作成
- 🔑 もらうもの：**`pina_` で始まるトークン**
- Pinterest に **「Macachette Sports｜東京の社会人スポーツ会」** という名前のボードを作っておく（1文字も違わない名前）

### ✅ ③ WordPress（10分）➔ ブログ記事
1. https://developer.wordpress.com/apps/ ➔ アプリ（151333）を開く。なければ **「Create New Application」**
2. 次のように入れて保存：
   - Website URL：`https://sportsbackstage1.wordpress.com`
   - **Redirect URLs：`http://localhost:8080/callback`**（ここが一番大事）
   - Type：**Web**
3. 画面の下にある **Client ID**（数字）と **Client Secret**（長い英数字）が鍵
- 🔑 もらうもの：**Client ID**・**Client Secret**
- ブログの「投稿 ➔ カテゴリー」に **「イベント案内」** を作っておく

### ✅ ④ Google（20分）➔ 配信管理表（スプレッドシート）を読み書きする
1. https://console.cloud.google.com/ ➔ 上の「プロジェクトを選択」➔ **「新しいプロジェクト」**（名前は何でもOK）
2. 左上の ☰ ➔ **「API とサービス ➔ ライブラリ」** ➔ 「Google Sheets API」を検索 ➔ **「有効にする」**
3. ☰ ➔ **「IAM と管理 ➔ サービスアカウント」** ➔ **「サービスアカウントを作成」** ➔ 名前を入れて「完了」（役割は選ばなくてOK）
4. できたサービスアカウントをクリック ➔ **「鍵」** タブ ➔ **「鍵を追加 ➔ 新しい鍵を作成 ➔ JSON」** ➔ ファイルがダウンロードされる
5. **配信管理表のあるスプレッドシート「大元の配信先」を開く**（https://docs.google.com/spreadsheets/d/19jGf5YypvpJOV8AtEpByoL6u5mPDGetQpLM-n6Kl53A/edit ）**➔ 右上の「共有」** ➔ サービスアカウントのメールアドレス（`〜@〜.iam.gserviceaccount.com`）を入れて **「編集者」** で共有
- 🔑 もらうもの：**ダウンロードした JSON ファイル**（ファイルのまま。中身を開かなくてOK）
- 「鍵の作成が組織のポリシーで無効」と出たら、会社のアカウントではなく **個人の Gmail** で作り直す

### ✅ ⑤ Instagram（30分）➔ リール・ストーリーズ
1. Instagram アプリ ➔ 設定 ➔ **「プロアカウントに切り替える」➔「ビジネス」**
2. Instagram を **Facebook ページとリンク** する（Instagram の設定 ➔「アカウントセンター」、または Facebook ページの設定 ➔「リンク済みのアカウント」）
3. https://developers.facebook.com/ ➔ **「マイアプリ」➔「アプリを作成」**（種類は「ビジネス」）
4. アプリの **「設定 ➔ ベーシック」** に **アプリID**（数字）と **app secret**（「表示」を押す）がある
5. https://developers.facebook.com/tools/explorer/ （Graph API エクスプローラー）を開く
   - 右の「Meta アプリ」で 3 のアプリを選ぶ
   - 「許可を追加」で **`instagram_basic`・`instagram_content_publish`・`pages_show_list`・`pages_read_engagement`** の4つにチェック
   - **「Generate Access Token」** ➔ ログインして許可 ➔ 表示された `EAA…` / `EAB…` で始まる長い文字が鍵
- 🔑 もらうもの：**アプリID**・**app secret**・**`EAA…`/`EAB…` のトークン**

### ✅ ⑥ Threads（30分）
1. ⑤ と同じ Meta のアプリ（または新しいアプリ）で、**「ユースケース」➔「Threads API にアクセス」** を追加
2. Threads の **「設定」** に **Threads アプリID** と **Threads App Secret** がある（Facebook のアプリIDとは別の番号）
3. 同じ画面の **「コールバックURL」**（リダイレクト）に **`https://sportsbackstage1.wordpress.com/`** を入れて保存
4. **「アプリの役割 ➔ 役割 ➔ Threads テスター」** に、自分の Threads アカウントを追加
5. Threads アプリ ➔ 設定 ➔ **アカウント ➔ ウェブサイトのアクセス許可 ➔ 招待** ➔ **承認**
- 🔑 もらうもの：**Threads アプリID**・**Threads App Secret**

---

## 3. コマンドを1回打つ（15分）

手順 1-3 の黒い画面に、次の1行を打って Enter。

| Mac | Windows |
|---|---|
| `python3 tools/setup_all.py` | `py tools\setup_all.py` |

あとは **画面の質問に答えるだけ** です。

1. 「JSON ファイルを、この画面にドラッグ＆ドロップ」➔ ④ でダウンロードした JSON ファイルを黒い画面にドラッグして Enter
2. 「Pinterest のアクセストークン」などを1つずつ聞かれる ➔ ② で集めた鍵を **貼り付けて Enter**
   - 貼り付け：Mac は `⌘ + V`、Windows は **右クリック**（または `Ctrl + V`）
   - **鍵を貼っても画面には何も表示されません**（安全のため）。そのまま Enter でOK
   - わからない・まだない鍵は **Enter だけ** で飛ばす
3. **WordPress**：ブラウザが開く ➔ **「承認（Approve）」** を押す ➔「受け取りました」と出たら黒い画面に戻る
4. **Threads**：ブラウザが開く ➔ **「許可」** を押す ➔ ブログのページが開く
   ➔ **そのページの、いちばん上のアドレス欄（URL）を全部コピー** ➔ 黒い画面に貼り付けて Enter
5. 最後に、結果が出ます：

```
== 3. 確認（読み取りだけ。何も投稿しない）
✓ 配信管理表: OK         ← ✓ はOK
✓ Pinterest: OK
－ Threads: 未設定        ← － はまだ設定していない（飛ばしたもの）
✗ ChatWork: NG HTTP 401  ← ✗ は鍵がまちがっている
```
- **全部 ✓ になれば成功！** 次の手順4へ。
- **－ や ✗ があっても大丈夫。** 下の「8. 困ったとき」を見て直し、**もう一度同じコマンド** を打てば、足りないところだけ聞かれます。

---

## 4. GitHub に鍵を預ける（10分）

自動投稿は GitHub（インターネット上）で動くので、鍵を GitHub の **金庫（Secrets）** に入れます。

### やり方A：画面でコピペする（インストール不要・おすすめ）
1. 手順3で、フォルダに **`.secrets.upload.env`** というファイルができています。**メモ帳（Mac は「テキストエディット」）** で開く
   - 見つからないとき：Mac はフォルダで `⌘ + Shift + .`（ピリオド）、Windows はエクスプローラーの「表示 ➔ 隠しファイル」で見えるようになります
2. GitHub のリポジトリ ➔ **「Settings」➔ 左の「Secrets and variables」➔「Actions」**
3. 緑の **「New repository secret」** ➔
   - **Name**：ファイルの `=` の **左側**（例：`PINTEREST_ACCESS_TOKEN`）
   - **Secret**：`=` の **右側の ' と ' の間**（' は入れない）
   - **「Add secret」**
4. ファイルの行の数だけ 3 をくり返す（最大7つ）
5. **終わったら `.secrets.upload.env` を削除** する（ゴミ箱も空にする）

### やり方B：コマンドで一気に入れる（gh CLI が使える人）
1. https://cli.github.com/ から gh を入れる ➔ 黒い画面で `gh auth login`（GitHub.com ➔ HTTPS ➔ ブラウザでログイン）
2. `python3 tools/setup_all.py --upload`（Windows は `py tools\setup_all.py --upload`）
   - ✓ が7つ並べば完了。ファイルは自動で消えます。

---

## 5. テスト（GitHub のボタンを押すだけ・15分）

### 5-1. まず「確認だけ」（何も投稿しない）
1. GitHub のリポジトリ ➔ 上の **「Actions」** ➔ 左の **「post-queue」**
2. 右の **「Run workflow」** ➔ `dry_run` は **1**、`test_post` は **none** ➔ 緑の **「Run workflow」**
3. 1分待つ ➔ 一覧の一番上をクリック ➔ **「queue」➔「run queue」** を開く
4. 手順3と同じ ✓ が並んでいればOK（✗ があれば「8. 困ったとき」へ）

### 5-2. 本当に投稿してみる（1つずつ・この順番で）
同じ「Run workflow」で、`test_post` を変えて実行します。

| 順番 | test_post | 何が起きる？ | 確認したら |
|---|---|---|---|
| 1 | `chatwork` | ChatWork のルームに「接続テスト」が届く | そのままでOK |
| 2 | `wordpress` | ブログに **下書き** が1件できる（公開されない） | WordPress の「投稿 ➔ 下書き」から削除 |
| 3 | `threads` | Threads に「接続テスト」が **公開** される | Threads アプリで削除 |

- Pinterest と Instagram のテストは画像が必要なので、パソコンから行います（任意）：
  画像を `content/2026-10/media/` に入れて ➔
  `python3 tools/run_queue.py --test-post pinterest --file content/2026-10/media/画像の名前.png`
  （Instagram は `--test-post instagram`。ストーリーズは24時間で消えます）

**3つとも届いたら、初期設定は完了です！🎉**

---

## 6. 本番スタート（自動投稿を始める）

1. GitHub ➔ **「Settings」➔「Secrets and variables」➔「Actions」➔「Variables」タブ ➔「New repository variable」**
2. 2つ作る：
   - Name `QUEUE_ENABLED` ／ Value `true`（定期実行を始める）
   - Name `DRY_RUN` ／ Value `0`（本当に投稿する）
3. これで、毎日 10時・12時・18時・20時・21時ごろに、配信管理表で `ready` の投稿が自動で出ます。
- **止めたいとき**：Variables の `QUEUE_ENABLED` を削除するだけ。

---

## 7. 毎日やること（人の作業）
- **X**：`x_reserve_posts.md` を見て、X の予約投稿で予約 ➔ 配信管理表を `manual_posted` に
- **Instagram のフィード・カルーセル・スタンプ付きストーリーズ、公式LINE、note**：`manual_posts.md` を見て手で投稿
- **動画ができたら**：`content/2026-10/media/` に入れる ➔ その動画を使う投稿が自動で `ready` になる
- **ChatWork に失敗の通知が来たら**：書いてある「次の対応」を見る。わからなければ Claude に通知の文をそのまま見せる（鍵は書かれていません）

---

## 8. 困ったとき

| 画面に出たこと | 原因 | 直し方 |
|---|---|---|
| `python3: command not found` / `py は認識されません` | Python が入っていない | 手順 1-1。Windows は「Add python.exe to PATH」にチェックして入れ直す |
| `No such file or directory: tools/setup_all.py` | フォルダに入っていない | 手順 1-3 をやり直す |
| `✗ 配信管理表: NG HTTP 403` | 配信管理表をサービスアカウントに共有していない | 手順 2-④ の5 |
| `✗ 配信管理表: NG … 1行目が …ではない` | 配信管理表の1行目が変わっている | 1行目を `id / platform / scheduled_at / status / posted_at / log` に戻す |
| `✗ Pinterest: NG HTTP 401` | トークンの期限切れ・まちがい | 手順 2-② で作り直して、手順3をもう一度 |
| `✗ Instagram: NG HTTP 400 / 190` | トークンの期限切れ・権限不足 | 手順 2-⑤ の5 で4つの権限にチェックしてトークンを作り直す ➔ `.env` の `META_ACCESS_TOKEN` と `INSTAGRAM_ACCESS_TOKEN` の行を消して手順3 |
| `権限が足りません：instagram_content_publish` | 手順 2-⑤ の5 のチェック漏れ | 手順 2-⑤ の5 をやり直す |
| `Instagram ビジネスアカウントにつながった Facebook ページが見つかりません` | 手順 2-⑤ の1・2 ができていない | プロアカウント（ビジネス）にして Facebook ページとリンク |
| WordPress で `redirect_uri` のエラー | Redirect URL の登録ミス | 手順 2-③ の2 を `http://localhost:8080/callback` に（1文字も違わない） |
| Threads で `redirect_uri` のエラー | コールバックURLの登録ミス | 手順 2-⑥ の3 を `https://sportsbackstage1.wordpress.com/` に（最後の `/` も） |
| Threads で「アプリにアクセスできません」 | テスターの招待を承認していない | 手順 2-⑥ の4・5 |
| `✗ ChatWork: NG HTTP 401` | トークンのまちがい | 手順 2-① で確認して、`.env` の `CHATWORK_API_TOKEN` の行を消して手順3 |
| GitHub の実行が赤い ✗ | Secrets の名前か値のまちがい | ログの ✗ の行を Claude に見せる（鍵は表示されないので安全） |

> 💡 鍵を入れ直したいとき：フォルダの `.env` をメモ帳で開き、その鍵の行の `=` より右を消して保存 ➔ 手順3をもう一度。

---

## 🤖 AI（Claude Code）向け：この初期設定を案内するときの手順

人がこのガイドのどこにいるかを、次の順で確かめてから、**次の1手だけ** を案内する。説明をくり返さず、番号で示す（例：「手順 2-④ の5 をお願いします」）。

1. **状態を聞く／見る**：人に `python3 tools/setup_all.py --no-input` の出力（✓／－／✗ の行）を貼ってもらう。鍵の値は出力に含まれないので、貼ってもらって安全。
2. **判定と次の一手**

| 出力 | 次に案内すること |
|---|---|
| `.env がなかったので作りました` | 手順3（質問形式で実行） |
| `－ 配信管理表` | 手順 2-④ ➔ 手順3 |
| `－ <媒体>: 取得に必要な … がない` | その媒体の手順2 ➔ 手順3 |
| `✗ <媒体>` | 「8. 困ったとき」の該当行 |
| ✓ のみ（－ は使わない媒体だけ） | 手順4 ➔ 手順5 |
| 手順5 の3つのテストが届いた | 初期設定完了。手順6を案内 |

3. **守ること**
   - 鍵の値をチャットに貼るよう求めない。貼られたら使わずに、作り直しを勧める。
   - GitHub へのアクセス（push・PR・マージ・Actions の起動・ログの読み取り）は **1日2回まで**。人が画面で行う操作はその枠の外として、人に任せる。
   - X は自動投稿しない（手動予約）。Make は使わない。
   - テスト投稿（`--test-post`）は人が頼んだときだけ。順番は chatwork ➔ wordpress ➔ threads。
4. **確認用コマンド（どれも投稿しない）**
   - `python3 tools/run_queue.py --check`：鍵と配信管理表の確認
   - `python3 tools/run_queue.py --now 2026-10-28T12:05`：その時刻に送る予定の投稿
   - `python3 tools/run_queue.py --self-test`：通信なしの動作確認
