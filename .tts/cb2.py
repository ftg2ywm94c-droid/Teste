import sys, torchaudio as ta
from chatterbox.mtl_tts import ChatterboxMultilingualTTS
txt,out,ref,ex=sys.argv[1],sys.argv[2],sys.argv[3],float(sys.argv[4])
m=ChatterboxMultilingualTTS.from_pretrained(device="cpu")
w=m.generate(txt,language_id="pt",audio_prompt_path=ref,exaggeration=ex,cfg_weight=0.4)
ta.save(out,w,m.sr); print(out,w.shape[-1]/m.sr)
