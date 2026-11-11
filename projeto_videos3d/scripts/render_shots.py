#!/usr/bin/env python3
"""Renderiza os planos da prova de conceito (um MP4 por plano).
Uso: python3 scripts/render_shots.py --shot S1 [--ss 2] [--size 540x960] [--still 0,60,120]"""
import sys, os, json, argparse, subprocess, time
import numpy as np, cv2
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from engine.rt import Camera, render, tonemap, V
from engine.assets import environment, character, car, Path, bezier, sstep, STRIDE

FPS = 30; V0 = 1.283
def spring(t, f=3.2, d=5.0): return np.exp(-d * t) * np.cos(2 * np.pi * f * t) if t > 0 else 1.0
def lerp(a, b, t): return np.asarray(a, float) + (np.asarray(b, float) - np.asarray(a, float)) * t
def blink(t, times): return min([1.0] + [abs(t - b) / 0.07 for b in times if abs(t - b) < 0.07]) * 0.9 + 0.1

PATH1 = Path([(-20, 4.0), (10, 4.0)])
PATH2 = Path(np.r_[[(-6.0, 4.0)], bezier((-3.6, 4.0), (-1.6, 4.0), (-0.25, 4.05), (-0.05, 3.42))[1:]])
S2_S0 = round(PATH2.len / STRIDE) * STRIDE - V0 * 2.65   # termina com os dois pés no chão
T_CUT = 2.6; CAR_STOP = -4.1; T_BRAKE = 1.9; BRAKE_DUR = 1.4; CAR_V = 10.0

def shot1(t):
    """S1 (5,0 s): tracking – Téo anda pela calçada; o carro cresce ao fundo."""
    s = 6.0 + V0 * t; glance = sstep(1.9, 2.5, t) - sstep(3.5, 4.1, t)
    ch, info = character(PATH1, s, head_yaw=-0.55 * glance + 0.05 * np.sin(t * 2.1), head_pitch=-0.03,
                         expr=dict(eye_open=blink(t, (1.15, 3.95)), smile=0.6 + 0.4 * glance, gaze=-glance))
    cx = -30.5 - CAR_V * (5.0 - t)
    e = sstep(0, 5.0, t); off = lerp((6.6, 1.75, -1.55), (3.1, 1.30, -1.75), e)
    r = info['root']; cam = Camera(r + off + V(0, 0.02 * np.sin(t * 5.1), 0), r + V(0.35 + 0.5 * (1 - e), 1.12, 0.1 * (1 - e)), vfov=lerp(58, 46, e))
    return ch + car(cx, 0.95, cx), cam, dict(s=s, car_x=cx, car_v=CAR_V, cam=cam.pos.tolist(), brake=0.0)

def shot2(t):
    """S2 (5,0 s): Téo chega à faixa; o carro freia forte; reação; alívio."""
    t1 = 2.2; td = 0.9
    if t < t1: s = V0 * t
    else: u = min((t - t1) / td, 1); s = V0 * t1 + V0 * td * (u - u * u / 2)
    s += S2_S0; walk = 1 - sstep(t1 + 0.2, t1 + td, t)
    # carro: cruzeiro -> desaceleração constante -> parado, com mergulho do nariz e rebote
    if t < T_BRAKE: cx = CAR_STOP - CAR_V * BRAKE_DUR / 2 - CAR_V * (T_BRAKE - t); v = CAR_V; br = 0.0
    elif t < T_BRAKE + BRAKE_DUR: u = (t - T_BRAKE); v = CAR_V * (1 - u / BRAKE_DUR); cx = CAR_STOP - v * (BRAKE_DUR - u) / 2; br = 1.0
    else: cx = CAR_STOP; v = 0.0; br = 0.0
    ts = t - (T_BRAKE + BRAKE_DUR)
    pitch = 0.075 * sstep(T_BRAKE, T_BRAKE + 0.25, t) if ts < 0 else 0.075 * spring(ts, 2.6, 4.5)
    # atuação
    tr = t - 2.55; scare = sstep(0, 0.12, tr) * (1 - sstep(1.0, 1.6, tr)); relief = sstep(1.3, 1.9, tr)
    hop = 0.16 * max(0, np.sin(np.pi * tr / 0.38)) if 0 < tr < 0.38 else 0.0
    squash = (sstep(0.38, 0.46, tr) - sstep(0.46, 0.7, tr)) if tr > 0 else 0.0
    look = sstep(-0.25, 0.1, tr)
    ch, info = character(PATH2, s, walk=walk, hop=hop, squash=squash, lean=-0.16 * scare, head_yaw=0.85 * look * (1 - 0.35 * relief),
                         head_pitch=-0.05, arm_raise=scare * 0.95,
                         expr=dict(eye_open=blink(t, (0.8, 4.35)), wide=scare, brow=1.0 * scare, mouth_open=scare, smile=0.5 - 0.9 * look + 1.1 * relief, gaze=look * 0.6))
    shake = 0.05 * np.exp(-6 * max(ts, 0)) * np.sin(38 * ts) if ts > 0 else 0.0
    if t < T_CUT:   # S2: sobre o ombro, na calçada, vendo o carro chegar de frente
        e = sstep(0.0, T_CUT, t)
        cam = Camera(lerp((3.6, 1.45, 4.9), (2.3, 2.0, 6.0), e), lerp((-3.0, 1.0, 3.4), (-4.4, 0.6, 1.0), e), vfov=lerp(54, 50, e))
    else:           # S3: contra-plano por cima do capô, reação e alívio
        e = sstep(T_CUT, 5.0, t)
        cam = Camera(lerp((-2.2, 1.2, -2.8), (-3.0, 1.45, -2.3), e) + V(0, shake, 0), lerp((-0.6, 1.15, 3.2), (-0.8, 1.1, 3.0), e), vfov=lerp(44, 38, e), roll=shake * 0.3)
    return ch + car(cx, 0.95, cx, pitch=pitch, drop=0.4 * abs(pitch)), cam, dict(s=s, car_x=cx, car_v=v, cam=cam.pos.tolist(), brake=br, hop=float(hop > 0))

SHOTS = {'S1': (shot1, 5.0), 'S2': (shot2, T_CUT), 'S3': (lambda t: shot2(t + T_CUT), 5.0 - T_CUT)}

if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--shot', required=True); ap.add_argument('--ss', type=float, default=2.0)
    ap.add_argument('--size', default='540x960'); ap.add_argument('--still'); ap.add_argument('--out', default='renders/preview')
    a = ap.parse_args(); W, H = map(int, a.size.split('x')); fn, dur = SHOTS[a.shot]; n = int(round(dur * FPS))
    RW, RH = int(W * a.ss), int(H * a.ss); env = environment(); os.makedirs(a.out, exist_ok=True)
    if a.still:
        for f in map(int, a.still.split(',')):
            t0 = time.time(); dyn, cam, _ = fn(f / FPS); img = tonemap(render(env + dyn, cam, RW, RH), W, H)
            cv2.imwrite(f'{a.out}/{a.shot}_f{f:03d}.png', img[..., ::-1]); print(f, round(time.time() - t0, 1), 's', flush=True)
        sys.exit()
    tmp = f'{a.out}/{a.shot}.tmp.mp4'
    ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                           '-c:v', 'libx264', '-crf', '12', '-preset', 'medium', '-pix_fmt', 'yuv420p', tmp], stdin=subprocess.PIPE)
    ev = []; t0 = time.time()
    for f in range(n):
        dyn, cam, info = fn(f / FPS); ff.stdin.write(tonemap(render(env + dyn, cam, RW, RH), W, H).tobytes()); ev.append(info)
        if f % 15 == 0: print(a.shot, f, n, round(time.time() - t0), 's', flush=True)
    ff.stdin.close()
    if ff.wait() == 0: os.replace(tmp, f'{a.out}/{a.shot}.mp4'); json.dump(dict(shot=a.shot, fps=FPS, dur=dur, sec_per_frame=(time.time() - t0) / n, frames=ev), open(f'{a.out}/{a.shot}_events.json', 'w'))
