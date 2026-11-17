"""Bounce radar: scan S&P 500 for prices near repeatedly-held levels and render the HTML page.
Usage: python3 radar.py OUT.html"""
import json,sys,os,urllib.request,concurrent.futures as cf,datetime as d
H=os.path.dirname(os.path.abspath(__file__))
TOL,REV,BRK,NEAR=0.03,0.15,0.10,0.05
def get(s):
    for _ in range(3):
        try:
            u=f"https://query1.finance.yahoo.com/v8/finance/chart/{s}?period1=0&period2=4000000000&interval=1d"
            r=json.load(urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'}),timeout=40))['chart']['result'][0]
            q=r['indicators']['quote'][0];W={};Dd=[]
            for a,o,l,h,c,v in zip(r['timestamp'],q['open'],q['low'],q['high'],q['close'],q['volume']):
                if not(l and h and c): continue
                Dd.append((a,o or c,h,l,c,v or 0))
                k=d.datetime.fromtimestamp(a,d.timezone.utc).isocalendar()[:2]
                if k in W: x=W[k];W[k]=[x[0],min(x[1],l),max(x[2],h),c,x[4]+(v or 0)]
                else: W[k]=[a,l,h,c,v or 0]
            ct=contrarian(s,Dd)  # computed here so the daily rows can be dropped
            return list(W.values()),ct,get4h(s)
        except Exception: pass
def get4h(s):
    # 4-hour bars from Yahoo hourly data (last ~2 years): 09:30-13:30 and 13:30-16:00 local. Only closed bars are returned.
    import time
    for _ in range(3):
        try:
            now=int(time.time());u=f"https://query1.finance.yahoo.com/v8/finance/chart/{s}?period1={now-120*86400}&period2={now}&interval=1h"
            r=json.load(urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'}),timeout=40))['chart']['result'][0]
            q=r['indicators']['quote'][0];off=r['meta']['gmtoffset'];W={}
            for a,l,h,c in zip(r['timestamp'],q['low'],q['high'],q['close']):
                if not(l and h and c): continue
                loc=a+off;k=(loc//86400,0 if (loc%86400)<13*3600+1800 else 1)
                if k in W: x=W[k];W[k]=[x[0],min(x[1],l),max(x[2],h),c]
                else: W[k]=[a,l,h,c]
            ks=sorted(W);B=[W[k] for k in ks];cur=B[-1][3] if B else None
            if ks:
                nl=now+off;end=ks[-1][0]*86400+(13*3600+1800 if ks[-1][1]==0 else 16*3600)
                if nl<end: B=B[:-1]
            return B,cur,off
        except Exception: pass
def fakeouts4h(s,lv,X,W):
    # Same shape on 4-hour bars: 8 closes above a strong weekly level, a 1.5-5% pierce within 3 bars, then a 4h close
    # back above it. Signals from the last 10 closed bars; dropped once target 1 (+3%) is reached or a 4h close is below the wick.
    # Backtest (S&P 500, 2 years of hourly data, 223 signals): +3% reached before stop-out in ~60%, +5% in 50%, +8% in 42%.
    if not X or not X[0] or len(X[0])<25: return []
    B,cur,off=X;out=[];seen=set()
    for k in range(10):
        i=len(B)-1-k;b=B[i];c=b[3];w=B[i-2:i+1];lo=min(x[1] for x in w);after=B[i+1:]
        for L in lv:
            p=L['p']
            if not L['a'] or L['h']<3 or round(p,2) in seen: continue
            if not(p<=c<=p*1.03 and p*0.95<=lo<=p*0.985 and (B[i-1][3]<p or b[1]<=p*0.985)): continue
            if min(x[3] for x in B[i-10:i-2])<=p: continue
            seen.add(round(p,2));ps=pos52(W[-53:],c)
            if not(MID[0]<=ps<=MID[1]): continue
            if any(x[3]<lo for x in after) or cur<lo or max([x[2] for x in after]+[cur])>=c*1.03: continue
            t=d.datetime.fromtimestamp(b[0]+off,d.timezone.utc)
            out.append(dict(s=s,side='دعم',level=round(p,2),holds=L['h'],close=round(c,2),ext=round(lo,2),pen=round((1-lo/p)*100,1),wk=t.strftime('%Y-%m-%d ')+('صباحاً' if t.hour<13 else 'مساءً'),age=k,hit=0,pos=round(ps*100),cur=round(cur,2),chg=round((cur/c-1)*100,1),T=[round(c*1.03,2),round(c*1.05,2),round(c*1.08,2)],kind='4 ساعات'))
    return out
try:
    from zoneinfo import ZoneInfo
    NY=ZoneInfo('America/New_York')
except Exception: NY=d.timezone(d.timedelta(hours=-5))
def ny_now(): return d.datetime.now(NY)
def ny_date(ts): return d.datetime.fromtimestamp(ts,NY).date()
# --- Contrarian study: what the crowd typically does on a signal, and what happened next ---
# key: (crowd action, contrarian direction) ; +1 = contrarian buys, -1 = contrarian sells/avoids
CT={'panic':1,'fomo':-1,'hi52':-1,'lo52':1,'rsi70':1,'rsi30':-1,'golden':-1,'death':1}
def contrarian(s,Dd):
    full=Dd;ny=ny_now()
    if Dd and ny_date(Dd[-1][0])==ny.date() and (ny.hour,ny.minute)<(16,15): Dd=Dd[:-1]  # today's candle not closed
    n=len(Dd)
    if n<320: return None
    from collections import deque
    c=[x[4] for x in Dd];o=[x[1] for x in Dd];v=[x[5] for x in Dd];t=[x[0] for x in Dd]
    cs=[0.0];vs=[0.0]
    for i in range(n): cs.append(cs[-1]+c[i]);vs.append(vs[-1]+v[i])
    ev=[];base={};last={};cand=[];hq=deque();lq=deque();lastHi=lastLo=-999;ag=al=0.0;rsi_prev=50.0;ma_prev=None
    def fire(k,i):
        if i-last.get(k,-99)<20: return
        last[k]=i
        if i+1>=n:
            if i>=n-10: cand.append((k,i))
            return
        e=o[i+1];f20=c[i+20]/e-1 if i+20<n else None;f60=c[i+60]/e-1 if i+60<n else None
        ev.append((k,t[i]//2629800,f20,f60))
        if i>=n-10: cand.append((k,i))
    for i in range(1,n):
        ch=c[i]-c[i-1];g=max(ch,0);l=max(-ch,0)
        if i<=14: ag+=g/14;al+=l/14
        else: ag=(ag*13+g)/14;al=(al*13+l)/14
        rsi=100-100/(1+ag/al) if al>0 else 100.0
        # rolling 252-day high/low of close, excluding today
        if i>=253:
            while hq and hq[0]<i-252: hq.popleft()
            while lq and lq[0]<i-252: lq.popleft()
            if c[i]>c[hq[0]]:
                if i-lastHi>60: fire('hi52',i)
                lastHi=i
            if c[i]<c[lq[0]]:
                if i-lastLo>60: fire('lo52',i)
                lastLo=i
        while hq and c[hq[-1]]<=c[i]: hq.pop()
        hq.append(i)
        while lq and c[lq[-1]]>=c[i]: lq.pop()
        lq.append(i)
        if i>=200:
            r=ch/c[i-1];av=(vs[i]-vs[i-50])/50
            if av>0 and v[i]>=2.5*av:
                if r<=-0.07: fire('panic',i)
                elif r>=0.07: fire('fomo',i)
            if rsi_prev<70<=rsi: fire('rsi70',i)
            if rsi_prev>30>=rsi: fire('rsi30',i)
            ma=(cs[i+1]-cs[i-49])/50-(cs[i+1]-cs[i-199])/200
            if ma_prev is not None:
                if ma_prev<=0<ma: fire('golden',i)
                if ma_prev>=0>ma: fire('death',i)
            ma_prev=ma
            if i%5==0 and i+60<n:
                e=o[i+1];m=t[i]//2629800;bb=base.setdefault(m,[0.0,0.0,0])
                bb[0]+=c[i+20]/e-1;bb[1]+=c[i+60]/e-1;bb[2]+=1
        rsi_prev=rsi
    cur=full[-1][4]
    cd=[dict(s=s,k=k,date=ny_date(t[i]).isoformat(),sig=round(c[i],2),cur=round(cur,2),chg=round((cur/c[i]-1)*100,1),mx=round(max([x[2] for x in full[i+1:]]+[cur]),2)) for k,i in cand]
    return ev,base,cd
def ct_stats(evs,base):
    import statistics as S
    bm={m:(x[0]/x[2],x[1]/x[2]) for m,x in base.items() if x[2]>=20}
    out={}
    for k,dr in CT.items():
        E=[e for e in evs if e[0]==k and e[3] is not None and e[1] in bm]
        if len(E)<200: continue
        mon={}
        for _,m,f20,f60 in E: mon.setdefault(m,[]).append((f20-bm[m][0],f60-bm[m][1]))
        ex60=[S.mean(x[1] for x in v) for v in mon.values()];ex20=[S.mean(x[0] for x in v) for v in mon.values()]
        cut=1262304000//2629800  # 2010-01
        h1=[S.mean(x[1] for x in v) for m,v in mon.items() if m<cut];h2=[S.mean(x[1] for x in v) for m,v in mon.items() if m>=cut]
        m60=S.mean(ex60);tt=m60/(S.stdev(ex60)/len(ex60)**.5)
        a1=S.mean(h1) if h1 else 0;a2=S.mean(h2) if h2 else 0
        if tt*dr>2 and a1*dr>0 and a2*dr>0: vd='win'      # doing the opposite of the crowd worked
        elif tt*dr<-2 and a1*dr<0 and a2*dr<0: vd='lose'  # the crowd was right
        else: vd='none'
        out[k]=dict(n=len(E),raw60=round(100*S.mean(e[3] for e in E),1),pos60=round(100*sum(e[3]>0 for e in E)/len(E)),ex20=round(100*S.mean(ex20),1),ex60=round(100*m60,1),t=round(tt,1),h1=round(100*a1,1),h2=round(100*a2,1),dir=dr,vd=vd)
    return out
def zigzag(B):
    P=[];trend=0;ext=B[0]
    for b in B:
        if trend>=0:
            if b[2]>=ext[2]: ext=b
            if b[1]<=ext[2]*(1-REV): P.append((ext[0],ext[2]));trend=-1;ext=b;continue
        if trend<=0:
            if b[1]<=ext[1]: ext=b
            if b[2]>=ext[1]*(1+REV): P.append((ext[0],ext[1]));trend=1;ext=b
    return P
def track(B):
    idx={b[0]:i for i,b in enumerate(B)};levels=[];ev=[]
    for t,price in zigzag(B):
        if any(L['a'] and abs(L['p']-price)/price<=TOL for L in levels): continue
        L={'p':price,'a':True,'h':1};levels.append(L);st='away';p=price
        for j in range(idx[t]+1,len(B)):
            lo,hi,c=B[j][1],B[j][2],B[j][3]
            if st=='away':
                if hi>=p*(1+2*TOL+.05): side,st='S','wait'
                elif lo<=p*(1-2*TOL-.05): side,st='R','wait'
            elif st=='wait':
                if (side=='S' and lo<=p*(1+TOL)) or (side=='R' and hi>=p*(1-TOL)):
                    st='touch';w=[x[3] for x in B[max(0,j-40):j]];tr='up' if B[j-1][3]>sum(w)/len(w) else 'dn'
            else:
                if (side=='S' and c<p*(1-BRK)) or (side=='R' and c>p*(1+BRK)): ev.append((L['h'],1,side,tr));L['a']=False;break
                if (side=='S' and hi>=p*(1+REV)) or (side=='R' and lo<=p*(1-REV)): ev.append((L['h'],0,side,tr));L['h']+=1;st='wait'
    return levels,ev
MODEL={"w": [0.2222, 0.0105, 0.0613, 0.091, 0.0657, -0.1411, 0.0486, 0.0518, 0.1216, 0.1329, -0.0496], "b": 0.477, "mu": [0.0328, 0.72148, 4.01462, 1.16078, 0.52638, -0.10803, -0.02809, 0.33343, 0.08595, 0.01259, -0.09784], "sd": [0.01849, 0.44827, 1.30825, 0.62904, 0.24674, 0.16369, 0.11541, 0.28163, 0.04494, 0.00875, 0.15055], "cut": [0.566, 0.6497], "info": {"n_train": 2463, "n_test": 1349, "base_test": 65.0, "auc_train": 0.611, "auc_test": 0.611, "test": {"C": [506, 56.1], "B": [497, 66.8], "A": [346, 75.4]}, "test_mid": {"C": [260, 56.5], "B": [192, 66.1], "A": [94, 68.1]}, "base_test_mid": 61.9, "n_test_mid": 546}}  # from train_model.py: logistic model scoring weekly buy-side false breakouts
FEATS=['pen','same','holds','rvol','clv','trend','mkt','pos','atr','margin','mom13']
def spy_map():
    # market regime per ISO week: S&P 500 ETF close relative to its 40-week average
    u="https://query1.finance.yahoo.com/v8/finance/chart/SPY?period1=0&period2=4000000000&interval=1wk"
    for _ in range(3):
        try:
            r=json.load(urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'}),timeout=40))['chart']['result'][0]
            X=[(a,c) for a,c in zip(r['timestamp'],r['indicators']['quote'][0]['close']) if c];m={}
            for i in range(40,len(X)):
                k=d.datetime.fromtimestamp(X[i][0],d.timezone.utc).isocalendar()[:2]
                m[k]=X[i][1]/(sum(x[1] for x in X[i-40:i])/40)-1
            return m
        except Exception: pass
    return {}
def feats(C,i,p,lo,holds,spy):
    # C: closed weekly bars [ts,low,high,close,vol]; i: signal week. Returns None if history is too short.
    if i<53: return None
    b=C[i];c=b[3];k=d.datetime.fromtimestamp(b[0],d.timezone.utc).isocalendar()[:2]
    if k not in spy: return None
    av=sum(x[4] for x in C[i-20:i])/20;rg=b[2]-b[1]
    return dict(pen=1-lo/p,same=1.0 if C[i-1][3]>=p else 0.0,holds=min(holds,8),rvol=min(b[4]/av,5) if av>0 else 1.0,
        clv=(c-b[1])/rg if rg>0 else 0.5,trend=c/(sum(x[3] for x in C[i-40:i])/40)-1,mkt=spy[k],pos=pos52(C[i-52:i+1],c),
        atr=sum((x[2]-x[1])/x[3] for x in C[i-10:i])/10,margin=c/p-1,mom13=c/C[i-13][3]-1)
def score(f):
    if not MODEL or not f: return None
    import math
    z=MODEL['b']+sum(MODEL['w'][j]*((f[n]-MODEL['mu'][j])/MODEL['sd'][j]) for j,n in enumerate(FEATS))
    pr=1/(1+math.exp(-z));g='A' if pr>=MODEL['cut'][1] else 'B' if pr>=MODEL['cut'][0] else 'C'
    return round(pr*100),g
SPY={}
MID=(0.2,0.8)  # user's choice: only signals in the middle of the 52-week range, not near its top or bottom
def pos52(W,c):
    h=max(x[2] for x in W);l=min(x[1] for x in W)
    return (c-l)/(h-l) if h>l else 0.5
def fakeouts(s,lv,B):
    # Weekly false breakout: price traded 1-8% through a strong level (>=3 holds) and a CLOSED weekly candle
    # closed back inside the zone. The 4 weekly closes before the break must all be on the right side of the level
    # (clean 'above -> pierce -> close back above' shape, not chop around the level). Signals from the last 4 closed weeks are tracked: dropped once a weekly close
    # goes beyond the wick (stop), flagged once price has already reached target 1/2/3.
    ny=ny_now();C=B
    if ny_date(B[-1][0]).isocalendar()[:2]==ny.date().isocalendar()[:2] and (ny.weekday()<4 or (ny.weekday()==4 and (ny.hour,ny.minute)<(16,15))): C=B[:-1]  # week not closed
    if len(C)<10: return []
    out=[];seen=set();cur=B[-1][3]
    for k in range(4):
        i=len(C)-1-k;last=C[i];prev=C[i-1];pre=[x[3] for x in C[i-5:i-1]];w=C[i-1:i+1];after=B[i+1:]
        lo=min(x[1] for x in w);hi=max(x[2] for x in w);wk=ny_date(last[0]).isoformat();c=last[3]
        ps=pos52(C[max(0,i-52):i+1],c)
        if not(MID[0]<=ps<=MID[1]): continue
        for L in lv:
            p=L['p']
            if not L['a'] or L['h']<3: continue
            up=min(pre)>p and p<=c<=p*(1+TOL) and p*0.92<=lo<=p*0.99 and (prev[3]<p or last[1]<=p*0.99)
            dn=max(pre)<p and p*(1-TOL)<=c<=p and p*1.01<=hi<=p*1.08 and (prev[3]>p or last[2]>=p*1.01)
            if not(up or dn) or (round(p,2),up) in seen: continue
            seen.add((round(p,2),up))
            if up:
                T=[c*1.05,c*1.087,c*1.12];mx=max([x[2] for x in after],default=0);hit=sum(mx>=x for x in T)
                if hit or any(x[3]<lo for x in after): continue  # reached a target already, or stopped out
                sc=score(feats(C,i,p,lo,L['h'],SPY))
                out.append(dict(s=s,side='دعم',level=round(p,2),holds=L['h'],close=round(c,2),ext=round(lo,2),pen=round((1-lo/p)*100,1),wk=wk,age=k,pos=round(ps*100),hit=hit,pr=sc[0] if sc else None,grade=sc[1] if sc else None,cur=round(cur,2),chg=round((cur/c-1)*100,1),T=[round(x,2) for x in T],kind='ذيل في نفس الشمعة' if prev[3]>=p else 'رجوع بعد إغلاق تحت المستوى'))
            else:
                T=[c*0.95,c*0.946,c*0.88];mn=min([x[1] for x in after],default=9e9);hit=sum(mn<=x for x in T)
                if hit or any(x[3]>hi for x in after): continue
                out.append(dict(s=s,side='مقاومة',level=round(p,2),holds=L['h'],close=round(c,2),ext=round(hi,2),pen=round((hi/p-1)*100,1),wk=wk,age=k,pos=round(ps*100),hit=hit,cur=round(cur,2),chg=round((cur/c-1)*100,1),T=[round(x,2) for x in T],kind='ذيل في نفس الشمعة' if prev[3]<=p else 'رجوع بعد إغلاق فوق المستوى'))
    return out
def grp(h): return '1' if h==1 else '2-3' if h<=3 else '4-6' if h<=6 else '7+'
def main(out):
    SPY.update(spy_map())
    S=open(os.path.join(H,'tickers.txt')).read().split();ev=[];cand=[];cev=[];cbase={};ccand=[]
    with cf.ThreadPoolExecutor(12) as ex: data=list(ex.map(get,S))
    fake=[];fake4=[]
    okn=sum(1 for x in data if x)
    if okn<450: sys.exit(f'ERROR: only {okn} of {len(S)} stocks downloaded; not writing the page')
    for s,X in zip(S,data):
        if not X or len(X[0])<260: continue
        B,ct,X4=X
        if ct:
            cev+=ct[0];ccand+=ct[2]
            for m,x in ct[1].items():
                bb=cbase.setdefault(m,[0.0,0.0,0]);bb[0]+=x[0];bb[1]+=x[1];bb[2]+=x[2]
        lv,e=track(B)
        fake4+=fakeouts4h(s,lv,X4,B);fake+=fakeouts(s,lv,B);ev+=e;last=B[-1][3];sma=sum(x[3] for x in B[-41:-1])/40
        for L in lv:
            if L['a'] and L['h']>=3 and abs(last-L['p'])/L['p']<=NEAR:
                cand.append(dict(s=s,price=round(last,2),level=round(L['p'],2),holds=L['h'],side='دعم' if last>=L['p'] else 'مقاومة',dist=round((last/L['p']-1)*100,1),tr='صاعد' if last>sma else 'هابط'))
    st={}
    for t in 'SR':
        for tr in ('up','dn'):
            for g in ('1','2-3','4-6','7+'):
                x=[e for e in ev if e[2]==t and e[3]==tr and grp(e[0])==g];st[f'{t}|{tr}|{g}']=(round(100*sum(e[1] for e in x)/max(1,len(x))),len(x))
    by={}
    for c in cand:
        if c['s'] not in by or abs(c['dist'])<abs(by[c['s']]['dist']): by[c['s']]=c
    cur=sorted(by.values(),key=lambda c:abs(c['dist']))
    for c in cur: c['br']=st[f"{'S' if c['side']=='دعم' else 'R'}|{'up' if c['tr']=='صاعد' else 'dn'}|{grp(c['holds'])}"][0]
    fake.sort(key=lambda f:(f['side']!='دعم',-(f.get('pr') or 0),f['age']))
    cst=ct_stats(cev,cbase)
    ccand=[dict(c,vd=cst[c['k']]['vd'],dir=cst[c['k']]['dir']) for c in ccand if c['k'] in cst and cst[c['k']]['vd']!='none']
    ccand.sort(key=lambda c:c['date'],reverse=True)
    keep=[];seen=set()
    for c in ccand:
        if c['vd']=='win' and c['dir']>0:
            c['tgt']=round(c['sig']*(1+cst[c['k']]['raw60']/100),2)
            if c['mx']>=c['tgt']: continue  # already reached its target once: drop it
        if (c['s'],c['vd'],c['dir']) in seen: continue  # newest signal per stock only
        seen.add((c['s'],c['vd'],c['dir']));keep.append(c)
    ccand=keep
    tp=os.path.join(H,'template.html')
    if not os.path.exists(tp): tp=os.path.join(H,'template.txt')  # name used by the copy stored with the artifact
    html=open(tp,encoding='utf8').read().replace('__DATA__',json.dumps(dict(st=st,cur=cur,fake=fake,fake4=fake4,model=MODEL['info'],ct=dict(st=cst,cand=ccand,n=len(cev))),ensure_ascii=False)).replace('__DATE__',d.date.today().isoformat()).replace('__N__',str(len(ev)//1000))
    open(out,'w',encoding='utf8').write(html)
    print(len([x for x in data if x]),'stocks',len(ev),'events',len(cur),'candidates')
    print('FAKEOUTS',json.dumps(fake,ensure_ascii=False))
    print('FAKEOUTS_4H',json.dumps(fake4,ensure_ascii=False))
    print('CONTRARIAN_STATS',json.dumps(cst))
    print('CONTRARIAN_CANDIDATES',json.dumps(ccand))
if __name__=='__main__': main(sys.argv[1])
