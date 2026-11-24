#!/usr/bin/env bash
# Quadros de conferência do vídeo 19 (A Noite Livre): um quadro (ou os dados) por plano em out/nl_stills/NN_FFFF.png (escala 0.5).
cd "$(dirname "$0")/.."; export TMPDIR=$PWD/.tmp REMOTION_TMP=$PWD/.tmp; mkdir -p .tmp out/nl_stills
CH=/opt/pw-browsers/chromium-1243/chrome-linux64/chrome
for fr in "$@"; do
  npx remotion still src/index.ts NoiteLivreShort out/nl_stills/$(printf %04d $fr).png --frame=$fr --scale=0.5 --gl=swangle --timeout=300000 --browser-executable=$CH --log=error || echo "FALHOU $fr"
done
