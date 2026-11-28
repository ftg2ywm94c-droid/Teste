#!/usr/bin/env bash
# Fila da noite de 16/11: refaz os planos do 09 afetados pelas zonas seguras 9:16, renderiza as bases da thumbnail do 09 (uma por vez,
# para não faltar memória) e depois retoma o render do vídeo 10.
cd "$(dirname "$0")/../.."
SHOTS="A1 B1 D1 D2 E2" bash v2/ep09/render_all.sh >> v2/ep09/frames/render.log 2>&1
mkdir -p thumbnails/_09_base
[ -s thumbnails/_09_base/still_0066.png ] || RENDER_OUT=thumbnails/_09_base PREVIEW_RES=1080x1920 timeout 3000 blender -b --python v2/ep09/render.py -- --shot A1 --mode final --still 66 --spp 48 > thumbnails/_09_base/log_a1.txt 2>&1
[ -s thumbnails/_09_base/still_1440.png ] || RENDER_OUT=thumbnails/_09_base PREVIEW_RES=1080x1920 timeout 3000 blender -b --python v2/ep09/render.py -- --shot E2 --mode final --still 1440 --spp 32 > thumbnails/_09_base/log_e2.txt 2>&1
echo "$(date +%H:%M:%S) bases da thumbnail 09 prontas" >> v2/ep09/frames/render.log
bash v2/ep10/render_all.sh >> v2/ep10/frames/render.log 2>&1
