"""Drive の写真・動画を取り込む（11/14：「Macachette素材」を「リンクを知っている全員（閲覧者）」に共有済み）。

ファイルの一覧は Claude の Drive コネクタ（search_files・parentId で最後のページまで）で ID を取り、ここで1つずつ取り込む。
取り込み先は studio/photos・studio/clips（GitHub に入れない）。HEIC は JPG に変える。
使い方: python3 tools/drive_fetch.py <ファイルID> <保存名> [<ファイルID> <保存名> ...]
"""
import os, sys, subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def fetch(fid, name):
    ext = os.path.splitext(name)[1].lower()
    dest_dir = os.path.join(ROOT, "studio", "clips" if ext in (".mov", ".mp4") else "photos")
    tmp = os.path.join(dest_dir, "_dl_" + name)
    subprocess.run(["curl", "-sSL", "-o", tmp, f"https://drive.usercontent.google.com/download?id={fid}&export=download&confirm=t"], check=True)
    if ext == ".heic":
        import pillow_heif
        from PIL import Image, ImageOps
        pillow_heif.register_heif_opener()
        out = os.path.join(dest_dir, os.path.splitext(name)[0] + ".jpg")
        ImageOps.exif_transpose(Image.open(tmp)).convert("RGB").save(out, quality=92); os.remove(tmp)
    else:
        out = os.path.join(dest_dir, name); os.replace(tmp, out)
    return out


if __name__ == "__main__":
    a = sys.argv[1:]
    for fid, name in zip(a[::2], a[1::2]):
        print(fetch(fid, name))
