# 01 — Distância de parada (aguardando aprovação)

## Narração (texto para a ElevenLabs)

Dez quilômetros por hora acima do limite. O Téo achava que isso não fazia diferença nenhuma.

Todo dia, ele cruzava esta rua a sessenta, numa via de cinquenta. Até que uma bola rolou para a rua, trinta e cinco metros à frente. E um menino correu atrás dela.

O Téo levou um segundo e meio para perceber e pisar no freio. Nesse tempo, o carro andou vinte e cinco metros sem frear nada. Sobraram só dez.

Você acha que deu tempo? Me conta nos comentários.

O problema é que a distância de frenagem cresce com o quadrado da velocidade. A cinquenta por hora, o carro para em trinta e cinco metros. A sessenta, precisa de quarenta e cinco. No ponto exato onde o carro a cinquenta já estaria parado, o Téo ainda passaria a mais de quarenta por hora.

Por sorte, o menino ouviu a freada e pulou de volta para a calçada. O carro passou por onde ele estava e só parou dez metros depois. Desde então, o Téo dirige a cinquenta. Não por causa dos dez quilômetros por hora. Por causa dos dez metros.

## Base dos números
Premissas do governo de Queensland (Austrália): tempo de reação 1,5 s, pista seca, desaceleração ≈ 7 m/s².
- 50 km/h: 20,8 m de reação + 13,8 m de frenagem = 34,6 m (tabela oficial: 21 + 14 = 35 m).
- 60 km/h: 25,0 m de reação + 19,8 m de frenagem = 44,8 m (tabela oficial: 45 m).
- Velocidade do carro a 60 km/h ao passar pelos 34,6 m: √(16,67² − 2·7·(34,6 − 25)) = 11,97 m/s ≈ 43 km/h.
- Frenagem ∝ v²: (60/50)² = 1,44 → 13,8 m × 1,44 = 19,8 m.
Fontes: https://www.qld.gov.au/transport/safety/road-safety/driving-safely/stopping-distances ,
https://www.qld.gov.au/transport/safety/road-safety/driving-safely/stopping-distances/graph ,
https://www.brake.org.uk/get-involved/take-action/mybrake/knowledge-centre/speed/stopping-distances
