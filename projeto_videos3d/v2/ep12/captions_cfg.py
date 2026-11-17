"""Legenda do vídeo 12 (vendaval à noite, escolha A/B). SPOKEN: a legenda mostra só o que a voz disse."""
SPOKEN = True
KEYPH = ['11 da noite,', 'Alerta severo.', '90 quilômetros por hora.', 'Calma demais.', 'o vento chega.', 'a luz pisca', 'e apaga.',
         'estalo grave.', 'na sua direção.', '10 segundos.', 'Opção A,', 'Opção B,', 'A ou B?']
HLW = ('apaga.', 'direção.', 'escolhe?')
def HUD(wt):
    return []
def NOTES(wt):
    return [(0.0, 3.7, 'história ilustrativa', r'\an2'),
            (13.1, 17.2, 'alerta real da Defesa Civil RS para 17 a 19/11/2026', r'\an2'),
            (64.0, 71.16, 'alertas reais: Defesa Civil · SMS 40199 (envie seu CEP)', r'\an2')]
