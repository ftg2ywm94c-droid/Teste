#!/usr/bin/env bash
# Retoma o 14 depois do reinício do contêiner (retomável; duas passadas para cobrir falhas).
cd "$(dirname "$0")/.."
mkdir -p out/vendaval2_seq
scripts/render_vendaval2.sh; scripts/render_vendaval2.sh
echo FILA_FIM
