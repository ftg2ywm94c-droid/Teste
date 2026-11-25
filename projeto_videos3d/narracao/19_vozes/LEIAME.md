# Vozes da Noite Livre · Ep. 1: falas finais (25/11/2026)

- **Geração:** API da ElevenLabs (Starter), modelo `eleven_multilingual_v2`, similarity 0,8, speaker boost. Textos e parâmetros em `falas.tsv`.
- **Tensão crescente (pedido do usuário):** a cada fala a *stability* cai (0,50 → 0,25) e o *style* sobe (0,30 → 0,85), acompanhando o suspense. A TV fica fria e formal (0,60 / 0,15).

| Fala | Personagem | Texto | Conferência (Whisper medium) |
|---|---|---|---|
| 01_tv | TV (Diego) | Atenção. Faltam três minutos… Fiquem em casa. | ok |
| 02_mae | Mãe (Roberta) | Tranca a porta dos fundos. E fecha essa cortina. | ok |
| 03_pai | Pai (Will) | Tudo trancado. Agora ninguém sai. | ok |
| 04_bia | Bia (Keren) | Pai… cadê o Thor? | ok no medium (o small ouviu "toa") |
| 05_pai | Pai | Tava no quintal… agora mesmo. | ok |
| 06_bia | Bia | O portão tá aberto! Quem foi o último a entrar? | ok |
| 07_mae | Mãe | Ninguém abre essa porta. | ok |
| 08_bia | Bia | Mãe! É o Thor! | **take 2 de 3** (stability 0,25, style 0,85). A 1ª versão e as takes 1 e 3 saíram "Mãe, eu tô" e baixas (−27 a −29 LUFS); ficam em `takes/` |
| 09_tv | TV | Faltam dois minutos. | ok |
| 10_pai | Pai | Se correr… dá pra chegar nele em trinta segundos. | ok |
| 11_mae | Mãe | E se eles chegarem primeiro? | ok (sai quase sussurrada: medo no pico) |

- O volume entre as falas varia de −15 a −26 LUFS. A montagem nivela cada fala.
- Gasto: cerca de 150 caracteres de 40.000.
