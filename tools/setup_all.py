#!/usr/bin/env python3
"""自動投稿の初期設定をまとめて行う（ご本人のPCで、リポジトリ直下から実行する）。

使い方（くわしくは SETUP.md）:
  python3 tools/setup_all.py            # 質問に答えていくだけ（足りない鍵を聞かれたら貼り付けて Enter。分からなければ Enter で飛ばす）
  python3 tools/setup_all.py --upload   # さらに GitHub Secrets へ一括登録（gh CLI が必要）
  python3 tools/setup_all.py --google-json ~/Downloads/xxxx.json   # サービスアカウントの JSON を先に指定する

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
import getpass
import json
import os
import re
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
# Threads は https のリダイレクトURIしか登録できないため、Threads のときだけ自分のサイトのURLを使う
HTTPS_REDIRECT = "https://sportsbackstage1.wordpress.com/"
# (取得したい鍵, 取得に必要な鍵, get_tokens の手順, 説明)
STEPS = [
    (["WORDPRESS_TOKEN"], ["WORDPRESS_CLIENT_ID", "WORDPRESS_CLIENT_SECRET"], get_tokens.wordpress, "WordPress"),
    (["THREADS_ACCESS_TOKEN"], ["THREADS_APP_ID", "THREADS_APP_SECRET"], get_tokens.threads, "Threads"),
    (["INSTAGRAM_ACCESS_TOKEN", "INSTAGRAM_USER_ID"], ["META_APP_ID", "META_APP_SECRET", "META_ACCESS_TOKEN"],
     get_tokens.instagram, "Instagram"),
]


# 質問する鍵：(名前, 画面に出す説明, 入力を隠すか, 正しい形)
ID = r"\d{3,20}"
SECRET = r"[A-Za-z0-9]{16,128}"
ASK = [
    ("PINTEREST_ACCESS_TOKEN", "Pinterest のアクセストークン（pina_ で始まる）", True, r"pina_[A-Za-z0-9_\-]{20,}"),
    ("CHATWORK_API_TOKEN", "ChatWork の API トークン（英数字30文字くらい）", True, r"[A-Za-z0-9]{20,64}"),
    ("WORDPRESS_CLIENT_ID", "WordPress アプリの Client ID（数字）", False, ID),
    ("WORDPRESS_CLIENT_SECRET", "WordPress アプリの Client Secret", True, SECRET),
    ("THREADS_APP_ID", "Threads のアプリID（Meta の画面「Threads の設定」にある数字）", False, ID),
    ("THREADS_APP_SECRET", "Threads のApp Secret", True, SECRET),
    ("META_APP_ID", "Meta（Facebook）アプリのアプリID（数字）", False, ID),
    ("META_APP_SECRET", "Meta（Facebook）アプリの app secret", True, SECRET),
    ("META_ACCESS_TOKEN", "Graph API エクスプローラーで作ったトークン（EAA… / EAB… で始まる）", True, r"EA[A-Za-z0-9]{50,}"),
]
TRIES = 3
TOKEN_FOR = {"WORDPRESS_CLIENT_ID": "WORDPRESS_TOKEN", "WORDPRESS_CLIENT_SECRET": "WORDPRESS_TOKEN",
             "THREADS_APP_ID": "THREADS_ACCESS_TOKEN", "THREADS_APP_SECRET": "THREADS_ACCESS_TOKEN",
             "META_APP_ID": "INSTAGRAM_ACCESS_TOKEN", "META_APP_SECRET": "INSTAGRAM_ACCESS_TOKEN",
             "META_ACCESS_TOKEN": "INSTAGRAM_ACCESS_TOKEN"}


def flush_input():
    """貼り付けた文字が多すぎたとき、あふれた分が次の質問に流れ込まないよう捨てる。"""
    try:
        import termios
        termios.tcflush(sys.stdin, termios.TCIFLUSH)
    except Exception:  # Windows（termios なし）や、画面以外からの入力では何もしない
        pass


def read_answer(prompt, hidden):
    try:
        raw = getpass.getpass(prompt) if hidden else input(prompt)
    except UnicodeDecodeError:
        raw = "\ufffd"  # 文字化けした入力は「形がおかしい」として聞き直す
    flush_input()
    return raw.encode("utf-8", "replace").decode("utf-8").strip()


def ask_missing(interactive):
    """足りない鍵を1つずつ聞いて .env に保存する。Enter だけなら飛ばす（あとで聞き直せる）。
    鍵の形がおかしいとき（余計な文字まで貼り付けた等）は保存せずに聞き直す。前に保存した値の形がおかしいときも聞き直す。"""
    if not interactive:
        return
    for name, label, hidden, pattern in ASK:
        current = env_value(name)
        if current and re.fullmatch(pattern, current):
            continue  # すでに正しい形で入っている
        if not current and env_value(TOKEN_FOR.get(name, "")):
            continue  # それで作るトークンがもうある
        if current:
            print(f"  ⚠ 前に入れた {label} の形が正しくないので、もう一度聞きます")
        prompt = f"  {label}\n  ➔ 貼り付けて Enter（{'画面には表示されません。' if hidden else ''}分からなければ Enter だけ）："
        for attempt in range(TRIES):
            value = read_answer(prompt, hidden)
            if not value:
                break
            if re.fullmatch(pattern, value):
                get_tokens.save({name: value})
                os.environ[name] = value
                break
            print(f"  ✗ 形が正しくありません（{len(value)}文字・余計な文字やスペースが入っているかも）。"
                  "鍵だけをコピーし直して、もう一度貼り付けてください")
        else:
            print(f"  － {label} は飛ばします（あとでもう一度このコマンドを打てば、また聞きます）")
        if current and env_value(name) == current:  # 聞き直しても直らなかった値は消す（まちがった鍵で ✗ にしないため）
            get_tokens.save({name: ""})
            os.environ[name] = ""


def ask_google_json(interactive):
    if env_value("GOOGLE_SERVICE_ACCOUNT_JSON") or not interactive:
        return
    path = input("  サービスアカウントの JSON ファイルを、この画面にドラッグ＆ドロップして Enter（なければ Enter だけ）：")
    path = path.strip().strip("'\"").replace("\\ ", " ")
    if path:
        google_json(path)


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
        default = get_tokens.REDIRECT
        if label == "Threads" and not os.environ.get("OAUTH_REDIRECT_URI"):
            get_tokens.REDIRECT = HTTPS_REDIRECT
            print(f"  リダイレクトURI：{HTTPS_REDIRECT}（Meta の画面に登録したものと同じであること）")
        try:
            step()
        except SystemExit as e:  # 1つ失敗しても残りは続ける
            print(f"✗ {label}: {e}")
        finally:
            get_tokens.REDIRECT = default
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
    parser.add_argument("--no-input", action="store_true", help="質問せずに .env の値だけで進める")
    args = parser.parse_args()
    if sys.version_info < (3, 9):
        sys.exit("Python 3.9 以上が必要です。https://www.python.org/downloads/ から新しいものを入れてください")
    interactive = not args.no_input and sys.stdin.isatty()
    if not get_tokens.ENV.exists():
        shutil.copy(ROOT / ".env.example", get_tokens.ENV)
        get_tokens.ENV.chmod(0o600)
        print(".env がなかったので作りました（鍵はこのファイルに保存されます。人に見せない・送らない）")
        if not interactive:
            sys.exit("鍵を .env に入れてから、もう一度実行してください")
    reload_env()

    print("== 1. サービスアカウント（配信管理表）")
    if args.google_json:
        google_json(args.google_json)
    ask_google_json(interactive)
    reload_env()
    print("✓ 配信管理表: .env にある" if env_value("GOOGLE_SERVICE_ACCOUNT_JSON")
          else "－ 配信管理表: --google-json でファイルを指定してください")
    print("== 2. 鍵の入力とトークンの取得")
    ask_missing(interactive)
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
