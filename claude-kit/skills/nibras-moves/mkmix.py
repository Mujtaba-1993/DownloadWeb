# build a beat-accurate mix from named parts of the original excerpt; prints cut frames + opening offsets
import numpy as np, soundfile as sf, json, sys
U={'FL':(0,1.09,0),'B1':(2.40,3.19,.33),'B2':(3.19,4.27,.54),'G1':(4.27,5.33,.52),'G2':(5.33,6.36,.51),'G3':(6.36,7.40,.52)}
def build(names,out,src='/root/films/nibras/types/music/orig1.wav'):
    y,sr=sf.read(src); d=0.012; xf=int(0.008*sr); o=np.zeros((0,2)); T=[0.0]; op=[]
    for nm in names:
        a0,b0,s=U[nm]; a,b=int(max(0,a0-d)*sr) if a0>0 else 0,min(len(y),int((b0-d)*sr)); pre=max(0,a-xf); ch=y[pre:b].copy(); n0=a-pre
        if len(o) and n0>0:
            w=np.linspace(0,1,n0)[:,None]; o[-n0:]=o[-n0:]*np.cos(w*np.pi/2)+ch[:n0]*np.sin(w*np.pi/2)
        o=np.concatenate([o,ch[n0:]]); T.append(len(o)/sr); op.append(int(round((s+d)*30)))
    NF=int(round(T[-1]*30)); cuts=[int(round(t*30-0.3)) for t in T[1:-1]]; n=int(NF/30*sr); o=o[:n]; o=np.concatenate([o,np.zeros((max(0,n-len(o)),2))]); k=int(.004*sr); o[-k:]*=np.linspace(1,0,k)[:,None]
    sf.write(out,o,sr); return {'cuts':cuts,'NF':NF,'open':op[1:]}
if __name__=='__main__': print(json.dumps(build(sys.argv[2].split(','),sys.argv[1])))
