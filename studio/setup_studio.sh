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
# 2) Python と ffmpeg
python3 -c "import PIL, numpy, cv2" 2>/dev/null || pip install -q -r ../requirements.txt
command -v ffmpeg >/dev/null || echo "✗ ffmpeg がありません（apt-get install -y ffmpeg）"
# 3) 実写素材（顔が写っているので、公開リポジトリには絶対に入れない）
need="clips/96bd7101d80345dea32585cc72954439.MOV clips/29da73e9795845e4aea114b14fb8c95c.MOV clips/IMG_4049.JPG clips/IMG_4093.MOV clips/IMG_4096.MOV photos/IMG_3560.jpg photos/IMG_3750.jpg photos/IMG_3754.jpg inputs/d2c9044b-Macachette_LINE___45s_SE__.mp4"
miss=0; for f in $need; do [ -f "$f" ] || { echo "✗ 素材なし: studio/$f"; miss=1; }; done
for w in Black Bold Medium; do [ -f fonts/NotoSansCJK-$w.ttc ] || { echo "✗ フォントなし: NotoSansCJK-$w.ttc"; miss=1; }; done
if [ $miss = 1 ]; then
  echo "→ 加藤さんに「2_素材パック_動画.zip」「3_素材パック_写真.zip」を添付してもらい、リポジトリのルートに展開してください（多くは Drive「00_共通素材」から取ったもの）"
else
  echo "✓ 準備OK（python3 studio/make_dec_cal.py で動作確認できます）"
fi
