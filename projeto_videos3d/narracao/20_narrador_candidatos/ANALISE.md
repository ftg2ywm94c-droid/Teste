# Narrador do próximo vídeo: voz de idoso, rouca e de suspense (análise de 26/11/2026)

- **Busca:** biblioteca de vozes da ElevenLabs, só vozes masculinas em pt-BR, com os termos old, grave, rouco, suspense, terror, mistério e narrador. Foram 57 candidatas (`cands.txt`). Ficaram as 8 marcadas como "old", ou descritas como gravelly ou hoarse.
- **Material:** as amostras gratuitas de cada voz (`prev_*.mp3`). Nenhum crédito foi gasto.
- **Medição** com Praat (parselmouth):
  - F0 mediana: quanto mais baixa, mais grave a voz;
  - jitter e shimmer: quanto mais altos, mais irregular, ou "rouca";
  - HNR: quanto mais baixo, mais ar e aspereza.

| Voz | Rótulo e descrição da biblioteca | Clonagens | F0 | Jitter | Shimmer | HNR |
|---|---|---|---|---|---|---|
| Papai Noel | old, "60 anos, um pouco de rouquidão" | 21.175 | 95 Hz | 3,75% | 13,5% | 8,6 dB |
| Sergio (Deep, Resonant) | old, "sênior, grave, sério; documentários" | 34.516 | 108 Hz | 2,76% | 10,4% | 10,7 dB |
| Jaan | old, "grave, sério, homem mais velho" | 869 | 102 Hz | 2,28% | 8,8% | 10,7 dB |
| Moutella | old, "maduro, médio-grave" | 5.405 | 123 Hz | 3,01% | 9,8% | 9,9 dB |
| Manoel Lopes | old, "idoso, caloroso" | 3.213 | 187 Hz | 2,68% | 8,0% | 14,7 dB |
| Jairo Moraes | old, "60 anos, interior de SP" | 1.541 | 152 Hz | 4,14% | 16,2% | 6,9 dB |
| Eliel (Deep, Gravelly) | middle_aged, "grave e áspera; épico" | 81.024 | 68 Hz | 3,86% | 9,6% | 7,0 dB |
| David (Deep, Gravelly) | middle_aged, "grave e áspera; trailers" | 120.992 | 68 Hz | 3,22% | 10,1% | 8,7 dB |

**Cuidados:**
- Cada amostra tem um texto e uma gravação diferentes, então os números servem para comparar por alto, não como prova.
- A amostra do Jairo tem só 1,9 s e não dá para confiar nela.
- O Manoel Lopes é idoso, mas tem a voz limpa (HNR 14,7), não rouca.

**Para testar** (a mesma frase de suspense, ~200 caracteres cada, ~800 no total):
1. Papai Noel: a única voz marcada como idosa e rouca, e as medidas confirmam. O nome é de personagem, e na fala de suspense isso precisa ser conferido.
2. Sergio: idoso, grave e a mais usada entre as idosas.
3. Jaan: idoso e grave.
4. Eliel: a mais áspera e grave, mas marcada como meia-idade.

A conta tem 7 das 10 vagas de voz ocupadas. Para testar as 4, é preciso liberar uma vaga, por exemplo tirando a Fabi ou a Elena Vinter, que foram reprovadas como narradoras do vídeo 19. Isso depende de autorização do usuário.

## Decisão (26/11/2026)
- **O usuário escolheu o Eliel** (`y3X5crcIDtFawPx7bcNq`), ouvindo as amostras. A voz foi adicionada à conta como "Eliel - Narrador", e agora são 8 de 10 vagas. Não foi preciso tirar nenhuma voz.
- **Teste em pt-BR** (`teste_Eliel_suspense.mp3`):
  - frase de suspense de 25 palavras, gerada com eleven_multilingual_v2, stability 0,4, similarity 0,8 e style 0,35;
  - o Whisper medium transcreveu exatamente o texto pedido;
  - duração 9,27 s, ou 2,7 palavras/s. A meta das referências é ~3/s, e o ritmo vai ser ajustado pelo texto do roteiro, sem mudar a velocidade do áudio.
