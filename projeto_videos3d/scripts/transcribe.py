#!/usr/bin/env python3
"""Transcreve a narração com faster-whisper (tempo por palavra) e salva JSON.
Uso: python3 scripts/transcribe.py narracao/01_narracao.mp3 analysis/narracao/01_words.json [modelo]"""
import os, sys, json, subprocess, numpy as np
from faster_whisper import WhisperModel
src, dst = sys.argv[1], sys.argv[2]; model = sys.argv[3] if len(sys.argv) > 3 else 'medium'
raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', src, '-ac', '1', '-ar', '16000', '-f', 'f32le', '-'], check=True, capture_output=True).stdout
m = WhisperModel(model, device='cpu', compute_type='int8', cpu_threads=4)
segs, info = m.transcribe(np.frombuffer(raw, np.float32), language='pt', word_timestamps=True, beam_size=5, vad_filter=False,
                          initial_prompt=os.environ.get('WHISPER_PROMPT', 'Téo, quilômetros por hora, distância de frenagem.'))
words = [dict(w=w.word.strip(), s=round(w.start, 3), e=round(w.end, 3), p=round(w.probability, 3)) for s in segs for w in s.words]
json.dump(dict(model=model, words=words), open(dst, 'w'), ensure_ascii=False, indent=0)
print(' '.join(w['w'] for w in words)); print(len(words), 'palavras; fim', words[-1]['e'])
