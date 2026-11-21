# Playbook por dados — séries "Você decide" / "E se…?"

Criado em 18/11/2026. Todo roteiro, gancho, título e CTA passam por este checklist antes de eu mandar para aprovação. Atualizo o arquivo a cada leitura de métricas.

## 0. Protocolo de verificação (vale para toda análise)
Regra: nenhum número ou afirmação sobre um vídeo vai para o usuário sem ter sido conferido na fonte. O que não deu para conferir é apresentado como dúvida, nunca como fato.

1. **Identificar o vídeo pelo conteúdo, nunca pela duração ou pela data.** Comparar título, legenda, ID ou o próprio vídeo (assistir com `vidiq_watch_shortform_content`, ou o usuário confirma). Se não der para ter certeza, perguntar.
2. **Lista completa e atual antes de analisar.** Puxar a lista de vídeos publicados no dia da análise (`vidiq_user_videos` no YouTube, `vidiq_tiktok_profile_videos` no TikTok) e conferir que nenhum ficou de fora. O relatório de Analytics chega com 1–2 dias de atraso e sozinho não serve.
3. **Não afirmar onde um vídeo está publicado** sem ver o post (link, ID ou confirmação do usuário).
4. **Separar o que é medido do que é estimativa.** Na resposta, cada número diz de onde veio (vidIQ/Analytics, Metricool, contagem pública, print do usuário). Médias de mercado e horários "padrão" ficam marcados como estimativa.
5. **Dado faltando = dizer que falta.** Por exemplo: "% assistido ainda não saiu", "Metricool sem dados do Instagram". Nunca preencher o buraco com suposição.
6. **Erro encontrado = corrigir no arquivo de análise** com data, e avisar o usuário.

### Pesquisa de referência obrigatória (antes de cada vídeo)
1. Buscar o **mesmo tema** em YouTube Shorts (PT e EN, `vidiq_outliers`) e em TikTok/Instagram (EN/PT/ES, `vidiq_instagram_tiktok_outlier_search`).
2. Ficar só com posts acima de 5× a mediana do criador, e anotar título, 1ª linha da legenda, hashtags, duração e quadro 0.
3. Usar como padrão só o que aparece em **2 ou mais** posts.
4. Traduzir e adaptar para o português, sem copiar o texto literal, e testar 2 títulos no `score_title`.
5. Salvar a tabela em `analysis/canal/AAAA-MM-DD_referencias_<tema>.md` e mandar ao usuário junto com o pacote de postagem, **antes** da publicação.

## 1. De onde vêm as regras

**Nosso canal** (detalhes em `analysis/canal/`):
- YouTube: média de 1.281 views nos 13 vídeos 3D de novembro. O lote de outubro (vários por dia, 61 s, política) teve média de 530.
- O vendaval A/B foi o Short que mais trouxe inscritos (+10) e o que mais teve comentários (5) em 15 h.
- TikTok: teste fixo de ~130 views. Só 5 de 20 vídeos passaram disso, com teto de 931.
- Títulos com data ou só "E se ?" ficaram entre os piores.

**Vídeos que viralizaram no nicho** (vidIQ, posts em português de ago–nov/2026, 5 a 286× a mediana de cada criador):

| Conta | Views | Primeiro quadro (0–3 s) | Detalhe |
|---|---|---|---|
| @contosderisco (IG, 3D) | 4,5 mi | "TODO MUNDO FICOU CEGO. MENOS VOCÊ." + som de impacto | legenda: "Manda pra única…" |
| @historiasdeeterror (IG) | 1,6 mi | "ONTEM. A DEFESA CIVIL AVISOU. E NINGUÉM LEVOU A SÉRIO." + drone grave | escolha A/B no fim |
| @animahtml (IG) | 1,3 mi | "IMAGINA QUE VOCÊ ACORDA E TODAS AS SIRENES DA CIDADE ESTÃO TOCANDO." + sirene | escolha de vida ou morte |
| @mundoempane (IG) | 1,0 mi | "MINHA AVÓ MORREU HÁ 3 ANOS." | "Manda pra quem correria atrás do vô" |
| @nicoperrengue (IG) | 1,1 mi | 1ª pessoa no carro, 3 h da manhã, passageiro misterioso | votação nos comentários |
| @informantex.ofc (TikTok) | 3,4 mi | olho abrindo + música grave | 173 s |
| @wesllen017 (TikTok) | 1,2 mi | "IMAGINA QUE VOCÊ ESCORREGOU DA PASSARELA DE UMA BARRAGEM" | 79 s |
| O Zé Topa? (YT, 1,4 mil inscritos) | 22 mil (7,4×) | — | título: "Parte 2 \| Comenta ENTRA ou MATO" |
| Souzeira (YT) | 360–456 mil | — | "… 😨 Parte 4 / Parte 9", 1:17–1:28 |
| Origin Labz (YT) | 782 mil (43×) | — | "Você ficou trancado numa loja gigante… e agora? 😱" |

**Conclusão:** o formato A/B em série é exatamente o que está viralizando no Brasil, inclusive em contas pequenas (1,7 mil a 4 mil seguidores). O que separa esses vídeos dos nossos é a execução dos primeiros 3 segundos, do título e da legenda, não o formato.

## 2. Regras de roteiro e gancho
1. **Quadro 0 = premissa em uma frase, em maiúsculas, na tela**, com som de impacto (alarme, sirene, estrondo, toque) no mesmo instante. Nada de logo, selo ou recapitulação antes.
2. **Primeira frase em 2ª pessoa e no presente**, com o risco e um detalhe concreto: hora, número, lugar ("11 da noite", "8%", "último ônibus").
3. **Recapitulação do episódio anterior: no máximo 1,5 s**, e só depois do gancho. De preferência como texto pequeno ("vocês escolheram B") por cima da ação.
4. **Um evento novo a cada 4–6 s**, sempre com corte ou mudança de câmera.
5. **Cenário do dia a dia brasileiro**: casa, prédio, ônibus, aplicativo, Defesa Civil, vizinha. Nada de política do momento.
6. **Duração: 65–80 s.** No TikTok, mais de 60 s também é exigência do programa de pagamento. Nunca exatamente 60 s.
7. **Escolha A/B no fim**: duas opções curtas e opostas, com uma delas claramente arriscada. Contagem regressiva na tela.
8. **CTA falado em duas partes:**
   - comentário: "Comenta A ou B, a mais comentada vira o próximo episódio";
   - envio: "Manda pra quem escolheria diferente de você".
9. **Fim que volta ao começo quando der** (loop): a última imagem casa com a primeira.

### Lições do Things Explained (1,15 mi de views, mesmo estilo 3D toon que o nosso)
- **Pergunta fixa no topo da tela durante o vídeo todo** (ex.: "O QUE EMPURROU O CAMINHÃO?"), além da legenda.
- **O quadro 0 mostra uma coisa estranha acontecendo** (o tranco sozinho), não só um texto.
- **Cortes a cada 1–3 s.** Nos nossos vídeos, mirar no máximo 3 s por plano nos trechos de explicação.
- **Uma imagem de "raio-X"/corte** que explique o mecanismo sozinha.
- **Um personagem secundário com humor** (mentor, vizinho, motorista) para virar história, não aula.
- **Final com frase de efeito que volta ao começo (loop).** Nos vídeos "E se…?" de curiosidade, o CTA falado pode sair. Na série A/B, o CTA continua, porque é ele que gera os comentários.
- **Duração testável: 2:00–2:17** nos vídeos de explicação, já que os maiores sucessos deles passam de 2 min.

## 3. Regras de título, legenda e tags
- **YouTube:** `[Série] Ep. N: [situação concreta]. [pergunta]?`. Sem data, sem "E se ?" sozinho, sem hashtag no título. Testar 2 opções no vidIQ (`score_title`) e usar a maior.
- **Legenda TikTok/IG:** primeira linha = a premissa do quadro 0, depois "Comenta A ou B 👇" e "📩 Manda pra quem…". No Instagram, "Ep. 1 no perfil" no lugar de link.
- **Hashtags (5, só do tema):** #suspense #vocedecide #ese + 2 do tema. Proibidas: #claude, #fyp, #insightcreatorsearch, #puzzle e outras sem relação.
- **Tags do YouTube:** tema, sinônimos, "você decide", "escolha a ou b", "história de suspense", "história de ficção", "recorte curioso".
- **Rótulo de IA:** marcar no TikTok e no Instagram (voz sintética). No YouTube não é exigido, porque é animação.

## 4. Postagem
- **1 vídeo por dia por rede.** Pode ser o mesmo nas três redes no mesmo dia.
- **Horário (BRT):** YouTube às 12h, que é o horário da maioria dos nossos vídeos com mais de 1,4 mil views. TikTok às 10h, ou às 18h como segunda opção. Instagram: o Ônibus Ep. 1 (172 mil) saiu numa sexta às 18:15, mas o Vendaval Ep. 1 saiu às 18:46 e ficou em 2,8 mil: o horário sozinho não explica; a legenda e o gancho pesaram mais. Manter 18h para a série e medir. Dias úteis rendem mais que o fim de semana.
- **Sempre o MP4 original**, nunca o baixado com marca d'água de outra rede.
- **Comentário fixado com a escolha**, mais a nota de segurança quando houver risco real.
- **Ligar os episódios**: na descrição do novo, o link do anterior; e editar o anterior com o link do novo.

## 5. Medição (48 h e 7 dias depois de cada post)

| Métrica | Fonte | Nossa base hoje | Meta da próxima fase |
|---|---|---|---|
| Views YouTube (7 d) | vidIQ | 1.281 | 3.000 |
| % assistido YouTube | vidIQ (Analytics, 1–2 dias de atraso) | ~52% | 65% |
| Comentários por vídeo | vidIQ / público | 0–5 | 20 |
| Inscritos por vídeo | vidIQ | 0–10 | 20 |
| TikTok: vídeos que passam do teste (>300 views) | vidIQ / Metricool | 5 em 20 | metade |
| TikTok: % que assiste até o fim | Metricool (sincronizando) | — | medir |
| Instagram: views / % assistido / comentários | vidIQ (insights do dono, conectado em 21/11) | mediana ~2,3 mil / ~32% / 0 (sem o Ônibus Ep. 1) | 20 mil / 45% / 1% das views |

O que fazer com cada leitura:
- **% assistido caiu antes de 3 s** → o problema é o gancho: troco imagem, texto e som do quadro 0.
- **Queda no meio** → corto o trecho e coloco um evento novo.
- **Poucos comentários com bom % assistido** → a escolha A/B está fraca: opções mais opostas, mais risco.

## 6. Registro
| Data | Vídeo | Mudança testada | Resultado em 48 h / 7 d |
|---|---|---|---|
| 17/11 | Vendaval Ep. 1 (A/B) | primeiro episódio com escolha | 1.257 views em 15 h, 5 comentários, +10 inscritos |
| 20/11 18:15 | Ônibus Ep. 1 | legenda do playbook (escolha na 1ª linha + "Manda pra…"), 5 hashtags de tema | Instagram (insights do dono, vidIQ, 21/11): 172.742 views, 3.227 comentários, 52% assistido, pulo 26% — 36x a média do perfil |
| 18/11 11:29 | Vendaval Ep. 2 | título 86/100, legenda com "Manda pra…" | ~1 dia: 1.242 views, 8 comentários |
