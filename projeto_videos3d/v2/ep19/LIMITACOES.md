# Limitações conhecidas: vídeo 19 (A Noite Livre · Ep. 1)

- **Resolução:** render nativo em 1080x1920 na skill Xavier (Remotion + three.js, `teste_xavier/src/videos/noitelivre/`, composição `NoiteLivreShort`), 30 fps, 1937 quadros, sem ampliação. A primeira PNG foi conferida: 1080x1920. Títulos (`mograph.py`) e legenda também são 1080x1920.
- **Vozes:** todas de IA, geradas na ElevenLabs:
  - narradora: Ana Dias;
  - TV: Diego; pai: Will; mãe: Roberta; Bia: Keren.
  - Cada take foi conferido com Whisper. Os takes errados foram refeitos: 08_bia, take 2; N5 "E se...", take t2.
  - A velocidade das vozes não foi alterada. Na faixa, a voz da TV passa por um filtro de banda (320–3800 Hz), para soar como TV.
- **Ficção:** "história de ficção" aparece na tela de 0 a 3 s. O nome dos filmes não aparece em lugar nenhum e as máscaras são lisas e genéricas.
- **Violência:** os facões com vermelho escorrendo foram pedidos pelo usuário. São cartoon e não mostram ataque nem ferimento. Há risco de restrição de idade ou de menos alcance (ver `POSTAGEM.md`).
- **Ajustes feitos depois do render, todos conferidos no MP4:**
  1. O QC achou um trecho parado de ~2 s no plano final do loop, porque a câmera era estática. O plano 24 agora tem o mesmo zoom lento do plano 1 e chega exatamente na lente do quadro 0. Só esse plano (61 quadros) foi refeito, e o QC passou a dar 0 trechos parados.
  2. A legenda cobria o letreiro do telejornal no plano 2 (3,55–8,36 s) e na TV em 21:58 (38,86–40,53 s). Nesses trechos ela desce (`LEG_MV`).
  3. A frase "a mais comentada vira a PARTE 2" ficava por cima das cabeças da família. Ela ganhou um fundo escuro.
- **Item de QC reprovado `frames`:** o MP4 tem 1938 quadros (64,60 s) e a narração tem 64,58 s. A regra do `qc.py` aceita meio quadro de diferença, e aqui a diferença é de 0,6 quadro: um quadro final repetido pelo `assemble.py` para cobrir o áudio. Os outros 14 itens passam. Não é perceptível e fica anotado.
- **Emenda do loop:** a diferença média entre o último quadro e o quadro 0 é de 1,2 em 255, porque o HUD e o selo são iguais e a lente é contínua.
- **Atraso de 1 quadro (33 ms):** o mesmo de `assemble.py` dos vídeos anteriores, sem efeito perceptível.
