#!/usr/bin/env bash
# Render do vídeo 21 (ChaveShort) plano por plano em JPEG q95 1080x1920 -> projeto_videos3d/v2/ep21/frames/<plano>/NNNN.jpg
# Os planos 1–5 são links para os quadros do piloto (ep90) e são pulados. Retomável: planos completos são pulados;
# um plano incompleto é refeito inteiro. 1 aba por padrão (com 3 abas o piloto saiu com quadros em branco e sem lanterna).
cd "$(dirname "$0")/.."; export TMPDIR=$PWD/.tmp REMOTION_TMP=$PWD/.tmp
DST=/home/user/Teste/projeto_videos3d/v2/ep21/frames; CH=/opt/pw-browsers/chromium-1243/chrome-linux64/chrome
SHOTS=$(cd /home/user/Teste/projeto_videos3d/v2/ep21 && python3 -c "import plan; print(' '.join(f'{s.name}:{s.a}:{s.b}' for s in plan.SHOTS))")
for it in $SHOTS; do
  IFS=: read n a b <<< "$it"; want=$((b-a)); mkdir -p $DST/$n
  have=$(find -L $DST/$n \( -name '*.png' -o -name '*.jpg' \) -size +1k | wc -l)
  [ "$have" -ge "$want" ] && { echo "$n completo"; continue; }
  tmp=out/chave_seq/$n; rm -rf $tmp; mkdir -p $tmp; t0=$(date +%s)
  npx remotion render src/index.ts ChaveShort $tmp --sequence --frames=$a-$((b-1)) --image-format=jpeg --jpeg-quality=95 --concurrency=${CONC:-1} \
    --gl=swangle --timeout=300000 --browser-executable=$CH --log=error > out/chave_seq/log_$n.txt 2>&1 || { echo "$n FALHOU"; tail -5 out/chave_seq/log_$n.txt; continue; }
  i=$a; for f in $(ls $tmp/*.jpeg $tmp/*.jpg 2>/dev/null | sort -V); do mv "$f" $DST/$n/$(printf %04d $i).jpg; i=$((i+1)); done
  rm -rf .tmp/remotion-webpack-bundle-* .tmp/org.chromium.Chromium.*   # o pacote é refeito a cada plano: sem isto o disco enche
  echo "$n ok $(find $DST/$n -name '*.jpg' | wc -l) quadros em $(( $(date +%s)-t0 ))s"
done
echo FIM
