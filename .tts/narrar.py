"""Narração por frase com Chatterbox multilíngue (MIT): N tentativas por frase, escolhe pela transcrição (faster-whisper)
e pela velocidade de fala; junta com pausas de narrador. Uso: narrar.py roteiro.txt saida.wav ref.wav [N] [exag]"""
import sys, re, json, subprocess, numpy as np, torch, torchaudio as ta, difflib
from chatterbox.mtl_tts import ChatterboxMultilingualTTS
txt, out, ref = sys.argv[1], sys.argv[2], sys.argv[3]
N = int(sys.argv[4]) if len(sys.argv) > 4 else 3; EX = float(sys.argv[5]) if len(sys.argv) > 5 else 0.55
text = open(txt).read().strip()
sents = [s.strip() for s in re.split(r'(?<=[.!?…])\s+|(?<=\.\.\.)\s+', text) if s.strip()]
m = ChatterboxMultilingualTTS.from_pretrained(device="cpu"); SR = m.sr
from faster_whisper import WhisperModel
wm = WhisperModel("small", device="cpu", compute_type="int8")
norm = lambda s: re.sub(r'[^a-zà-ú0-9 ]', ' ', s.lower()).split()
def score(wav, s):
    a = ta.functional.resample(wav, SR, 16000).squeeze().numpy().astype(np.float32)
    seg, _ = wm.transcribe(a, language="pt"); hyp = " ".join(x.text for x in seg)
    r = difflib.SequenceMatcher(None, norm(s), norm(hyp)).ratio()
    wps = len(s.split()) / (wav.shape[-1] / SR)
    return r - 0.15 * max(0, abs(wps - 2.5) - 0.6), hyp, wps
def trim(w, thr=0.01):
    x = w.abs().squeeze(); idx = (x > thr).nonzero()
    if len(idx) == 0: return w
    a, b = max(0, idx[0].item() - int(.03*SR)), min(w.shape[-1], idx[-1].item() + int(.08*SR)); return w[:, a:b]
def pause(s, nxt):
    if nxt and nxt.lower().startswith(("opção", "comenta")): return 0.85
    if s.endswith("..."): return 0.75
    if s.endswith("?") or s.endswith("!"): return 0.5
    if len(s.split()) <= 3: return 0.45
    return 0.38
parts, log = [], []
for i, s in enumerate(sents):
    best = None
    for k in range(N):
        torch.manual_seed(1000 * i + k)
        w = trim(m.generate(s, language_id="pt", audio_prompt_path=ref, exaggeration=EX, cfg_weight=0.45, temperature=0.75))
        sc, hyp, wps = score(w, s)
        if best is None or sc > best[0]: best = (sc, w, hyp, wps)
        if sc > 0.97: break
    log.append({"i": i, "frase": s, "score": round(best[0], 3), "ouvido": best[2], "palavras_s": round(best[3], 2)})
    print(i, round(best[0], 3), s[:50], "|", best[2][:60], flush=True)
    parts.append(best[1]); parts.append(torch.zeros(1, int(pause(s, sents[i+1] if i+1 < len(sents) else "") * SR)))
w = torch.cat(parts, -1); ta.save(out, w, SR)
json.dump(log, open(out + ".log.json", "w"), ensure_ascii=False, indent=1); print("dur", w.shape[-1] / SR)
