"""Legenda do vídeo 05: expressões-chave (amarelo), textos de apoio (HUD) e notas de honestidade visual.
As notas ficam embaixo (\\an2) para não cobrir rótulos e painéis da parte de cima."""
SPOKEN = True     # a legenda segue o que a voz disse (o roteiro é a referência de grafia)
KEYPH = ['todo o oxigênio', 'vinte segundos', 'impossível', 'quase dois terços', 'hidrogênio', 'quase metade',
         'dois terços da massa', 'primeiro segundo', 'átomos soltos', 'primeiro instante']
HLW = ('problema.', 'tudo.', 'gás.', 'firmeza.', 'segundo.', 'sozinhas.', 'importam.', 'instante.')
def HUD(wt):
    return []
def NOTES(wt):
    return [(3.55, 6.30, 'experimento mental: impossível na realidade', r'\an2'),
            (14.90, 20.30, 'ilustração: átomos fora de escala', r'\an2'),
            (25.30, 34.60, 'ilustração simplificada', r'\an2'),
            (34.60, 38.30, 'ilustração simplificada'),
            (38.30, 43.85, 'ilustração simplificada', r'\an2'),
            (54.10, 65.10, 'ilustração: átomos fora de escala', r'\an2')]
