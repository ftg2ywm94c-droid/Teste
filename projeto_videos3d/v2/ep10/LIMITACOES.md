# Limitações conhecidas — vídeo 10

- Resolução: render nativo em 720x1280 (Cycles, 8 amostras + OIDN), ampliado para 1080x1920. Os motion graphics (números, painéis, notas) são desenhados direto em 1080x1920 por cima. Estilo 2 (`v2/ESTILO.md`).
- Thumbnail: render próprio em 1080x1920 nativo (planos A1 e D1, 24 amostras), composto por `v2/thumb.py`.
- "Cinco meses" é uma estimativa do IBPT (2025), um instituto privado cuja metodologia é discutida. Na tela aparece "estimativa do IBPT (2025)".
- "Quase um terço" e "mais de 40%" vêm do Tesouro Nacional (2024). "Maior carga da América Latina" vem da OCDE/CEPAL, com dados de 2023.
- Gasolina 2022: a queda de 8,9% (ANP) também teve a ajuda da desoneração federal e do petróleo. A tela avisa: "a queda também teve corte de tributos federais". Os mais de R$ 100 bi de perda são a conta dos estados (Comsefaz), e a tela mostra "segundo os estados".
- Kansas: resumo do experimento de 2012–2017. Os defensores atribuem o resultado a outros fatores (gastos, crises setoriais). As barras 3D do gráfico mostram a tendência, sem escala nem valores reais. A tela só traz a nota "Kansas, EUA, 2012 a 2017", sem "ilustração".
- Café e balança: ilustração da regressividade do imposto sobre consumo (Ipea TD 2823). Não é um cálculo do imposto de um produto real.
- Narração: MP3 do usuário (voz "Brittney – Social Media Voice"), sem mudança de velocidade. Com a aprovação do usuário, cortei só o trecho mal pronunciado "nos EUA" (35,49–36,50 s do original). O original está em `narracao/10_narracao_original.mp3`.
- Efeitos, música e camada de tensão foram feitos por código (`v2/ep10/audio.py`, `v2/lib/tensao.py`).
- Tom neutro: sem partidos, políticos atuais ou logos.
