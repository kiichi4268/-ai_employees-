# 外部タイマー（cron-job.org）で自動投稿を時刻どおりに動かす

GitHub の定時実行（毎時5分）は、動きの少ないリポジトリでは後回しにされ、1日2〜3回しか動かないことがある（11/8〜11/9 に確認）。
そこで、無料の外部タイマー **cron-job.org** から、決まった時刻に GitHub へ「今動いて」と送る。費用0円。Claude の GitHub アクセスは増えない。

---

## 1. GitHub で「動かすだけ」の鍵を作る（5分・パソコン推奨）
1. https://github.com/settings/personal-access-tokens/new を開く（Fine-grained token）
2. 次のとおり入れる
   | 項目 | 入れるもの |
   |---|---|
   | Token name | `cron-job-instagram` |
   | Expiration | 366 days（期限の前に作り直す） |
   | Repository access | **Only select repositories** → `kiichi4268/-ai_employees-` だけ |
   | Permissions → Repository permissions → **Actions** | **Read and write**（ほかは触らない） |
3. 「Generate token」→ 表示された `github_pat_…` をコピー（**チャットには貼らない**。次の手順で cron-job.org に直接貼る）

この鍵でできるのは「このリポジトリの Actions を動かす」ことだけ。投稿の中身や Secrets は見られない。

## 2. cron-job.org にタイマーを2つ作る（5分）
1. https://cron-job.org で無料登録 → ログイン → 「CREATE CRONJOB」
2. **タイマー①：投稿（毎時5分・8〜23時）**
   | 項目 | 入れるもの |
   |---|---|
   | Title | `Instagram 投稿` |
   | URL | `https://api.github.com/repos/kiichi4268/-ai_employees-/actions/workflows/instagram.yml/dispatches` |
   | Execution schedule | Custom：Minutes **5**／Hours **8〜23**（Every day）／Time zone **Asia/Tokyo** |
   | ADVANCED → Request method | **POST** |
   | ADVANCED → Headers | `Authorization` = `Bearer （手順1の github_pat_…）`<br>`Accept` = `application/vnd.github+json`<br>`X-GitHub-Api-Version` = `2022-11-28` |
   | ADVANCED → Request body | `{"ref":"main","inputs":{"dry_run":"0"}}` |
3. **タイマー②：数字（毎晩23:50）**：①を「COPY」して、次の2つだけ変える
   - URL の `instagram.yml` を `ig_insights.yml` に
   - Schedule を Minutes **50**／Hours **23**
   - Request body を `{"ref":"main","inputs":{"dry_run":"0","days":"3"}}` に
4. 保存したら、①の「TEST RUN」を押す → 結果が **204** なら成功（GitHub の Actions に「instagram」の実行が1つ増える）

## 3. 確かめ方・止め方
- GitHub の Actions に、毎時5分ごろ「instagram」の実行（workflow_dispatch）が並べば成功。投稿したものは ChatWork に届く。
- 出し済みの投稿は二重に出ない（ig_queue.py が Instagram 側を確かめる）。GitHub の定時実行が同じ時刻に動いても大丈夫。
- 止めたいとき：cron-job.org でタイマーを OFF にする（または GitHub の Variables の `IG_ENABLED` を消す）。
- 鍵の期限の前（1年後）に、手順1で作り直して cron-job.org の Authorization を上書きする。

## 関連
- 予定から **4時間** を過ぎた下書きは送らずに ChatWork に知らせる（11/9 に2時間から延長）。
- 自動投稿のスイッチ：Variables の `IG_ENABLED` = `true`（GitHub の定時実行用。外部タイマーからの起動はスイッチなしでも動く）。
