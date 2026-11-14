#!/usr/bin/env python3
"""QA do MP4: formato, quadros pretos/congelados, movimento por frame, loudness/clipping, contact sheet.
Uso: python3 scripts/quality_check.py output/poc_540x960.mp4 [dur_min dur_max]"""
import sys, json, subprocess, re, numpy as np, cv2
p = sys.argv[1]; dmin, dmax = (float(sys.argv[2]), float(sys.argv[3])) if len(sys.argv) > 3 else (8, 12)
m = json.loads(subprocess.run(['ffprobe', '-v', 'error', '-show_format', '-show_streams', '-of', 'json', p], capture_output=True, text=True).stdout)
v = [s for s in m['streams'] if s['codec_type'] == 'video'][0]; a = [s for s in m['streams'] if s['codec_type'] == 'audio'][0]
log = subprocess.run(['ffmpeg', '-hide_banner', '-i', p, '-vf', 'blackdetect=d=0.1:pix_th=0.08,freezedetect=n=0.002:d=0.25', '-af', 'ebur128=peak=true', '-f', 'null', '-'], capture_output=True, text=True).stderr
cap = cv2.VideoCapture(p); prev = None; diffs = []; thumbs = []; i = 0; fps = cap.get(5)
while True:
    ok, f = cap.read()
    if not ok: break
    g = cv2.cvtColor(cv2.resize(f, (135, 240)), cv2.COLOR_BGR2GRAY).astype(int)
    if prev is not None: diffs.append(float(np.abs(g - prev).mean()))
    if i % int(fps) == 0: t = cv2.resize(f, (216, 384)); cv2.putText(t, f'{i // int(fps)}s', (6, 22), 0, .6, (255, 255, 255), 2); thumbs.append(t)
    prev = g; i += 1
cv2.imwrite(p.rsplit('/', 1)[0] + '/contact_sheet.jpg', np.hstack(thumbs)); d = np.array(diffs)
dur = float(m['format']['duration']); I = re.findall(r'I:\s+(-?[\d.]+) LUFS', log); pk = re.findall(r'Peak:\s+(-?[\d.]+) dBFS', log)
r = dict(file=p, duration=dur, video=dict(codec=v['codec_name'], w=v['width'], h=v['height'], fps=v['r_frame_rate'], frames=i, pix_fmt=v['pix_fmt']),
         audio=dict(codec=a['codec_name'], sample_rate=a['sample_rate'], channels=a['channels']),
         black_segments=len(re.findall('black_start', log)), freeze_segments=len(re.findall('freeze_start', log)),
         motion=dict(mean=float(d.mean()), min=float(d.min()), static_frames=int((d < 0.05).sum()), hard_cuts_at_s=[round((k + 1) / fps, 2) for k in np.flatnonzero(d > 25)]),
         loudness_lufs=float(I[-1]) if I else None, true_peak_dbfs=float(pk[-1]) if pk else None)
r['checks'] = dict(duration_ok=dmin <= dur <= dmax, h264=v['codec_name'] == 'h264', aac=a['codec_name'] == 'aac', fps30=v['r_frame_rate'] == '30/1', vertical_9x16=abs(v['width'] / v['height'] - 9 / 16) < .01,
                   no_black=r['black_segments'] == 0, no_freeze=r['freeze_segments'] == 0, always_moving=r['motion']['static_frames'] == 0, no_clipping=(r['true_peak_dbfs'] or 0) < -0.5)
r['pass'] = all(r['checks'].values()); json.dump(r, open(p.rsplit('/', 1)[0] + '/qc_report.json', 'w'), indent=1); print(json.dumps(r, indent=1))
