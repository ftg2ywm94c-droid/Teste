# Registro de mudanças

## v0.1-poc — versão funcional preservada (commit `be24c75`; tag local `v0.1-poc`)
- Prova de conceito de 10 s: motor NumPy (`engine/`), planos S1–S3, trilha sintetizada, `output/poc_540x960.mp4` (QC aprovado).
- `scripts/add_narration.py`: MP3 → MP4 com legenda sincronizada, ducking e −14 LUFS.
- Para recuperar: `git checkout be24c75 -- projeto_videos3d` (a tag não pôde ser enviada ao GitHub: o acesso desta sessão só permite o branch de trabalho).

## v0.3 — vídeo 02 "E se a Terra parasse de girar" entregue (2026-11-12)
- Arquivo: `v2/ep02/out/02_terra_parasse_de_girar_1080x1920.mp4` (76,5 s, 2295 quadros, 30 fps, H.264 + AAC 48 kHz, 135 MB; fora do git por tamanho).
- **Render nativo 720x1280** (Cycles, 6–9 amostras + OIDN), **ampliado para 1080x1920**. Não é render nativo em 1080x1920.
- Narração original do usuário sem alteração de velocidade: atraso 0 ms, deriva 0 ms, correlação 0,997.
- QC (`v2/ep02/qc_report_02.json`): todos os itens aprovados — −13,9 LUFS, pico −1,5 dBTP, sem quadros pretos/congelados, legenda com erro 0,0 s.
- Tempo de render: ~6 h em CPU (A–K), mais 18 min para refazer o fim do plano E.
- Texturas da Terra: Solar System Scope (CC BY 4.0); relevo: NOAA ETOPO5; modelo da redistribuição dos oceanos: Fraczek (Esri).
- Pipeline compartilhado (`captions.py`, `assemble.py`, `qc.py`) agora aceita `EP=02`; saída do vídeo 01 conferida como idêntica (só ganhou o estilo "Nota", não usado).

### Correções após o QC da v0.3
- Plano E: câmera e ônibus ficavam parados 1,5 s (31,8–33,3 s) → recuo lento da câmera a partir de 30,6 s; quadros 918–998 refeitos (antigos guardados em `v2/ep02/frames/_bak_E_v0.2/`).
- Nota "giro acelerado na animação" cobria o rótulo "1 volta por dia" → movida para a parte de baixo (4º campo opcional em `NOTES`).

## v0.2 — vídeo 01 "Distância de parada" entregue (2026-11-11)
- Arquivo: `v2/out/01_distancia_de_parada_1080x1920.mp4` (68,0 s, 2040 quadros, 30 fps, H.264 + AAC 48 kHz, 143 MB; fora do git por tamanho).
- **Render nativo 720x1280** (Cycles, 12 amostras + OIDN), **ampliado para 1080x1920** (lanczos + nitidez). Não é render nativo em 1080x1920.
- Narração original do usuário sem alteração de velocidade: QC mediu atraso 0 ms, deriva 0 ms, correlação 0,991.
- QC (`v2/qc_report_01.json`): todos os itens aprovados — −13,9 LUFS, pico −1,4 dBTP, sem quadros pretos/congelados, legenda com erro 0,0 s, folga mínima menino 1,28 m / bola 4,04 m.
- Tempo de render: ~10,5 h em CPU (15–19 s/quadro). D1 e E refeitos (motorista reposicionado; rótulo de 10 m não cobre o menino).

### Histórico da produção v0.2
- `tools/setup_env.sh`: instala Blender 4.2.3 LTS, libEGL e faster-whisper num container novo.
- `add_narration.py`: Whisper passa a receber o áudio decodificado pelo ffmpeg (o leitor interno quebrava com PyAV ≥ 15).
- Medições do ambiente (2026-11-11), cena de teste simples:
  Cycles CPU 1080x1920 48 amostras = 31 s/quadro; 12 amostras + denoiser = 13,8 s/quadro; EEVEE por software (llvmpipe) = 59 s/quadro.
