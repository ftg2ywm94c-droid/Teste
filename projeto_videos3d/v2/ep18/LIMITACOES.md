# Limitações conhecidas: vídeo 18 (Jogador 2 · Ep. 1)

- Resolução: render nativo em 1080x1920 na skill Xavier (Remotion + three.js, `teste_xavier/src/videos/jogador2/`, composição `Jogador2Short`), 30 fps, 1938 quadros, sem ampliação. Os títulos (`mograph.py`) e a legenda também são 1080x1920.
- Direitos: nada da identidade visual do jogo (logo, arte, personagens, interface ou trechos) e nenhuma marca de console aparece. O console, o controle e a tela da TV ("INSTALANDO… 99%", "JOGADOR 2 CONECTADO") são genéricos e foram desenhados aqui. "GTA 6" aparece só na narração, no título e na legenda da postagem.
- Narração: MP3 do usuário (`narracao/18_narracao.mp3`, 64,60 s), sem mudança de velocidade e sem cortes. A transcrição tem 158 palavras e bate com o roteiro. As diferenças restantes são só de grafia ("pra"/"para", "2"/"dois").
- História de ficção ("história de ficção" na tela de 0 a 3 s). Nenhum dado inventado sobre o jogo: os "dois dias pra baixar" são da história do personagem.
- Som: efeitos sintetizados e CC0, sem som de fabricante:
  - vento, grilos e latidos sincronizados com a imagem, que cortam secos no "param";
  - zumbido da TV, a energia caindo, o apito do LED, o estalo e o chiado da TV ligando;
  - um som genérico de conexão e a almofada vibrando;
  - trilha de tensão com 24 deixas.
- Ajustes feitos depois do render, todos conferidos no MP4:
  1. O primeiro QC deu correlação da narração 0,585, com os efeitos uns 9 dB acima do vídeo 16. Vento, latidos e vibração foram abaixados, e a vibração foi filtrada abaixo de 700 Hz. Correlação final: 0,893, com −14,4 LUFS e TP −1,7.
  2. A legenda cobria o texto da TV nos planos 1–2 e 12. Ela desce para baixo do rack nesses trechos (`LEG_MV`). O gancho e o selo do episódio foram descidos para não cobrir o relógio 03:12.
  3. No plano 12, "JOGADOR 2" saía cortado nas bordas do 9:16. A câmera foi afastada e só esse plano (129 quadros) foi refeito. Os quadros antigos estão guardados fora do git.
- A correlação da narração (0,893) é menor que a do vídeo 16 (0,967), porque este vídeo tem mais efeitos de ambiente. A voz fica clara acima deles na conferência por trecho.
- Atraso de 1 quadro (33 ms) entre os PNGs e o MP4, vindo de `assemble.py`. Já existia nos vídeos anteriores e não é perceptível. Fica anotado para corrigir com calma.
