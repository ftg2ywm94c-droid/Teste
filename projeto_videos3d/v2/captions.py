#!/usr/bin/env python3
"""Legenda ASS 1080x1920 a partir do texto APROVADO + tempos de palavra do Whisper (alinhamento por difflib).
Também gera os textos de apoio (HUD) com tempos amarrados à narração.
Uso: python3 v2/captions.py roteiros/01_distancia_de_parada.md analysis/narracao/01_words.json v2/out/legenda.ass"""
import sys, re, json, difflib, unicodedata
script_md, words_json, out = sys.argv[1:4]
txt = open(script_md).read().split('## Narração (texto para a ElevenLabs)')[1].split('## Base')[0].strip()
S = txt.split()
Wd = json.load(open(words_json))['words']
def norm(w):
    w = unicodedata.normalize('NFD', w.lower()); w = ''.join(c for c in w if unicodedata.category(c) != 'Mn')
    return re.sub(r'[^a-z0-9]', '', w)
a, b = [norm(x) for x in S], [norm(x['w']) for x in Wd]
sm = difflib.SequenceMatcher(a=a, b=b, autojunk=False)
tim = [None] * len(S); diffs = []
for tag, i1, i2, j1, j2 in sm.get_opcodes():
    if tag == 'equal':
        for k in range(i2 - i1): tim[i1 + k] = (Wd[j1 + k]['s'], Wd[j1 + k]['e'])
    else:
        diffs.append((tag, ' '.join(S[i1:i2]), ' '.join(x['w'] for x in Wd[j1:j2])))
        if i2 - i1 == j2 - j1:
            for k in range(i2 - i1): tim[i1 + k] = (Wd[j1 + k]['s'], Wd[j1 + k]['e'])
for i in range(len(S)):          # interpola palavras sem par (não deve acontecer neste áudio)
    if tim[i] is None:
        p = next(tim[k][1] for k in range(i - 1, -1, -1) if tim[k]); n = next(tim[k][0] for k in range(i + 1, len(S)) if tim[k]); tim[i] = (p, n)
# Whisper costuma esticar o fim da última palavra de cada frase sobre a pausa: limita a 0,55 s por sílaba longa
KEY = {'dez', 'sessenta', 'cinquenta', 'trinta', 'cinco', 'vinte', 'quarenta', 'segundo', 'meio', 'quadrado', 'metros', 'comentarios', 'parado', 'freio', 'frear'}
KEYPH = ['dez quilômetros por hora', 'trinta e cinco metros', 'vinte e cinco metros', 'um segundo e meio', 'quarenta e cinco', 'quadrado da velocidade', 'dez metros']
low = [w.lower().strip('.,?!…"') for w in S]
hl = [False] * len(S); pid = [None] * len(S)
for q, ph in enumerate(KEYPH):
    p = ph.split(); n = len(p)
    for i in range(len(S) - n + 1):
        if low[i:i + n] == p: hl[i:i + n] = [True] * n; pid[i:i + n] = [(q, i)] * n
for i, w in enumerate(low):
    if w in ('sessenta', 'cinquenta', 'quarenta', 'dez', 'comentários'): hl[i] = True
# blocos: separa em trechos por pontuação/pausa; cada trecho vira blocos de ≤ 16 caracteres, sem partir expressão-chave
# nem terminar bloco em palavra curta (artigo/preposição). Escolhe a divisão com menos blocos e tamanhos mais parecidos.
segs, cur = [], []
for i, w in enumerate(S):
    cur.append(i); gap = (tim[i + 1][0] - tim[i][1]) if i + 1 < len(S) else 9
    if re.search(r'[.,?!…]$', w) or gap > 0.22: segs.append(cur); cur = []
if cur: segs.append(cur)
def ok_cut(j):      # pode cortar depois da palavra j?
    if j + 1 >= len(S): return True
    if pid[j] is not None and pid[j] == pid[j + 1]: return False
    return len(norm(S[j])) > 3 or S[j].lower() in ('só', 'dez', 'é')
from functools import lru_cache
chunks = []
for seg in segs:
    n = len(seg)
    @lru_cache(None)
    def best(a):
        if a == n: return (0, 0.0, ())
        res = None
        for b in range(a + 1, n + 1):
            text = ' '.join(S[j] for j in seg[a:b]); L = len(text)
            if L > 25 and b - a > 1: break
            if b < n and not ok_cut(seg[b - 1]): continue
            if L > 16 and b - a > 1 and not any(pid[j] is not None for j in seg[a:b]): break
            k, cost, parts = best(b); cand = (k + 1, cost + (L - 12) ** 2 + (400 if L > 16 else 0), ((a, b),) + parts)
            if res is None or cand[:2] < res[:2]: res = cand
        return res or (99, 9e9, ((a, n),))
    for a, b in best(0)[2]: chunks.append(seg[a:b])
def ts(t): return f"{int(t // 3600)}:{int(t // 60 % 60):02d}:{t % 60:05.2f}"
YEL = '&H0028D7FF&'
ev = []
for k, c in enumerate(chunks):
    st = tim[c[0]][0]; en = min(tim[c[-1]][1], tim[c[-1]][0] + 0.9)
    if k + 1 < len(chunks): en = min(max(en, st + 0.25), tim[chunks[k + 1][0]][0])
    if k + 1 < len(chunks) and tim[chunks[k + 1][0]][0] - en < 0.15: en = tim[chunks[k + 1][0]][0]
    parts = []
    for j in c:
        w = S[j].upper()
        parts.append('{\\c' + YEL + '}' + w + '{\\c&HFFFFFF&}' if hl[j] else w)
    ev.append((st, en, ' '.join(parts)))
# HUD: rótulos de apoio no topo (amarrados à fala)
def wt(phrase, which='s'):
    p = phrase.split(); n = len(p)
    for i in range(len(S) - n + 1):
        if low[i:i + n] == p: return tim[i][0] if which == 's' else tim[i + n - 1][1]
    raise KeyError(phrase)
HUD = [(0.15, wt('do limite', 'e') + 0.3, '60 km/h  ·  limite 50'),
       (wt('trinta e cinco metros') - 0.1, wt('à frente', 'e') + 0.4, '35 m até o menino'),
       (wt('levou um segundo') - 0.1, wt('no freio', 'e') + 0.2, 'tempo de reação: 1,5 s'),
       (wt('cresce com o quadrado') - 0.1, wt('quadrado da velocidade', 'e') + 0.6, 'frenagem cresce com v²'),
       (wt('a mais de quarenta') - 0.1, 50.25, 'ainda a 43 km/h'),
       (wt('o téo dirige') - 0.1, wt('a cinquenta', 'e') + 0.6 if False else 62.9, '50 km/h')]
head = f"""[Script Info]
; Texto: roteiro aprovado. Tempos: faster-whisper (medium) por palavra, alinhado ao roteiro.
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Leg,Poppins,92,&H00FFFFFF,&H00FFFFFF,&H00101010,&H78000000,-1,0,0,0,100,100,0,0,1,5,2,2,90,90,560,1
Style: Hud,Poppins,62,&H00FFFFFF,&H00FFFFFF,&H50000000,&H50000000,-1,0,0,0,100,100,1,0,3,18,0,8,80,80,250,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
L = [f"Dialogue: 1,{ts(s)},{ts(e)},Leg,,0,0,0,,{{\\fad(40,30)\\fscx92\\fscy92\\t(0,90,\\fscx100\\fscy100)}}{t}" for s, e, t in ev]
L += [f"Dialogue: 0,{ts(s)},{ts(e)},Hud,,0,0,0,,{{\\fad(180,180)}}{t}" for s, e, t in HUD]
open(out, 'w').write(head + '\n'.join(L) + '\n')
json.dump(dict(diffs=diffs, words=[dict(w=S[i], s=tim[i][0], e=tim[i][1], key=hl[i]) for i in range(len(S))],
               chunks=[dict(s=s, e=e, t=t) for s, e, t in ev], hud=HUD), open(out.replace('.ass', '.json'), 'w'), ensure_ascii=False, indent=0)
print('palavras', len(S), 'blocos', len(ev), 'divergências roteiro x áudio:', diffs)
