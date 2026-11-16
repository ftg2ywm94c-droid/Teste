"""Legenda do vídeo 10: expressões-chave (amarelo) e notas de fonte/honestidade visual (embaixo, \\an2).
A narração teve o trecho "nos EUA" cortado (pronúncia errada da voz): SPOKEN = True faz a legenda mostrar só o que foi dito."""
SPOKEN = True
KEYPH = ['cinco meses', 'um terço', 'maior carga', 'quarenta por cento', 'escondido no preço', 'nove por cento', 'cem bilhões',
         'não veio', 'mesmo imposto', 'pesa muito mais.', 'de quem.', 'fim de maio,']
HLW = ('menos?', 'despencou,', 'kansas')
def HUD(wt):
    return []
def NOTES(wt):
    return [(0.00, 4.90, 'estimativa do IBPT (2025)', r'\an2'),
            (9.75, 15.75, 'Tesouro Nacional (2024) · OCDE/CEPAL (2023)', r'\an2'),
            (15.75, 20.40, 'Tesouro Nacional (2024): impostos sobre bens e serviços', r'\an2'),
            (24.40, 28.40, 'a queda também teve corte de tributos federais', r'\an2'),
            (28.40, 34.40, 'segundo os estados (Comsefaz)', r'\an2'),
            (34.40, 43.70, 'Kansas, EUA, 2012 a 2017', r'\an2'),
            (43.70, 56.66, 'ilustração', r'\an2'),
            (56.66, 61.55, 'estimativa do IBPT (2025)', r'\an2')]
