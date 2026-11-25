"""Legenda do vídeo 19 (A Noite Livre · Ep. 1). SPOKEN: a legenda mostra só o que foi dito (narração + personagens)."""
SPOKEN = True
KEYPH = ['noite livre', 'nada é crime', 'três minutos', 'cadê o thor', 'o portão tá aberto', 'foi você', 'no meio da rua', 'três pessoas de máscara',
         'ninguém abre essa porta', 'é o thor', 'dois minutos', 'trinta segundos', 'chegarem primeiro', 'para de latir', 'abana o rabo', 'uma das máscaras',
         'você decide', 'pega o thor', 'pela janela', 'a ou b', 'parte 2']
HLW = ('máscaras', 'máscara')
def HUD(wt):
    return []
def NOTES(wt):
    return [(0.0, 3.0, 'história de ficção', r'\an2')]
# a legenda desce nos dois trechos em que cobriria o letreiro do telejornal (S02_tv 3,55–8,36 s e a TV em 21:58, 38,86–40,53 s)
LEG_MV = [(3.55, 8.36, 330), (38.86, 40.53, 330)]
