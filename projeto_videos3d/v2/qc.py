#!/usr/bin/env python3
"""QC do MP4 final: formato, quadros, pretos/congelados, movimento, loudness/pico, narração preservada (correlação de
envelope com o MP3 original: atraso ~0 e escala de tempo 1,0), legendas amarradas às palavras, colisões da cinemática,
folha de contato. Uso: python3 v2/qc.py v2/out/01_distancia_de_parada_1080x1920.mp4"""
import sys, os, json, re, subprocess, numpy as np, cv2
HERE = os.path.dirname(os.path.abspath(__file__)); PROJ = os.path.dirname(HERE); sys.path[:0] = [os.path.join(HERE, 'lib'), HERE]
import story as S, shots as SH
p = sys.argv[1]
m = json.loads(subprocess.run(['ffprobe', '-v', 'error', '-show_format', '-show_streams', '-of', 'json', p], capture_output=True, text=True).stdout)
v = [s for s in m['streams'] if s['codec_type'] == 'video'][0]; a = [s for s in m['streams'] if s['codec_type'] == 'audio'][0]
log = subprocess.run(['ffmpeg', '-hide_banner', '-i', p, '-vf', 'blackdetect=d=0.1:pix_th=0.06,freezedetect=n=0.001:d=0.5', '-af', 'ebur128=peak=true',
                      '-f', 'null', '-'], capture_output=True, text=True).stderr
cap = cv2.VideoCapture(p); prev = None; diffs = []; thumbs = []; i = 0; bad = 0
while True:
    ok, f = cap.read()
    if not ok: break
    if f is None or f.size == 0: bad += 1; continue
    g = cv2.cvtColor(cv2.resize(f, (135, 240)), cv2.COLOR_BGR2GRAY).astype(np.int16)
    if prev is not None: diffs.append(float(np.abs(g - prev).mean()))
    if i % 60 == 0:
        t_ = cv2.resize(f, (180, 320)); cv2.putText(t_, f'{i / 30:.0f}s', (6, 22), 0, .6, (255, 255, 255), 2); thumbs.append(t_)
    prev = g; i += 1
rows = [np.hstack(thumbs[k:k + 9] + [np.zeros_like(thumbs[0])] * (9 - len(thumbs[k:k + 9]))) for k in range(0, len(thumbs), 9)]
sheet = os.path.join(os.path.dirname(p), 'contact_sheet.jpg'); cv2.imwrite(sheet, np.vstack(rows))
d = np.array(diffs)
# narração preservada: envelope do MP3 original x envelope da faixa final
def envl(path, sr=1000):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-ac', '1', '-ar', '16000', '-af', 'highpass=f=200,lowpass=f=3500', '-f', 'f32le', '-'], capture_output=True).stdout
    x = np.abs(np.frombuffer(raw, np.float32)); n = len(x) // 16; return x[:n * 16].reshape(n, 16).mean(1)
eo, ef = envl(os.path.join(PROJ, 'narracao', '01_narracao.mp3')), envl(p)
n = min(len(eo), len(ef)); eo_, ef_ = eo[:n] - eo[:n].mean(), ef[:n] - ef[:n].mean()
lags = range(-200, 201); cc = [np.dot(eo_[max(0, -L):n - max(0, L)], ef_[max(0, L):n - max(0, -L)]) for L in lags]
lag = list(lags)[int(np.argmax(cc))]; corr = float(np.corrcoef(eo_, ef_)[0, 1])
half = n // 2  # deriva de tempo: atraso no 1º e no 2º tempo
def lag_of(a_, b_):
    c_ = [np.dot(a_[max(0, -L):len(a_) - max(0, L)], b_[max(0, L):len(b_) - max(0, -L)]) for L in range(-100, 101)]; return int(np.argmax(c_)) - 100
drift = lag_of(eo_[half:], ef_[half:]) - lag_of(eo_[:half], ef_[:half])
cap_j = json.load(open(os.path.join(HERE, 'out', 'legenda.json')))
words = cap_j['words']; ch = cap_j['chunks']
cap_err = max(min(abs(c['s'] - w['s']) for w in words) for c in ch)
kid_gap, ball_gap = S.collision_report()
dur = float(m['format']['duration']); I = re.findall(r'I:\s+(-?[\d.]+) LUFS', log); pk = re.findall(r'Peak:\s+(-?[\d.]+) dBFS', log)
r = dict(file=p, duration=dur, video=dict(codec=v['codec_name'], w=v['width'], h=v['height'], fps=v['r_frame_rate'], frames=i, pix_fmt=v['pix_fmt'], unreadable=bad),
         audio=dict(codec=a['codec_name'], sample_rate=a['sample_rate'], channels=a['channels']),
         black_segments=len(re.findall('black_start', log)), freeze_segments=len(re.findall('freeze_start', log)),
         motion=dict(mean=round(float(d.mean()), 3), min=round(float(d.min()), 4), static_frames=int((d < 0.02).sum())),
         loudness_lufs=float(I[-1]) if I else None, true_peak_dbfs=float(pk[-1]) if pk else None,
         narration=dict(lag_ms=lag, drift_ms=drift, envelope_corr=round(corr, 3)), caption_start_max_err_s=round(cap_err, 3),
         collision_min_gap_m=dict(kid=round(kid_gap, 2), ball=round(ball_gap, 2)), render_resolution='720x1280 (ampliado para 1080x1920)')
r['checks'] = dict(duration=abs(dur - SH.END) < 0.05, frames=i == round(SH.END * 30), h264=v['codec_name'] == 'h264', aac=a['codec_name'] == 'aac',
                   size_1080x1920=(v['width'], v['height']) == (1080, 1920), fps30=v['r_frame_rate'] == '30/1', no_black=r['black_segments'] == 0,
                   no_freeze=r['freeze_segments'] == 0, no_unreadable=bad == 0, loudness=abs((r['loudness_lufs'] or 0) + 14) <= 1.0,
                   no_clipping=(r['true_peak_dbfs'] or 0) <= -1.0, narration_aligned=abs(lag) <= 2 and abs(drift) <= 2, narration_present=corr > 0.5,
                   captions_on_words=cap_err < 0.01, no_collision=kid_gap > 0.3 and ball_gap > 0.1)
r['pass'] = all(r['checks'].values())
json.dump(r, open(os.path.join(os.path.dirname(p), 'qc_report.json'), 'w'), indent=1, ensure_ascii=False); print(json.dumps(r, indent=1, ensure_ascii=False))
