"""Legenda do vídeo 03: expressões-chave (amarelo), textos de apoio (HUD) e notas de honestidade visual."""
SPOKEN = True     # a voz disse "passa mais de" (sem o "a" do roteiro): a legenda segue o áudio
KEYPH = ['trinta e cinco mil quilômetros por hora', 'trinta e oito minutos', 'três mil quilômetros', 'cinco mil graus',
         'doze quilômetros', 'sem peso', 'núcleo de ferro', 'mais forte']
HLW = ('surpresa.', 'enfraquece.', 'parado,', 'sempre.', 'parede.', 'comentários.')
def HUD(wt):
    return []
def NOTES(wt):
    return [(16.35, 27.9, 'personagem e túnel fora de escala'),
            (36.95, 40.45, 'tempo acelerado', r'\an2'),
            (40.55, 47.35, 'câmera lenta'),
            (47.45, 50.05, 'tempo acelerado'),
            (56.6, 58.75, 'crosta e poço em escala'),
            (58.85, 62.45, 'rotação acelerada'),
            (62.55, 65.95, 'tempo acelerado · na vida real, bateria na parede em ~20 s')]
