"""Legenda do vídeo 15 (O último ônibus, Parte 2). SPOKEN: a legenda mostra só o que a voz disse."""
SPOKEN = True
# minúsculas e sem pontuação: o casamento é feito com as palavras do roteiro já limpas
KEYPH = ['a porta fecha', 'passa direto', 'fora de serviço', 'nenhum poste aceso', 'da frente pro fundo', 'boa escolha',
         'não olha pro retrovisor', 'banco do fundo', 'tem alguém sentado lá', 'garagem enorme', 'nenhum motorista', 'última parada',
         'número desconhecido', 'cinco segundos', 'opção a', 'opção b', 'a ou b', 'parte três', 'você decide']
HLW = ('apagar', 'vibra')
def HUD(wt):
    return []
def NOTES(wt):
    return [(0.0, 3.4, 'história de ficção', r'\an2')]
