"""Narração com VoxCPM2 (Apache-2.0) clonando a voz aprovada (amostra gerada por nós). Frase a frase, N tentativas,
escolhe pela transcrição + tom dentro da faixa da voz aprovada. Uso: narrar_vox.py roteiro.txt saida.wav ref.wav "texto da ref" [N]"""
import os, sys, re, json, difflib, numpy as np, torch, torchaudio as ta, torchaudio.functional as F, soundfile as sf
from voxcpm import VoxCPM
from faster_whisper import WhisperModel
txt, out, ref, reftext = sys.argv[1:5]; N = int(sys.argv[5]) if len(sys.argv) > 5 else 3
_fr = [s.strip() for s in re.split(r'(?<=[.!?…])\s+', open(txt).read().strip()) if s.strip()]
sents, cur = [], ""
for f in _fr:
    brk = f.lower().startswith(("opção", "comenta", "manda", "você decide"))
    if cur and (brk or len((cur + " " + f).split()) > int(os.environ.get('MAXW', 24))): sents.append(cur); cur = f
    else: cur = (cur + " " + f).strip()
    if f.lower().startswith("opção"): sents.append(cur); cur = ""
if cur: sents.append(cur)
STYLE = "(voz feminina jovem, natural e conversacional, contando uma história de suspense com calma e emoção sutil)"
m = VoxCPM.from_pretrained("openbmb/VoxCPM2", load_denoiser=False); SR = m.tts_model.sample_rate
wm = WhisperModel("small", device="cpu", compute_type="int8")
norm = lambda s: re.sub(r'[^a-zà-ú0-9 ]', ' ', s.lower().replace('pra ', 'para ').replace(' tá ', ' está ').replace('tava', 'estava')).split()
def f0(a):
    w = F.resample(torch.tensor(a, dtype=torch.float32)[None], SR, 16000)
    p = F.detect_pitch_frequency(w, 16000, freq_low=60, freq_high=400).flatten(); p = p[(p > 65) & (p < 380)]
    return float(p.median()) if len(p) else 0.0
def score(a, s):
    w = F.resample(torch.tensor(a, dtype=torch.float32)[None], SR, 16000).squeeze().numpy()
    seg, _ = wm.transcribe(w, language="pt"); hyp = " ".join(x.text for x in seg)
    r = difflib.SequenceMatcher(None, norm(s), norm(hyp)).ratio(); hz = f0(a); wps = len(s.split()) / (len(a) / SR)
    pen = 0.3 if not (float(os.environ.get('F0_LO', 160)) <= hz <= float(os.environ.get('F0_HI', 215))) else 0.0
    return r - pen - 0.15 * max(0, abs(wps - 2.6) - 0.7), hyp, hz, wps
def trim(a, thr=0.01):
    idx = np.nonzero(np.abs(a) > thr)[0]
    return a if len(idx) == 0 else a[max(0, idx[0] - int(.03*SR)): idx[-1] + int(.1*SR)]
def pause(s, nxt):
    if nxt.lower().startswith(("opção", "comenta")): return 0.85
    if s.endswith("..."): return 0.75
    return 0.45 if len(s.split()) <= 3 else 0.35
parts, log = [], []
for i, s in enumerate(sents):
    best = None
    for k in range(N):
        torch.manual_seed(100 * i + k)
        a = trim(m.generate(text=s, reference_wav_path=ref, prompt_wav_path=ref, prompt_text=reftext, cfg_value=float(os.environ.get('CFG', 1.6)), inference_timesteps=int(os.environ.get('STEPS', 20))))
        sc, hyp, hz, wps = score(a, s)
        if best is None or sc > best[0]: best = (sc, a, hyp, hz, wps)
        if sc > 0.96: break
    log.append({"i": i, "frase": s, "score": round(best[0], 3), "ouvido": best[2].strip(), "f0": round(best[3]), "palavras_s": round(best[4], 2)})
    print(i, round(best[0], 3), round(best[3]), s[:45], "|", best[2][:55], flush=True)
    parts += [best[1], np.zeros(int(pause(s, sents[i+1] if i+1 < len(sents) else "") * SR))]
a = np.concatenate(parts); sf.write(out, a, SR)
json.dump(log, open(out + ".log.json", "w"), ensure_ascii=False, indent=1); print("dur", len(a) / SR)
