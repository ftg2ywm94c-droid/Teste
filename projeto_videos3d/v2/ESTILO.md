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
