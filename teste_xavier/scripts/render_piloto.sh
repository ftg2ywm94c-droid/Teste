#!/usr/bin/env bash
# Render do piloto de qualidade (PilotoShort) plano por plano em PNG 1080x1920 -> projeto_videos3d/v2/ep90/frames/<plano>/NNNN.png
# Retomável: planos completos são pulados; um plano incompleto é refeito inteiro.
cd "$(dirname "$0")/.."; export TMPDIR=$PWD/.tmp REMOTION_TMP=$PWD/.tmp
DST=/home/user/Teste/projeto_videos3d/v2/ep90/frames; CH=/opt/pw-browsers/chromium-1243/chrome-linux64/chrome
SHOTS=$(cd /home/user/Teste/projeto_videos3d/v2/ep90 && python3 -c "import plan; print(' '.join(f'{s.name}:{s.a}:{s.b}' for s in plan.SHOTS))")
for it in $SHOTS; do
  IFS=: read n a b <<< "$it"; want=$((b-a)); mkdir -p $DST/$n
  have=$(find $DST/$n -name '*.png' -size +1k | wc -l)
  [ "$have" -ge "$want" ] && { echo "$n completo"; continue; }
  tmp=out/piloto_seq/$n; rm -rf $tmp; mkdir -p $tmp; t0=$(date +%s)
  npx remotion render src/index.ts PilotoShort $tmp --sequence --frames=$a-$((b-1)) --image-format=png --concurrency=${CONC:-3} \
    --gl=swangle --timeout=300000 --browser-executable=$CH --log=error > out/piloto_seq/log_$n.txt 2>&1 || { echo "$n FALHOU"; tail -5 out/piloto_seq/log_$n.txt; continue; }
  i=$a; for f in $(ls $tmp/*.png | sort -V); do mv "$f" $DST/$n/$(printf %04d $i).png; i=$((i+1)); done
  echo "$n ok $(( $(find $DST/$n -name '*.png' | wc -l) )) quadros em $(( $(date +%s)-t0 ))s"
done
echo FIM
