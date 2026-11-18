# Limitações conhecidas — vídeo 11 (E se faltasse luz por 3 dias?)

- Resolução: render nativo em 1080x1920 na skill Xavier (Remotion + three.js, `teste_xavier/src/videos/luz/`), 30 fps, sem ampliação. Os títulos (`mograph.py`) e a legenda também são desenhados em 1080x1920.
- Personagens e cenários são ilustrações (estilo cartoon). Eles não representam pessoas nem lugares reais. As cenas do Amapá (2020) e de São Paulo (2024) só ambientam o fato narrado.
- Power bank: desenho genérico (branco, com anel magnético), sem marca nem logo. Não é uma foto do produto Eletromind. O celular também é genérico, sem logo.
- "Pix" aparece só como texto, sem o logotipo oficial.
- "≈ 4 H / geladeira fechada" é a orientação do USDA FSIS para geladeira cheia e fechada (freezer cheio: ~48 h). O relógio na tela é ilustrativo.
- A bomba d'água do prédio, a antena com gerador e a maquininha sem sinal são situações gerais ("em muitos prédios", "quando falham"). Não são casos documentados de um lugar específico. A antena com gerador tem base no relato do setor de telecom no apagão do Amapá (Teletime, 2020).
- Números: Amapá, nov 2020, religamento após ~4 dias (imprensa/Aneel). São Paulo, 11 out 2024, 2,1 milhões de clientes Enel sem energia. As fontes estão em `roteiros/11_luz_3_dias.md`.
- Produto: o vídeo não afirma quantas cargas completas o power bank dá, porque o anúncio não informa. O preço também não aparece. A compatibilidade (iPhone 12 a 17) vem do próprio anúncio.
- Publicidade: "#publi · link de afiliado na bio" fica na tela durante todo o cartão final (67,4–72,5 s) e também vai na descrição. Link: https://meli.la/33otkVF
- Narração: MP3 do usuário (`narracao/11_narracao.mp3`), sem mudança de velocidade e sem cortes.
- Som: sons reais CC0 de `assets/sfx_cc0/` (créditos em `assets/sfx_cc0/CREDITOS.md`) e efeitos sintetizados (vibração, encaixe magnético, bipes, chiado de rádio, mensagem, carga). A trilha e a camada de tensão foram feitas por código (`v2/ep11/audio.py`, `v2/lib/tensao.py`).
- Pequeno detalhe visual: no fim do plano da geladeira (S06), o cartão "LEITE" encosta na borda esquerda e fica um pouco cortado, mas continua legível.
