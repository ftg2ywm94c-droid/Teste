"""Monta a narração do vídeo 21: o áudio do piloto inteiro (0–15,6 s, intacto) + as 4 falas novas (Spuds Oxley, eleven_v3),
cada uma num instante fixo. Nenhuma fala é acelerada ou esticada: só se põe silêncio entre elas (para as travessias de câmera).
Fim da última palavra de cada take (Whisper no take sozinho): C1 13,1 s, C2 8,94 s, C3 11,42 s, C4 12,6 s.
(1ª versão usou silencedetect e errou o fim do C1: "Olhando você procurar" ficava por cima do C2.)"""
import os, subprocess, json
H = os.path.dirname(os.path.abspath(__file__)); N = os.path.dirname(H)
AT = [('piloto/piloto_narracao.mp3', 0.0), ('21_vozes/C1.mp3', 16.1), ('21_vozes/C2.mp3', 29.7), ('21_vozes/C3.mp3', 39.6), ('21_vozes/C4.mp3', 51.6)]
END = 65.0
ins = sum([['-i', os.path.join(N, f)] for f, _ in AT], [])
fc = ''.join(f'[{i}:a]aresample=48000,pan=mono|c0=c0,adelay={int(t*1000)}[a{i}];' for i, (_, t) in enumerate(AT))
fc += ''.join(f'[a{i}]' for i in range(len(AT))) + f'amix=inputs={len(AT)}:normalize=0:duration=longest,apad=whole_dur={END},atrim=0:{END}[o]'
wav = os.path.join(N, '21_vozes', '21_narracao.wav')
subprocess.run(['ffmpeg', '-y', '-v', 'error', *ins, '-filter_complex', fc, '-map', '[o]', '-c:a', 'pcm_s16le', wav], check=True)
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', wav, '-c:a', 'libmp3lame', '-b:a', '192k', os.path.join(N, '21_narracao.mp3')], check=True)
json.dump(dict(at=AT, end=END), open(os.path.join(H, '21_linhas.json'), 'w'), indent=1); print('ok', END)
