import sys, torch, torchaudio as ta
from chatterbox.mtl_tts import ChatterboxMultilingualTTS
txt, out = sys.argv[1], sys.argv[2]
ex = float(sys.argv[3]) if len(sys.argv)>3 else 0.5
m = ChatterboxMultilingualTTS.from_pretrained(device="cpu")
w = m.generate(txt, language_id="pt", exaggeration=ex, cfg_weight=0.5)
ta.save(out, w, m.sr); print(out, w.shape[-1]/m.sr)
