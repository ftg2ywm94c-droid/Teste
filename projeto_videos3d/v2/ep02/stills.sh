#!/usr/bin/env bash
# Quadros de checagem do vídeo 02 + folha de contato. Uso: bash v2/ep02/stills.sh "A:30 C:500" saida.png
set -u; cd "$(dirname "$0")/../.."; out=${2:-/tmp/claude-0/sheet2.png}; list=()
for it in $1; do s=${it%%:*}; f=${it##*:}
  timeout 1200 blender -b --python v2/ep02/render.py -- --shot $s --still $f > /tmp/claude-0/st2_${s}_$f.log 2>&1 || { echo "FALHOU $s:$f"; grep -E "Error|line [0-9]+" /tmp/claude-0/st2_${s}_$f.log | tail -6; }
  p=v2/ep02/preview/$s/still_$(printf %04d $f).png; [ -f $p ] && list+=("$p")
done
[ ${#list[@]} -gt 0 ] && python3 - "$out" "${list[@]}" <<'PY'
import sys, cv2, numpy as np
ims = []
for p in sys.argv[2:]:
    im = cv2.imread(p); cv2.putText(im, p.split('/')[-2] + ' ' + p[-8:-4], (6, 20), 0, 0.55, (255, 255, 255), 2); ims.append(im)
rows = [np.hstack(ims[i:i + 6] + [np.zeros_like(ims[0])] * (6 - len(ims[i:i + 6]))) for i in range(0, len(ims), 6)]
cv2.imwrite(sys.argv[1], np.vstack(rows))
PY
