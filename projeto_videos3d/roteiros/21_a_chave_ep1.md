# 21 — A Chave · Ep. 1 (suspense, a partir do piloto de qualidade)

Status: roteiro para aprovação (25/11/2026). O usuário pediu para transformar o piloto no vídeo inteiro: "Se quiser já gerar o vídeo inteiro, esse roteiro parece interessante... Pode começar."

**Base:** os 15,6 s do piloto ficam **iguais** (voz, tempos, planos, som), como gancho. O resto continua a história.

**O que o usuário pediu para este vídeo:**
- tudo do piloto: luz real, câmera que acompanha a fala, celular na mão, legenda de uma palavra, som pela cena;
- **menos cortes:** a câmera atravessa o cenário de uma cena até a outra;
- **luz do dia até a noite:** sol, nuvens fazendo sombra no chão, entardecer, noite.

Duração estimada: ~62 s, 9:16, escolha A/B no fim, loop. Ficção ("história de ficção" na tela).

## Roteiro (com cena)
| # | Fala (narrador Spuds Oxley) | Na tela e câmera | Luz |
|---|---|---|---|
| 1–5 | (os 15,6 s do piloto) Duas da manhã… E ele está segurando a sua chave. | os 5 planos do piloto | noite, poste, lanterna |
| 6 | Você perdeu essa chave hoje à tarde, na praça. | **sem corte:** do close da chave a câmera sobe acima dos telhados; o céu volta de noite para tarde (o tempo "rebobina") e a câmera desce na praça ao lado | noite → dia, sol alto |
| 7 | Procurou embaixo do banco, na grama, no meio-fio. | a câmera segue você de banco em banco, rente à grama | sol; sombra das nuvens passando pelo chão |
| 8 | E do outro lado da praça, tinha um homem parado. Olhando você procurar. | a câmera atravessa a praça e chega no homem (o mesmo da chave), parado na sombra de uma árvore | dia |
| 9 | O sol foi embora. Você desistiu, chamou o chaveiro e trocou a fechadura. | a câmera sobe a rua da praça até a sua casa enquanto o sol se põe; o chaveiro na porta | entardecer → noite |
| 10 | Então você está seguro… né? | da porta, a câmera desce a rua de volta até o poste apagado, às duas da manhã | noite |
| 11 | Só que agora ele levanta a chave. E aponta pra sua casa. | o homem levanta a chave; a câmera gira e segue o braço até a sua casa no fim da rua | noite, lanterna |
| 12 | A luz do seu quarto acende. Você mora sozinho. | a janela do seu quarto acende (luz real saindo da janela para a rua) | noite |
| 13 | Você decide. A: pega a chave da mão dele. B: corre pra casa. Comenta A ou B. A mais comentada vira a Parte 2. E se... | cartões A/B; o último segundo emenda no 1º quadro (você andando na rua) | noite |

### Narração nova (bloco único, Spuds Oxley, só a continuação)
Você perdeu essa chave hoje à tarde, na praça. Procurou embaixo do banco, na grama, no meio-fio. E do outro lado da praça, tinha um homem parado. Olhando você procurar. O sol foi embora. Você desistiu, chamou o chaveiro e trocou a fechadura. Então você está seguro… né? Só que agora ele levanta a chave. E aponta pra sua casa. A luz do seu quarto acende. Você mora sozinho. Você decide. A: pega a chave da mão dele. B: corre pra casa. Comenta A ou B. A mais comentada vira a Parte 2. E se...

**Contagem:** 95 palavras; com a Spuds (~2,1 palavras/s) dá ~45 s. Com os 15,6 s do piloto, ~61 s. Custo: 491 caracteres (`eleven_v3`, `pt`).

## Técnica nova
- **Hora do dia contínua:** os presets de luz `day`, `golden` e `night` (já existentes) passam a ser misturados quadro a quadro, para o sol se pôr dentro do mesmo plano.
- **Sombra das nuvens:** manchas suaves que andam pelo chão no sentido do vento, multiplicando a luz do sol.
- **Câmera que atravessa:** planos longos com caminho de câmera contínuo entre os cenários (rua → céu → praça → rua → casa), poucos cortes.
- **Cenário novo:** praça com bancos, grama, árvores e meio-fio, ao lado da rua do piloto; a sua casa no fim da rua, com a janela do quarto.

## Cuidados
- Ficção, sem violência: o homem só fica parado e aponta.
- Não usar a velocidade alterada; a narração nova é a mesma voz do piloto (Spuds Oxley, `eleven_v3`).

## Ideias para a Parte 2 (não decididas)
- **A:** você pega a chave, e ela está quente, como se alguém tivesse acabado de usar.
- **B:** você corre pra casa, e a fechadura nova está aberta.
