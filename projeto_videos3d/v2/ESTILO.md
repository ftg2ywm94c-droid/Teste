# Estilo visual — padrão a partir do vídeo 08

Aprovado pelo usuário em 2026-11-15, depois do teste no plano A4 do vídeo 07 (`v2/ep07/out/comparacao_estilo2_A4.mp4`).
Código: `v2/lib/style2.py`. Nos episódios novos, o `render.py` liga o estilo com `os.environ.setdefault('STYLE2', '1')`.
O vídeo 07 continua como foi entregue: lá o estilo só liga com `STYLE2=1`.

## 1. Câmera viva
- A câmera nunca fica parada: tem uma deriva leve contínua (`cam_fx`, drift 3,5 cm).
- Chicote (whip) na entrada (0,20 s) e na saída (0,13 s) de cada plano, com desfoque de movimento. Para desligar num plano: `shot.whip = False`.
- Aproximação rápida nas palavras-chave: `shot.push = (t, ...)` (zoom de +16% em 0,2 s).

## 2. Snap nas poses
- As poses entram em cerca de 5 quadros, passando um pouco do ponto (`pose_seq` com `ease_out_back`).
- O rosto troca junto com a pose.
- O personagem respira e mexe a cabeça o tempo todo: nunca congela.
- Nas cenas de dados (painéis, gráficos), o snap fica só no personagem, para não atrapalhar a leitura.

## 3. Acabamento em camadas (compositor, `finish`)
- Brilho nas luzes (glare fog glow), profundidade de campo pelo canal Z com foco no personagem, correção de cor (sombras frias, luzes quentes), leve aberração de lente e vinheta.
- Isso se soma ao que cada cena já tem: névoa, partículas e iluminação.

## Custo
- No teste, o render ficou cerca de 27% mais lento (1967 s contra 1546 s no plano A4), quase tudo por causa do desfoque de movimento.
- Se o prazo apertar, deixar o desfoque de movimento só nos planos com chicote.

## 4. Formato 9:16 e zonas seguras (vale a partir do vídeo 09)
- Tudo é feito para 9:16, que é o formato de envio para TikTok, Reels e Shorts. O vídeo final sai em 1080x1920 (render nativo de 720x1280 ampliado, declarado como ampliação), e a thumbnail sai em 1080x1920.
- As zonas seguras valem para a tela de 1080x1920:
  - topo: as abas do aplicativo ocupam o alto da tela; texto e gráfico começam em y ≥ 230;
  - direita: os botões (curtir, comentar, compartilhar) ficam da metade para baixo; abaixo de y = 600, nada importante passa de x = 930;
  - embaixo: o nome e a descrição do post ficam a partir de ~1550; a legenda fica em ~1270–1360 e as notas de fonte em ~1420–1470 (`captions.py`, `SAFE916`);
  - motion graphics (vídeo 10 em diante): `SAFE` em `v2/ep10/mograph.py`, com gráficos entre y 230 e 1180.
- O QC confere 1080x1920 (`size_1080x1920`).

## 5. Melhoria contínua do visual (pedido do usuário em 17/11)
- A cada vídeo, subir um degrau nos gráficos e nas texturas, sem quebrar o que já funciona e medindo o custo no render.
- Vídeo 10: acabamento procedural em `v2/ep10/scene.py` (`acabamento`, `piso_brilhante`, `luzes_recorte`): metal escovado, papel com fibra, papelão, pintura com variação de brilho, piso escuro brilhante com grade luminosa que some nas bordas e recortes ciano/laranja. Custo medido: cerca de +10% por quadro. Dá para desligar com `ACAB=0`.

## 6. Camada de tensão / suspense (desde 17/11/2026; v2 com impactos em camadas, riser de Shepard, whoosh nos cortes, zumbido, queda de energia e falha digital)

Todo vídeo em produção ganha uma camada sonora de tensão, original e sintetizada (`v2/lib/tensao.py`), com deixas por episódio em
`v2/epXX/tensao_cfg.py` presas aos tempos da narração: drone grave, pulso, relógio, coração, cluster agudo, subida (riser) antes das
revelações, braam nos números fortes e "queda" para o silêncio. Ela entra no leito de efeitos + música e é abaixada pela voz
(sidechain), então a narração continua intacta e na frente. Peso padrão 0,75 (`W_TENSAO`). Sem `out/tensao.wav`, a montagem é a antiga.

## 7. CTA obrigatório no fim da narração

Todo roteiro termina com CTA falado: pedido de inscrição/seguir + gancho para o próximo ("…e fica atento para o próximo. E se..."),
ou um pedido de comentário. Em vídeo com produto de afiliado, a frase do produto ("o que aparece no vídeo está no link da bio")
vem logo antes e o CTA de inscrição fecha o vídeo. Manter curto (≤ 5 s).
