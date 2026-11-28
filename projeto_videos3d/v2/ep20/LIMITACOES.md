# Limitações conhecidas: vídeo 20 (A Visita · Ep. 1), versão 2

- **Resolução:** render nativo em 1080x1920 na skill Xavier (Remotion + three.js, `teste_xavier/src/videos/visita/`, composição `VisitaShort`), 30 fps, 2280 quadros PNG, sem ampliação. Títulos e HUD (`mograph.py`) e legenda também são 1080x1920.
- **Vozes:** todas de IA, ElevenLabs `eleven_v3`: narrador Spuds Oxley e avó Edna (`narracao/20_narracao.mp3`, 76,01 s). A velocidade não foi alterada.
- **Ficção:** "história de ficção" na tela de 0 a 3 s. O app de mensagens é desenhado por nós (sem logo nem cores de marca).
- **O que mudou da v1 para a v2** (os quadros da v1 continuam em `v2/ep20/frames_v1/`, fora do git):
  - o celular fica na mão, visto de costas (dedos na borda), nos planos em que você segura; a tela ilumina o rosto;
  - luzes práticas reais: tela do celular, despertador, luar pela janela e luz da varanda com sombra, fresta da porta e portão da dona Célia;
  - quarto menos escuro.
  - Brilho medido no quadro do meio de cada plano (0–255), da v1 para a v2: S01 30→42, S05 30→75, S12 61→102, S15 52→82, S21 31→77. Os planos de mensagem (S19, S20, S22) ficaram um pouco mais escuros (76→65, 72→65, 74→66), porque o cartão chapado do celular virou o aparelho de costas.
- **Ajustes depois do render, todos conferidos no MP4:**
  1. **Volume:** a primeira montagem deu −15,2 LUFS, porque o limitador de pico (−1,9 dBFS) tira ~1,2 dB depois do loudnorm. O `assemble.py` ganhou a opção `LOUD_I` por episódio (o padrão continua −14, então os outros vídeos não mudam), e o vídeo 20 usa −12,8. Resultado: −14,1 LUFS, pico −1,6 dBTP.
  2. **Legenda x carimbo:** "TOCA SOZINHO." ficava embaixo do carimbo "BIP BIP" no plano 2 (o mesmo na v1). Entre 1,9 e 4,3 s a legenda desce (`LEG_MV`, margem 380). O diff do `.ass` mostra que só essa linha mudou.
  3. **Emenda do loop:** com a luz nova, o celular aceso no criado-mudo no último quadro destoava do quadro 0 (celular apagado). No plano 27 o celular volta apagado (`phoneOn` em `story.ts`), e só esse plano (45 quadros) foi refeito. A diferença média entre o último quadro e o quadro 0 caiu de 7,0 para 3,4 em 255. O que sobra é o despertador começando a tocar no quadro 0, que é o começo da história (na metade direita da imagem, 1,2).
  4. **Render com falha:** a primeira tentativa de refazer o plano 27 saiu sem texturas e com o 1º quadro branco, sem erro no log. Um quadro isolado saiu certo; foram apagadas as pastas antigas de assets do Remotion em `.tmp` e o plano foi refeito (45 quadros, brilho 41,1–41,6 em todos).
- **Item de QC reprovado `frames`:** o MP4 tem 2281 quadros (76,03 s) e a narração tem 76,01 s: 0,7 quadro, um quadro final repetido para cobrir o áudio (o mesmo caso do vídeo 19). Os outros 14 itens passam.
- **Correlação da narração:** 0,525 (o mínimo do QC é 0,5). É mais baixa que a do vídeo 19 (0,923); a causa não foi medida (a mixagem tem chuva e trilha de tensão por baixo de quase todo o vídeo). Atraso e deriva medidos: 0 ms.
- **Capa:** quadro de 33,1 s do próprio vídeo (`thumbnails/20_a_visita_ep1_capa.jpg`): a avó pelo olho mágico, "O CASACO DO ENTERRO" no topo, sem legenda por cima.
