# Narração para gravar na ElevenLabs

O vídeo tem **10,0 s** e já está pronto (imagem, efeitos, música e estilo da legenda).
Só falta a voz. Grave **um único arquivo** com as três frases abaixo, nesta ordem.

## Texto para colar

```
Todo dia, o Téo faz o mesmo caminho. Mas hoje… <break time="0.8s" />
um carro vinha rápido demais. <break time="0.8s" />
Ufa!
```

As tags `<break>` deixam um silêncio entre as frases: é por esse silêncio que o script
separa as frases e encaixa cada uma no seu plano. Se o modelo que você usar não aceitar a tag,
apague-a e deixe cada frase numa linha; o que importa é ter uma pausa audível (≥ 0,5 s) entre elas.

## Onde cada frase entra e quanto tempo pode durar

| Frase | Entra em | Cabe até | Duração máxima |
|---|---|---|---|
| "Todo dia, o Téo faz o mesmo caminho. Mas hoje…" | 0,30 s (plano S1, Téo andando) | ~4,9 s | **≈ 4,6 s** |
| "um carro vinha rápido demais." | 5,15 s (plano S2, carro chegando) | ~8,4 s | **≈ 3,2 s** |
| "Ufa!" | 8,60 s (plano S3, logo depois que o carro para) | 10,0 s | **≈ 1,2 s** |

Se uma frase passar do limite, a próxima é empurrada para depois. Se a narração inteira
passar do fim do vídeo, o vídeo é desacelerado na mesma proporção (até 1,30x, com interpolação de
quadros). Acima disso o script para e avisa. Ritmo de narrador de Shorts (rápido, contínuo) cabe com folga.

## Exportação

- MP3 (44,1 kHz, 128 kbps ou mais) ou WAV. Qualquer um serve.
- Sem música nem efeitos: só a voz. A trilha já está no vídeo e abaixa sozinha quando a voz entra.
- Não precisa normalizar volume; o script ajusta tudo para −14 LUFS, igual às referências.

## Depois de gravar

Mande o arquivo aqui. Vou rodar:

```
python3 scripts/add_narration.py narracao/narracao.mp3
```

Saída: `output/final_1080x1920.mp4` (H.264 + AAC 48 kHz, 9:16), mais
`output/captions_final.ass` (legenda com os tempos da sua voz) e `output/narration_sync.json`
(onde cada frase e cada palavra caiu).
