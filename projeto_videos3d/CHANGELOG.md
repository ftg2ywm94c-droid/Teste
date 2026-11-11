# Registro de mudanças

## v0.1-poc — versão funcional preservada (tag git `v0.1-poc`)
- Prova de conceito de 10 s: motor NumPy (`engine/`), planos S1–S3, trilha sintetizada, `output/poc_540x960.mp4` (QC aprovado).
- `scripts/add_narration.py`: MP3 → MP4 com legenda sincronizada, ducking e −14 LUFS.
- Para recuperar: `git checkout v0.1-poc`.

## Em andamento — v0.2 (produção do primeiro vídeo de 60–65 s)
- `tools/setup_env.sh`: instala Blender 4.2.3 LTS, libEGL e faster-whisper num container novo.
- `add_narration.py`: Whisper passa a receber o áudio decodificado pelo ffmpeg (o leitor interno quebrava com PyAV ≥ 15).
- Medições do ambiente (2026-11-11), cena de teste simples:
  Cycles CPU 1080x1920 48 amostras = 31 s/quadro; 12 amostras + denoiser = 13,8 s/quadro; EEVEE por software (llvmpipe) = 59 s/quadro.
