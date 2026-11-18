#!/usr/bin/env bash
# Fila: espera o render do vídeo 13 terminar, refaz os planos do 13 feitos antes da correção das pernas
# (S02, S03, S05, S08) e depois renderiza o vídeo 14. Log em out/fila_13_14.log.
cd "$(dirname "$0")/.."
while pgrep -f render_onibus.sh >/dev/null; do sleep 30; done
F=/home/user/Teste/projeto_videos3d/v2/ep13/frames
rm -rf $F/S02_corredor $F/S03_cochilo $F/S05_acorda $F/S08_aproxima
echo "refazendo planos do 13"; scripts/render_onibus.sh
echo "render do 14"; mkdir -p out/vendaval2_seq; scripts/render_vendaval2.sh
echo FILA_FIM
