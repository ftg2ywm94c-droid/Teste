#!/usr/bin/env python3
"""Auditoria frame a frame dos vídeos de referência.
Uso: python3 scripts/audit_references.py references/ analysis/
Mede (por frame): brilho, saturação, nitidez, diferença de histograma, fluxo óptico.
Detecta cortes, extrai contact sheets (1 s) e keyframes por corte, faz OCR das
legendas queimadas e mede o áudio (loudness/silêncios)."""
import sys, os, json, subprocess, glob, re
import numpy as np, cv2

def ffprobe(p):
    o = subprocess.run(["ffprobe","-v","error","-show_format","-show_streams","-of","json",p],capture_output=True,text=True).stdout
    return json.loads(o)

def ocr(img):
    """OCR da legenda queimada: máscara de pixels brancos pouco saturados."""
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    m = ((hsv[...,2] > 235) & (hsv[...,1] < 30)).astype(np.uint8)*255
    if m.mean() < 1.5: return ""
    m = cv2.copyMakeBorder(cv2.resize(255-m, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC),20,20,20,20,cv2.BORDER_CONSTANT,value=255)
    r = subprocess.run(["tesseract","stdin","stdout","--psm","7","-l","eng"],input=cv2.imencode(".png", m)[1].tobytes(),capture_output=True)
    return re.sub(r"[^A-Za-z0-9' ,.!?]","",r.stdout.decode(errors="ignore")).strip(" .,'")

def audit(path, out, name):
    os.makedirs(f"{out}/reference_contact_sheets", exist_ok=True)
    os.makedirs(f"{out}/keyframes/{name}", exist_ok=True)
    meta = ffprobe(path)
    cap = cv2.VideoCapture(path); fps = cap.get(cv2.CAP_PROP_FPS)
    prev_h = prev_g = None; rows=[]; thumbs=[]; caps=[]; i=0; frames_small={}
    while True:
        ok, f = cap.read()
        if not ok: break
        hsv = cv2.cvtColor(f, cv2.COLOR_BGR2HSV)
        g = cv2.cvtColor(cv2.resize(f,(128,228)), cv2.COLOR_BGR2GRAY)
        h = cv2.calcHist([hsv],[0,1,2],None,[12,6,6],[0,180,0,256,0,256]); h/=h.sum()
        hd = float(cv2.compareHist(prev_h,h,cv2.HISTCMP_BHATTACHARYYA)) if prev_h is not None else 0.0
        if prev_g is not None:
            fl = cv2.calcOpticalFlowFarneback(prev_g,g,None,0.5,2,13,2,5,1.1,0)
            mag = float(np.linalg.norm(fl,axis=2).mean()); pd = float(np.abs(g.astype(int)-prev_g).mean())
        else: mag=pd=0.0
        rows.append(dict(f=i,t=round(i/fps,3),bright=float(hsv[...,2].mean()),sat=float(hsv[...,1].mean()),
                         hue=float(np.median(hsv[...,0])),sharp=float(cv2.Laplacian(g,cv2.CV_64F).var()),
                         hist_diff=hd,flow=mag,pix_diff=pd))
        if i % int(round(fps)) == 0:
            t = cv2.resize(f,(128,228)); cv2.putText(t,f"{i//int(round(fps))}s",(4,16),0,0.5,(255,255,255),2); thumbs.append(t)
        if i % 3 == 0:
            H=f.shape[0]; caps.append((round(i/fps,2), ocr(f[int(H*.675):int(H*.735), 40:-40])))
        prev_h, prev_g = h, g; i+=1
    # cortes: pico local de diferença de histograma, >3x a mediana local (robusto a câmera em movimento)
    hd=np.array([r["hist_diff"] for r in rows])
    for k in range(2,len(hd)-2):
        if hd[k]>0.22 and hd[k]==hd[k-2:k+3].max() and hd[k]>3*np.median(hd[max(0,k-12):k+12]):
            rows[k]["cut"]=True; cap.set(cv2.CAP_PROP_POS_FRAMES,k); ok,f=cap.read()
            if ok: cv2.imwrite(f"{out}/keyframes/{name}/cut_{k:05d}_{k/fps:06.2f}s.jpg", cv2.resize(f,(256,455)))
    cap.release()
    cols=10; pad=[np.zeros_like(thumbs[0])]*((-len(thumbs))%cols); th=thumbs+pad
    sheet=np.vstack([np.hstack(th[r:r+cols]) for r in range(0,len(th),cols)])
    cv2.imwrite(f"{out}/reference_contact_sheets/{name}_1s.jpg", sheet)
    cuts=[r["t"] for r in rows if r.get("cut")]
    shots=np.diff([0]+cuts+[rows[-1]["t"]])
    # legenda: colapsa repetições
    words=[]
    for t,w in caps:
        if w and len(w)>1 and re.search('[A-Za-z]{2}',w) and (not words or words[-1][1].lower()!=w.lower()): words.append((t,w))
    # áudio
    a = subprocess.run(["ffmpeg","-hide_banner","-i",path,"-af","silencedetect=n=-35dB:d=0.35,ebur128","-f","null","-"],capture_output=True,text=True).stderr
    sil=[(float(s),float(e)) for s,e in zip(re.findall(r"silence_start: ([\d.]+)",a),re.findall(r"silence_end: ([\d.]+)",a))]
    lufs=re.findall(r"I:\s+(-?[\d.]+) LUFS",a); lra=re.findall(r"LRA:\s+([\d.]+) LU",a)
    arr=lambda k: np.array([r[k] for r in rows])
    v=[s for s in meta["streams"] if s["codec_type"]=="video"][0]
    summ=dict(file=os.path.basename(os.path.realpath(path)),duration=float(meta["format"]["duration"]),bitrate=int(meta["format"]["bit_rate"]),
        video=dict(codec=v["codec_name"],w=v["width"],h=v["height"],fps=v["r_frame_rate"],frames=i),
        audio={k:[s for s in meta["streams"] if s["codec_type"]=="audio"][0][k] for k in("codec_name","sample_rate","channels")},
        cuts=cuts,n_cuts=len(cuts),shot_len=dict(mean=float(shots.mean()),median=float(np.median(shots)),min=float(shots.min()),max=float(shots.max())),
        brightness_mean=float(arr("bright").mean()),saturation_mean=float(arr("sat").mean()),
        flow_mean=float(arr("flow").mean()),static_frames_pct=float((arr("pix_diff")[1:]<0.15).mean()*100),
        dark_pct=float((arr("bright")<90).mean()*100),
        caption_words_ocr=words,caption_changes_per_s=len(words)/float(meta["format"]["duration"]),
        loudness_lufs=float(lufs[-1]) if lufs else None,lra=float(lra[-1]) if lra else None,silences=sil)
    return summ, rows

if __name__=="__main__":
    ref,out=sys.argv[1],sys.argv[2]; res={}
    for p in sorted(glob.glob(f"{ref}/*.mov")+glob.glob(f"{ref}/*.mp4")):
        n=os.path.splitext(os.path.basename(p))[0]; s,rows=audit(p,out,n); res[n]=s
        json.dump(rows,open(f"{out}/{n}_per_frame.json","w"))
        print(n,s["duration"],s["n_cuts"],s["shot_len"],round(s["flow_mean"],2),s["loudness_lufs"],flush=True)
    json.dump(res,open(f"{out}/reference_analysis.json","w"),indent=1)
