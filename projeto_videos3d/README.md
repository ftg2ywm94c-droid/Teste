# Vídeos 3D por código — prova de conceito

## Rodar tudo (Python 3.11+, numpy, scipy, opencv-python, ffmpeg com libass)
```
python3 scripts/audit_references.py references analysis      # auditoria (≈3 min/vídeo com OCR)
python3 scripts/render_shots.py --shot S1 --ss 2             # um MP4 por plano em renders/preview
python3 scripts/render_shots.py --shot S2 --ss 2
python3 scripts/render_shots.py --shot S3 --ss 2
python3 scripts/mix_audio.py                                 # trilha sintetizada a partir dos eventos da animação
python3 scripts/assemble.py                                  # concat + legenda ASS + áudio -> output/poc_540x960.mp4
python3 scripts/quality_check.py output/poc_540x960.mp4      # qc_report.json + contact_sheet.jpg
```

## Narração (ElevenLabs) → MP4 final
O texto e os tempos para gravar estão em `narracao/ROTEIRO_ELEVENLABS.md`. Com o arquivo gravado:
```
python3 scripts/add_narration.py narracao/narracao.mp3       # -> output/final_1080x1920.mp4
```
Encaixa cada frase no seu plano (âncoras `narration_at` em `shots/shots.json`), refaz a legenda com os tempos reais da voz,
abaixa a trilha sob a voz (sidechain), normaliza em −14 LUFS e roda o QC. Opções: `--sync continuo`, `--size 540x960`, `--out`.
Se `faster-whisper` estiver instalado, os tempos de palavra vêm da transcrição; senão, do roteiro distribuído pelos trechos de fala.
Dependências: `pip install numpy scipy opencv-python-headless` + ffmpeg com libass. A fonte Poppins Bold (OFL) está em `fonts/`.
Quadros soltos para revisão rápida: `python3 scripts/render_shots.py --shot S2 --ss 1 --still 0,40,77`.

## Estrutura
- `engine/rt.py` — renderizador 3D (ray casting analítico em NumPy): primitivas, câmera, sombras, luz toon, névoa, contorno.
- `engine/assets.py` — personagem rigado (IK de pernas com pés plantados, FK de braços, expressões), carro, cenário.
- `scripts/` — auditoria, render por plano, áudio, montagem, QA.
- `shots/shots.json` — shot list + legendas. `config/` — ambiente e parâmetros.
- `blender/poc_blender.py` — a mesma cena em bpy para rodar no Blender do notebook (**não testado**).
- `analysis/` — relatório, JSON por frame, contact sheets e keyframes das referências (vídeos de referência não incluídos no zip).
- `output/` — MP4, legenda, contact sheet, QC, `LIMITACOES.md`.
- `narracao/` — roteiro para a ElevenLabs; o MP3 gravado entra aqui.
- `fonts/` — Poppins Bold + licença OFL (usada pelo filtro de legenda via `fontsdir`).
