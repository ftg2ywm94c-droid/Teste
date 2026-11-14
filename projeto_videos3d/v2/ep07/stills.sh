#!/usr/bin/env bash
# Quadros de teste do vídeo 07: um quadro no meio (ou no tempo dado) de cada plano -> v2/ep07/stills/<plano>.png
cd "$(dirname "$0")/../.."; mkdir -p v2/ep07/stills; RES=${RES:-270x480}
for item in ${LIST:-$(cd v2/ep07 && python3 -c "import plan; print(' '.join(f'{s.name}:{round((s.t0+s.t1)/2*30)}' for s in plan.SHOTS))")}; do
  s=${item%%:*}; f=${item##*:}
  RENDER_OUT=v2/ep07/stills/tmp PREVIEW_RES=$RES timeout 1200 blender -b --python v2/ep07/render.py -- --shot $s --still $f --spp ${SPP:-6} > v2/ep07/stills/log_$s.txt 2>&1
  mv v2/ep07/stills/tmp/still_$(printf %04d $f).png v2/ep07/stills/$s.png 2>/dev/null && echo "$s ok" || { echo "$s FALHOU"; grep -E "Error|Traceback" -A3 v2/ep07/stills/log_$s.txt | head -8; }
done
