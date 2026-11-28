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
- **Capa (v2):** quadro de 10,0 s, guardada em `thumbnails/122_the_key_ep2_cover_v2.jpg`.

## v3: câmera contínua (2026-11-28; padrão ESTILO §10)
- **Pedido:** a câmera não seguia para a cena seguinte (13 cortes). Agora é uma câmera só do quadro 0 ao fim: a spline `TRAVEL2` (Hermite com tempo) atravessa a rua, entra pela porta real da casa e sobe a escada. O único corte é o do loop (63,93 s), medido com `select=gt(scene,0.3)` no MP4.
- **Cenário ligado:** o corredor foi encaixado atrás da fachada da casa (`HALL`), e a porta da fachada é a porta do corredor. Personagens e luzes seguem o tempo do vídeo, não o plano.
- **Simulação antes do render** (`simcam.py`): sem colisão com parede, porta, degraus ou personagens; giro máximo 5,9°/quadro na entrada pela porta (ação), 4,5°/quadro na escada.
- **Corrigido depois do 1º render v3:**
  - 49,0–50,2 s mostrava uma parede vazia na fala "You decide". Agora a câmera contorna você e sobe a escada de costas, olhando para você. Quadros 1356–1916 refeitos.
  - QC reprovado por 2 congelamentos no plano final (51,4 s e 63,2 s). Agora há uma aproximação lenta até o fim. Quadros 1523–1916 refeitos.
- **Varredura dos 1950 quadros:** nenhum vazio ou lavado (desvio < 3). Maiores mudanças entre quadros, todas de movimento real:
  - giro rápido para olhar para ele (17,5–18,7 s);
  - porta passando na frente (22,4 s);
  - troca do desenho de frente para o de lado (41,5 s).
- **Limitações:** dentro do corredor estreito você aparece em close, sem caber de corpo inteiro. A troca de desenho frente/lado é um salto de 1 quadro, característica do sistema de sprites.
- **QC v3:** 15/15. −14,1 LUFS, pico −1,8 dBTP, correlação da narração 0,931, 0 trechos congelados ou pretos, emenda do loop 0,17/255 nos quadros. Áudio e legenda iguais ao v2.
- **Versões:** quadros v2 em `frames_v2_backup/`, MP4 v2 em `out/122_the_key_ep2_v2_1080x1920.mp4` (fora do git).
- **Capa v3:** quadro de 12,0 s, você na frente e ele atrás, "RUN. HE'S CHASING YOU" (`thumbnails/122_the_key_ep2_cover.jpg`, script `v2/ep122/capa.py`).
