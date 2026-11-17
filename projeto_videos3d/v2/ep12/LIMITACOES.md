# Limitações conhecidas — vídeo 12 (Vendaval: você sai ou fica? — suspense com escolha A/B)

- Resolução: render nativo em 1080x1920 na skill Xavier (Remotion + three.js, `teste_xavier/src/videos/vendaval/`), 30 fps, sem ampliação. Os títulos, a camada de chuva/vento (`mograph.py`) e a legenda também são desenhados em 1080x1920.
- História ilustrativa em segunda pessoa: não aconteceu com uma pessoa específica. O aviso "história ilustrativa" aparece na tela no começo.
- Fato real usado: a Defesa Civil RS emitiu alerta de temporais com rajadas acima de 90 km/h para 17 a 19/11/2026 (fontes em `roteiros/12_vendaval_escolha.md`). A nota na tela diz só isso.
- Tela do celular: cartão genérico ("DEFESA CIVIL / ALERTA SEVERO / VENDAVAL / 90 km/h"), sem logotipo nem layout oficial. O som de alarme é sintetizado e genérico. Não é o som oficial do cell broadcast.
- O alarme no celular depende de aparelho compatível (4G/5G). O roteiro só diz "dispara um alarme", sem prometer que funciona em qualquer celular.
- A árvore que inclina, a telha voando e a falta de luz são situações ilustrativas, sem números inventados.
- Resposta segura (B, cômodo interno sem janela) não é dita na narração. Ela vai no comentário fixado e na descrição:
  "Resposta: B. Num vendaval, a orientação da Defesa Civil é ficar dentro de casa, num cômodo interno e longe de janelas e vidros. Na rua, você fica exposto a galhos, telhas, placas e fios caídos. Receba os alertas: envie seu CEP por SMS para 40199."
  No final a tela mostra "resposta no comentário fixado" e "alertas reais: Defesa Civil · SMS 40199 (envie seu CEP)".
- Narração: MP3 do usuário (`narracao/12_narracao.mp3`), sem mudança de velocidade e sem cortes. A voz diz "E si?" no fim; a legenda mostra "E SE...".
- Legenda: números ditos como algarismos pela transcrição ("11", "90", "10") aparecem por extenso, como no roteiro aprovado.
- Som: sons CC0 de `assets/sfx_cc0/` (créditos em `assets/sfx_cc0/CREDITOS.md`) e efeitos sintetizados (vento com rajadas, assobio, gotas, rangido, estalo, alarme, tique da contagem). Os efeitos têm barramento próprio (ESTILO §9) e foram medidos contra a voz: ficam abaixo dela enquanto ela fala e só sobem nas pausas.
- Chuva: além das gotas 3D (suaves por causa da profundidade de campo), há uma camada 2D nítida de gotas, respingos, rajadas e folhas nos planos externos de tempestade.
