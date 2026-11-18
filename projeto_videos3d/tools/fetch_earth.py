#!/usr/bin/env python3
"""Baixa texturas da Terra/Sol/Lua/estrelas (Solar System Scope, CC BY 4.0, baseadas em dados da NASA) e o relevo
NOAA ETOPO5 (domínio público), e gera assets/earth/etopo5_u16.png (metros + 32768, lon -180..180, lat 90..-90).
Uso: python3 tools/fetch_earth.py"""
import os, urllib.request, numpy as np, cv2
UA = {'User-Agent': 'video3d-pipeline/0.2 (educational video project)'}
D = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'assets', 'earth'); os.makedirs(D, exist_ok=True)
SSS = 'https://www.solarsystemscope.com/textures/download/'
FILES = [SSS + f for f in ('8k_earth_daymap.jpg', '8k_earth_nightmap.jpg', '8k_earth_clouds.jpg', '8k_stars_milky_way.jpg', '2k_sun.jpg', '2k_moon.jpg')]
FILES.append('https://www.ngdc.noaa.gov/mgg/global/relief/ETOPO5/TOPO/ETOPO5/ETOPO5.DAT')
for u in FILES:
    dst = os.path.join(D, os.path.basename(u))
    if os.path.exists(dst) and os.path.getsize(dst) > 0: continue
    with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=300) as r, open(dst + '.part', 'wb') as o: o.write(r.read())
    os.replace(dst + '.part', dst)
a = np.fromfile(os.path.join(D, 'ETOPO5.DAT'), '>i2').reshape(2160, 4320).astype(np.int32)
a = np.roll(a, 2160, axis=1)          # o arquivo começa em 0° de longitude; a textura começa em -180°
cv2.imwrite(os.path.join(D, 'etopo5_u16.png'), (a + 32768).astype(np.uint16))
open(os.path.join(D, 'CREDITOS.txt'), 'w').write('Texturas: Solar System Scope (solarsystemscope.com/textures), CC BY 4.0, baseadas em dados da NASA.\n'
                                                 'Relevo: NOAA NGDC ETOPO5 (domínio público).\n')
print('ok', D)
