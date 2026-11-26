"""Monta a narração do vídeo 121 (A Chave Ep. 1 em INGLÊS) sobre o MESMO vídeo do 21 (sem novo render 3D):
cada frase em inglês (cortada do take nas pausas, sem acelerar nem esticar) começa no instante em que a frase em português começava.
Se uma frase em inglês for mais longa e encostar na seguinte, a seguinte é empurrada (o atraso fica registrado).
Saídas: narracao/121_narracao.mp3, analysis/narracao/121_words.json, 121_vozes/121_linhas.json (tempos e atrasos)."""
import os, json, subprocess
H = os.path.dirname(os.path.abspath(__file__)); N = os.path.dirname(H); P = os.path.dirname(N)
L = lambda f: (lambda w: w['words'] if isinstance(w, dict) else w)(json.load(open(f)))
pt = L(os.path.join(P, 'analysis', 'narracao', '21_words.json'))
# 1ª palavra de cada frase, na ordem: (português, take inglês, inglês)
FR = [('Duas da', 0, 'Two'), ('Você volta', 0, "You're"), ('O poste', 0, 'The'), ('Você liga', 0, 'You'), ('No fim', 0, 'At'), ('E ele', 0, 'and'),
      ('Você perdeu', 1, 'You lost'), ('Procurou', 1, 'You looked'), ('E do', 1, 'and across'), ('olhando', 1, 'watching'),
      ('O sol', 2, 'The'), ('Você desistiu', 2, 'You'), ('Então', 2, 'So'),
      ('Só que', 3, 'Except'), ('A luz', 3, 'Your bedroom'), ('Você mora', 3, 'You live'),
      ('Você decide', 4, 'You'), ('A. Pega', 4, 'A.'), ('Pega', 4, 'Take'), ('B. Corre', 4, 'B.'), ('Corre', 4, 'Run'), ('Comenta', 4, 'Comment'), ('A mais', 4, 'The most'), ('E se', 4, 'What')]
norm = lambda s: s.lower().strip('.,?!…')
def find(ws, word, after):            # índice da próxima palavra (ou sequência, "Your bedroom") igual a `word` a partir de `after`
    seq = word.split()
    for i in range(after, len(ws) - len(seq) + 1):
        if all(norm(ws[i + j]['w']) == norm(x) for j, x in enumerate(seq)): return i
    raise SystemExit(f'não achei {word!r} depois de {after}')
EN = [L(os.path.join(H, f'E{k}.words.json')) for k in range(5)]
pi, ei = 0, [0] * 5; starts = []
for w_pt, k, w_en in FR:
    pi = find(pt, w_pt, pi); ei[k] = find(EN[k], w_en, ei[k]); starts.append((pt[pi]['s'], k, ei[k])); pi += 1; ei[k] += 1
segs = []
for j, (t_pt, k, i0) in enumerate(starts):
    nxt = [s for s in starts[j + 1:] if s[1] == k]; i1 = nxt[0][2] if nxt else len(EN[k])
    a = max(0.0, EN[k][i0]['s'] - 0.06); b = EN[k][i1 - 1]['e'] + 0.12
    if nxt: b = min(b, EN[k][i1]['s'] - 0.02)
    segs.append(dict(k=k, a=a, b=b, t=t_pt, words=EN[k][i0:i1]))
# nas frases com ação na tela, alinha a PALAVRA DA AÇÃO (não o começo da frase) com a palavra em português que dispara a cena
ANC = {2: ('apaga', 'dies'), 4: ('parado', 'standing'), 13: ('aponta', 'points')}
for j, (wp, we) in ANC.items():
    s = segs[j]; tp = next(x['s'] for x in pt if norm(x['w']) == wp and x['s'] >= s['t'] - 0.5)
    te = next(x['s'] for x in s['words'] if norm(x['w']) == we); s['t'] = tp - (te - s['a'])
END = 65.0; cur = 0.0
for s in segs:
    s['at'] = max(s['t'], cur + 0.08); s['atraso'] = round(s['at'] - s['t'], 2); cur = s['at'] + (s['b'] - s['a'])
assert cur <= END, ('passa do fim', cur)
ins, fc = [], ''
for i, s in enumerate(segs):
    ins += ['-i', os.path.join(H, f"E{s['k']}.mp3")]
    fc += f"[{i}:a]atrim={s['a']:.3f}:{s['b']:.3f},asetpts=PTS-STARTPTS,afade=t=in:d=0.015,afade=t=out:st={s['b'] - s['a'] - 0.03:.3f}:d=0.03,aresample=48000,pan=mono|c0=c0,adelay={int(round(s['at'] * 1000))}[a{i}];"
fc += ''.join(f'[a{i}]' for i in range(len(segs))) + f'amix=inputs={len(segs)}:normalize=0:duration=longest,apad=whole_dur={END},atrim=0:{END}[o]'
wav = os.path.join(H, '121_narracao.wav')
subprocess.run(['ffmpeg', '-y', '-v', 'error', *ins, '-filter_complex', fc, '-map', '[o]', '-c:a', 'pcm_s16le', wav], check=True)
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', wav, '-c:a', 'libmp3lame', '-b:a', '192k', os.path.join(N, '121_narracao.mp3')], check=True)
words = [dict(w=w['w'], s=round(w['s'] - s['a'] + s['at'], 3), e=round(w['e'] - s['a'] + s['at'], 3), p=w.get('p', 1)) for s in segs for w in s['words']]
json.dump(dict(model='medium (cada fala sozinha) + posição na faixa', words=words), open(os.path.join(P, 'analysis', 'narracao', '121_words.json'), 'w'), ensure_ascii=False, indent=0)
json.dump([dict(take=f"E{s['k']}", corte=[round(s['a'], 3), round(s['b'], 3)], pt=round(s['t'], 2), em=round(s['at'], 2), atraso=s['atraso'], texto=' '.join(w['w'] for w in s['words'])) for s in segs],
          open(os.path.join(H, '121_linhas.json'), 'w'), ensure_ascii=False, indent=1)
for s in segs: print(f"{s['t']:6.2f} -> {s['at']:6.2f} (+{s['atraso']:.2f}) {s['b'] - s['a']:5.2f}s  {' '.join(w['w'] for w in s['words'])}")
print('fim da fala', round(cur, 2))
