"""Legenda do vídeo 13 (O último ônibus, Ep. 1). SPOKEN: a legenda mostra só o que a voz disse."""
SPOKEN = True
# minúsculas e sem pontuação: o casamento é feito com as palavras do roteiro já limpas
KEYPH = ['meia-noite e dez', 'último ônibus', 'um celular', 'não é o seu', 'número desconhecido', 'não desce no próximo ponto',
         'pelo retrovisor', 'ele já sabe que você viu', 'é o seu', 'um poste piscando', 'fica sentado', 'cinco segundos',
         'opção a:', 'opção b:', 'a ou b', 'próximo episódio', 'você decide']
HLW = ('desvia', 'frear')
def HUD(wt):
    return []
def NOTES(wt):
    return [(0.0, 3.4, 'história de ficção', r'\an2')]
