#!/usr/bin/env bash
# Prévia em movimento de todos os planos (baixa resolução, 1 de cada N quadros) -> v2/preview/preview.mp4
cd "$(dirname "$0")/.."; STEP=${STEP:-2}; export PREVIEW_RES=${PREVIEW_RES:-180x320}
for s in ${SHOTS:-A B C D1 D2 E F G H I}; do
  rm -rf v2/preview/$s; timeout 3000 blender -b --python v2/render.py -- --shot $s --step $STEP --spp 4 > v2/preview/log_$s.txt 2>&1
  echo "$s $(grep -c 'Saved' v2/preview/log_$s.txt) quadros $(grep -E '^\[.*render' v2/preview/log_$s.txt)"
done
python3 - <<'PY'
import os, glob, subprocess
fr = sorted(glob.glob('v2/preview/*/[0-9][0-9][0-9][0-9].png'), key=lambda p: int(os.path.basename(p)[:4]))
step = int(os.environ.get('STEP', 2))
with open('v2/preview/list.txt', 'w') as f:
    for p in fr: f.write(f"file '{os.path.abspath(p)}'\nduration {step / 30:.5f}\n")
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-f', 'concat', '-safe', '0', '-i', 'v2/preview/list.txt', '-i', 'narracao/01_narracao.mp3',
                '-vf', 'fps=30,format=yuv420p', '-c:v', 'libx264', '-crf', '23', '-c:a', 'aac', '-shortest', 'v2/preview/preview.mp4'], check=True)
print('prévia', len(fr), 'quadros')
PY
