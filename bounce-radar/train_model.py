"""Fit and validate the scoring model for weekly buy-side false breakouts. Prints the MODEL dict for radar.py.
Train: signals before 2015. Test (out of sample): 2015 onward. Target: +5% reached before a weekly close below the wick, within 13 weeks."""
import sys,os,json,concurrent.futures as cf,numpy as np
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)));import radar as R
R.contrarian=lambda s,D:None;R.get4h=lambda s:None
def levels(B):
    idx={b[0]:i for i,b in enumerate(B)};out=[];TOL,REV,BRK=R.TOL,R.REV,R.BRK
    for t,p in R.zigzag(B):
        if any(abs(L['p']-p)/p<=TOL and L['t0']<t and (L['brk'] is None or L['brk']>t) for L in out): continue
        L={'p':p,'t0':t,'holds':[t],'brk':None};out.append(L);st='away'
        for j in range(idx[t]+1,len(B)):
            lo,hi,c=B[j][1:4]
            if st=='away':
                if hi>=p*(1+2*TOL+.05): side,st='S','wait'
                elif lo<=p*(1-2*TOL-.05): side,st='R','wait'
            elif st=='wait':
                if (side=='S' and lo<=p*(1+TOL)) or (side=='R' and hi>=p*(1-TOL)): st='touch'
            else:
                if (side=='S' and c<p*(1-BRK)) or (side=='R' and c>p*(1+BRK)): L['brk']=B[j][0];break
                if (side=='S' and hi>=p*(1+REV)) or (side=='R' and lo<=p*(1-REV)): L['holds'].append(B[j][0]);st='wait'
    return out
def run(s):
    try:
        X=R.get(s)
        if not X or len(X[0])<260: return []
        B=X[0];Ls=levels(B);res=[]
        for i in range(60,len(B)-14):
            t=B[i][0];last=B[i];prev=B[i-1];pre=[x[3] for x in B[i-5:i-1]];lo=min(last[1],prev[1]);c=last[3]
            for L in Ls:
                p=L['p']
                if not(p<=c<=p*1.03): continue
                h=sum(1 for x in L['holds'] if x<t)
                if L['t0']>=t or (L['brk'] and L['brk']<=t) or h<3: continue
                if min(pre)>p and p*0.92<=lo<=p*0.99 and (prev[3]<p or last[1]<=p*0.99):
                    f=R.feats(B,i,p,lo,h,SPY)
                    if not f: continue
                    y=0
                    for x in B[i+1:i+14]:
                        if x[2]>=c*1.05: y=1;break
                        if x[3]<lo: break
                    res.append((t,[f[n] for n in R.FEATS],y))
        return res
    except Exception as e: return []
SPY=R.spy_map();S=open(os.path.join(R.H,'tickers.txt')).read().split();o=[]
with cf.ThreadPoolExecutor(12) as ex:
    for r in ex.map(run,S): o+=r
T=np.array([a[0] for a in o]);X=np.array([a[1] for a in o]);Y=np.array([a[2] for a in o],float)
tr=T<1420070400;te=~tr
mu=X[tr].mean(0);sd=X[tr].std(0)+1e-9;Z=(X-mu)/sd
w=np.zeros(Z.shape[1]);b=0.0
for _ in range(4000):
    p=1/(1+np.exp(-(Z[tr]@w+b)));g=Z[tr].T@(p-Y[tr])/tr.sum()+0.01*w;w-=0.3*g;b-=0.3*(p-Y[tr]).mean()
P=1/(1+np.exp(-(Z@w+b)));cut=[float(np.quantile(P[tr],1/3)),float(np.quantile(P[tr],2/3))]
def auc(p,y):
    r=p.argsort().argsort()+1;n1=y.sum();n0=len(y)-n1
    return (r[y==1].sum()-n1*(n1+1)/2)/(n1*n0)
def grades(m):
    out={}
    for g,sel in (('C',P<cut[0]),('B',(P>=cut[0])&(P<cut[1])),('A',P>=cut[1])):
        k=m&sel;out[g]=[int(k.sum()),round(100*Y[k].mean(),1) if k.sum() else None]
    return out
pos=X[:,R.FEATS.index('pos')];mid=(pos>=0.2)&(pos<=0.8)
info=dict(n_train=int(tr.sum()),n_test=int(te.sum()),base_test=round(100*Y[te].mean(),1),auc_train=round(float(auc(P[tr],Y[tr])),3),auc_test=round(float(auc(P[te],Y[te])),3),
    test=grades(te),test_mid=grades(te&mid),base_test_mid=round(100*Y[te&mid].mean(),1),n_test_mid=int((te&mid).sum()))
print('WEIGHTS',dict(zip(R.FEATS,[round(float(x),3) for x in w])))
print('UNIVARIATE (test set: win rate when feature is below / above its median)')
for j,n in enumerate(R.FEATS):
    m=np.median(X[te,j]);print(' ',n,round(100*Y[te&(X[:,j]<=m)].mean(),1),round(100*Y[te&(X[:,j]>m)].mean(),1))
print('INFO',json.dumps(info))
print('MODEL',json.dumps(dict(w=[round(float(x),4) for x in w],b=round(float(b),4),mu=[round(float(x),5) for x in mu],sd=[round(float(x),5) for x in sd],cut=[round(x,4) for x in cut],info=info)))
