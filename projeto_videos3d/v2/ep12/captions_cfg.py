"""Legenda do vídeo 12 (vendaval à noite, escolha A/B). SPOKEN: a legenda mostra só o que a voz disse."""
SPOKEN = True
# minúsculas e sem pontuação: o casamento é feito com as palavras do roteiro já limpas
KEYPH = ['onze da noite', 'alerta severo', 'noventa quilômetros por hora', 'calma demais', 'o vento chega', 'a luz pisca',
         'e apaga', 'estalo grave', 'na sua direção', 'dez segundos', 'opção a', 'opção b', 'a ou b']
HLW = ('apaga', 'direção', 'escolhe')
def HUD(wt):
    return []
def NOTES(wt):
    return [(0.0, 3.7, 'história ilustrativa', r'\an2'),
            (13.1, 17.2, 'alerta real da Defesa Civil RS para 17 a 19/11/2026', r'\an2'),
            (64.0, 71.16, 'alertas reais: Defesa Civil · SMS 40199 (envie seu CEP)', r'\an2')]
# S14 (bateria, 46,0–50,3 s): o "8%" do celular fica na altura da legenda; ela desce para a parte escura da tela
LEG_MV = [(46.0, 50.3, 330)]
