"""Fit and validate the scoring model for contrarian buys (panic drop, 52-week low). Prints CMODEL for radar.py.
Train: signals before 2015. Test: 2015 onward. Target: the stock's high reaches the signal's average 60-day gain within 60 trading days."""
import sys,os,json,concurrent.futures as cf,numpy as np
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)));import radar as R
R.get4h=lambda s:None;R.COLLECT=[];R.SPY.update(R.spy_map())
S=open(os.path.join(R.H,'tickers.txt')).read().split()
with cf.ThreadPoolExecutor(12) as ex: list(ex.map(R.get,S))
o=[e for e in R.COLLECT if e[0]>=757382400]  # 1994+: market-regime data exists
T=np.array([a[0] for a in o]);K=np.array([a[1] for a in o]);X=np.array([a[2] for a in o]);Y=np.array([a[3] for a in o],float)
tr=T<1420070400;te=~tr
mu=X[tr].mean(0);sd=X[tr].std(0)+1e-9;Z=(X-mu)/sd;w=np.zeros(Z.shape[1]);b=0.0
for _ in range(4000):
    p=1/(1+np.exp(-(Z[tr]@w+b)));w-=0.3*(Z[tr].T@(p-Y[tr])/tr.sum()+0.01*w);b-=0.3*(p-Y[tr]).mean()
P=1/(1+np.exp(-(Z@w+b)));cut=[float(np.quantile(P[tr],1/3)),float(np.quantile(P[tr],2/3))]
def auc(p,y):
    r=p.argsort().argsort()+1;n1=y.sum();n0=len(y)-n1
    return (r[y==1].sum()-n1*(n1+1)/2)/(n1*n0)
def grades(m):
    return {g:[int((m&sel).sum()),round(100*Y[m&sel].mean(),1)] for g,sel in (('C',P<cut[0]),('B',(P>=cut[0])&(P<cut[1])),('A',P>=cut[1]))}
info=dict(n_train=int(tr.sum()),n_test=int(te.sum()),base_test=round(100*Y[te].mean(),1),auc_train=round(float(auc(P[tr],Y[tr])),3),auc_test=round(float(auc(P[te],Y[te])),3),
    test=grades(te),base={k:round(100*Y[te&(K==k)].mean(),1) for k in ('panic','lo52')},n={k:int((te&(K==k)).sum()) for k in ('panic','lo52')})
print('WEIGHTS',dict(zip(R.CFEATS,[round(float(x),3) for x in w])))
print('INFO',json.dumps(info))
print('CMODEL',json.dumps(dict(w=[round(float(x),4) for x in w],b=round(float(b),4),mu=[round(float(x),6) for x in mu],sd=[round(float(x),6) for x in sd],cut=[round(x,4) for x in cut],info=info)))
