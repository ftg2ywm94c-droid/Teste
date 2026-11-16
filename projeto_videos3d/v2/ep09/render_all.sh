#!/usr/bin/env bash
# Render final do vídeo 09 (720x1280), um processo Blender por plano. Retomável: quadros prontos são pulados;
# se o Blender cair, o plano é reiniciado até 4 vezes e continua de onde parou.
# Uso: setsid nohup bash v2/ep09/render_all.sh >> v2/ep09/frames/render.log 2>&1 &
cd "$(dirname "$0")/../.."; mkdir -p v2/ep09/frames
ALL=$(cd v2/ep09 && python3 -c "import plan; print(' '.join(s.name for s in plan.SHOTS if s.kind != 'trailer'))")
for s in ${SHOTS:-$ALL}; do
  kind=$(cd v2/ep09 && python3 -c "import plan; print(plan.BY_NAME['$s'].kind)")
  spp=8
  echo "$(date +%H:%M:%S) início $s ($kind, $spp amostras)"
  for try in 1 2 3 4; do
    find v2/ep09/frames/$s -name '[0-9]*.png' -size 0 -delete 2>/dev/null
    timeout 18000 blender -b --python v2/ep09/render.py -- --shot $s --mode final --spp $spp > v2/ep09/frames/log_$s.txt 2>&1 && break
    echo "$(date +%H:%M:%S) $s caiu (tentativa $try), retomando"
  done
  echo "$(date +%H:%M:%S) fim $s: $(ls v2/ep09/frames/$s 2>/dev/null | grep -c '^[0-9]*.png$') quadros $(grep -E '^\[.*render' v2/ep09/frames/log_$s.txt)"
done
echo "$(date +%H:%M:%S) TUDO PRONTO"
