#!/usr/bin/env bash
# Prévia em movimento do vídeo 05 (baixa resolução, 1 de cada STEP quadros) -> v2/ep05/preview/preview.mp4
cd "$(dirname "$0")/../.."; STEP=${STEP:-3}; export PREVIEW_RES=${PREVIEW_RES:-180x320}
for s in ${SHOTS:-$(cd v2/ep05 && python3 -c "import plan; print(' '.join(s.name for s in plan.SHOTS))")}; do
  mkdir -p v2/ep05/preview/$s; rm -f v2/ep05/preview/$s/[0-9]*.png; timeout 3000 blender -b --python v2/ep05/render.py -- --shot $s --step $STEP --spp 4 > v2/ep05/preview/log_$s.txt 2>&1
  echo "$s $(grep -c 'Saved' v2/ep05/preview/log_$s.txt) quadros $(grep -E '^\[.*render' v2/ep05/preview/log_$s.txt)"
done
python3 - <<'PY'
import os, glob, subprocess
fr = sorted(glob.glob('v2/ep05/preview/*/[0-9][0-9][0-9][0-9].png'), key=lambda p: int(os.path.basename(p)[:4]))
step = int(os.environ.get('STEP', 3))
with open('v2/ep05/preview/list.txt', 'w') as f:
    for p in fr: f.write(f"file '{os.path.abspath(p)}'\nduration {step / 30:.5f}\n")
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-f', 'concat', '-safe', '0', '-i', 'v2/ep05/preview/list.txt', '-i', 'narracao/05_narracao.mp3',
                '-vf', 'fps=30,format=yuv420p', '-c:v', 'libx264', '-crf', '23', '-c:a', 'aac', '-shortest', 'v2/ep05/preview/preview.mp4'], check=True)
print('prévia', len(fr), 'quadros')
PY
