"""Gera as falas do vídeo 121 (A Chave em inglês) na ElevenLabs (somente eleven_v3, regra do PLAYBOOK §8). A chave é injetada pelo proxy.
Uso: python3 gerar.py [id ...]  -> <id>.mp3 (o take anterior vai para takes/)."""
import csv, json, os, sys, shutil, urllib.request
H = os.path.dirname(os.path.abspath(__file__)); os.makedirs(os.path.join(H, 'takes'), exist_ok=True)
rows = list(csv.DictReader(open(os.path.join(H, 'falas.tsv')), delimiter='\t'))
want = set(sys.argv[1:])
for r in rows:
    if want and r['id'] not in want: continue
    dst = os.path.join(H, r['id'] + '.mp3')
    if os.path.exists(dst):
        k = 1
        while os.path.exists(os.path.join(H, 'takes', f"{r['id']}_t{k}.mp3")): k += 1
        shutil.move(dst, os.path.join(H, 'takes', f"{r['id']}_t{k}.mp3"))
    body = json.dumps(dict(text=r['texto'], model_id='eleven_v3', language_code='en', voice_settings=dict(stability=float(r['stability'])))).encode()
    req = urllib.request.Request(f"https://api.elevenlabs.io/v1/text-to-speech/{r['voz']}?output_format=mp3_44100_128", body,
                                 {'xi-api-key': os.environ.get('ELEVENLABS_API_KEY', 'proxy-injected'), 'Content-Type': 'application/json'})
    open(dst, 'wb').write(urllib.request.urlopen(req, timeout=180).read()); print(r['id'], 'ok')
