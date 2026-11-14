#!/usr/bin/env python3
"""Concatena os planos, gera a legenda ASS palavra a palavra e faz o encode final com áudio.
Uso: python3 scripts/assemble.py"""
import subprocess, json, os
P = 'renders/preview'; shots = json.load(open('shots/shots.json'))
open(f'{P}/concat.txt', 'w').write(''.join(f"file '{s['id']}.mp4'\n" for s in shots['shots']))
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', f'{P}/concat.txt', '-c', 'copy', f'{P}/video_only.mp4'], check=True)
def ts(t): return f"{int(t // 3600)}:{int(t // 60 % 60):02d}:{t % 60:05.2f}"
ass = """[Script Info]
; Tempos ESTIMADOS a partir do roteiro: não há narração gravada nesta prova (sem TTS pt-BR no ambiente).
; Com edge-tts, substituir por tempos de palavra reais (WordBoundary) antes do corte final.
ScriptType: v4.00+
PlayResX: 540
PlayResY: 960
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: W,Poppins,62,&H00FFFFFF,&H00FFFFFF,&H00000000,&H96000000,-1,0,0,0,100,100,0,0,1,5,2,2,40,40,240,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
for w in shots['captions']:
    ass += f"Dialogue: 0,{ts(w['start'])},{ts(w['end'])},W,,0,0,0,,{{\\fscx88\\fscy88\\t(0,70,\\fscx100\\fscy100)}}{w['text']}\n"
open('output/captions.ass', 'w').write(ass)
out = 'output/poc_540x960.tmp.mp4'
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', f'{P}/video_only.mp4', '-i', 'audio/sfx/mix.wav', '-vf', 'ass=output/captions.ass:fontsdir=fonts',
                '-map', '0:v', '-map', '1:a', '-c:v', 'libx264', '-crf', '17', '-preset', 'slow', '-pix_fmt', 'yuv420p', '-r', '30',
                '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-shortest', '-movflags', '+faststart', out], check=True)
os.replace(out, 'output/poc_540x960.mp4'); print('ok output/poc_540x960.mp4')
