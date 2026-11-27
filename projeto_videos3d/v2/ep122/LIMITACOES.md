# Limitações conhecidas: vídeo 122 (The Key · Ep. 2, canal You Decide 3D)

- **Imagem:** 1950 quadros renderizados em 3D nativo 1080x1920 (Remotion + three.js, skill Xavier, composição `Chave2Short`), JPEG q95, sem upscale.
- **Roteiro:** continuação pela opção A, a mais pedida nos comentários do Ep. 1. Ação sem violência gráfica: arranco da chave, perseguição, porta batendo e silhueta na escada.
- **Voz:** a mesma do Ep. 1, ElevenLabs `eleven_v3`, `en` (IA). 4 takes (F1–F4) colocados com `montar.py`. Velocidade não alterada. Cada palavra conferida com o Whisper em inglês.
- **Mixagem (pedido: efeitos sem cobrir a narração):**
  - efeitos abaixam 8 dB pelo envelope da voz;
  - vibração do celular antes de "Your phone";
  - notas de tensão depois das palavras;
  - `SFX_BUS 1,6` e `W_TENSAO 0,55` (só neste episódio).
  - Medido no MP4 final, em janelas de 100 ms: mediana nas palavras −15,5 dB e mediana nas pausas −27,5 dB. O p95 nas pausas fica em −8,9 dB, com os efeitos fortes, contra −7,5 dB nas palavras.
- **1º render reprovado no QC** (6 trechos congelados): o loop ficava 1,1 s parado, e a escada (45 s) e o início da escolha (50 s) ficavam quase parados.
  - Correção: as câmeras dos planos 12–14 se movem o tempo todo, e o loop desacelera até a posição do quadro 0.
  - Os quadros antigos estão em `frames_v1_backup/` (fora do git).
- **Cortes bruscos verificados:**
  - perto de 7 s, um poste em primeiro plano cruza a câmera por cerca de 4 quadros (cena, não erro);
  - 44,8 s é a luz embaixo da porta apagando (roteiro).
- **QC:** 15/15. −14,1 LUFS, pico −1,8 dBTP, correlação da narração 0,931, 0 trechos congelados ou pretos, emenda do loop 0,1/255 nos quadros (0,8/255 no MP4).
- **Capa:** quadro de 10,0 s (a perseguição), "RUN. HE'S CHASING YOU" (`thumbnails/122_the_key_ep2_cover.jpg`).
