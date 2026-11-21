#!/usr/bin/env bash
# Vídeo 15: render retomável (duas passadas para cobrir falhas).
cd "$(dirname "$0")/.."
mkdir -p out/onibus2_seq
scripts/render_onibus2.sh; scripts/render_onibus2.sh
echo FILA_FIM
