"""新しい作業場で、制作に要る実写を Drive から取り込む（studio/materials.json の一覧。足りない物だけ）。
11/15 加藤さん：予約を毎回新しい会話で動かす（使う量を減らす）ための準備。Drive「Macachette素材」はリンク共有（閲覧）済み。
使い方: python3 tools/fetch_materials.py
"""
import json, os, subprocess, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S = os.path.join(ROOT, "studio")


def main():
    m = json.load(open(os.path.join(S, "materials.json"), encoding="utf-8"))
    got = miss = 0
    for rel, fid in m.items():
        if rel.startswith("_"): continue
        dest = os.path.join(S, rel)
        if os.path.exists(dest): continue
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        tmp = dest + ".dl"
        r = subprocess.run(["curl", "-sSL", "-o", tmp, f"https://drive.usercontent.google.com/download?id={fid}&export=download&confirm=t"])
        if r.returncode or os.path.getsize(tmp) < 10000:
            print("取れない:", rel); miss += 1
            if os.path.exists(tmp): os.remove(tmp)
            continue
        head = open(tmp, "rb").read(16)
        if b"ftypheic" in head or b"ftypmif1" in head or b"ftypheix" in head:  # HEIC → JPG
            try:
                import pillow_heif; pillow_heif.register_heif_opener()
                from PIL import Image, ImageOps
                ImageOps.exif_transpose(Image.open(tmp)).convert("RGB").save(dest, quality=92)
            except ImportError:
                # pillow_heif が無い作業場：ffmpeg でタイルを読んで並べる tools/heic2jpg.py（11/18）
                if subprocess.run([sys.executable, os.path.join(ROOT, "tools", "heic2jpg.py"), tmp, dest]).returncode:
                    print("HEIC を変換できない（処理済みの背景 content/instagram/media/bg を使う）:", rel); miss += 1
                    os.remove(tmp); continue
            os.remove(tmp)
        else:
            os.replace(tmp, dest)
        got += 1
    print(f"取り込み {got}件・取れない {miss}件")
    return miss


if __name__ == "__main__":
    sys.exit(1 if main() else 0)
