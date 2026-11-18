"""Legenda do vídeo 11 (apagão de 3 dias + power bank de afiliado). SPOKEN: a legenda mostra só o que a voz disse."""
SPOKEN = True
KEYPH = ['três dias?', 'quase quatro dias.', 'dois milhões', 'Tudo apaga.', 'quatro horas.', 'viram risco.', 'bomba elétrica.',
         'o sinal some,', 'o Pix não passa.', 'carga extra,', 'sem fio.', 'bem diferente.']
HLW = ('apaga.', 'risco.', 'diferente.')
def HUD(wt):
    return []
def NOTES(wt):
    return [(5.10, 10.10, 'apagão do Amapá, nov. 2020 (imprensa)', r'\an2'),
            (10.10, 17.00, 'temporal de 11/10/2024, clientes da Enel SP (Aneel/imprensa)', r'\an2'),
            (19.70, 26.70, 'geladeira cheia e fechada: ~4 h (USDA)', r'\an2'),
            (52.20, 62.60, 'compatível com iPhone 12 a 17 · outros: capinha magnética · sem cabo', r'\an2'),
            (67.40, 72.52, '#publi · link de afiliado na bio', r'\an2')]
