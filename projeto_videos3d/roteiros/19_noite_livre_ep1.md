# 19 — A Noite Livre · Ep. 1 (formato com elenco de vozes)

Status: produzido e entregue (25/11/2026), `v2/ep19/out/19_noite_livre_ep1_1080x1920.mp4`.
Referência de formato: `analysis/canal/2026-11-24_referencia_noite_de_crime.md`. A história é original. Não copia cenas nem falas do reel de referência e não usa o nome dos filmes.
Duração estimada: ~65 s, 9:16, escolha A/B no fim.

## Elenco e vozes
| Personagem | Voz |
|---|---|
| Narrador | **usuário** (MP3 do Davinci) |
| Apresentador da TV | Diego (IA, vidIQ) |
| Pai | Will (IA, vidIQ) |
| Mãe | Roberta (IA, vidIQ) |
| Bia, irmã mais velha (~20 anos) | Keren (IA, vidIQ) |
| Você (irmão do meio) | não fala, é quem decide |
| Thor (cachorro) | latidos |

## Roteiro (com cena)
| # | Quem | Fala | Na tela |
|---|---|---|---|
| 1 | NARRADOR | Imagina que o governo anuncia a Noite Livre. Das dez da noite às seis da manhã, nada é crime. E faltam três minutos. | Família no sofá, rostos iluminados pela TV. Texto: "FALTAM 3 MINUTOS". |
| 2 | TV | Atenção. Faltam três minutos para o início da Noite Livre. A polícia não vai atender chamados até as seis da manhã. Fiquem em casa. | Telejornal "AO VIVO", relógio 21:57. |
| 3 | MÃE | Tranca a porta dos fundos. E fecha essa cortina. | Mãe puxando a cortina. |
| 4 | PAI | Tudo trancado. Agora ninguém sai. | Pai girando a chave, trinco. |
| 5 | BIA | Pai... cadê o Thor? | Bia olhando a caminha vazia do cachorro. |
| 6 | PAI | Tava no quintal agora mesmo. | Quintal vazio pela janela. |
| 7 | BIA | O portão tá aberto. Quem foi o último a entrar? | Portão aberto; todos olham pra você. |
| 8 | NARRADOR | Foi você. E lá fora, o Thor tá parado no meio da rua, latindo. Na esquina, três pessoas de máscara olham pra ele. | Rua escura, Thor latindo, 3 silhuetas mascaradas paradas na esquina (sem arma, sem violência). |
| 9 | MÃE | Ninguém abre essa porta. | Mão da mãe na maçaneta. |
| 10 | BIA | Mãe, é o Thor! | Close na Bia. |
| 11 | TV | Faltam dois minutos. | TV: 21:58. |
| 12 | PAI | Se correr, dá pra chegar nele em trinta segundos... | Pai olhando a porta. |
| 13 | MÃE | E se eles chegarem primeiro? | Uma das máscaras vira a cabeça pra casa. |
| 14 | NARRADOR | Você decide. Opção A: correr lá fora e buscar o Thor. Opção B: ficar trancado e chamar ele pela janela. Comenta A ou B. A mais comentada vira a Parte 2. E se... | Cartões A/B, "COMENTA A OU B". |

## Falas por voz (para gerar com IA)
- **Diego (TV):** "Atenção. Faltam três minutos para o início da Noite Livre. A polícia não vai atender chamados até as seis da manhã. Fiquem em casa." / "Faltam dois minutos."
- **Will (pai):** "Tudo trancado. Agora ninguém sai." / "Tava no quintal agora mesmo." / "Se correr, dá pra chegar nele em trinta segundos..."
- **Roberta (mãe):** "Tranca a porta dos fundos. E fecha essa cortina." / "Ninguém abre essa porta." / "E se eles chegarem primeiro?"
- **Keren (Bia):** "Pai... cadê o Thor?" / "O portão tá aberto. Quem foi o último a entrar?" / "Mãe, é o Thor!"

Custo no vidIQ: cada voz tem menos de 1000 caracteres, então 28 créditos por voz e 112 no total. O saldo atual é 12. A renovação em 09/12 traz 150.

## Cuidados
- Ficção ("história de ficção" na tela). Nenhuma violência mostrada. Os mascarados só olham.
- Sem nome, logo, máscara icônica ou trilha dos filmes. As máscaras são lisas e genéricas.
- O Thor não sofre nada no Ep. 1.

## Ideias para a Parte 2 (não decididas)
- A: você chega no Thor, e a sirene da Noite Livre toca no meio da rua.
- B: o Thor vem com o chamado, mas não vem sozinho: uma das máscaras segue ele até o portão.

## Produção (24/11/2026)
- As cenas já estão prontas na skill Xavier (`teste_xavier/src/videos/noitelivre/`, composição `NoiteLivreShort`), com 22 planos. Os quadros de conferência ficam em `analysis/19_noite_livre_quadros.jpg`.
- Novidades no desenho dos personagens (`toon.ts` da cópia):
  - cabelo comprido (mãe e Bia);
  - boca que abre e fecha enquanto o personagem fala (`talk`);
  - máscara lisa genérica, de frente e de perfil.
- Cenário novo:
  - telejornal genérico na TV (AO VIVO, relógio 21:57/21:58, faixa), com tudo dentro da faixa central que aparece no 9:16;
  - cortina que a mãe fecha e a caminha vazia do Thor;
  - muro e portão meio aberto na frente da casa;
  - Thor latindo no meio da rua e três máscaras na esquina.
- **Os tempos ainda são provisórios** (`LINES` no `story.ts`). Quando chegarem os áudios (créditos do vidIQ renovam em 09/12, mais a narração do usuário), os tempos e as bocas passam a vir dos áudios reais.

## Roteiro v2 (25/11/2026): técnicas das referências aplicadas (`analysis/refs/MANUAL_REFERENCIAS.md`)

As mudanças, cada uma com o dado que a apoia:
1. **Narração mais rápida** (~3 palavras/s; as referências fazem 2,7–3,6 e o nosso vídeo 18 fez ~2,5). Frases curtas, a voz começando no quadro 0.
2. **Reviravolta 5–10 s antes do CTA** (as quatro referências fazem isso): o Thor para de latir e **abana o rabo pra uma das máscaras**. Sugere que é alguém conhecido, deixa a Parte 2 armada e não tem violência.
3. **HUD fixo**: "● NOITE LIVRE · 21:57 · FALTAM 3 MIN", contando até 21:59 (o relógio e a bateria da RTR; o relógio da Souzeira).
4. **Palavra-chave no topo** por plano, **onomatopeias** carimbadas ("CLAC" na tranca, "AU! AU!"), **círculo** nas máscaras e no portão. A maquete está em `analysis/19_mock_overlays.jpg`.
5. **Final em loop**: o último segundo repete o 1º quadro (o sofá com "A NOITE LIVRE · EP. 1").
6. A **identidade nossa continua**: 3D toon, Poppins, amarelo, "E se..." no fim e "história de ficção".

### Falas do narrador v2 (bloco único para gravar)
Imagina: o governo anuncia a Noite Livre. Das dez da noite às seis da manhã, nada é crime. E faltam três minutos. Foi você. Lá fora, o Thor tá no meio da rua, latindo. Na esquina, três pessoas de máscara olham pra ele. Aí o Thor para de latir. E abana o rabo. Pra uma das máscaras. Você decide. A: corre lá fora e pega o Thor. B: fica trancado e chama ele pela janela. Comenta A ou B. A mais comentada vira a Parte 2. E se...

As falas da TV, do pai, da mãe e da Bia continuam as mesmas da v1. Plano novo a fazer quando chegarem os áudios: o Thor quieto abanando o rabo, virado para a máscara do meio.
