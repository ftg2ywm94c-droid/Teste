# Teste de desempenho do render (2026-11-13)

Quadros do vídeo 03 renderizados de novo em 720x1280, com as mesmas amostras do render final. Máquina: CPU de 4 núcleos.
A qualidade foi medida pelo PSNR contra o quadro original: acima de 40 dB a diferença é praticamente invisível, acima de 44 dB é imperceptível.

| Plano | Original | Sem árvore de luzes (`OPT=lt0`) | Ganho | PSNR |
|---|---|---|---|---|
| E (túnel quente) | 49,1 s | 21,7 s | 2,3× | 45,5 dB |
| L (túnel, parede) | 58,1 s | 19,6 s | 3,0× | 45,0 dB |
| C (poço com céu) | 22,9 s | 16,5 s | 1,4× | 46,9 dB |
| H (polo) | 12,2 s | 11,2 s | 1,1× | 45,0 dB |
| D (Terra em corte) | 10,4 s | 10,2 s | — | 46,8 dB |

- Causa: a árvore de luzes (light tree) do Cycles custa caro na CPU com dezenas de malhas emissivas, como os anéis do túnel. Sem ela, a imagem fica igual na comparação lado a lado.
- Variantes com ganho pequeno, não adotadas:
  - parede sem amostragem de emissão e menos rebatimentos de luz: −28% sozinhas, quase nada além do `lt0`;
  - desligar o desfoque de movimento: −8%, e muda o visual;
  - menos amostras (4–6): −18 a −21%, mas o PSNR cai para 38–42 dB e há risco de cintilação do denoiser.
- Estimativa para o vídeo 03: cerca de 9,0 h de render → cerca de 6,2 h só com `lt0`.
- Decisão: a partir do vídeo 04, `use_light_tree = False` vira padrão nos episódios novos. Os vídeos 01–03 ficam como estão (`OPT` vazio = comportamento original).
