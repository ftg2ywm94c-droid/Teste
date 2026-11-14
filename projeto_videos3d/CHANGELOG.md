# Registro de mudanças

## v0.1-poc — versão funcional preservada (commit `be24c75`; tag local `v0.1-poc`)
- Prova de conceito de 10 s: motor NumPy (`engine/`), planos S1–S3, trilha sintetizada, `output/poc_540x960.mp4` (QC aprovado).
- `scripts/add_narration.py`: MP3 → MP4 com legenda sincronizada, ducking e −14 LUFS.
- Para recuperar: `git checkout be24c75 -- projeto_videos3d` (a tag não pôde ser enviada ao GitHub: o acesso desta sessão só permite o branch de trabalho).

## v0.7 — vídeo 06 "E se começasse um apocalipse zumbi no Brasil?" entregue (2026-11-14)
- Arquivo: `v2/ep06/out/06_apocalipse_zumbi_brasil_1080x1920.mp4` (74,3 s, 2228 quadros, 30 fps, H.264 + AAC, 100 MB). Versão leve: `06_apocalipse_zumbi_brasil_1080x1920_leve.mp4` (60 MB). As duas ficam fora do git por tamanho.
- **Render nativo em 720x1280** (Cycles, 6–8 amostras + OIDN), **ampliado para 1080x1920**.
- 27 planos. Cenários novos: cidade abandonada ao entardecer com zumbis estilizados, mata em escala de formiga, fungo e esporos, termômetro, vírus da raiva, cão e morcego. Painéis com a curva dos fungos, o calendário da raiva e o modelo de surto.
- Narração original do usuário sem alteração de velocidade: atraso 0 ms, deriva 0 ms, correlação 0,976.
- QC (`v2/ep06/qc_report_06.json`): todos os itens aprovados. Volume −14,1 LUFS, pico −1,4 dBFS.
- Correção depois do QC: o plano C3 foi refeito porque o rótulo "37 °C" saía cortado.
- Tempo de render: cerca de 9 h em CPU, dividindo o processador com outras tarefas. O container reiniciou 4 vezes, e o render foi retomado cada vez a partir dos quadros salvos.
- Thumbnail: `thumbnails/06_apocalipse_zumbi_thumb.jpg`. É um render próprio em 1080x1920 nativo, com a composição feita por `v2/thumb.py`.

## v0.6 — vídeo 05 "E se TODO o oxigênio sumisse por 20 segundos?" entregue (2026-11-13)
- Arquivo: `v2/ep05/out/05_todo_oxigenio_sumisse_1080x1920.mp4` (73,4 s, 2202 quadros, 30 fps, H.264 + AAC, 142 MB). Versão leve: `05_todo_oxigenio_sumisse_1080x1920_leve.mp4` (59 MB, feita automaticamente pelo `assemble.py`). As duas ficam fora do git por tamanho.
- **Render nativo em 720x1280** (Cycles, 6–8 amostras + OIDN), **ampliado para 1080x1920**.
- 29 planos com corte e câmera em movimento. Cenários reaproveitados do vídeo 04, mais três novos: prédio que se desfaz em blocos e pó, moléculas de água que perdem o O e mar que vira vapor.
- Narração original do usuário sem alteração de velocidade: atraso 0 ms, deriva 0 ms, correlação 0,987.
- QC (`v2/ep05/qc_report_05.json`): todos os itens aprovados. Volume −14,3 LUFS, pico −1,3 dBFS, nenhum quadro preto ou congelado, erro da legenda 0,0 s.
- Tempo de render: cerca de 7 h em CPU, dividindo o processador com a prévia do vídeo 06. O container reiniciou 1 vez, e o render foi retomado a partir dos quadros salvos.

## v0.5 — vídeo 04 "E se o oxigênio sumisse por 20 segundos?" entregue (2026-11-13)
- Arquivo: `v2/ep04/out/04_oxigenio_sumisse_20s_1080x1920.mp4` (74,4 s, 2232 quadros, 30 fps, H.264 + AAC, 117 MB; fora do git por tamanho).
- **Render nativo em 720x1280** (Cycles, 6–8 amostras + OIDN, light tree desligado), **ampliado para 1080x1920**.
- Ritmo novo: 31 planos, corte combinado com câmera em movimento.
- Narração original do usuário sem alteração de velocidade: deriva 0 ms, correlação 0,996.
- QC (`v2/ep04/qc_report_04.json`): todos os itens aprovados. Volume −14,1 LUFS, pico −1,4 dBFS, nenhum quadro preto ou congelado.
- Tempo de render: cerca de 7 h em CPU. O container reiniciou 4 vezes, e o render foi retomado cada vez a partir dos quadros salvos.

### Correções após o QC da v0.5
- As notas "moléculas fora de escala" (2,65 s), "ilustração" (21,35 s) e "ilustração simplificada" (34,45 s) cobriam o contador "20 s" e o painel de altitude. Foram movidas para a parte de baixo.
- Versão leve para baixar no celular: `04_oxigenio_sumisse_20s_1080x1920_leve.mp4` (59 MB, H.264 em 2 passagens a 6,2 Mbps, SSIM 0,988 em relação ao original). O arquivo de 117 MB não mostrava o botão de baixar no app.

## v0.4 — vídeo 03 "E se você pulasse num buraco que atravessa a Terra?" entregue (2026-11-13)
- Arquivo: `v2/ep03/out/03_buraco_atravessa_a_terra_1080x1920.mp4` (66,0 s, 1980 quadros, 30 fps, H.264 + AAC 48 kHz, 65 MB; fora do git por tamanho).
- **Render nativo 720x1280** (Cycles, 6–9 amostras + OIDN), **ampliado para 1080x1920**. Não é render nativo em 1080x1920.
- Narração original do usuário sem alteração de velocidade: atraso 0 ms, deriva 0 ms, correlação 0,995.
- QC (`v2/ep03/qc_report_03.json`): todos os itens aprovados. Volume −14,0 LUFS, pico −1,1 dBTP, nenhum quadro preto ou congelado, erro da legenda 0,0 s.
- Física (`v2/ep03/fisica.py`): queda pelo modelo PREM. Ida em 38 min 11 s, velocidade máxima de 35.700 km/h, gravidade de 10,7 m/s² na fronteira do núcleo.
- Tempo de render: cerca de 9,5 h em CPU. O container reiniciou 3 vezes no meio, e o render retomou cada vez a partir dos quadros já salvos.
- Texturas da Terra: Solar System Scope (CC BY 4.0).

### Correções após o QC da v0.4
- Plano J: a câmera ficava parada em 4 trechos (50,3–58,8 s). Ganhou deriva lenta no começo e aproximação final em Kola, e o plano inteiro foi refeito. Os quadros antigos estão em `v2/ep03/frames/_bak_J_v0/`.
- A nota "tempo acelerado" (36,95–40,45 s) cobria o rótulo "38 min" e foi movida para a parte de baixo.

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
