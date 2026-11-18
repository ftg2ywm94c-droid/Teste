# Limitações conhecidas — vídeo 14 (Vendaval · Ep. 2 — continuação do vídeo 12, a maioria escolheu B)

- Resolução: render nativo em 1080x1920 na skill Xavier (Remotion + three.js, `teste_xavier/src/videos/vendaval2/`), 30 fps, sem ampliação. Títulos, camada de chuva e vento (`mograph.py`) e legenda também são desenhados em 1080x1920.
- Ficção em segunda pessoa, continuação do vídeo 12: mesma casa, mesmo personagem, mesma noite. Não aconteceu com uma pessoa nem num lugar real. A tela mostra "história de ficção".
- A queda da árvore usa a física de uma haste rígida girando na base (θ'' = (3g/2L)·sen θ), com impacto marcado no "estrondo" e um pequeno quique amortecido. A chuva, os galhos, as telhas e o fio são ilustrativos, sem números inventados.
- A opção A (atravessar a sala no escuro, com o fio solto no caminho) é a arriscada de propósito. O que fazer na vida real aparece na tela ("fio caído: não chegue perto · emergência: Bombeiros 193 · Defesa Civil 199") e no comentário fixado:
  "Vendaval · Ep. 2. Comenta A (atravessar a sala e ajudar agora) ou B (ficar e ligar 193). A mais comentada vira o Ep. 3.
  Na vida real: nunca chegue perto de fio caído, nem para ajudar alguém. Ligue 193 (Bombeiros) ou 199 (Defesa Civil) e avise a companhia de energia."
- Fatos usados e conferidos em 18/11/2026 em páginas do Governo do RS:
  - manter distância da rede elétrica e de fios, cabos e postes caídos ou atingidos pela água;
  - a concessionária pede que ninguém chegue perto de fios caídos e que a ocorrência seja comunicada pelos canais oficiais;
  - telefones de emergência: 193 (Corpo de Bombeiros) e 199 (Defesa Civil).
  Fontes: https://estado.rs.gov.br/saiba-como-agir-em-caso-de-temporal e https://estado.rs.gov.br/autoridades-de-seguranca-publica-alertam-para-riscos-de-circulacao-durante-alagamentos
- As telas do celular ("8 %", lanterna, chamada da vizinha com "6 %", "chamando… 193 Bombeiros") são genéricas, sem marca nem layout de nenhum aparelho real.
- Narração: MP3 do usuário (`narracao/14_narracao.mp3`, 67,40 s), sem mudança de velocidade e sem cortes.
- Som: sons CC0 de `assets/sfx_cc0/` (créditos em `assets/sfx_cc0/CREDITOS.md`) e efeitos sintetizados. Os efeitos ficam num barramento próprio (ESTILO §9). O estrondo foi abaixado para não esconder os outros efeitos com a normalização de pico.
- Conferência dos quadros antes da montagem: os planos 11 (fumaça), 12 (fresta) e 13 (sala vista pela fresta) foram refeitos. A fumaça virou translúcida e sai pela fresta de baixo da porta. A parede ganhou o vão da porta, com um corredor escuro e o brilho das faíscas, e a fresta da sala ficou mais larga.
