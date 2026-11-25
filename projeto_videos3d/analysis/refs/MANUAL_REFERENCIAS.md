# Manual técnico: 4 Shorts de suspense com escolha (análise de 25/11/2026)

Manual para quem vai produzir (pessoa ou IA). O objetivo é reconstruir **como** os vídeos foram feitos e **por que** prendem, para fazer vídeos **originais** com os mesmos princípios. Não é para copiar cenas, falas ou personagens.

**Como ler as marcações:**
- **[medido]** é um número tirado do arquivo com ffmpeg, Whisper ou Python. Os dados brutos estão em `data/`.
- **[visto]** é o que aparece nos quadros (amostra de 1 quadro por segundo em `sheets/`, mais trechos a 10 quadros por segundo).
- **[hipótese]** é uma inferência que não dá para confirmar só pelo arquivo.

**Limites da amostragem:**
- Os quadros foram vistos a 1 por segundo. Só os trechos de 20–25 s (Porteiros) e 21–25 s (Nome) foram vistos a 10 por segundo.
- Entre quadros não vistos, movimentos de câmera não são afirmados. O "movimento" abaixo é a diferença média de brilho entre quadros a 10 por segundo, uma medida de quanto a imagem muda, e não a direção do movimento.

## 0. Os 4 vídeos

| Código | Vídeo | Canal | Duração | Views | Curtidas | Comentários | Comentários/view |
|---|---|---|---|---|---|---|---|
| **RTR** | "DIA 1: o céu ficou verde e a cidade inteira apagou... você abriria a porta? 🌌🚪😱 #shorts" (XyJVQ90bAbY) | historias de rtr | 90,7 s | 68.011 | 1.481 | 98 | 0,14% |
| **POR** | "Tinha DOIS porteiros no prédio… e só um é de verdade 😨 Parte 4" (R-CFbMRWssQ) | Souzeira | 76,1 s | 473.133 | 11.369 | 2.780 | **0,59%** |
| **3D** | "Eu não abri os olhos... e de manhã tinha pegadas em volta da casa (Parte 4) #shorts" (51jaNk5C40k) | Como Isso Funciona 3D ? | 72,3 s | 21.171 | 1.463 | 98 | 0,46% |
| **NOM** | "Perguntei o NOME dela… e a cara dela não parou de trocar 😨 Temporada 2 · Parte 2" (bxi_s0a5bf4) | Souzeira | 58,2 s | 123.566 | 2.896 | 458 | 0,37% |

- **Fonte:** vidIQ `get_videos_by_ids` em 25/11/2026.
- **Curtidas por view:** 3D 6,9%, POR 2,4%, NOM 2,3%, RTR 2,2%.
- **Arquivos:** todos em 1080x1920, 30 fps, H.264, AAC 44,1 kHz estéreo, ~1,7–2,0 Mb/s [medido].

---

## 1. Diagnóstico geral

1. **Nenhum deles tem gráfico caro.**
   - RTR e Souzeira são 2D vetorial simples.
   - O 3D é low-poly com bonecos de cabeça grande.
   - **A qualidade que segura a audiência está no roteiro, na edição e no texto na tela, não na renderização.**
2. **A voz começa no quadro 0 nos quatro** [medido: 1ª palavra em 0,00 s].
   - Não tem logo, vinheta nem silêncio no início.
   - A 1ª frase já é a situação: "Imagina que você acorda às 3 da manhã…", "Vocês escolheram correr.", "Você não abriu os olhos…", "Escuro total."
3. **A fala é mais rápida que a nossa.**
   - Eles: 2,7 a 3,6 palavras/s [medido].
   - Nós: vídeo 18 ≈ 2,5 palavras/s (160 palavras em 64 s), vídeo 16 ≈ 2,2.
4. **O fundo sonoro nunca some.**
   - Nenhum trecho de ≥0,35 s abaixo de −35 dB nos quatro [medido, `silencedetect`].
   - Sempre tem cama de música ou ambiente.
5. **Todos fecham com A/B (ou 1/2) dentro da história** e dizem o que o voto decide ("decide a parte 5", "vira a parte cinco", "amanhã é o dia 2").
6. **A série é explícita no título e na tela** ("DIA 1", "Parte 4", "Temporada 2 · Parte 2"). A Parte 4 abre lembrando o que o público escolheu.
7. **O melhor do grupo (POR, 473 mil, 0,59% de comentários) é o mais denso:**
   - legenda frase a frase;
   - palavra-chave no topo;
   - onomatopeias desenhadas ("TUM", "TOC");
   - fundo alto;
   - quase sem pausa (12 pausas ≥0,35 s em 75 s).

---

## 2. Identidade visual de cada um

### RTR (historias de rtr): 2D vetorial "palitinho"
- **Técnica [visto]:**
  - 2D chapado, sem contorno grosso.
  - Personagens são bonecos de palito brancos com cabeça redonda e rosto de 2–3 traços.
  - Cenários em formas geométricas: prédios em retângulos com janelas acesas, porta com número "303", sofá, relógio, quadro.
- **Paleta [visto]:**
  - azul-marinho e verde-petróleo escuros (noite);
  - acento verde da aurora;
  - vermelho só no celular de alerta e no "REGRA #";
  - amarelo-laranja da vela e da luz por baixo da porta.
  - Brilho médio 42/255 [medido], o mais escuro dos quatro.
- **HUD fixo no canto superior esquerdo [visto], o diferencial do vídeo:**
  - "● DIA 1";
  - relógio grande que avança com a história (03:12 → 03:14 → 06:40 → 09:20 → 15:10 → 18:06 → 19:30 → 22:00 → 22:01 → 23:58 → 23:59);
  - linha "SEM ENERGIA · BATERIA 94% → 81% → 80% → 78% → 52% → 41% → 37% → 19% → 8% → 7%".
  - **É uma barra de progresso disfarçada: o público vê o tempo e a bateria acabando.**
- **Cartão de regra [visto]:** etiqueta vermelha "REGRA #1…#4" e, embaixo, um título grande em fonte condensada branca ("ENCHA TUDO DE ÁGUA"), fixo durante a regra.
- **Câmera [visto]:** planos fixos e frontais, como palco de teatro. Há mudança de enquadramento entre quadros num mesmo cenário, por exemplo na mão com o celular aos 4–8 s e no corredor aos 51–55 s, com a lanterna se aproximando.

### POR e NOM (Souzeira): 2D ilustrado "de livro", série "Regras da madrugada"
- **Técnica [visto]:**
  - 2D com contorno preto grosso.
  - Personagens de rosto quadrado ou redondo, olhos grandes com brilho e lágrima azul.
  - Textura de papel ou grão por cima de tudo.
  - Vinheta forte nas bordas, colorida pelo clima: vermelho no perigo e no grito, verde na escada, azul no elevador, sépia na portaria.
- **Paleta [visto]:** dessaturada e escura (brilho médio 52–57 [medido]). Uma cor de destaque por cena: o elevador azul-claro, a porta vermelha da escada, a lâmpada âmbar.
- **Camada de texto, a mais rica dos quatro [visto]:**
  1. **Legenda frase a frase** em fonte condensada caixa-alta branca, a ~75% da altura. A palavra importante fica em vermelho ("ELEVADOR", "CORTINA", "PASSOS", "VIDRO", "DORMINDO", "ACORDA").
  2. **Palavra-chave no topo** com sublinhado amarelo ou vermelho: "A CORRENTE", "O SEU ANDAR", "PORTA ABERTA", "UNIFORME DO HOSPITAL", "IGUALZINHO", "TÉRREO", "A CHAVE", "OUTRO SEU VALDIR", "COMENTA AÍ". É um resumo do plano para quem está sem som.
  3. **Onomatopeias desenhadas no cenário**: "TUM" na escada, "TOC TOC" no vidro, "AAAAAAH" e "TATÁ!" em vermelho.
  4. **Marcações gráficas**: círculo amarelo na corrente da porta e no coque da mulher, um ✓ verde em "ESCADA" e um X vermelho em "ELEVADOR", crachá "OLÁ MEU NOME É LUCAS" riscado com o carimbo "NOME FALSO", fichas de rosto com o carimbo "EMPRESTADA", bilhete "REGRAS · TEMPORADA 2".
  5. **HUD**: relógio vermelho no topo esquerdo (02:21 → 02:23 em POR; "??:??" piscando em NOM, mais "PÔR DO SOL 18:12").
- **Câmera [visto e medido]:**
  - Planos curtos.
  - **Em POR, entre 20 e 36 s, a detecção de cena acusou cortes a cada ~0,3 s.** A 10 quadros por segundo dá para ver que não é corte: é a **luz piscando** no corredor e no elevador, com um zoom lento. Não conte isso como corte.
  - **Em NOM, entre 21,2 e 25,2 s, existe sim uma montagem de verdade**: os rostos trocam a cada 2–3 quadros (0,07–0,1 s) com fundo vermelho, cobrindo "ela grita com todas as vozes ao mesmo tempo, AAAAAH".
  - Linhas de velocidade brancas aparecem em algumas trocas (≈9 s e ≈36 s de POR) [visto]. **[hipótese]** transição de deslize ou chicote.

### 3D (Como Isso Funciona 3D ?): 3D low-poly
- **Técnica [visto]:**
  - 3D com sombreado suave e sombras projetadas.
  - Bonecos de cabeça enorme e olhos 2D desenhados por cima (traço preto, gota de suor azul).
  - Cenários simples: quarto com cama roxa, janela de madeira, casa caiada com telhado de telha, chão de terra, pinheiros low-poly, galo, neblina no fim.
  - **[hipótese]** Blender com Eevee ou um motor tipo Unity, pela luz suave e pelo raio de sol volumétrico na janela aos 28–30 s.
- **Paleta [visto]:**
  - O mais claro dos quatro (brilho médio 121 [medido]).
  - Noite azul-arroxeada no quarto, depois dia ensolarado com verde e céu azul, depois neblina branca.
  - **O contraste noite → dia é a virada da história** (o galo canta aos 17–19 s).
- **Câmera [visto]:**
  - Muitos planos de "ponto de vista": o cobertor em cima da câmera, os olhos fechados do protagonista e da mãe em close extremo.
  - Planos de detalhe: o pé da cama, o cobertor sendo puxado, a janela com marcas de unha circuladas em vermelho, as pegadas no chão.
- **Texto [visto]:**
  - Legenda **uma palavra por vez**, no centro (~65% da altura), branca com contorno.
  - Cabeçalho fixo nos 5 s iniciais: "PARTE 4: VOCÊ **NÃO ABRIU** OS OLHOS… MAS **ELE VOLTOU**", em amarelo e vermelho.
  - Pequenas "bolhas" no topo: "ELA REZA BAIXINHO…", "COCORICÓÓÓ!", "TUM… TUM… TUM…", "PODE ABRIR", "● DONA CIDA", "QUEM É?".
  - No fim: dois botões grandes, verde "1 IR ATÉ ELE" e vermelho "2 ENTRAR E TRANCAR", e um cartão de perfil "@ComoIssoFunciona3D + Seguir" que vira "Seguindo ✓".

---

## 3. Edição: números [medido]

| | RTR | POR | 3D | NOM | **Nosso vídeo 18** |
|---|---|---|---|---|---|
| Planos detectados | 14 | 50* | 19 | 36 | 21 |
| Duração média do plano | 6,5 s | 1,5 s* | 3,8 s | 1,6 s | 3,1 s |
| Duração mediana | 6,3 s | 0,8 s* | 3,6 s | 1,5 s | n/d |
| Plano mais longo | 10,2 s | 5,4 s | 11,0 s | 7,1 s | n/d |
| Movimento mediano (0–255 por 0,1 s) | 1,49 | 1,49 | 1,67 | 1,90 | 1,75 |
| Fração quase parada | 23% | 29% | 13% | 17% | 11% |
| Brilho médio (0–255) | 42 | 52 | 121 | 57 | 54 |
| Palavras/segundo | 2,66 | 2,93 | 3,16 | 3,55 | ≈2,5 |
| Pausas ≥0,35 s | 34 | 12 | 18 | 5 | n/d |

\* POR inclui o pisca-pisca de luz de 20–36 s contado como corte. Os cortes reais são menos, ~20 **[estimativa pela folha de quadros]**.

**Leitura:**
- Não existe um "ritmo certo" único: RTR troca de plano a cada 6,5 s e NOM a cada 1,6 s.
- O que os quatro têm em comum é que **algo muda na tela a cada 1–2 s**: legenda nova, palavra-chave, onomatopeia, relógio, bateria, círculo, luz piscando.
- **O nosso vídeo 18 já se mexe tanto quanto eles**: movimento 1,75 e só 11% parado. **Onde ficamos atrás é na camada de texto e na velocidade da fala.**

---

## 4. Linha do tempo de cada vídeo

Os tempos vêm do Whisper (por palavra) e do quadro a quadro.

### RTR: "DIA 1" (90,7 s), estrutura de "regras de sobrevivência" com relógio

| Tempo | Fala (resumo fiel) | Imagem [visto] | Função |
|---|---|---|---|
| 0,0–6,4 | "Imagina que você acorda às 3 da manhã e o céu da sua cidade está verde, seu celular vibra uma última vez." | Boneco na janela, céu verde, cidade; HUD 03:12, bateria 94% | Gancho: premissa estranha + "você" |
| 4–9 | "Alerta extremo. Tempestade solar." | Mãos segurando celular com alerta vermelho | Prova visual da ameaça |
| 9–13,6 | "quarteirão por quarteirão, a cidade inteira apaga" | Cidade com janelas apagando; HUD "SEM ENERGIA" | Escala |
| 13,5–18,2 | "De manhã, nenhuma luz, nenhum sinal, nenhuma notícia." | Sala com relógio 06:40, porta 303 | Tríade de perdas |
| 18,0–24,3 | "Regra 1, encha tudo de água… a caixa d'água seca hoje." | Cartão REGRA #1 + banheira enchendo, galões | 1ª regra |
| 24,3–32 | "Regra 2, não vá ao mercado. Às 9 todo mundo teve a mesma ideia. Às 10 estão brigando por água." | Fachada de supermercado, multidão de palitos | Consequência social |
| 32–39,3 | "o vizinho pergunta se você tem água. Você mente. Regra 3, não conte pra ninguém" | Duas portas 303/304, vizinho com garrafa | Dilema moral plantado |
| 39,1–44,4 | "Às 6 o sol se põe… você vê estrelas em cima da cidade." | Pôr do sol → céu estrelado | **Respiro visual** (único momento bonito) |
| 44,6–50,6 | "Regra 4, esconda qualquer luz. Uma vela na janela é um anúncio. Aqui tem comida." | Sala com vela, cortina vermelha | Regra que vira perigo |
| 50,6–60,6 | "Às 10, alguém testa as maçanetas do corredor. Uma por uma. Cada vez mais perto, a maçaneta da sua porta gira, devagar e para." | Corredor escuro com lanterna avançando; close da maçaneta girando | **Escalada de proximidade** |
| 60,7–69,3 | "Faltando dois minutos pra meia-noite, batem. Por favor, sou a vizinha do 302. Meu filho tá com febre. Eu só preciso de água." | HUD 23:58; vizinha de vestido em frente à porta, luz por baixo | Dilema humano |
| 69,4–75,9 | "Você não responde. Então ela sussurra: eu sei que você tá aí. Eu vi a luz por baixo da sua porta." | Close da porta / vizinha | Quebra a regra 4: você foi visto |
| 76,0–81,8 | "Pelo olho mágico, ela está sozinha. Mas no fim do corredor, uma lanterna se apaga." | Visão do olho mágico (círculo com distorção) | **Reviravolta final** |
| 82,3–88,8 | "E aí? Você abre ou deixa uma criança com febre lá fora? Comenta. Amanhã é o dia 2." | Cartão "VOCÊ ABRE A PORTA?" + botões "ABRIR" / "MANTER FECHADA" + "COMENTE ABAIXO ↓ · AMANHÃ: DIA 2 →" | CTA |
| 89–90,7 | n/d | Cartão "DIA 1 · O CÉU FICOU VERDE…" sobre o 1º cenário | **Fecho que volta ao começo**: o loop reinicia no mesmo cenário |

### POR: "Parte 4" (76,1 s), fuga em sequência de obstáculos

| Tempo | Fala | Imagem [visto] | Função |
|---|---|---|---|
| 0,0–1,2 | "Vocês escolheram correr." | "PARTE 4" + pílulas "A · CORTINA" / "B · CORRE" | Recompensa a quem votou |
| 1,5–7,7 | "abre a porta do banheiro, pega o Davi pela mão… as argolas da cortina começam a correr" | Mão abrindo a porta, mão do irmão | Ação imediata |
| 8,7–15 | "Devagar. Corredor. Sala. A porta da frente. A corrente ainda tá passada. Você tira a corrente com a mão tremendo." | Planos de 1 palavra cada; círculo amarelo na corrente | **Montagem de palavras soltas**, muito rápida |
| 15,4–20,1 | "a sua mãe, no telefone, fala uma coisa só. Escada. Nunca o elevador." | Mãe com celular, monitor cardíaco; ✓ ESCADA / ✗ ELEVADOR | Regra recebida |
| 20,4–31 | "o elevador já tá parado no seu andar, com a porta aberta… uma mulher com uniforme do hospital… o cabelo preso igualzinho ao da sua mãe" | Corredor e elevador com luz piscando; mulher de costas; círculo no coque | Tentação: "é a mãe?" |
| 30,9–35,4 | (sem fala, 4,5 s) | Ondas "LUCAS?"/"VEM COM A MAMÃE" + cartão "REGRA Nº1: OLÁ MEU NOME É LUCAS → NOME FALSO" | **Única pausa longa**: imagem e texto contam sozinhos |
| 35,4–45,5 | "pela escada. Um andar. Dois. Aí você escuta passos lá em cima… no mesmo ritmo. Você para. Os passos param. Um segundo depois." | Escada verde com "TUM" e uma criatura escura no andar de cima; rosto suado | Medo pelo som |
| 47–53,9 | "Térreo. A portaria tá apagada. A porta de vidro tá trancada… o seu Valdir, o porteiro, batendo no vidro." | Portaria âmbar; "TRANCADA"; porteiro; "TOC TOC" | Salvação aparente |
| 54,8–58,4 | "Abre aí, menino! Vem! Rápido! Eu tenho a chave!" | Porteiro com ondas sonoras saindo | **Única fala de outro personagem** [hipótese: outra voz] |
| 58,8–66,7 | "o Davi puxa a sua mão e aponta pra cabine… tem outro seu Valdir. Dormindo na cadeira. Com a chave pendurada no cinto." | Davi apontando; "OUTRO SEU VALDIR"; porteiro dormindo "zzz"; círculo na chave | **Reviravolta** (título "só um é de verdade") |
| 67,3–74,8 | "Comenta aí. A: acorda o seu Valdir da cabine. B: quebra o vidro e corre pra rua. O mais comentado decide a parte 5." | Tela dividida com os dois Valdir, pílulas A/B, "PARTE 5 · QUAL É O DE VERDADE?" | CTA |
| 75,0–76,1 | n/d | "PARTE 4" + pílulas A·CORTINA/B·CORRE, igual ao quadro 0 | **Loop perfeito**: o último quadro é o primeiro |

### 3D: "Parte 4" (72,3 s), noite de medo → manhã com pistas

| Tempo | Fala | Imagem [visto] | Função |
|---|---|---|---|
| 0–4,5 | "Você não abriu os olhos, apertou ainda mais forte e segurou a mão da sua mãe." | Cobertor por cima, dois rostos de olho fechado; cabeçalho "PARTE 4…" | Recapitula a escolha |
| 5–13,3 | "a voz para de sussurrar e fica brava. Alguma coisa começa a puxar o cobertor, devagar, pelo pé da cama." | Quarto escuro, cama vista do lado, cobertor sendo puxado | Ameaça física |
| 13,8–17 | "Sua mãe segura o cobertor com força e começa a rezar baixinho." | Rostos (mãe de olho aberto); bolha "ELA REZA BAIXINHO…" | |
| 17,3–21,2 | "lá longe, um galo canta e o puxão para na hora." | Galo ao amanhecer; bolha "COCORICÓÓÓ!" | **Virada noite → dia** |
| 21,5–31,7 | "O peso some… você só escuta o seu coração batendo… a luz do sol entra pela fresta… Pode abrir." | Cama vazia; close dos rostos ("TUM… TUM… TUM…"); raio de sol na janela | Alívio falso |
| 32–36,9 | "Você abre os olhos. O quarto está vazio. E a porta da frente está escancarada." | Personagem de camisa vermelha, olhos arregalados, ao lado da cama [visto]. Pela fala é "você" acordando [hipótese]; porta aberta | Inquietação |
| 37–44,9 | "No chão de terra, tem pegadas… dão a volta na casa inteira e terminam embaixo da janela do quarto" | Plano aéreo da casa com as pegadas; janela com arranhões circulados | **Prova física** |
| 45–54,3 | "a dona Cida, a vizinha, aparece… pálida… O seu pai voltou ontem à noite. Ele bateu na minha porta também." | Vizinha 3D chegando; rótulo "● DONA CIDA"; bolha com a fala | Nova informação que muda tudo |
| 54,7–60,9 | "Ela aponta para a estrada… parado no meio da neblina, tem um homem de chapéu, olhando para a sua casa." | Silhueta de chapéu na neblina branca; bolha "QUEM É?" | Imagem final de medo |
| 61,3–71,1 | "comenta 1 se você vai até ele ou 2 se você entra e tranca a porta. A mais comentada vira a parte cinco. Segue o Como Isso Funciona 3D…" | Botões 1/2 + cartão "Seguir → Seguindo ✓" | CTA de voto + inscrição |

### NOM: "Temporada 2 · Parte 2" (58,2 s), a mais curta e violenta

| Tempo | Fala | Imagem [visto] | Função |
|---|---|---|---|
| 0–6,2 | "Escuro total. A voz do seu irmão vem do teto, pedindo o seu nome, e você devolve a pergunta. E qual é o seu nome?" | Criatura de cabeça para baixo no teto, olhos brancos; "TEMPORADA 2 · PARTE 2"; pílula "B · PERGUNTAR O NOME DELA ✓" | Recapitulação + diálogo |
| 6,4–11,4 | "Silêncio. A coisa desce do teto devagar… pela primeira vez, o sorriso some." | "?" vermelho no preto; criatura descendo; close do sorriso; carimbo "O SORRISO SUMIU" | |
| 11,5–21,1 | "A cara dela começa a trocar… do Davi, da sua mãe, do seu Jair, do seu Valdir, do frentista. Rápido, cada vez mais rápido… Cada cara que ela usa é emprestada." | Rostos de personagens de episódios anteriores com rótulo; fichas com carimbo "EMPRESTADA" | Usa o elenco da série (fã reconhece) |
| 21,2–25,2 | "Ela grita, com todas as vozes ao mesmo tempo. AAAAAH!" | **Montagem de 2–3 quadros por rosto** em vermelho | Pico de choque |
| 25,3–29,9 | "se arrasta pro escuro… Regra número 2: se ela pedir o seu nome, pergunte o dela." | Bilhete "REGRAS · TEMPORADA 2" com a regra circulada | Regra explícita |
| 30,1–36,3 | "puxa a outra mão com tudo, o fio corta a pele, solta. Você corre… gira a maçaneta, abre." | Mãos amarradas com sangue; corrida | Fuga (conteúdo gráfico) |
| 36,5–48,4 | "o Davi, o de verdade, amarrado numa cadeira… a sua mãe, de jaleco, segurando o dino pelo rabo, sorrindo." | Casa de máquinas; Davi amarrado chorando; dino no chão ("TATÁ!"); "mãe" sorrindo | Reviravolta |
| 48,7–50,8 | "Pergunte o meu nome também, Lucas." | Rosto da "mãe" em close, olhos verdes, fundo vermelho | Fala da vilã |
| 51,2–58,0 | "Comenta aí. A: você pergunta o nome dela também. B: pega o Davi e corre… O mais comentado decide a parte 3." | Tela dividida mãe/Davi + pílulas | CTA |

---

## 5. Áudio [medido, salvo onde indicado]

| | RTR | POR | 3D | NOM | Nosso vídeo 18 |
|---|---|---|---|---|---|
| Loudness integrado | −19,6 LUFS | −13,4 | −14,5 | −14,0 | −14,4 |
| Faixa de loudness (LRA) | 2,0 LU | 3,9 | 4,0 | 4,5 | n/d |
| Voz (RMS durante a fala) | −18,3 dB | −12,7 | −14,1 | −13,4 | n/d |
| Fundo nas pausas | −23,2 dB | −15,3 | −21,8 | −16,9 | n/d |
| Voz acima do fundo | ~5 dB | **~2,6 dB** | ~7,7 dB | ~3,5 dB | n/d |
| Trechos sem som (−35 dB, ≥0,35 s) | 0 | 0 | 0 | 0 | n/d |

**Leitura:**
- **O fundo das Souzeira é quase tão alto quanto a voz** (2,6–3,5 dB de diferença) e mesmo assim a fala é clara. **[hipótese]** A voz é muito comprimida e "na cara", e o fundo é de frequências graves e médias que não disputam com a voz. Isso dá a sensação de "assiste de fone 🎧", que a própria descrição pede.
- **A RTR está baixa (−19,6 LUFS).** O YouTube não aumenta vídeos baixos, então ela soa mais fraca que as outras no feed. **Erro dela; não repetir.**
- **Pausas dramáticas:**
  - POR tem uma pausa grande de 4,5 s (30,9–35,4) sobre o cartão "NOME FALSO", e o resto é contínuo.
  - RTR é a mais pausada (34 pausas): fala em frases curtas com respiro.
  - NOM quase não para (5 pausas): ritmo de urgência.
- **Efeitos sonoros:**
  - Não dá para isolar por medição com segurança.
  - **[visto]** Os textos "TUM", "TOC TOC", "COCORICÓÓÓ!", "AAAAAAH", "TATÁ!" e "zzz" aparecem na tela exatamente na palavra falada, e o relógio muda exatamente na frase de hora.
  - **[hipótese]** Cada onomatopeia tem um efeito sonoro junto.
  - Picos de volume em POR [medido] em 3,7, 9,4, 19,1, 22,1, 27,2, 37,7, 40,6, 42,0, 51,8, 59,3, 62,8, 64,0 e 72,0 s, que batem com: argolas da cortina, troca de cena, "ESCADA ✓", luz piscando, passos "TUM", "TOC TOC" e a troca para o CTA.
  - Em NOM, picos em 5,8, 18,9 e 48,8–49,8 s ("E qual é o seu nome?", o carimbo "EMPRESTADA" e a fala da vilã).
- **Vozes:**
  - RTR, 3D e NOM usam uma voz principal de narrador.
  - POR e NOM têm falas de outros personagens (porteiro, vilã). **[hipótese]** Pode ser a mesma voz com outra interpretação ou uma voz diferente: o arquivo não prova qual.
  - Não afirmo se as vozes são humanas ou de IA.

---

## 6. Engenharia de retenção (o que cada recurso faz)

1. **Fala no quadro 0, sem respiro.** Quem rola o feed decide em menos de 1 s. Os quatro já estão no meio da ação.
2. **"Você" como protagonista** (todos) e **recapitulação da escolha** ("Vocês escolheram correr", pílula "B ✓"). Quem votou volta para ver a consequência; quem não votou entende tudo em 1 frase.
3. **Medidor de progresso na tela**: relógio e bateria (RTR), relógio vermelho (Souzeira). O cérebro quer ver o "fim do contador". É o principal recurso de retenção da RTR.
4. **Estrutura em degraus**:
   - RTR: regra 1 → 2 → 3 → 4, cada uma com cartão próprio.
   - POR: banheiro → sala → corredor → elevador → escada → térreo.
   - Cada degrau é uma "mini-meta" de 5–10 s, então sempre tem um próximo passo à vista.
5. **Escalada de proximidade**: "uma por uma… cada vez mais perto… a maçaneta da sua porta gira" (RTR), "passos descendo junto… no mesmo ritmo" (POR). O perigo chega mais perto a cada frase.
6. **Dupla impossível no fim**: dois Valdir, a mãe falsa e a verdadeira, a vizinha sozinha e uma lanterna apagando. **A reviravolta acontece 5–10 s antes do CTA**, então o público chega ao CTA com uma dúvida real para votar.
7. **Texto para quem está sem som**: palavra-chave no topo (Souzeira) e bolhas (3D). Mantém quem assiste mudo e reforça a memória.
8. **Escolha com consequência anunciada**: "o mais comentado decide a parte 5" e "amanhã é o dia 2". O comentário vira poder, e não só opinião.
9. **Loop**:
   - POR termina no mesmo quadro em que começa ("PARTE 4" + pílulas).
   - RTR termina num cartão que volta ao cenário de abertura.
   - **[hipótese]** Isso aumenta as re-visualizações automáticas (o Short recomeça sem emenda visível).
10. **Elenco recorrente** (Souzeira): Davi, seu Valdir, seu Jair e o dino aparecem de novo. O fã reconhece, e a Temporada 2 reaproveita rostos antigos como reviravolta ("cada cara é emprestada").

---

## 7. Título, descrição, tags e capa [dados do vidIQ e capas baixadas]

### Títulos
| Vídeo | Padrão |
|---|---|
| RTR | "**DIA 1:** [premissa]… **você abriria a porta?** 🌌🚪😱 #shorts". Marcador de série + premissa + pergunta direta + 3 emojis |
| POR | "Tinha **DOIS** porteiros no prédio… e só um é de verdade 😨 **Parte 4**". Paradoxo + 1 palavra em CAIXA-ALTA + reticências + 1 emoji + parte |
| 3D | "**Eu** não abri os olhos... e de manhã tinha pegadas em volta da casa **(Parte 4)** #shorts". 1ª pessoa + consequência |
| NOM | "**Perguntei** o **NOME** dela… e a cara dela não parou de trocar 😨 **Temporada 2 · Parte 2**". 1ª pessoa + CAIXA-ALTA + temporada |

**A fórmula comum:** a ação do personagem + "…" + um detalhe impossível + o marcador de parte. As Souzeira usam **1 palavra em caixa-alta** e **1 emoji 😨**.

### Descrições
- **RTR (longa):**
  - repete a premissa;
  - lista as 4 regras com emoji;
  - **ancora em fato real** (a descrição cita a tempestade solar de 1989 em Quebec e o Evento Carrington de 1859);
  - pede um comentário com palavra exata ("ABRO" ou "FECHADA");
  - "SEGUE o canal pra ver o DIA 2";
  - pede compartilhamento;
  - **22 hashtags**.
- **POR (curta):** "Parte 4 das Regras da madrugada. **Assiste de fone 🎧**. Qual seu Valdir é o de verdade? Comenta A ou B 👇" + 8 hashtags, incluindo a **hashtag própria da série #regrasdamadrugada**.
- **3D:** resume a história inteira (bom para busca) + "Comenta 1… ou 2… A mais comentada vira a Parte 5!" + "Segue…" + 8 hashtags.
- **NOM:** resume a parte + A/B + 10 hashtags (#temporada2, #creepypasta, #skinwalker).

### Tags
- As Souzeira usam as **mesmas tags genéricas do canal** em todo vídeo ("souzeira, animação, curiosidades, e se, shorts animados"), e o 3D não usa nenhuma.
- **O vídeo que mais performou tem as tags menos trabalhadas.** Nos Shorts, as tags pesam pouco: título, retenção e comentários pesam mais. **[hipótese apoiada pelos dados]**

### Capas (`thumbs/`)
- **RTR e 3D têm capa feita à mão.**
  - RTR: "DIA 1 / VOCÊ ABRIRIA A PORTA?" + imagem do olho mágico + selo "#1 TEMPESTADE SOLAR".
  - 3D: o cabeçalho "PARTE 4…" + um círculo vermelho na silhueta de chapéu.
- **As Souzeira usam um quadro do próprio vídeo**: o rosto com "TUM" vermelho e "UM SEGUNDO DEPOIS", e o close "O SORRISO SOME".
- **[hipótese]** Nos Shorts a capa aparece pouco no feed, mas pesa na aba do canal e na busca. As Souzeira escolhem um quadro que já tem um texto de impacto embutido.

---

## 8. Como reproduzir (com o nosso pipeline: Three.js/Remotion + Python + FFmpeg)

1. **Roteiro (o mais importante):**
   - 200–240 palavras para 60–75 s (≈3 palavras/s).
   - Frases de 2–8 palavras, com algumas de 1 palavra ("Corredor. Sala.").
   - Estrutura em 4–6 degraus, dupla impossível 5–10 s antes do CTA, e um CTA com consequência ("decide a parte X").
   - A 1ª frase recapitula a escolha (em episódio de continuação) ou joga a premissa ("Imagina que…").
2. **Voz:**
   - A narração do usuário, sem mudar a velocidade (regra nossa). **Pedir para gravar mais rápido e com frases mais curtas**, porque a velocidade vem da leitura, não da edição.
   - Personagens com vozes próprias nos picos (porteiro, vilã), como na Noite Livre.
3. **Imagem:**
   - O nosso 3D toon já está no nível de movimento deles (medido).
   - Para ganhar o "clima" das Souzeira, adicionar no `grade.ts` ou em pós:
     - (a) grão de papel ou filme leve;
     - (b) vinheta colorida por cena (vermelho no perigo, verde ou azul na fuga);
     - (c) luz piscando nos corredores (`lampOn` com padrão irregular).
   - **Contraste de dia e noite** como virada (3D: o galo).
4. **Camada de texto** (o que mais falta em nós), num `mograph.py` padrão:
   1. legenda frase a frase, com a palavra-chave em vermelho;
   2. palavra-chave no topo com sublinhado amarelo, uma por plano;
   3. onomatopeias desenhadas na palavra exata do Whisper ("TUM", "TOC TOC");
   4. círculos e ✓/✗ sobre objetos importantes;
   5. HUD fixo com relógio ou contador da série.
   - Tudo dentro da zona segura do 9:16.
5. **Montagem:**
   - Algo novo na tela a cada 1–2 s.
   - Planos de 1,5–4 s.
   - Montagem relâmpago (2–3 quadros por imagem) só no pico de choque, no máximo uma vez por vídeo.
6. **Som:**
   - −14 LUFS e pico real de −1,5 dB (o nosso `assemble.py` já faz).
   - Fundo contínuo: nunca deixar silêncio total.
   - Efeito sonoro em cada onomatopeia da tela.
   - **Corte seco do fundo** só num momento escolhido (o "param" do vídeo 18 é o mesmo princípio).
7. **Fecho em loop:** o último segundo repete o 1º quadro (título + pílulas da parte), para o Short emendar sem costura.
8. **Pacote de postagem:**
   - título no padrão "Ação… detalhe impossível 😨 Parte N";
   - descrição com resumo, A/B com palavra exata, "Assiste de fone 🎧", hashtag própria da série e "segue pra ver a parte N+1";
   - capa feita a partir de um quadro com texto de impacto.

---

## 9. Erros e limites dos originais

- **RTR:**
  - −19,6 LUFS: soa baixo.
  - Planos longos (até 10 s) com pouco movimento (23% quase parado).
  - Só 0,14% de comentários, mesmo pedindo palavra exata.
  - O CTA tem 3 partes ("E aí? Você abre ou deixa… Comenta. Amanhã é o dia 2."), longo para o fim.
- **POR:** o fundo quase no nível da voz cansa em celular sem fone **[hipótese]**. O texto na tela é muito denso: às vezes há 3 camadas ao mesmo tempo (topo, onomatopeia e legenda).
- **NOM:** conteúdo gráfico (mãos amarradas sangrando, criança amarrada chorando). Funciona para eles, mas arrisca restrição de idade e de monetização. **Para nós: não usar.**
- **3D:**
  - Legenda de uma palavra por vez é difícil de ler em 3,2 palavras/s.
  - CTA final com "segue o canal" falado gasta 2,4 s.
  - Visual claro e alegre (brilho 121) briga com o medo. **[hipótese]**
- **Os quatro:** nenhum mostra a ameaça por inteiro, e só um tem voz de personagem marcante. Aí dá para superar.

## 10. Recomendações para superar

1. **Velocidade de fala de ~3 palavras/s** e 1ª frase de recapitulação ou premissa em até 3 s. É o ajuste mais barato e de maior efeito.
2. **Camada de texto completa** (item 8.4), com um padrão nosso: palavra-chave no topo e um HUD próprio da série, por exemplo relógio e "FALTAM X MIN" na Noite Livre.
3. **Fecho em loop** em todos os episódios.
4. **A reviravolta 5–10 s antes do CTA**, sempre com uma "dupla" (dois de algo, um falso).
5. **Elenco recorrente com vozes**: a Noite Livre já está montada assim. Reaproveitar a família e o Thor nas partes seguintes.
6. **Loudness −14 LUFS com voz pelo menos 5 dB acima do fundo** (o nosso QC já mede isso). Mais claro que as Souzeira e mais forte que a RTR.
7. **Hashtag própria da série** (#anoitelivre, #ultimoonibus) e "Assiste de fone 🎧" na descrição.
8. **Sem violência gráfica**, e manter "história de ficção" quando houver risco.

---

### Arquivos de apoio
- `videos/` (fora do git): os 4 MP4.
- `sheets/`: folhas com 1 quadro por segundo e os trechos a 10 quadros por segundo.
- `thumbs/`: as capas.
- `data/*_words.json`: transcrição palavra a palavra.
- `data/edicao_audio.json`: cortes, duração dos planos, movimento, brilho e picos de volume.
- `data/*_cuts*.txt` e `data/*_silence.txt`: saídas brutas do ffmpeg.
