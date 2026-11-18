#!/usr/bin/env bash
# Render final em lotes (um processo Blender por plano). Retomável: quadros prontos são pulados.
# Uso: setsid nohup bash v2/render_all.sh > v2/frames/render.log 2>&1 &
cd "$(dirname "$0")/.."; mkdir -p v2/frames
for s in ${SHOTS:-A B C D1 D2 E F G H I}; do
  echo "$(date +%H:%M:%S) início $s"
  timeout 14400 blender -b --python v2/render.py -- --shot $s --mode final > v2/frames/log_$s.txt 2>&1
  echo "$(date +%H:%M:%S) fim $s: $(ls v2/frames/$s 2>/dev/null | grep -c '^[0-9]*.png$') quadros $(grep -E '^\[.*render' v2/frames/log_$s.txt)"
done
echo "$(date +%H:%M:%S) TUDO PRONTO"
