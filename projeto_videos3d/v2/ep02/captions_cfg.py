"""Legenda do vídeo 02: expressões-chave (amarelo), textos de apoio (HUD) e notas de honestidade visual."""
KEYPH = ['mil quilômetros por hora', 'mil seiscentos e setenta quilômetros por hora', 'mil e seiscentos por hora', 'quatro vezes mais forte',
         'um dia duraria um ano', 'seis meses de sol', 'seis de noite', 'continente gigante', 'dois milésimos de segundo por século']
HLW = ('equador', 'equador,', 'polos', 'polos?', 'leste', 'leste.')
def HUD(wt):
    return [(wt('a boa') - 0.1, 76.4, 'o dia aumenta ~1,78 ms por século')]
def NOTES(wt):
    return [(6.95, 14.1, 'giro acelerado na animação', r'\an2'),  # embaixo: no topo cobriria o rótulo '1 volta por dia'
            (wt('agora imagine'), 28.15, 'ilustração em câmera lenta'),
            (wt('e mesmo uma parada'), 60.4, 'ilustração fora de escala'),
            (wt('sem o giro'), 68.85, 'modelo: Fraczek (Esri) · relevo NOAA ETOPO5')]
