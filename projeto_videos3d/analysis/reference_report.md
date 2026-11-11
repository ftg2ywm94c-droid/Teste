# Auditoria das referências

Gerado por `scripts/audit_references.py` (todos os frames processados em sequência) + inspeção visual das contact sheets.

## Medidas por arquivo

| | Montanha-russa | Ferrovia | Motoristas |
|---|---|---|---|
| Arquivo | 9D730C64….mov | CC2DBC44….mov | F27E1C45….mov |
| Duração (s) | 63.17 | 65.18 | 62.25 |
| Vídeo | h264 512x910 @30/1, 1895 frames | h264 512x910 @30/1, 1955 frames | h264 512x910 @30/1, 1867 frames |
| Áudio | aac 44100 Hz 2ch | aac 44100 Hz 2ch | aac 44100 Hz 2ch |
| Bitrate | 4.92 Mb/s | 4.94 Mb/s | 4.92 Mb/s |
| Cortes detectados | 11 | 15 | 22 |
| Duração de plano: média / mediana (s) | 5.3 / 4.8 | 4.1 / 3.1 | 2.7 / 2.1 |
| Frames estáticos | 0.0 % | 0.0 % | 0.5 % |
| Frames escuros (V<90) | 4.8 % | 0.1 % | 12.1 % |
| Brilho / saturação médios (0–255) | 145 / 126 | 164 / 125 | 136 / 117 |
| Fluxo óptico médio (px/frame a 128 px) | 1.36 | 2.01 | 0.85 |
| Loudness integrado | -14.0 LUFS (LRA 1.7) | -14.1 LUFS (LRA 3.2) | -14.0 LUFS (LRA 2.2) |
| Silêncios ≥0,35 s | 0 | 0 | 0 |

## Cortes (timestamps em s)

- **This-Shape-Saved-Roller-Coasters (9D730C64…mov)**: 6.9, 16.0, 21.0, 28.6, 33.3, 34.1, 35.2, 41.4, 44.3, 46.1, 46.2
- **Why-Perfect-Railroads-Don-t-Work (CC2DBC44…mov)**: 3.7, 9.2, 11.6, 13.6, 28.5, 31.2, 31.3, 36.1, 48.1, 50.7, 54.5, 59.5, 59.6, 63.1, 64.3
- **Why-Drivers-Started-Filming-The-Road (F27E1C45…mov)**: 1.2, 1.4, 3.3, 4.8, 7.0, 10.2, 10.3, 12.9, 16.1, 18.6, 18.7, 27.2, 27.8, 29.5, 32.3, 36.8, 38.8, 46.8, 50.1, 50.2, 55.3, 60.2

Keyframes de cada corte em `analysis/keyframes/`; contact sheets de 1 s em `analysis/reference_contact_sheets/`.

## Estrutura narrativa (lida por OCR das legendas queimadas + quadros)

**This-Shape-Saved-Roller-Coasters (9D730C64…mov)** — Gancho 0–3 s: ação em andamento + frase em 3ª pessoa sobre ele ter entortado o loop. Contexto (≈3–10 s): primeiro brinquedo de cabeça para baixo, rival copia. Problema (≈10–20 s, noite/interior): boneco de teste volta amassado na véspera da inauguração; ele martela a base numa curva longa. Escalada (≈20–30 s, noite): rival aperta o loop até ficar alto e fino. Inauguração (≈30–40 s, dia). Explicação (≈40–47 s): analogia com carro em curva de estrada. Demonstração e desfecho (≈47–63 s): loop circular vs. o outro, gag final com explosão. CTA: nenhum detectado.

**Why-Perfect-Railroads-Don-t-Work (CC2DBC44…mov)** — Gancho 0–3 s: ele serra folgas no trilho a cada 39 pés. Contexto (≈3–12 s): duas empresas disputam uma linha sobre o cânion. Conflito (≈12–22 s): chefe fica roxo de raiva. Revés (≈22–37 s): concorrente termina primeiro, trens silenciosos; jornal zomba do 'clickety-clack'. Virada (≈37–48 s): no verão as folgas encolhem (dilatação), close no trilho com cores de calor. Desfecho (≈48–65 s): trilhos sem folga do rival entortam ao sol; trem final na ponte. CTA: nenhum detectado.

**Why-Drivers-Started-Filming-The-Road (F27E1C45…mov)** — Gancho 0–3 s: ele freia de propósito na rodovia e o carro de trás bate. Contexto (≈3–16 s): finge dor, o seguro paga. Escalada (≈16–33 s, entardecer→noite): repete com alvos escolhidos, um comparsa fecha a lateral, compra carro melhor. Consequência (≈33–43 s): escritório com contador, vizinhança desconfia. Virada (≈43–56 s, chuva): uma motorista tem uma caixinha no painel. Desfecho (≈56–62 s): imagem da dashcam com HUD (REC, MPH). CTA: nenhum detectado.

## Diagnóstico comparativo do estilo

1. **Gancho**: os três abrem no frame 0 com ação já em curso e uma frase em 3ª pessoa do tipo "Ele fez [coisa absurda]". A explicação só começa depois ("You see…").
2. **Estrutura**: protagonista teimoso → rival/autoridade que zomba → revés → virada física ou moral → desfecho curto. Nenhum termina com CTA.
3. **Legenda**: 1–2 palavras por vez, branca, negrito arredondado, contorno preto, centralizada a ~70 % da altura (não no rodapé). Em inglês.
4. **Câmera**: 0,0–0,5 % de frames estáticos — a câmera praticamente nunca para (tracking, push-in, órbita, POV de painel/cabine, vista aérea).
5. **Ritmo**: plano mediano de 2,1 s (motoristas) a 4,8 s (montanha-russa) — limite superior, ver confiança abaixo.
6. **Personagem**: cabeça esférica branca com rosto 2D de alto contraste e contorno preto, corpo pequeno, membros de traço fino preto, uma peça de roupa/chapéu que identifica cada um. Cenário é 3D "de jogo" com materiais lisos e sombras duras do sol.
7. **Luz/cor**: céu azul saturado de dia; noite azul-roxa com pontos emissivos (12 % dos frames do vídeo de motoristas são escuros); cânion vermelho-alaranjado no ferroviário.
8. **Áudio**: −14 LUFS nos três, LRA baixo (1,7–3,2), nenhum silêncio ≥0,35 s: narração contínua sobre cama sonora.

## Confiança e lacunas

- **Alta**: formato, duração, loudness, ausência de frames parados, posição e estilo da legenda.
- **Média**: contagem de cortes. O detector usa salto de histograma; whip pans, fusões (ex.: ~10 s na montanha-russa, ~48 s na ferrovia) e cortes entre planos de cor parecida escapam. O número real de planos é maior que o detectado.
- **Média/baixa**: texto da narração — vem de OCR das legendas (ruidoso, palavras repetidas), não de transcrição do áudio. Não havia Whisper no ambiente.
- **Não medido**: separação de voz/música/SFX, timbre do narrador, BPM, identificação de efeitos sonoros. Exige escuta ou modelos que não estavam disponíveis.
- **Não inferível só pelos pixels**: qual ferramenta gerou os originais.
