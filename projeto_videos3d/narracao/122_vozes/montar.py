"""Monta a narração do vídeo 122 (The Key Ep. 2): 4 falas do Spuds Oxley (eleven_v3, en), cada uma num instante fixo, sem acelerar nem esticar.
Saídas: narracao/122_narracao.mp3, analysis/narracao/122_words.json (palavras do Whisper de cada fala, na posição da faixa)."""
import os, json, subprocess
H = os.path.dirname(os.path.abspath(__file__)); N = os.path.dirname(H); P = os.path.dirname(N)
AT = [('F1', 0.0), ('F2', 13.1), ('F3', 33.6), ('F4', 49.4)]
END = 65.0
ins = sum([['-i', os.path.join(H, f + '.mp3')] for f, _ in AT], [])
fc = ''.join(f'[{i}:a]aresample=48000,pan=mono|c0=c0,adelay={int(t * 1000)}[a{i}];' for i, (_, t) in enumerate(AT))
fc += ''.join(f'[a{i}]' for i in range(len(AT))) + f'amix=inputs={len(AT)}:normalize=0:duration=longest,apad=whole_dur={END},atrim=0:{END}[o]'
wav = os.path.join(H, '122_narracao.wav')
subprocess.run(['ffmpeg', '-y', '-v', 'error', *ins, '-filter_complex', fc, '-map', '[o]', '-c:a', 'pcm_s16le', wav], check=True)
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', wav, '-c:a', 'libmp3lame', '-b:a', '192k', os.path.join(N, '122_narracao.mp3')], check=True)
L = lambda f: (lambda w: w['words'] if isinstance(w, dict) else w)(json.load(open(f)))
words = [dict(w=w['w'], s=round(w['s'] + t, 3), e=round(w['e'] + t, 3), p=w.get('p', 1)) for f, t in AT for w in L(os.path.join(H, f + '.words.json'))]
json.dump(dict(model='medium (cada fala sozinha) + posição na faixa', words=words), open(os.path.join(P, 'analysis', 'narracao', '122_words.json'), 'w'), ensure_ascii=False, indent=0)
print('ok', END, 'última palavra', words[-1])
