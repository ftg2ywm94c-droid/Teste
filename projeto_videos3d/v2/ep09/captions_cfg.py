"""Legenda do vídeo 09: expressões-chave (amarelo) e notas de honestidade visual.
Notas embaixo (\\an2), exceto em D1 (24,0–27,6 s), onde o painel fica embaixo e a nota vai para cima.
Os trechos do trailer já trazem o crédito na própria moldura."""
SPOKEN = True
KEYPH = ['nem levantaria', 'regras do jogo', 'um em cada dez', 'quatro andares', 'nenhum cachorro-quente', 'seis a oito semanas',
         'aguentar um acidente', 'crânio gigante', 'sem pescoço', 'bolsas de ar', 'tentar de novo', 'na vida real.']
HLW = ('metade.', 'atropelamento.', 'queda.', 'Graham:')
def HUD(wt):
    return []
def NOTES(wt):
    return [(1.46, 7.60, 'ilustração', r'\an2'),
            (14.50, 22.40, 'ilustração com boneco de teste', r'\an2'),
            (24.00, 27.60, 'ilustração com boneco de teste', r'\an2'),
            (27.60, 36.40, 'ilustração', r'\an2'),
            (36.40, 51.80, 'personagem nosso, inspirado no projeto Graham (TAC, 2016)', r'\an2'),
            (54.40, 58.90, 'ilustração', r'\an2')]
