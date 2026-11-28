"""Deixas de tensão do vídeo 21 (tempos em analysis/narracao/21_words.json). 0–15,6 s iguais às do piloto."""
END = 65.0
CUES = [
    ('drone', 0.0, 7.4, 0.3),                        # rua vazia
    ('braam', 6.12, 0.5),                            # e apaga
    ('coracao', 7.4, 12.5, 88, 0.3),                 # a lanterna, o fim da rua
    ('subida', 10.9, 12.45, 0.45), ('braam', 12.45, 0.65),   # alguém parado / segurando
    ('drone', 12.45, 16.3, 0.4), ('cluster', 14.0, 16.0, 0.35),   # a sua chave
    ('reverso', 18.4, 2.0, 0.35),                    # o tempo volta para a tarde (termina quando o céu fica de dia)
    ('pulso', 19.9, 26.0, 70, 0.18),                     # a busca na praça (leve)
    ('subida', 24.6, 26.2, 0.35), ('braam', 26.2, 0.5),   # um homem parado
    ('drone', 26.2, 36.1, 0.3),                      # olhando você procurar; o sol vai embora
    ('cluster', 36.2, 39.6, 0.3),                    # então você está seguro... né?
    ('coracao', 39.6, 47.2, 92, 0.32), ('braam', 42.56, 0.55),   # levanta a chave, aponta
    ('braam', 47.2, 0.7), ('drone', 47.2, 51.6, 0.4), ('queda', 50.4, 0.4),   # a luz acende; você mora sozinho
    ('pulso', 51.6, 63.5, 80, 0.2),                      # a escolha
]
