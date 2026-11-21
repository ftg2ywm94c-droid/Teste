import sys, numpy as np, soundfile as sf, torch
_orig = torch.load
torch.load = lambda *a, **k: _orig(*a, **{**k, "weights_only": False})
from bark import SAMPLE_RATE, generate_audio, preload_models
preload_models()
txt, outdir = sys.argv[1], sys.argv[2]
for sp in sys.argv[3:]:
    np.random.seed(0); torch.manual_seed(0)
    a = generate_audio(txt, history_prompt=f"v2/{sp}", text_temp=0.6, waveform_temp=0.6)
    sf.write(f"{outdir}/bark_{sp}.wav", a, SAMPLE_RATE); print(sp, len(a)/SAMPLE_RATE, flush=True)
