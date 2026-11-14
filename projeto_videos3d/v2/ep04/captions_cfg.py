"""Legenda do vídeo 04: expressões-chave (amarelo), textos de apoio (HUD) e notas de honestidade visual."""
SPOKEN = True     # a legenda segue o que a voz disse (o roteiro é a referência de grafia)
KEYPH = ['vinte segundos', 'vinte e um por cento', 'oitenta por cento', 'dois mil metros', 'catorze mil metros',
         'de nove a quinze segundos', 'quase metade', 'o problema é você']
HLW = ('você.', 'some.', 'planando.', 'adianta:', 'consciência.', 'Mito.', 'está.', 'dirigindo.')
def HUD(wt):
    return []
def NOTES(wt):
    return [(2.65, 5.25, 'ilustração: moléculas fora de escala', r'\an2'),
            (21.35, 24.65, 'ilustração', r'\an2'),
            (34.45, 40.25, 'ilustração simplificada', r'\an2'),
            (55.25, 59.65, 'modelo de átomos simplificado', r'\an2')]
