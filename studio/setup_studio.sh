#!/usr/bin/env bash
# 制作スタジオの準備（新しい作業環境で最初に1回）。リポジトリのルートから: bash studio/setup_studio.sh
set -u
cd "$(dirname "$0")"
mkdir -p fonts clips photos inputs out
# 1) フォント（Noto Sans CJK。リポジトリには入れない）
for w in Black Bold Medium; do
  f="NotoSansCJK-$w.ttc"
  [ -f "fonts/$f" ] && continue
  for d in /usr/share/fonts/opentype/noto /usr/share/fonts/noto-cjk /usr/share/fonts/truetype/noto; do
    [ -f "$d/$f" ] && cp "$d/$f" fonts/ && break
  done
done
if ! ls fonts/NotoSansCJK-Black.ttc >/dev/null 2>&1; then
  echo "フォントが無いので入れます（fonts-noto-cjk）"
  (sudo apt-get install -y fonts-noto-cjk || apt-get install -y fonts-noto-cjk) >/dev/null 2>&1
  for w in Black Bold Medium; do cp /usr/share/fonts/opentype/noto/NotoSansCJK-$w.ttc fonts/ 2>/dev/null; done
fi
if ! ls fonts/NotoSansCJK-Black.ttc >/dev/null 2>&1; then
  # 11/18：apt が使えない作業場では Google Fonts から Noto Sans JP（中身は同じ字形）を取って同じ名前で置く
  echo "Google Fonts から Noto Sans JP を取ります"
  css=$(curl -s -m 30 -A "curl/8" "https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@500;700;900&family=Noto+Serif+JP:wght@700;900")
  echo "$css" | awk '/font-family/{fam=$0} /font-weight/{w=$2} /src:/{match($0,/https:[^)]*/);print fam" "w" "substr($0,RSTART,RLENGTH)}' | tr -d ";'" | \
  while read -r _ fam1 fam2 fam3 w url; do
    n="$fam2$fam3"; [ "$fam2" = "Serif" ] && n="Serif$fam3"
    case "$w" in 500) ww=Medium;; 700) ww=Bold;; 900) ww=Black;; esac
    curl -s -m 120 -o "fonts/Noto${n}-$ww.ttf" "$url"
  done
  for w in Black Bold Medium; do [ -f fonts/NotoSansJP-$w.ttf ] && cp fonts/NotoSansJP-$w.ttf fonts/NotoSansCJK-$w.ttc; done
  mkdir -p ~/.fonts && cp fonts/Noto*JP-*.ttf ~/.fonts/ 2>/dev/null && fc-cache -f >/dev/null 2>&1
fi
# 2) Python と ffmpeg
python3 -c "import PIL, numpy, cv2" 2>/dev/null || pip install -q -r ../requirements.txt
command -v ffmpeg >/dev/null || echo "✗ ffmpeg がありません（apt-get install -y ffmpeg）"
# 3) 実写素材（顔が写っているので、公開リポジトリには絶対に入れない）
python3 -c "import pillow_heif" 2>/dev/null || pip install -q pillow-heif
python3 ../tools/fetch_materials.py || true  # 11/15：Drive から足りない実写を取り込む（毎回新しい会話の予約でも素材がそろう）
need="clips/96bd7101d80345dea32585cc72954439.MOV clips/29da73e9795845e4aea114b14fb8c95c.MOV clips/IMG_4049.JPG clips/IMG_4093.MOV clips/IMG_4096.MOV photos/IMG_3560.jpg photos/IMG_3750.jpg photos/IMG_3754.jpg inputs/d2c9044b-Macachette_LINE___45s_SE__.mp4"
miss=0; for f in $need; do [ -f "$f" ] || { echo "✗ 素材なし: studio/$f"; miss=1; }; done
for w in Black Bold Medium; do [ -f fonts/NotoSansCJK-$w.ttc ] || { echo "✗ フォントなし: NotoSansCJK-$w.ttc"; miss=1; }; done
if [ $miss = 1 ]; then
  echo "→ 加藤さんに「2_素材パック_動画.zip」「3_素材パック_写真.zip」を添付してもらい、リポジトリのルートに展開してください（多くは Drive「00_共通素材」から取ったもの）"
else
  echo "✓ 準備OK（python3 studio/make_dec_cal.py で動作確認できます）"
fi
