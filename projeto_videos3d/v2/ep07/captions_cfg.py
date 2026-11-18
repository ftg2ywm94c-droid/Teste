"""Legenda do vídeo 07: expressões-chave (amarelo), textos de apoio (HUD) e notas de honestidade visual.
Notas embaixo (\\an2), exceto onde os painéis de baixo (comparação e força, 19,7–25,9 s) ocupam a área."""
SPOKEN = True
KEYPH = ['duzentos e cinquenta quilômetros por hora', 'Avenida Paulista', 'dos mais fortes', 'uma defesa', 'centenas de árvores',
         'milhões de casas sem luz', 'mais que o dobro', 'quatro vezes mais', 'acelera', 'projéteis', 'furacão Catarina',
         'mar quente', 'sessenta quilômetros', 'em cima da serra', 'enfraquece', 'não chegam inteiros', 'tempestade comum']
HLW = ('Paulista.', 'conhece.', 'luz.', 'mais.', 'acelera.', 'projéteis.', 'Sul.', 'quente.', 'serra.', 'enfraquece.', 'capaz.')
def HUD(wt):
    return []
def NOTES(wt):
    return [(0.00, 4.68, 'ilustração: cenário hipotético', r'\an2'),
            (4.68, 7.60, 'ilustração: furacão fora de escala', r'\an2'),
            (7.60, 11.40, 'ilustração: cenário hipotético', r'\an2'),
            (11.40, 19.70, 'ilustração do temporal de 2023', r'\an2'),
            (19.70, 25.90, 'valores: escala Saffir-Simpson e Defesa Civil de SP'),
            (25.90, 32.95, 'ilustração: cenário hipotético', r'\an2'),
            (32.95, 37.60, 'ilustração: furacão fora de escala', r'\an2'),
            (39.80, 52.30, 'ilustração: relevo com altura exagerada', r'\an2'),
            (52.30, 61.25, 'ilustração', r'\an2')]
