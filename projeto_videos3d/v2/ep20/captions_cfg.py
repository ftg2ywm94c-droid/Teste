"""Legenda do vídeo 20 (A Visita · Ep. 1). SPOKEN: a legenda mostra só o que foi dito (narrador + avó)."""
SPOKEN = True
KEYPH = ['três da manhã', 'toca sozinho', 'sua avó', 'dois anos', 'bate na porta', 'três vezes', 'tá frio aqui fora', 'olho mágico', 'é ela',
         'casaco do enterro', 'abraçando o marido', 'oito anos', 'uma visita', 'deixar a vó entrar', 'vibra de novo', 'mandando mensagem',
         'você decide', 'abre a porta', 'responde a mensagem', 'a ou b', 'parte 2']
HLW = ('avó', 'vó')
def HUD(wt):
    return []
def NOTES(wt):
    return [(0.0, 3.0, 'história de ficção', r'\an2')]
# nos planos da tela do celular a legenda desce para baixo do aparelho; no S02 desce para baixo do carimbo "BIP BIP" (y 1250)
LEG_MV = [(1.9, 4.3, 380), (9.8, 13.5, 300), (15.2, 16.8, 300), (54.9, 56.2, 300), (59.6, 61.7, 300)]
