import sys, soundfile as sf, numpy as np
from kokoro import KPipeline
txt=sys.argv[1]; out=sys.argv[2]; voice=sys.argv[3]
p=KPipeline(lang_code='p')
a=np.concatenate([au for _,_,au in p(txt, voice=voice)])
sf.write(out,a,24000); print(out, len(a)/24000)
