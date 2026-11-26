# Limitações conhecidas: vídeo 121 (A Chave Ep. 1 em inglês, canal You Decide 3D)

- **Imagem:** os MESMOS 1950 quadros do vídeo 21 (`frames -> ../ep21/frames`), 3D nativo 1080x1920, sem novo render. Títulos (`mograph.py`), legenda e capa refeitos em inglês.
- **Voz:** Spuds Oxley, ElevenLabs `eleven_v3`, `language_code en` (IA), 5 falas (`narracao/121_vozes/falas.tsv`). Velocidade não alterada: cada frase foi cortada do take nas pausas e colocada no instante em que a frase em português começava (`montar.py`, tempos e atrasos em `121_linhas.json`).
- **Sincronia (medida):** como a cena foi feita para a fala em português, as palavras de ação caem perto, mas não no mesmo quadro. Nas frases "dies", "standing" e "points" alinhei a palavra de ação; depois disso, diferenças (inglês − português): dies 0,0 s, standing +0,06, points +0,52, raises +0,2, lock +0,9, house +0,5, alone −0,6, o resto dentro de ±0,5 s.
- **Take refeito:** o 1º take do E1 dizia "He looked" (o Whisper ouviu assim duas vezes); o take novo diz "You looked". O antigo está em `takes/E1_t1.mp3`.
- **Whisper:** `scripts/transcribe.py` ganhou `WHISPER_LANG` (padrão `pt`, os outros vídeos não mudam); com `pt` fixo ele traduzia o inglês.
- **Som:** efeitos, trilha e tensão iguais aos do 21 (são da cena, não da fala).
- **QC:** 15/15; −14,3 LUFS, pico −1,8 dBTP, correlação da narração 0,939; emenda do loop 1,8/255.
- **Capa:** quadro de 14,0 s, "2 AM… HE HAS YOUR KEY" (`thumbnails/121_the_key_ep1_cover.jpg`).
