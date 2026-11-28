import sys, soundfile as sf
from voxcpm import VoxCPM
m = VoxCPM.from_pretrained("openbmb/VoxCPM2", load_denoiser=False)
outdir = sys.argv[1]; txt = sys.argv[2]
designs = {
 "F_narradora_suspense": "(Uma mulher brasileira de uns 30 anos, voz natural e calorosa, narrando uma história de suspense com tom baixo e envolvente, ritmo calmo, sotaque brasileiro)",
 "F_jovem_natural": "(Mulher jovem brasileira, voz clara e natural, tom de conversa, como uma criadora de conteúdo contando uma história, sotaque de São Paulo)",
}
for name, d in designs.items():
    for k in range(2):
        wav = m.generate(text=d + txt, cfg_value=2.0, inference_timesteps=10)
        sf.write(f"{outdir}/vox_{name}_{k}.wav", wav, m.tts_model.sample_rate); print(name, k, len(wav)/m.tts_model.sample_rate, flush=True)
