#!/usr/bin/env bash
# Render final do vídeo 02 (720x1280), um processo Blender por plano. Retomável: quadros prontos são pulados;
# se o Blender cair (falha rara do Embree), o plano é reiniciado até 4 vezes e continua de onde parou.
# Uso: setsid nohup bash v2/ep02/render_all.sh > v2/ep02/frames/render.log 2>&1 &
cd "$(dirname "$0")/../.."; mkdir -p v2/ep02/frames
for s in ${SHOTS:-A B C D E F G H I J K}; do
  case $s in C|D|E|H) spp=9;; *) spp=6;; esac
  echo "$(date +%H:%M:%S) início $s ($spp amostras)"
  for try in 1 2 3 4; do
    find v2/ep02/frames/$s -name '[0-9]*.png' -size 0 -delete 2>/dev/null     # placeholder de quadro interrompido
    timeout 18000 blender -b --python v2/ep02/render.py -- --shot $s --mode final --spp $spp > v2/ep02/frames/log_$s.txt 2>&1 && break
    echo "$(date +%H:%M:%S) $s caiu (tentativa $try), retomando"
  done
  echo "$(date +%H:%M:%S) fim $s: $(ls v2/ep02/frames/$s 2>/dev/null | grep -c '^[0-9]*.png$') quadros $(grep -E '^\[.*render' v2/ep02/frames/log_$s.txt)"
done
echo "$(date +%H:%M:%S) TUDO PRONTO"
