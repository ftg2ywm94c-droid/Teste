#!/usr/bin/env bash
# Fila 2: refaz os planos internos do 13 (vidro noturno, pernas no banco do fundo) e depois termina o 14 (retomável).
cd "$(dirname "$0")/.."
F=/home/user/Teste/projeto_videos3d/v2/ep13/frames
for n in S02_corredor S03_cochilo S04_toca S05_acorda S06_sozinho S07_toca_de_novo S08_aproxima S11_motorista S12_retrovisor S15_porta S17_cinco_seg S19_opcao_b; do rm -rf $F/$n; done
echo "refazendo planos internos do 13"; scripts/render_onibus.sh
echo "render do 14"; mkdir -p out/vendaval2_seq; scripts/render_vendaval2.sh
echo "render do 14 (segunda passada)"; scripts/render_vendaval2.sh
echo FILA_FIM
