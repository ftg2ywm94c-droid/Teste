# Registro de mudanças

## v0.1-poc — versão funcional preservada (commit `be24c75`; tag local `v0.1-poc`)
- Prova de conceito de 10 s: motor NumPy (`engine/`), planos S1–S3, trilha sintetizada, `output/poc_540x960.mp4` (QC aprovado).
- `scripts/add_narration.py`: MP3 → MP4 com legenda sincronizada, ducking e −14 LUFS.
- Para recuperar: `git checkout be24c75 -- projeto_videos3d` (a tag não pôde ser enviada ao GitHub: o acesso desta sessão só permite o branch de trabalho).

## v0.26: vídeo 122 v3, câmera contínua (2026-11-28)
- `Chave2Short` refeito com uma câmera só (spline `TRAVEL2`) que atravessa a rua, entra pela porta real e sobe a escada. O corredor foi encaixado atrás da fachada, e personagens e luzes seguem o tempo do vídeo. Único corte: o loop.
- Escada sem parede vazia e plano final sem congelar. 1950 quadros nativos 1080x1920 varridos. QC 15/15.
- Novo padrão para todos os projetos: `v2/ESTILO.md` §10 e `CLAUDE.md` na raiz.
- v2 recuperável: `v2/ep122/frames_v2_backup/`, `out/122_the_key_ep2_v2_1080x1920.mp4`, `thumbnails/122_the_key_ep2_cover_v2.jpg`. Detalhes em `v2/ep122/LIMITACOES.md`.

## v0.25: vídeo 122 "The Key · Ep. 2" (continuação pela opção A, canal You Decide 3D) (2026-11-27)
- Nova composição `Chave2Short` (`teste_xavier/src/videos/chave2/`): agarrão e arranco da chave, perseguição na rua, fechadura, porta batendo, interior da casa, celular, escada com a luz do quarto apagando.
- Narração em inglês com a mesma voz do Ep. 1 (`narracao/122_vozes/`). Efeitos novos de IA em `assets/sfx_ia/` (ver `CREDITOS.md`).
- Mixagem com os efeitos abaixando pela voz. `assemble.py` passa a ler `W_TENSAO` por episódio (padrão 0,75, os outros vídeos não mudam).
- 1º render reprovado no QC por imagem congelada. Câmeras dos planos 12–14 refeitas e esses planos renderizados de novo.
- QC 15/15 (−14,1 LUFS, TP −1,8). Detalhes em `v2/ep122/LIMITACOES.md` e `v2/ep122/qc_report_122.json`. Capa: quadro de 10,0 s.

## v0.24: vídeo 121 "The Key · Ep. 1" (A Chave em inglês, canal You Decide 3D) (2026-11-26)
- Mesmos quadros do 21, sem novo render; voz Spuds Oxley em inglês (`eleven_v3`, `en`), cada frase no instante da frase em português (`narracao/121_vozes/montar.py`), palavras de ação alinhadas em 3 frases.
- Títulos, legenda, capa, foto de perfil e banner do canal em inglês (`canal_us/`). `transcribe.py` com `WHISPER_LANG` (padrão `pt`).
- QC 15/15 (−14,3 LUFS, TP −1,8). Detalhes em `v2/ep121/LIMITACOES.md`.

## v0.23: vídeo 21 "A Chave · Ep. 1" (2026-11-25)
- A partir do piloto (15,6 s iguais): praça, a sua casa, hora do dia contínua (noite → tarde → pôr do sol → noite), sombra de nuvens, câmera que atravessa o cenário de uma cena para outra (spline contínua do plano 6 ao 13).
- Câmera refeita depois do 1º render: mira por ângulo, volta em arco no homem, grua por cima dos telhados; praça compacta. Loop: plano 14 com as regras do plano 1 (emenda 1,9/255).
- `assemble.py`: nome de saída do 21 e pipe de quadros quando PNG e JPEG se misturam (só nesse caso).
- Abertura v2: quadro 0 sem texto, selo com fade e "02:00" grande (como o Ônibus Ep. 1, 26,6% de deslize); loop sem títulos.
- QC 15/15 (−13,7 LUFS, TP −1,7). Detalhes em `v2/ep21/LIMITACOES.md` e `v2/ep21/qc_report_21.json`. Capa: quadro de 14,0 s.

## v0.22: vídeo 20 "A Visita · Ep. 1", versão 2 (celular na mão e luz real) (2026-11-25)
- Render v2 completo, nativo 1080x1920, 2280 quadros (os da v1 guardados em `v2/ep20/frames_v1/`): celular visto de costas na mão, tela iluminando o rosto, luzes práticas (tela, despertador, luar, varanda, fresta, portão).
- `assemble.py`: opção `LOUD_I` por episódio (padrão −14, os outros vídeos não mudam); vídeo 20 em −12,8 para compensar o limitador.
- Legenda desce sob o carimbo "BIP BIP" no plano 2; celular apagado no plano do loop (só o plano 27 refeito).
- QC: −14,1 LUFS, TP −1,6, atraso e deriva 0 ms; só `frames` reprova por 0,7 quadro. Detalhes em `v2/ep20/LIMITACOES.md` e `v2/ep20/qc_report_20.json`. Capa: quadro de 33,1 s.
- Piloto de qualidade (EP=90) renderizado e montado: QC passa nos 15 itens; render com 1 aba (`CONC=1`), porque com 3 abas saíram quadros em branco e sem lanterna (`v2/ep90/LIMITACOES.md`); câmera do plano 2 se aproxima no escuro.
- Postagem passa a ser entregue em blocos no chat (sem `POSTAGEM.md`), a pedido do usuário.

## v0.21: vídeo 19 "A Noite Livre · Ep. 1" (série nova, elenco de vozes de IA e o processo das referências) (2026-11-25)
- Cenas na skill Xavier (`teste_xavier/src/videos/noitelivre/`, composição `NoiteLivreShort`): 24 planos cortados nos tempos das falas, render nativo 1080x1920, 1937 quadros.
- Elenco de vozes ElevenLabs, com a tensão das falas subindo junto com a história:
  - narradora Ana Dias;
  - TV Diego, pai Will, mãe Roberta, Bia Keren.
  - As bocas abrem e fecham pelo áudio real (`talk.ts`).
- Personagens e cenário novos:
  - mãe e Bia com cabelo comprido;
  - três mascarados com máscara lisa e facão com vermelho escorrendo;
  - Thor latindo e abanando o rabo;
  - telejornal "AO VIVO", cortina, portão meio aberto e rua.
- Processo novo, tirado de `analysis/refs/MANUAL_REFERENCIAS.md`:
  - voz no quadro 0;
  - HUD com relógio de 21:57 a 21:59;
  - palavra-chave no topo de cada plano;
  - "CLAC!" e "AU! AU!" carimbados, e um círculo na máscara;
  - reviravolta antes da escolha (o Thor abana o rabo);
  - final em loop;
  - capa tirada de um quadro do vídeo (45,0 s).
- Ajustes pós-render:
  - o plano 24 deixou de ser estático (o QC achou ~2 s parados);
  - a legenda desce nos letreiros da TV;
  - a frase da Parte 2 ganhou um fundo escuro.
- QC: −14,3 LUFS, TP −1,8, correlação da narração 0,912 (0,923 depois da troca do som), deriva 0 ms. Só o item `frames` reprova, por 0,6 quadro (explicado em `v2/ep19/LIMITACOES.md`). Pacote de postagem em `v2/ep19/POSTAGEM.md`.

## v0.20: vídeo 18 "Jogador 2 · Ep. 1" (série nova, suspense na espera pelo GTA 6) (2026-11-24)
- Cenas na skill Xavier (`teste_xavier/src/videos/jogador2/`, composição `Jogador2Short`). São 21 planos cortados nas palavras do MP3 do usuário, com render nativo 1080x1920 (1938 quadros).
- Novidades:
  - sala do sítio com TV de tela animada (instalando 99%, chiado, "JOGADOR 2 CONECTADO") e console e controle genéricos com LED;
  - sítio com casa, galpão com gerador, antena de rádio, milharal balançando e dois cachorros que latem e param;
  - almofada vibrando com brilho azul.
- Personagem sentado na beira do sofá, sem afundar (pedido do usuário).
- Ajustes pós-render:
  - efeitos abaixados (correlação da narração de 0,585 para 0,893);
  - legenda, gancho e selo tirados de cima do texto da TV;
  - plano 12 refeito com a câmera mais longe.
- QC aprovado: −14,4 LUFS, TP −1,7, deriva 0 ms. Thumbnail em `thumbnails/18_jogador2_ep1_thumb.png/.jpg` e pacote de postagem em `v2/ep18/POSTAGEM.md`.

## v0.19 — vídeo 16 "Vendaval · Ep. 3" (continuação do 14, a maioria escolheu B) (2026-11-23)
- Cenas na skill Xavier (`teste_xavier/src/videos/vendaval3/`, composição `Vendaval3Short`), 23 planos cortados nas palavras do MP3 do usuário, render nativo 1080x1920 (2308 quadros; render retomado uma vez após o limite de tempo).
- Novidades: tela do celular com discagem, cronômetro da chamada, onda de áudio, bateria 3% e tela apagando; escurecimento da cena quando o celular apaga; sirene vermelha se aproximando e parando; vizinha com lanterna batendo na porta; paredes novas na sala.
- Sem pergunta fixa no topo; avisos "no final, você decide de novo" e "NO FINAL: A OU B"; fecho "EP. 4: O FINAL".
- Conferência pós-render: rajada de faíscas forçada na palavra "faísca" (imagem e som), quadros 1640–1689 refeitos.
- QC aprovado: −13,9 LUFS, TP −1,8, correlação da narração 0,967, deriva 0 ms. Thumbnail `thumbnails/16_vendaval_ep3_thumb.png/.jpg`. Pacote de postagem em `v2/ep16/POSTAGEM.md`.

## v0.18 — vídeo 15 "O último ônibus · Parte 2" (continuação do 13, a maioria escolheu B) (2026-11-21)
- Cenas na skill Xavier (`teste_xavier/src/videos/onibus2/`, composição `Onibus2Short`), 21 planos cortados nas palavras do MP3 do usuário, render nativo 1080x1920 (2279 quadros).
- Novidades: letreiro trocando para FORA DE SERVIÇO, luzes do teto apagando uma por uma, rua sem postes, garagem com 18 ônibus parados e luz de sódio, passageiro sentado no banco do fundo (desenho da pessoa sentada melhorado no `toon.ts` da cópia onibus2).
- A silhueta preta foi trocada por uma pessoa comum sentada, a pedido do usuário.
- Avisos de que há escolha no fim, guiados pelo Instagram do Ep. 1 (`analysis/canal/2026-11-21_instagram_eselab3d.md`).
- QC aprovado: −13,9 LUFS, TP −1,8, correlação da narração 0,959, atraso e deriva 0 ms. Thumbnail `thumbnails/15_ultimo_onibus_parte2_thumb.png/.jpg`. Pacote de postagem em `v2/ep15/POSTAGEM.md`.
- Revisão 2: removida a pergunta fixa "PRA ONDE ELE TÁ INDO?" (o usuário não gostou); "NO FINAL: A OU B" sobe para o topo. QC aprovado de novo.

## v0.17 — vídeo 14 "Vendaval · Ep. 2" (continuação do 12, a maioria escolheu B) (2026-11-18)
- Cenas na skill Xavier (`teste_xavier/src/videos/vendaval2/`, composição `Vendaval2Short`), 20 planos cortados nas palavras-chave, render nativo 1080x1920 (2022 quadros).
- Queda da árvore com física de haste rígida girando na base, impacto no "estrondo", destroços com trajetória balística, goteira com gotas em queda livre e ondas na poça, fumaça, fio faiscando, porta do banheiro com dobradiça.
- Conferência dos quadros antes da montagem: planos 11 a 13 refeitos. A fumaça virou translúcida, saindo pela fresta de baixo da porta. A parede ganhou o vão da porta, com um corredor escuro e o brilho das faíscas atrás. A fresta da sala ficou mais larga.
- Cartão "B · FICAR E LIGAR 193" desce para baixo da legenda no plano do celular, para não cobrir o "193".
- Fontes da orientação sobre fio caído (Governo do RS) em `v2/ep14/LIMITACOES.md`.
- QC aprovado: −13,4 LUFS, TP −1,4, correlação da narração 0,967, atraso e deriva 0 ms. Thumbnail `thumbnails/14_vendaval_ep2_thumb.png/.jpg`.

## v0.16 — vídeo 13 "O último ônibus" (série "Você decide", Ep. 1) (2026-11-18)
- Cenas na skill Xavier (`teste_xavier/src/videos/onibus/`, composição `OnibusShort`), 21 planos cortados nas palavras-chave, render nativo 1080x1920 (2118 quadros).
- Física (pedido do usuário): pessoa sentada com o quadril no assento e os pés no chão, as duas pernas visíveis (no banco do fundo o cartão fica quase paralelo ao encosto), celular deitado no banco vibrando, suspensão do ônibus (mergulho na freada, balanço ao parar, marcha lenta), rodas girando com a distância andada, luz das janelas no chão.
- Conferência dos quadros antes da montagem: a rua aparecia clara como de dia pelas janelas nos planos internos. Agora, nos planos de dentro, o vidro (laterais e traseiro) e o vão da porta escurecem a rua. 12 planos internos refeitos.
- Tela do celular: "Número desconhecido" saía cortado; o texto agora cabe na largura. 4 planos de tela refeitos.
- `v2/assemble.py`: nomes de saída dos vídeos 13 e 14.
- QC aprovado: −13,9 LUFS, TP −1,4, correlação da narração 0,945, atraso e deriva 0 ms. Thumbnail `thumbnails/13_ultimo_onibus_thumb.png/.jpg`. Limitações em `v2/ep13/LIMITACOES.md`.

## v0.15 — vídeo 12 "Vendaval: você sai ou fica?" (suspense em 2ª pessoa, escolha A/B) (2026-11-17)
- Cenas na skill Xavier (`teste_xavier/src/videos/vendaval/`, composição `VendavalShort`), 18 planos cortados nas palavras-chave, render nativo 1080x1920 (2135 quadros).
- Chuva e vento mais nítidos (pedido do usuário): camada 2D em `v2/ep12/mograph.py` (gotas em duas profundidades, respingos, rajadas e folhas) por cima das gotas 3D. No som, gotas agudas sintetizadas e rajadas mais fortes.
- "ALERTA SEVERO" em duas linhas grandes na tela do celular (pedido do usuário).
- `v2/assemble.py`: limitador opcional `LIMITER` no `plan.py`, rodando a 192 kHz para segurar picos entre amostras. Sem o atributo, nada muda nos vídeos anteriores.
- `v2/captions.py`: (1) trocas desiguais roteiro x voz ("oito por cento" falado como "8%") dividem o tempo dito em vez de gerar legenda de duração zero; (2) `LEG_MV` opcional no `captions_cfg.py` desloca a legenda num trecho (no ep12, desce no plano da bateria para não cobrir o "8%"). Legendas antigas não foram regeradas.
- `v2/ep12/captions_cfg.py`: as expressões de destaque estavam com maiúsculas e pontuação e não casavam; corrigidas.
- QC aprovado: −13,6 LUFS, TP −1,1, correlação da narração 0,96, atraso e deriva 0 ms. Limitações em `v2/ep12/LIMITACOES.md`.

## v0.14 — vídeo 11 v2: efeitos sonoros com presença (2026-11-17)
- Pedido do usuário: caprichar mais nos efeitos. Diagnóstico: na v1 os efeitos ficavam 30–50 dB abaixo da voz, porque eram abaixados junto com a música.
- `v2/assemble.py`: canal opcional de efeitos `SFX_BUS = (ganho, razão)` no `plan.py`, com ducking leve. Sem esse atributo, a mixagem é a mesma de antes (vídeos 01–10 inalterados).
- `v2/ep11/audio.py` v2 (49 eventos, antes 27): swish em cada corte, whoosh + impacto grave em cada título, power down (Amapá, "apaga", gerador), power up e luzes acendendo em onda no estéreo, grilos, gorgolejo da caixa d'água, estática real no rádio e no sinal, tom de "sinal perdido", alerta no "risco", aplausos na volta da luz e sino no "inscrever". A v1 está em `v2/ep11/audio_v1.py`, e o MP4 v1 em `out/..._v1.mp4` (fora do git).
- Efeitos em relação à voz (medidos): ações de −1 a −9 dB, ambientes de −10 a −20 dB.
- 20 sons CC0 novos do OpenGameArt em `assets/sfx_cc0/`, com créditos em `CREDITOS.md`.
- QC aprovado: −13,9 LUFS, TP −1,4, correlação da narração 0,990, atraso e deriva 0 ms. Regra registrada em `v2/ESTILO.md` §9.

## v0.13 — vídeo 11 "E se faltasse luz por 3 dias?" (afiliado) na skill Xavier (2026-11-17)
- Vídeo 11: 72,5 s, 2176 quadros, 13 planos. **Render nativo em 1080x1920** (Remotion + three.js, `teste_xavier/src/videos/luz/`, `scripts/render_luz.sh`), sem ampliação (`NATIVE = True` em `v2/ep11/plan.py`; `assemble.py` pula a ampliação).
- Arquivo: `v2/ep11/out/11_luz_3_dias_1080x1920.mp4` (32 MB, fora do git).
- Títulos em 1080x1920 (`v2/ep11/mograph.py`), sobrepostos pelo `assemble.py`. Correção: "≈" não existe na Poppins (virava um quadrado) e foi trocado por "~4 H". O título também saiu de cima do relógio e foi para a direita (novo parâmetro de centro x).
- Som: sons reais CC0 e efeitos sintetizados (`v2/ep11/audio.py`), camada de tensão com cortes de `tensao_cfg.CORTES`.
- QC (`v2/ep11/qc_report_11.json`): aprovado. −13,9 LUFS, TP −1,4, correlação da narração 0,998, atraso e deriva 0 ms.
- Thumbnail: `thumbnails/11_thumb.json` sobre quadros nativos (S03 chuva + recorte do power bank no S11). Limitações em `v2/ep11/LIMITACOES.md`, com #publi no cartão final.
- `v2/lib/tensao.py` aceita `CORTES` no cfg. `v2/qc.py` registra `RENDER_RES` do plano.

## v0.12 — vídeo 10 "E se o Brasil cobrasse menos impostos?" + teste da skill Xavier (2026-11-17)
- Vídeo 10: 64,4 s, 1933 quadros, 15 planos. **Render nativo em 720x1280** (Cycles, 8 amostras + OIDN), **ampliado para 1080x1920**. Os motion graphics são desenhados em 1080x1920.
- Arquivo: `v2/ep10/out/10_brasil_menos_impostos_1080x1920.mp4` (37 MB, fora do git).
- Som: efeitos, música e camada de tensão v2 (`v2/ep10/tensao_cfg.py`).
- QC (`v2/ep10/qc_report_10.json`): aprovado. −14,1 LUFS, TP −1,0, correlação da narração 0,998, atraso e deriva 0 ms.
- Thumbnail: `thumbnails/10_thumb.json`, sobre um render próprio em 1080x1920 nativo. Limitações em `v2/ep10/LIMITACOES.md`.
- Camada de tensão v2 (`v2/lib/tensao.py`): braam em camadas, subida Shepard, whoosh automático nos cortes e reverb de sala escura. O vídeo 09 foi remontado com ela (v3), e a v2 ficou guardada.
- Biblioteca de sons reais CC0 (OpenGameArt) em `assets/sfx_cc0/`, com 14 sons e créditos em `CREDITOS.md`.
- Vídeo 11 (afiliado, apagão): roteiro, legendas e camada de tensão prontos.
- Teste da skill Xavier (Remotion + three.js) em `teste_xavier/`: 6 s do vídeo 11 em 1080x1920 nativo (`teste_xavier/entrega/`). Fica aguardando a decisão do usuário.

## v0.11 — vídeo 09 "E se a vida real seguisse as regras do GTA?" + zonas seguras 9:16 + tensão (2026-11-17)
- Vídeo 09 (61,9 s, 1857 quadros, render nativo 720x1280 ampliado para 1080x1920). A versão 1 (antes dos ajustes) foi guardada em `v2/ep09/out/..._v1.mp4` (fora do git), e os quadros antigos em `v2/ep09/frames_v1/`.
- Zonas seguras 9:16 (TikTok, Reels, Shorts): o HUD desceu, o painel da queda subiu e as notas saíram da faixa da legenda. Os planos A1, B1, D1, D2 e E2 foram refeitos. Regras em `v2/ESTILO.md` §4.
- Camada de tensão/suspense (`v2/lib/tensao.py` + `v2/epXX/tensao_cfg.py`) para os vídeos 09, 10 e 11. Ela entra no leito de efeitos e é abaixada pela voz. Sem o arquivo, a montagem antiga é usada (§6).
- QC: aprovado, −14 LUFS, TP −1,5, correlação da narração 0,997. Thumbnail: `thumbnails/09_thumb.json`.
- Materiais e texturas melhorados no vídeo 10 (§5). Regra de CTA no fim do roteiro (§7).
- Quadros dos vídeos 01–05 apagados com autorização do usuário para liberar disco. Os MP4 entregues foram mantidos.

## v0.10 — vídeo 08 "E se o fogo nunca tivesse sido descoberto?" (2026-11-16)
- Tema enviado pelo inscrito @desORDEM2026. O comentário dele aparece num cartão próprio (avatar, nome e texto exato), sem copiar a interface da plataforma.
- Primeiro vídeo inteiro no estilo 2: 17 planos e 1977 quadros, render nativo 720x1280 com 8 amostras, ampliado para 1080x1920.
- Narração: voz "Spuds Oxley – Grandpa", 65,9 s. A versão longa com a voz Mark (81 s) ficou guardada.
- Cenários novos em `v2/ep08/scene.py`: savana de dia e de noite, fogueira, ancestrais, estúdio (raízes, aço/cerâmica/vidro, cérebro) e Terra à noite.
- Thumbnail: plano THUMB (só com `THUMB=1`), `thumbnails/08_thumb.json`.
- Limitações em `v2/ep08/LIMITACOES.md`.

## v0.9 — estilo visual novo aprovado (2026-11-15)
- Baseado na análise de um short de dicas de animação que o usuário enviou. Adotamos três ideias: câmera que nunca para, snap nas poses e acabamento em camadas. O rosto e as proporções do canal citado não foram copiados.
- Módulo `v2/lib/style2.py` e guia `v2/ESTILO.md`. Teste antes/depois em `v2/ep07/out/comparacao_estilo2_A4.mp4` (fora do git).
- Padrão a partir do vídeo 08. O vídeo 07 entregue não muda (lá o estilo só liga com `STYLE2=1`).

## v0.8 — vídeo 07 "E se um furacão chegasse na Avenida Paulista?" entregue (2026-11-14)
- Arquivo: `v2/ep07/out/07_furacao_avenida_paulista_1080x1920.mp4` (63,8 s, 1913 quadros, 30 fps, H.264 + AAC, 133 MB). Versão leve: `07_furacao_avenida_paulista_1080x1920_leve.mp4` (50 MB). As duas ficam fora do git por tamanho.
- **Render nativo em 720x1280** (Cycles, 8 amostras + OIDN), **ampliado para 1080x1920**.
- Primeiro roteiro no guia novo (`roteiros/GUIA_ROTEIRO.md`): choque, promessa, escalada em 3 degraus, virada, final em loop e CTA no fim.
- 22 planos. Cenários novos: Avenida Paulista sob tempestade (chuva, rajadas, destroços, árvore caindo, apagão), globo com furacão e Catarina, e relevo da costa até a serra.
- Som refeito com mais detalhe: vento com rajadas e uivos, chuva com gotas e escoamento, trovões, árvore, apagão, destroços sincronizados com as palavras, e reverb.
- Narração original do usuário sem alteração de velocidade: atraso 0 ms, deriva 0 ms, correlação 0,995.
- QC (`v2/ep07/qc_report_07.json`): todos os itens aprovados. Volume −14,4 LUFS, pico −1,8 dBFS. Mudança no `qc.py`: a contagem de quadros aceita diferença de até meio quadro, porque a narração dura 63,75 s (1912,5 quadros).
- Correções depois da revisão visual: rótulos dos planos F2 e G2 reposicionados e os planos refeitos. A1 também foi refeito por um carro na frente da câmera. Os quadros antigos estão em `_bak_*`.
- Tempo de render: cerca de 9 h em CPU. O container reiniciou várias vezes por inatividade. A solução foi manter uma tarefa de acompanhamento sempre ativa.
- Thumbnail: `thumbnails/07_furacao_paulista_thumb.jpg`. É um render próprio em 1080x1920 nativo (plano THUMB, só existe com `THUMB=1`), com a composição feita por `v2/thumb.py`.

## v0.7 — vídeo 06 "E se começasse um apocalipse zumbi no Brasil?" entregue (2026-11-14)
- Arquivo: `v2/ep06/out/06_apocalipse_zumbi_brasil_1080x1920.mp4` (74,3 s, 2228 quadros, 30 fps, H.264 + AAC, 100 MB). Versão leve: `06_apocalipse_zumbi_brasil_1080x1920_leve.mp4` (60 MB). As duas ficam fora do git por tamanho.
- **Render nativo em 720x1280** (Cycles, 6–8 amostras + OIDN), **ampliado para 1080x1920**.
- 27 planos. Cenários novos: cidade abandonada ao entardecer com zumbis estilizados, mata em escala de formiga, fungo e esporos, termômetro, vírus da raiva, cão e morcego. Painéis com a curva dos fungos, o calendário da raiva e o modelo de surto.
- Narração original do usuário sem alteração de velocidade: atraso 0 ms, deriva 0 ms, correlação 0,976.
- QC (`v2/ep06/qc_report_06.json`): todos os itens aprovados. Volume −14,1 LUFS, pico −1,4 dBFS.
- Correção depois do QC: o plano C3 foi refeito porque o rótulo "37 °C" saía cortado.
- Tempo de render: cerca de 9 h em CPU, dividindo o processador com outras tarefas. O container reiniciou 4 vezes, e o render foi retomado cada vez a partir dos quadros salvos.
- Thumbnail: `thumbnails/06_apocalipse_zumbi_thumb.jpg`. É um render próprio em 1080x1920 nativo, com a composição feita por `v2/thumb.py`.

## v0.6 — vídeo 05 "E se TODO o oxigênio sumisse por 20 segundos?" entregue (2026-11-13)
- Arquivo: `v2/ep05/out/05_todo_oxigenio_sumisse_1080x1920.mp4` (73,4 s, 2202 quadros, 30 fps, H.264 + AAC, 142 MB). Versão leve: `05_todo_oxigenio_sumisse_1080x1920_leve.mp4` (59 MB, feita automaticamente pelo `assemble.py`). As duas ficam fora do git por tamanho.
- **Render nativo em 720x1280** (Cycles, 6–8 amostras + OIDN), **ampliado para 1080x1920**.
- 29 planos com corte e câmera em movimento. Cenários reaproveitados do vídeo 04, mais três novos: prédio que se desfaz em blocos e pó, moléculas de água que perdem o O e mar que vira vapor.
- Narração original do usuário sem alteração de velocidade: atraso 0 ms, deriva 0 ms, correlação 0,987.
- QC (`v2/ep05/qc_report_05.json`): todos os itens aprovados. Volume −14,3 LUFS, pico −1,3 dBFS, nenhum quadro preto ou congelado, erro da legenda 0,0 s.
- Tempo de render: cerca de 7 h em CPU, dividindo o processador com a prévia do vídeo 06. O container reiniciou 1 vez, e o render foi retomado a partir dos quadros salvos.

## v0.5 — vídeo 04 "E se o oxigênio sumisse por 20 segundos?" entregue (2026-11-13)
- Arquivo: `v2/ep04/out/04_oxigenio_sumisse_20s_1080x1920.mp4` (74,4 s, 2232 quadros, 30 fps, H.264 + AAC, 117 MB; fora do git por tamanho).
- **Render nativo em 720x1280** (Cycles, 6–8 amostras + OIDN, light tree desligado), **ampliado para 1080x1920**.
- Ritmo novo: 31 planos, corte combinado com câmera em movimento.
- Narração original do usuário sem alteração de velocidade: deriva 0 ms, correlação 0,996.
- QC (`v2/ep04/qc_report_04.json`): todos os itens aprovados. Volume −14,1 LUFS, pico −1,4 dBFS, nenhum quadro preto ou congelado.
- Tempo de render: cerca de 7 h em CPU. O container reiniciou 4 vezes, e o render foi retomado cada vez a partir dos quadros salvos.

### Correções após o QC da v0.5
- As notas "moléculas fora de escala" (2,65 s), "ilustração" (21,35 s) e "ilustração simplificada" (34,45 s) cobriam o contador "20 s" e o painel de altitude. Foram movidas para a parte de baixo.
- Versão leve para baixar no celular: `04_oxigenio_sumisse_20s_1080x1920_leve.mp4` (59 MB, H.264 em 2 passagens a 6,2 Mbps, SSIM 0,988 em relação ao original). O arquivo de 117 MB não mostrava o botão de baixar no app.

## v0.4 — vídeo 03 "E se você pulasse num buraco que atravessa a Terra?" entregue (2026-11-13)
- Arquivo: `v2/ep03/out/03_buraco_atravessa_a_terra_1080x1920.mp4` (66,0 s, 1980 quadros, 30 fps, H.264 + AAC 48 kHz, 65 MB; fora do git por tamanho).
- **Render nativo 720x1280** (Cycles, 6–9 amostras + OIDN), **ampliado para 1080x1920**. Não é render nativo em 1080x1920.
- Narração original do usuário sem alteração de velocidade: atraso 0 ms, deriva 0 ms, correlação 0,995.
- QC (`v2/ep03/qc_report_03.json`): todos os itens aprovados. Volume −14,0 LUFS, pico −1,1 dBTP, nenhum quadro preto ou congelado, erro da legenda 0,0 s.
- Física (`v2/ep03/fisica.py`): queda pelo modelo PREM. Ida em 38 min 11 s, velocidade máxima de 35.700 km/h, gravidade de 10,7 m/s² na fronteira do núcleo.
- Tempo de render: cerca de 9,5 h em CPU. O container reiniciou 3 vezes no meio, e o render retomou cada vez a partir dos quadros já salvos.
- Texturas da Terra: Solar System Scope (CC BY 4.0).

### Correções após o QC da v0.4
- Plano J: a câmera ficava parada em 4 trechos (50,3–58,8 s). Ganhou deriva lenta no começo e aproximação final em Kola, e o plano inteiro foi refeito. Os quadros antigos estão em `v2/ep03/frames/_bak_J_v0/`.
- A nota "tempo acelerado" (36,95–40,45 s) cobria o rótulo "38 min" e foi movida para a parte de baixo.

## v0.3 — vídeo 02 "E se a Terra parasse de girar" entregue (2026-11-12)
- Arquivo: `v2/ep02/out/02_terra_parasse_de_girar_1080x1920.mp4` (76,5 s, 2295 quadros, 30 fps, H.264 + AAC 48 kHz, 135 MB; fora do git por tamanho).
- **Render nativo 720x1280** (Cycles, 6–9 amostras + OIDN), **ampliado para 1080x1920**. Não é render nativo em 1080x1920.
- Narração original do usuário sem alteração de velocidade: atraso 0 ms, deriva 0 ms, correlação 0,997.
- QC (`v2/ep02/qc_report_02.json`): todos os itens aprovados — −13,9 LUFS, pico −1,5 dBTP, sem quadros pretos/congelados, legenda com erro 0,0 s.
- Tempo de render: ~6 h em CPU (A–K), mais 18 min para refazer o fim do plano E.
- Texturas da Terra: Solar System Scope (CC BY 4.0); relevo: NOAA ETOPO5; modelo da redistribuição dos oceanos: Fraczek (Esri).
- Pipeline compartilhado (`captions.py`, `assemble.py`, `qc.py`) agora aceita `EP=02`; saída do vídeo 01 conferida como idêntica (só ganhou o estilo "Nota", não usado).

### Correções após o QC da v0.3
- Plano E: câmera e ônibus ficavam parados 1,5 s (31,8–33,3 s) → recuo lento da câmera a partir de 30,6 s; quadros 918–998 refeitos (antigos guardados em `v2/ep02/frames/_bak_E_v0.2/`).
- Nota "giro acelerado na animação" cobria o rótulo "1 volta por dia" → movida para a parte de baixo (4º campo opcional em `NOTES`).

## v0.2 — vídeo 01 "Distância de parada" entregue (2026-11-11)
- Arquivo: `v2/out/01_distancia_de_parada_1080x1920.mp4` (68,0 s, 2040 quadros, 30 fps, H.264 + AAC 48 kHz, 143 MB; fora do git por tamanho).
- **Render nativo 720x1280** (Cycles, 12 amostras + OIDN), **ampliado para 1080x1920** (lanczos + nitidez). Não é render nativo em 1080x1920.
- Narração original do usuário sem alteração de velocidade: QC mediu atraso 0 ms, deriva 0 ms, correlação 0,991.
- QC (`v2/qc_report_01.json`): todos os itens aprovados — −13,9 LUFS, pico −1,4 dBTP, sem quadros pretos/congelados, legenda com erro 0,0 s, folga mínima menino 1,28 m / bola 4,04 m.
- Tempo de render: ~10,5 h em CPU (15–19 s/quadro). D1 e E refeitos (motorista reposicionado; rótulo de 10 m não cobre o menino).

### Histórico da produção v0.2
- `tools/setup_env.sh`: instala Blender 4.2.3 LTS, libEGL e faster-whisper num container novo.
- `add_narration.py`: Whisper passa a receber o áudio decodificado pelo ffmpeg (o leitor interno quebrava com PyAV ≥ 15).
- Medições do ambiente (2026-11-11), cena de teste simples:
  Cycles CPU 1080x1920 48 amostras = 31 s/quadro; 12 amostras + denoiser = 13,8 s/quadro; EEVEE por software (llvmpipe) = 59 s/quadro.
