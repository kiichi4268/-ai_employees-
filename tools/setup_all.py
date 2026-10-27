#!/usr/bin/env python3
"""自動投稿の初期設定をまとめて行う（ご本人のPCで、リポジトリ直下から実行する）。

使い方:
  python3 tools/setup_all.py --google-json ~/Downloads/xxxx.json   # 鍵の取得 ➔ 確認 ➔ Secrets 用ファイルを作る
  python3 tools/setup_all.py --upload                              # さらに GitHub Secrets へ一括登録（gh CLI が必要）

やること（足りないものだけ。すでに .env にある鍵はそのまま使う）:
  1. サービスアカウントの JSON ファイルを読み、1行にして .env の GOOGLE_SERVICE_ACCOUNT_JSON に入れる
  2. WORDPRESS_TOKEN・THREADS_ACCESS_TOKEN・INSTAGRAM_ACCESS_TOKEN/USER_ID がなければ、
     tools/get_tokens.py の手順で取得する（WordPress・Threads はブラウザで「許可」を1回押す）
  3. run_queue.py --check と同じ確認を、読み取りだけで行う（何も投稿しない）
  4. GitHub Secrets に登録する7つだけを .secrets.upload.env に書き出す（画面から手で登録するとき用。git には入らない）
     --upload のときは gh CLI で1つずつ登録する（値は標準入力で渡すので、画面にもコマンド履歴にも残らない）。
     終わったら .secrets.upload.env を消す。✗ が1つでもあれば登録しない

.env に先に入れておくもの: WORDPRESS_CLIENT_ID/SECRET、THREADS_APP_ID/SECRET、META_APP_ID/SECRET、
META_ACCESS_TOKEN、PINTEREST_ACCESS_TOKEN、CHATWORK_API_TOKEN（.env.example を参照）
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import get_tokens  # noqa: E402

SECRETS = ["GOOGLE_SERVICE_ACCOUNT_JSON", "THREADS_ACCESS_TOKEN", "PINTEREST_ACCESS_TOKEN", "WORDPRESS_TOKEN",
           "INSTAGRAM_ACCESS_TOKEN", "INSTAGRAM_USER_ID", "CHATWORK_API_TOKEN"]
UPLOAD = ROOT / ".secrets.upload.env"
# (取得したい鍵, 取得に必要な鍵, get_tokens の手順, 説明)
STEPS = [
    (["WORDPRESS_TOKEN"], ["WORDPRESS_CLIENT_ID", "WORDPRESS_CLIENT_SECRET"], get_tokens.wordpress, "WordPress"),
    (["THREADS_ACCESS_TOKEN"], ["THREADS_APP_ID", "THREADS_APP_SECRET"], get_tokens.threads, "Threads"),
    (["INSTAGRAM_ACCESS_TOKEN", "INSTAGRAM_USER_ID"], ["META_APP_ID", "META_APP_SECRET", "META_ACCESS_TOKEN"],
     get_tokens.instagram, "Instagram"),
]


def env_value(name):
    return os.environ.get(name, "")


def reload_env():
    for line in get_tokens.ENV.read_text(encoding="utf-8").splitlines() if get_tokens.ENV.exists() else []:
        if "=" in line and not line.lstrip().startswith("#"):
            key, value = line.split("=", 1)
            os.environ[key.strip()] = value.strip().strip("'")


def google_json(path):
    try:
        info = json.loads(Path(path).expanduser().read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        sys.exit(f"サービスアカウントの JSON を読めません：{e}")
    missing = [k for k in ("client_email", "private_key", "token_uri") if not info.get(k)]
    if info.get("type") != "service_account" or missing:
        sys.exit("サービスアカウントの JSON ではありません（OAuth クライアントの JSON と間違えていないか確認してください）")
    get_tokens.save({"GOOGLE_SERVICE_ACCOUNT_JSON": json.dumps(info, separators=(",", ":"))})
    print(f"  配信管理表の「共有」に {info['client_email']} を「編集者」で追加してください（済んでいれば不要）")


def fetch_missing():
    for wanted, needs, step, label in STEPS:
        if all(env_value(n) for n in wanted):
            print(f"✓ {label}: .env にあるのでそのまま使う")
            continue
        absent = [n for n in needs if not env_value(n)]
        if absent:
            print(f"－ {label}: 取得に必要な {', '.join(absent)} が .env にないため飛ばす")
            continue
        print(f"▶ {label}: トークンを取得します")
        try:
            step()
        except SystemExit as e:  # 1つ失敗しても残りは続ける
            print(f"✗ {label}: {e}")
        reload_env()


def check():
    import run_queue
    return run_queue.check(ROOT / "content" / sorted(p.name for p in (ROOT / "content").iterdir() if p.is_dir())[-1])


def write_upload():
    lines, absent = [], []
    for name in SECRETS:
        value = env_value(name)
        if not value:
            absent.append(name)
        elif "'" in value or "\n" in value:
            sys.exit(f"{name} に ' か改行が入っているため書き出せません。値を確認してください")
        else:
            lines.append(f"{name}='{value}'")
    UPLOAD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    UPLOAD.chmod(0o600)
    return len(lines), absent


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--google-json", help="ダウンロードしたサービスアカウントの JSON ファイル")
    parser.add_argument("--upload", action="store_true", help="gh CLI で GitHub Secrets に一括登録する")
    args = parser.parse_args()
    if not get_tokens.ENV.exists():
        shutil.copy(ROOT / ".env.example", get_tokens.ENV)
        get_tokens.ENV.chmod(0o600)
        sys.exit(".env がなかったので .env.example から作りました。鍵を入れてから、もう一度実行してください")
    reload_env()

    print("== 1. サービスアカウント")
    if args.google_json:
        google_json(args.google_json)
        reload_env()
    print("✓ 配信管理表: .env にある" if env_value("GOOGLE_SERVICE_ACCOUNT_JSON")
          else "－ 配信管理表: --google-json でファイルを指定してください")
    print("== 2. トークンの取得")
    fetch_missing()
    print("== 3. 確認（読み取りだけ。何も投稿しない）")
    ng = check()
    print("== 4. GitHub Secrets")
    count, absent = write_upload()
    print(f"  {count}/{len(SECRETS)} 個を {UPLOAD.name} に書き出しました" + (f"（未設定：{', '.join(absent)}）" if absent else ""))
    if ng:
        print(f"✗ が {ng} 件あります。直してからもう一度実行してください（Secrets には登録しません）")
        UPLOAD.unlink()
        sys.exit(1)
    if not args.upload:
        print(f"  登録するには：python3 tools/setup_all.py --upload（gh CLI がないときは {UPLOAD.name} の値を画面から登録し、"
              "終わったらこのファイルを消す）")
        return
    if not shutil.which("gh"):
        sys.exit("gh CLI がありません。https://cli.github.com/ から入れて `gh auth login` してから実行してください")
    UPLOAD.unlink()
    failed = []
    for name in SECRETS:
        if env_value(name):
            result = subprocess.run(["gh", "secret", "set", name], input=env_value(name), text=True, cwd=ROOT,
                                    capture_output=True)
            print(f"  {'✓' if result.returncode == 0 else '✗'} {name}")
            if result.returncode:
                failed.append(name)
    if failed:
        sys.exit(f"GitHub Secrets への登録に失敗：{', '.join(failed)}（gh auth status でログインを確認してください）")
    print("✓ GitHub Secrets に登録しました。Actions ➔ post-queue ➔ Run workflow（dry_run=1）で確認してください")


if __name__ == "__main__":
    main()
