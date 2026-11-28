# Limitações conhecidas: piloto de qualidade (15,6 s, EP=90)

- **Resolução:** render nativo 1080x1920 na skill Xavier (`teste_xavier/src/videos/piloto/`, composição `PilotoShort`), 30 fps, 468 quadros, sem ampliação.
- **Voz:** `narracao/90_narracao.mp3`, cópia byte a byte de `narracao/piloto/piloto_narracao.mp3` (md5 b203de76…). Velocidade não alterada.
- **QC:** passa nos 15 itens: 468 quadros, −14,4 LUFS, pico −1,9 dBTP, correlação da narração 0,976, atraso e deriva 0 ms (`out/qc_report.json`).
- **Render com 3 abas falhou:** na 1ª rodada (`CONC=3`), P3 e P5 caíram com "Page crashed!" e P2/P4 saíram com 7 quadros em branco e, no P4, o resto sem a luz da lanterna e sem a textura do asfalto. Com `CONC=1` os 5 planos saíram certos (sem quadro em branco; P4 com brilho 44–48 em todos os quadros). Tempo com 1 aba: 3,1 a 3,7 s por quadro (vídeo 20 com 3 abas: ~4 s por quadro). A causa da falha com 3 abas não foi encontrada. O vídeo 20 e o 19 foram varridos quadro a quadro e não têm quadro em branco; os saltos de brilho do vídeo 20 caem todos nos relâmpagos programados (`BOLTS`).
- **Trecho parado:** o QC achou 0,73 s parado (6,67–7,40 s), no escuro depois do "apaga", porque a câmera do plano 2 quase não andava de 5,0 a 7,4 s. A câmera agora se aproxima devagar da lâmpada até o corte (zoom 40°→33°); só o plano 2 foi refeito e o QC deixou de acusar.
