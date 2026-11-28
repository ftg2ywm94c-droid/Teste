"""Deixas de tensão do vídeo 122 (The Key Ep. 2; tempos em analysis/narracao/122_words.json).
Os "braam" caem no respiro logo DEPOIS da palavra (não em cima dela), para não cobrir a narração (medido em medir_mix.py)."""
END = 65.0
CUES = [
    ('braam', 0.02, 0.55),                           # arranca a chave (antes da 1ª palavra)
    ('coracao', 0.8, 5.6, 96, 0.3), ('braam', 4.85, 0.6),     # ele agarra o pulso; "hard"
    ('subida', 5.4, 7.38, 0.4),                      # você se solta... e corre
    ('pulso', 7.38, 13.0, 120, 0.3),                 # a perseguição (rápido)
    ('coracao', 13.0, 21.6, 118, 0.32), ('cluster', 17.3, 18.9, 0.35),   # a chave não entra; ele vindo
    ('drone', 23.2, 30.2, 0.35),                     # as pancadas
    ('queda', 30.3, 0.35),                           # then... silence (a tensão cai junto)
    ('drone', 33.6, 42.2, 0.28), ('braam', 41.1, 0.5),       # "I made two keys"
    ('cluster', 42.66, 44.78, 0.3), ('braam', 45.3, 0.6),   # a luz do quarto apaga
    ('subida', 46.0, 48.48, 0.45), ('braam', 49.15, 0.7),    # someone is already inside
    ('pulso', 49.4, 63.8, 84, 0.2),                  # a escolha
]
