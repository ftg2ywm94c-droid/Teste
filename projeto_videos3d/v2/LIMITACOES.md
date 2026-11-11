# Limitações conhecidas — vídeo 01

- Resolução: render nativo 720x1280, ampliado para 1080x1920.
- Plano A usa a geometria antiga do motorista (renderizado antes do ajuste); quase não aparece.
- Plano D1: o rosto do Téo aparece atrás do para-brisa com reflexo do céu; a expressão é legível, mas suave.
- Plano B: um poste cruza o carro por um instante (paralaxe da câmera aérea).
- Plano D2: o rótulo "25 m" se sobrepõe ao carro por um instante.
- Vidros sem refração real (shader de vidro fino) para manter o tempo de render.
- Efeitos sonoros e música são sintetizados por código (sem bibliotecas licenciadas).
