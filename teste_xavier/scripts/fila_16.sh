#!/usr/bin/env bash
# Vídeo 16: render retomável (duas passadas para cobrir falhas).
cd "$(dirname "$0")/.."
mkdir -p out/vendaval3_seq
scripts/render_vendaval3.sh; scripts/render_vendaval3.sh
echo FILA_FIM
