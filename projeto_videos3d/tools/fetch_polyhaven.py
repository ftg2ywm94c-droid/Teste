#!/usr/bin/env python3
"""Baixa assets CC0 do Poly Haven (texturas, HDRI, modelos glTF) para assets/polyhaven/<id>/ e registra a licença.
Uso: python3 tools/fetch_polyhaven.py"""
import json, os, urllib.request, concurrent.futures as cf
UA = {'User-Agent': 'video3d-pipeline/0.2'}
ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'assets', 'polyhaven')
TEX = ['asphalt_02', 'concrete_pavement', 'leafy_grass', 'painted_plaster_wall', 'grey_plaster_02', 'clay_roof_tiles_02', 'grey_roof_tiles', 'brick_4',
       'coast_sand_01', 'red_sandstone_pavement', 'snow_02', 'dark_rock', 'metal_plate']
MAPS = ['Diffuse', 'nor_gl', 'Rough']
HDRI = ['kloofendal_48d_partly_cloudy_puresky']
MODELS = ['island_tree_01', 'tree_small_02', 'shrub_01', 'shrub_02', 'shrub_04', 'street_lamp_01', 'fire_hydrant', 'metal_trash_can', 'football']
def get(url, dst):
    if os.path.exists(dst) and os.path.getsize(dst) > 0: return
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120) as r, open(dst + '.part', 'wb') as o: o.write(r.read())
    os.replace(dst + '.part', dst)
def files(a): return json.load(urllib.request.urlopen(urllib.request.Request(f'https://api.polyhaven.com/files/{a}', headers=UA), timeout=30))
jobs = []
for t in TEX:
    f = files(t)
    for m in MAPS:
        u = f[m]['1k']['jpg']['url']; jobs.append((u, f'{ROOT}/{t}/{os.path.basename(u)}'))
for h in HDRI:
    u = files(h)['hdri']['2k']['hdr']['url']; jobs.append((u, f'{ROOT}/{h}/{os.path.basename(u)}'))
for m in MODELS:
    g = files(m)['gltf']['1k']['gltf']; jobs.append((g['url'], f'{ROOT}/{m}/{os.path.basename(g["url"])}'))
    for rel, inc in g['include'].items(): jobs.append((inc['url'], f'{ROOT}/{m}/{rel}'))
with cf.ThreadPoolExecutor(8) as ex: list(ex.map(lambda j: get(*j), jobs))
json.dump(dict(source='https://polyhaven.com', license='CC0 1.0', textures=TEX, hdris=HDRI, models=MODELS), open(f'{ROOT}/LICENSE.json', 'w'), indent=1)
print('ok', len(jobs), 'arquivos')
