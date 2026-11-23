# Limitações conhecidas — vídeo 16 (Você decide · Vendaval · Ep. 3)

- Resolução: render nativo em 1080x1920 na skill Xavier (Remotion + three.js, `teste_xavier/src/videos/vendaval3/`, composição `Vendaval3Short`), 30 fps, 2308 quadros, sem ampliação. Títulos (`mograph.py`) e legenda também em 1080x1920.
- História de ficção em segunda pessoa. Avisos na tela: "história de ficção" (0–3 s), "na vida real: nunca chegue perto de fio caído" (18,1–22,7 s) e "emergência: Bombeiros 193 · Defesa Civil 199" (66,6 s até o fim).
- A ligação pro 193 não tem voz inventada do atendente: só chiado de linha, o cronômetro e a narração contando o que ele disse. A orientação (não chegar perto do fio, ficar em local seguro) é a mesma conferida no vídeo 14 (fontes em `v2/ep14/LIMITACOES.md`).
- Narração: MP3 do usuário (`narracao/16_narracao.mp3`, 76,93 s), sem mudança de velocidade e sem cortes. Transcrição (faster-whisper medium) com 169 palavras, batendo com o roteiro.
- Som: efeitos sintetizados (tons de discagem, chamada, clique de atender, chiado, bipes de 3%, desligamento, sirene se aproximando e parando, batidas sincronizadas, trovões nos relâmpagos, faíscas sincronizadas com a imagem, passos na opção A) e trilha de tensão (`lib/tensao.py`, 27 deixas). Nenhum toque de fabricante.
- Conferência depois do render: na palavra "faísca" (54,8 s) o piscar aleatório do fio estava apagado. Foi forçada uma rajada (2 de cada 3 quadros por ~1 s), na imagem (`story.ts`) e no som (`audio.py`), e os quadros 1640–1689 foram refeitos. Quadros anteriores guardados fora do git.
- O plano do silêncio (S14, ~36–38 s) é de propósito quase vazio: parede escura e o resto do vermelho da sirene no chão.
- Atraso de 1 quadro (33 ms) entre os PNGs e o MP4, vindo da montagem por lista do ffmpeg (`assemble.py`). Já existia nos vídeos anteriores e não é perceptível. Fica anotado para corrigir com calma num próximo vídeo, sem mexer agora no que funciona.
- O final da série (vídeo 17) já está escrito em duas versões em `roteiros/17_vendaval_ep4_final.md`.
