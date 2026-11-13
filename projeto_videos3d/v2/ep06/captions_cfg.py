"""Legenda do vídeo 06: expressões-chave (amarelo), textos de apoio (HUD) e notas de honestidade visual (embaixo, \\an2)."""
SPOKEN = True
KEYPH = ['apocalipse zumbi', 'o fungo zumbi existe', 'quatro espécies', 'controlam formigas', 'não pega', 'trinta e sete',
         'um escudo', 'a raiva', 'semanas', 'esperar é o pior plano', 'agir rápido', 'só para formigas', 'sem vacina']
HLW = ('aqui.', 'esporos.', 'escudo.', 'segundos.', 'plano.', 'surto.', 'formigas.', 'vacina.')
def HUD(wt):
    return []
def NOTES(wt):
    return [(0.00, 6.16, 'ficção: personagens estilizados', r'\an2'),
            (6.16, 8.40, 'ilustração: fungo e formiga fora de escala', r'\an2'),
            (12.38, 25.52, 'ilustração simplificada', r'\an2'),
            (36.38, 40.30, 'ilustração: vírus ampliado milhões de vezes', r'\an2'),
            (63.82, 68.30, 'ilustração simplificada', r'\an2')]
