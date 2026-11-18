#!/usr/bin/env python3
"""Recebe a narração gravada (MP3/WAV da ElevenLabs) e gera o MP4 final.

Uso (dentro de projeto_videos3d/):
    python3 scripts/add_narration.py narracao/narracao.mp3
    python3 scripts/add_narration.py narracao/narracao.mp3 --sync continuo --size 540x960

O que faz:
 1. Acha os trechos de fala do arquivo (silencedetect do ffmpeg).
 2. --sync planos (padrão): agrupa a fala em uma frase por plano (shots.json -> "narration") e
    ancora cada frase no início previsto do seu plano; se uma frase não couber, empurra a próxima.
    --sync continuo: usa o áudio como veio, começando em --offset segundos.
 3. Se a narração passar do fim do vídeo, desacelera vídeo e efeitos na mesma proporção (até 1,30x).
 4. Legenda palavra a palavra com os tempos reais da fala (faster-whisper se estiver instalado;
    senão distribui as palavras do roteiro pelos trechos de fala, proporcional ao tamanho).
 5. Mixa voz + trilha (ducking por sidechain), normaliza em -14 LUFS / -1,5 dBTP (igual às referências).
 6. Encode H.264 + AAC 48 kHz, roda o quality_check.
"""
import argparse, json, os, re, subprocess, sys
import numpy as np
from scipy.io import wavfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
SR = 48000
SHORT = {'o', 'a', 'os', 'as', 'um', 'uma', 'de', 'do', 'da', 'e', 'em', 'no', 'na', 'que', 'se', 'ele', 'ela', 'mas', 'por', 'pra', 'com'}


def run(cmd, **kw):
    return subprocess.run(cmd, check=True, capture_output=True, text=True, **kw)


def probe_dur(p):
    return float(run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', p]).stdout)


def load_mono(p):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', p, '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'], check=True, capture_output=True).stdout
    return np.frombuffer(raw, np.float32).copy()


def speech_segments(x, thr_db=-38.0, min_gap=0.16, min_len=0.06):
    """Trechos com fala por energia RMS em janelas de 10 ms (limiar relativo ao pico)."""
    hop = SR // 100
    n = len(x) // hop
    rms = np.sqrt((x[:n * hop].reshape(n, hop) ** 2).mean(1) + 1e-12)
    db = 20 * np.log10(rms / rms.max())
    on = db > thr_db
    segs, i = [], 0
    while i < n:
        if on[i]:
            j = i
            while j < n and on[j]: j += 1
            segs.append([i / 100, j / 100]); i = j
        else: i += 1
    merged = []
    for s in segs:
        if merged and s[0] - merged[-1][1] < min_gap: merged[-1][1] = s[1]
        else: merged.append(s)
    return [s for s in merged if s[1] - s[0] >= min_len]


def group_phrases(segs, n):
    """Junta os trechos nos menores intervalos de silêncio até sobrar n grupos."""
    groups = [[s] for s in segs]
    while len(groups) > n:
        gaps = [groups[k + 1][0][0] - groups[k][-1][1] for k in range(len(groups) - 1)]
        k = int(np.argmin(gaps)); groups[k] += groups.pop(k + 1)
    return groups


def chunk_words(text):
    """1–2 palavras por legenda; artigos/preposições curtos grudam na palavra seguinte."""
    words, out, buf = text.split(), [], []
    for w in words:
        buf.append(w)
        if re.sub(r'\W', '', w.lower()) in SHORT and len(buf) < 2 and not re.search(r'[.,!?…]$', w): continue
        out.append(' '.join(buf)); buf = []
    if buf: out.append(' '.join(buf))
    return out


def weight(c):
    core = re.sub(r'[^\wÀ-ÿ]', '', c)
    return max(len(core), 2) + (3 if re.search(r'[.,!?…]$', c) else 0)


def distribute(chunks, segs):
    """Espalha os blocos de legenda pelo tempo de fala (pula silêncios), proporcional ao tamanho."""
    total = sum(e - s for s, e in segs); w = np.array([weight(c) for c in chunks], float)
    edges = np.r_[0, np.cumsum(w) / w.sum() * total]
    def at(u):  # tempo de fala acumulado -> tempo real
        for s, e in segs:
            if u <= e - s + 1e-9: return s + u
            u -= e - s
        return segs[-1][1]
    out = []
    for k, c in enumerate(chunks):
        a, b = at(edges[k] + 1e-6), at(edges[k + 1])
        out.append(dict(text=c, start=a, end=max(b, a + 0.18)))
    return out


def whisper_words(path):
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        return None
    m = WhisperModel('small', device='cpu', compute_type='int8')
    # decodifica com ffmpeg: o leitor interno (PyAV) quebra com av>=15 (argumento metadata_errors)
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-ac', '1', '-ar', '16000', '-f', 'f32le', '-'], check=True, capture_output=True).stdout
    segs, _ = m.transcribe(np.frombuffer(raw, np.float32), language='pt', word_timestamps=True)
    return [dict(text=w.word.strip(), start=w.start, end=w.end) for s in segs for w in s.words]


def ts(t):
    return f"{int(t // 3600)}:{int(t // 60 % 60):02d}:{t % 60:05.2f}"


def write_ass(caps, path, note):
    head = open('scripts/caption_style.ass').read().replace('{NOTE}', note)
    lines = [f"Dialogue: 0,{ts(c['start'])},{ts(c['end'])},W,,0,0,0,,{{\\fscx88\\fscy88\\t(0,70,\\fscx100\\fscy100)}}{c['text']}" for c in caps]
    open(path, 'w').write(head + '\n'.join(lines) + '\n')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('audio')
    ap.add_argument('--sync', choices=['planos', 'continuo'], default='planos')
    ap.add_argument('--offset', type=float, default=0.25, help='início da fala no modo continuo (s)')
    ap.add_argument('--size', default='1080x1920')
    ap.add_argument('--out', default=None)
    ap.add_argument('--max-stretch', type=float, default=1.30)
    ap.add_argument('--no-whisper', action='store_true')
    a = ap.parse_args()

    shots = json.load(open('shots/shots.json'))
    os.makedirs('output', exist_ok=True); os.makedirs('renders/tmp', exist_ok=True)
    W, H = map(int, a.size.split('x'))
    out = a.out or f'output/final_{W}x{H}.mp4'

    # vídeo base (concat dos planos já renderizados)
    P = 'renders/preview'
    open(f'{P}/concat.txt', 'w').write(''.join(f"file '{s['id']}.mp4'\n" for s in shots['shots']))
    run(['ffmpeg', '-y', '-v', 'error', '-f', 'concat', '-safe', '0', '-i', f'{P}/concat.txt', '-c', 'copy', f'{P}/video_only.mp4'])
    vdur = probe_dur(f'{P}/video_only.mp4')

    x = load_mono(a.audio)
    segs = speech_segments(x)
    if not segs: sys.exit('Nenhuma fala detectada no arquivo.')
    lines = [s['narration'] for s in shots['shots']]
    anchors = [s.get('narration_at', s['start'] + 0.15) for s in shots['shots']]

    # monta a linha do tempo: lista de (trecho_origem_ini, trecho_origem_fim, destino_ini)
    if a.sync == 'planos' and len(segs) >= len(lines):
        groups = group_phrases(segs, len(lines))
        place, t = [], 0.0
        for g, anc in zip(groups, anchors):
            g0, g1 = g[0][0], g[-1][1]
            dst = max(anc, t + 0.20 if place else anc)
            place.append((g0, g1, dst)); t = dst + (g1 - g0)
        mode = 'planos'
    else:
        if a.sync == 'planos':
            print(f'aviso: só {len(segs)} trecho(s) de fala para {len(lines)} frases; usando modo continuo')
        g0, g1 = segs[0][0], segs[-1][1]
        place = [(g0, g1, a.offset)]; groups = [segs]; mode = 'continuo'

    end = place[-1][2] + place[-1][1] - place[-1][0]
    k = max(1.0, (end + 0.35) / vdur)
    if k > a.max_stretch:
        sys.exit(f'Narração longa demais: termina em {end:.2f}s, vídeo tem {vdur:.2f}s '
                 f'(precisaria desacelerar {k:.2f}x, limite {a.max_stretch}). Encurte o texto ou fale mais rápido.')
    if k > 1.0:
        # desacelera o vídeo; reancora as frases na nova escala, mantendo sem sobreposição
        print(f'vídeo desacelerado {k:.3f}x para caber a narração')
        new, t = [], 0.0
        for (g0, g1, _), anc in zip(place, anchors):
            dst = max(anc * k, t + 0.20 if new else anc * k); new.append((g0, g1, dst)); t = dst + g1 - g0
        place = new
    T = vdur * k

    # trilha de voz posicionada
    voice = np.zeros(int(T * SR) + SR)
    pad = 0.04
    for g0, g1, dst in place:
        i0, i1 = max(0, int((g0 - pad) * SR)), min(len(x), int((g1 + pad) * SR))
        d = int((dst - pad) * SR); piece = x[i0:i1].copy()
        f = int(0.01 * SR); piece[:f] *= np.linspace(0, 1, f); piece[-f:] *= np.linspace(1, 0, f)
        voice[max(d, 0):max(d, 0) + len(piece)] += piece[:len(voice) - max(d, 0)]
    voice = voice[:int(T * SR)]
    wavfile.write('renders/tmp/voice.wav', SR, voice.astype(np.float32))

    # legendas
    caps = None
    if not a.no_whisper:
        ww = whisper_words(a.audio)
        if ww:
            caps = []
            for w in ww:
                for g0, g1, dst in place:
                    if g0 - 0.1 <= w['start'] <= g1 + 0.1:
                        caps.append(dict(text=w['text'], start=dst + w['start'] - g0, end=dst + w['end'] - g0)); break
            src = 'faster-whisper (palavras transcritas do áudio)'
    if caps is None:
        caps = []
        if mode == 'planos':
            for g, (g0, g1, dst), line in zip(groups, place, lines):
                caps += distribute(chunk_words(line), [(s - g0 + dst, e - g0 + dst) for s, e in g])
        else:
            caps = distribute(chunk_words(' '.join(lines)), [(s - g0 + place[0][2], e - g0 + place[0][2]) for s, e in segs])
        src = 'texto do roteiro distribuído pelos trechos de fala detectados'
    for c, n in zip(caps, caps[1:] + [None]):   # sem sobreposição e sem piscar entre palavras próximas
        if n:
            c['end'] = min(max(c['end'], c['start'] + 0.18), n['start'])
            if 0 < n['start'] - c['end'] < 0.12: c['end'] = n['start']
    write_ass(caps, 'output/captions_final.ass', f'Tempos: {src}. Modo {mode}, fator de tempo {k:.3f}.')

    # mix: trilha (esticada se preciso) com ducking pela voz, loudness -14 LUFS
    sfx = 'audio/sfx/mix.wav'
    af_sfx = f'atempo={1 / k:.5f},' if k > 1.0 else ''
    fc = (f'[1:a]{af_sfx}aresample={SR},volume=0.85[bed];'
          f'[0:a]aresample={SR},highpass=f=80,acompressor=threshold=-20dB:ratio=3:attack=5:release=80,volume=1.6,asplit=2[v][vk];'
          f'[bed][vk]sidechaincompress=threshold=0.03:ratio=6:attack=15:release=250[duck];'
          f'[v][duck]amix=inputs=2:normalize=0:duration=first,loudnorm=I=-14:TP=-1.5:LRA=7,aresample={SR}[mix]')
    run(['ffmpeg', '-y', '-v', 'error', '-i', 'renders/tmp/voice.wav', '-i', sfx, '-filter_complex', fc, '-map', '[mix]',
         '-ac', '2', '-ar', str(SR), 'renders/tmp/final_mix.wav'])

    vf = (f'setpts={k:.5f}*PTS,framerate=fps=30:interp_start=0:interp_end=255,' if k > 1.0 else '') + f'scale={W}:{H}:flags=lanczos,fps=30,ass=output/captions_final.ass:fontsdir=fonts'
    tmp = out.replace('.mp4', '.tmp.mp4')
    run(['ffmpeg', '-y', '-v', 'error', '-i', f'{P}/video_only.mp4', '-i', 'renders/tmp/final_mix.wav', '-vf', vf,
         '-map', '0:v', '-map', '1:a', '-c:v', 'libx264', '-crf', '18', '-preset', 'slow', '-pix_fmt', 'yuv420p',
         '-c:a', 'aac', '-b:a', '192k', '-ar', str(SR), '-t', f'{T:.3f}', '-movflags', '+faststart', tmp])
    os.replace(tmp, out)

    json.dump(dict(audio=a.audio, mode=mode, stretch=k, duration=T, caption_source=src,
                   phrases=[dict(src=[round(g0, 2), round(g1, 2)], at=round(dst, 2)) for g0, g1, dst in place],
                   captions=[dict(c, start=round(c['start'], 2), end=round(c['end'], 2)) for c in caps]),
              open('output/narration_sync.json', 'w'), indent=1, ensure_ascii=False)
    print('frases:', [(round(g0, 2), round(g1, 2), '->', round(d, 2)) for g0, g1, d in place])
    print('ok', out)
    subprocess.run([sys.executable, 'scripts/quality_check.py', out, str(T - 0.3), str(T + 0.3)], check=False,
                   stdout=subprocess.DEVNULL)
    r = json.load(open(os.path.join(os.path.dirname(out), 'qc_report.json')))
    print('QC:', 'PASSOU' if r['pass'] else 'FALHOU', {k_: v for k_, v in r['checks'].items() if not v} or '', f"{r['loudness_lufs']} LUFS")


if __name__ == '__main__':
    main()
