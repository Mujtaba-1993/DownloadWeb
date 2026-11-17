"""Bounce radar: scan S&P 500 for prices near repeatedly-held levels and render the HTML page.
Usage: python3 radar.py OUT.html"""
import json,sys,os,urllib.request,urllib.parse,concurrent.futures as cf,datetime as d
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
                k=wk(a)
                if k in W: x=W[k];W[k]=[x[0],min(x[1],l),max(x[2],h),c,x[4]+(v or 0)]
                else: W[k]=[a,l,h,c,v or 0]
            ct=contrarian(s,Dd)  # computed here so the daily rows can be dropped
            if FCOLLECT is not None: fake_hist(list(W.values()))
            return list(W.values()),ct,(get4h(s) if MK['h4'] else None),[(ny_date(x[0]).isoformat(),x[2],x[3],x[4],x[1]) for x in Dd[-150:]]
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
# --- Markets. Everything below runs once per market; MK is the market being processed.
# wd: days to shift so the trading week groups correctly (Saudi week is Sunday-Thursday).
MARKETS={'us':dict(id='us',tickers='tickers.txt',index='SPY',wd=0,tz='America/New_York',off=-5,close=(16,15),h4=True,minok=450),
         'sa':dict(id='sa',tickers='tickers_sa.txt',index=['1120.SR','1010.SR','2010.SR','7010.SR','1150.SR','1211.SR','2280.SR','1050.SR','1060.SR','4030.SR','2020.SR','1140.SR'],wd=1,tz='Asia/Riyadh',off=3,close=(15,30),h4=False,minok=200,with_crowd=True)}
MK=MARKETS['us']
def _tz():
    try:
        from zoneinfo import ZoneInfo
        return ZoneInfo(MK['tz'])
    except Exception: return d.timezone(d.timedelta(hours=MK['off']))
def ny_now(): return d.datetime.now(_tz())            # "now" on the current market's clock
def ny_date(ts): return d.datetime.fromtimestamp(ts,_tz()).date()
def wk(ts): return d.datetime.fromtimestamp(ts+MK['wd']*86400,d.timezone.utc).isocalendar()[:2]   # trading-week key of a bar
def wkd(day): return (day+d.timedelta(days=MK['wd'])).isocalendar()[:2]
def week_open(now):
    tw=(now.weekday()+MK['wd'])%7   # 0 = first trading day of the week, 4 = last
    return tw<4 or (tw==4 and (now.hour,now.minute)<MK['close'])
# --- Contrarian study: what the crowd typically does on a signal, and what happened next ---
# key: (crowd action, contrarian direction) ; +1 = contrarian buys, -1 = contrarian sells/avoids
CT={'panic':1,'fomo':-1,'hi52':-1,'lo52':1,'rsi70':1,'rsi30':-1,'golden':-1,'death':1}
CT_TGT={'panic':0.072,'lo52':0.059}  # average 60-day gain after each signal = the target used for grading
CFEATS=['ret1','rvol','dd52','trend200','rsi','mkt','vol20','mom60','gap','clv','panic']
CMODEL={"w": [0.0589, -0.0822, -0.3486, 0.1517, -0.0816, -0.1833, 0.3906, -0.0739, 0.1353, -0.0104, -0.0459], "b": 1.4105, "mu": [-0.08854, 3.604136, -0.331989, -0.146995, 30.99618, -0.031611, 0.033559, -0.143723, -0.039988, 0.23586, 0.539514], "sd": [0.069585, 2.351438, 0.173095, 0.223767, 8.987024, 0.116046, 0.01931, 0.218932, 0.065726, 0.223017, 0.498436], "cut": [0.745, 0.8266], "info": {"n_train": 7238, "n_test": 5568, "base_test": 74.2, "auc_train": 0.669, "auc_test": 0.68, "test": {"C": [2519, 63.9], "B": [2099, 78.6], "A": [950, 92.0]}, "base": {"panic": 70.9, "lo52": 77.5}, "n": {"panic": 2735, "lo52": 2833}}}  # from train_ct.py
COLLECT=None  # train_ct.py sets this to a list to gather (time, kind, features, outcome)
def cscore(f):
    if not CMODEL or not f: return None
    import math
    z=CMODEL['b']+sum(CMODEL['w'][j]*((f[j]-CMODEL['mu'][j])/CMODEL['sd'][j]) for j in range(len(CFEATS)))
    pr=1/(1+math.exp(-z));return round(pr*100),('A' if pr>=CMODEL['cut'][1] else 'B' if pr>=CMODEL['cut'][0] else 'C')
def contrarian(s,Dd):
    full=Dd;ny=ny_now()
    if Dd and ny_date(Dd[-1][0])==ny.date() and (ny.hour,ny.minute)<MK['close']: Dd=Dd[:-1]  # today's candle not closed
    n=len(Dd)
    if n<320: return None
    from collections import deque
    c=[x[4] for x in Dd];o=[x[1] for x in Dd];v=[x[5] for x in Dd];t=[x[0] for x in Dd]
    hi=[x[2] for x in Dd];lw=[x[3] for x in Dd];cf={}
    cs=[0.0];vs=[0.0]
    for i in range(n): cs.append(cs[-1]+c[i]);vs.append(vs[-1]+v[i])
    ev=[];base={};last={};cand=[];hq=deque();lq=deque();lastHi=lastLo=-999;ag=al=0.0;rsi_prev=50.0;ma_prev=None
    def fire(k,i):
        if i-last.get(k,-99)<20: return
        last[k]=i
        if k in CT_TGT:
            r=[c[j]/c[j-1]-1 for j in range(i-19,i+1)];m=sum(r)/20;rg=hi[i]-lw[i];av=(vs[i]-vs[i-50])/50
            kk=wk(t[i])
            cf[(k,i)]=[c[i]/c[i-1]-1,min(v[i]/av,8) if av>0 else 1.0,c[i]/max(c[hq[0]] if hq else c[i],c[i])-1,c[i]/((cs[i+1]-cs[i-199])/200)-1,
                rsi,SPY.get(kk,0.0),(sum((x-m)**2 for x in r)/20)**.5,c[i]/c[i-60]-1,o[i]/c[i-1]-1,(c[i]-lw[i])/rg if rg>0 else 0.5,1.0 if k=='panic' else 0.0]
            if COLLECT is not None and i+60<n:
                e=o[i+1]
                COLLECT.append((t[i],k,cf[(k,i)],1 if max(hi[i+1:i+61])>=c[i]*(1+CT_TGT[k]) else 0,([x/e-1 for x in hi[i+1:i+61]],[x/e-1 for x in lw[i+1:i+61]],[x/e-1 for x in c[i+1:i+61]],0.0)))
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
    cd=[dict(s=s,k=k,date=ny_date(t[i]).isoformat(),sig=round(c[i],2),cur=round(cur,2),chg=round((cur/c[i]-1)*100,1),mx=round(max([x[2] for x in full[i+1:]]+[cur]),2),f=cf.get((k,i))) for k,i in cand]
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
        ms=sorted(mon);cut=ms[len(ms)//2]  # split this market's own history in two halves, to check the effect holds in both
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
    # market regime per trading week: the market index relative to its 40-week average.
    # MK['index'] is one symbol, or a basket of leading stocks averaged equally when no index history is available.
    def weekly(sym):
        u="https://query1.finance.yahoo.com/v8/finance/chart/"+urllib.parse.quote(sym)+"?period1=0&period2=4000000000&interval=1d"
        for _ in range(3):
            try:
                r=json.load(urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'}),timeout=40))['chart']['result'][0]
                W={}
                for a,c in zip(r['timestamp'],r['indicators']['quote'][0]['close']):
                    if c: W[wk(a)]=c
                return W
            except Exception: pass
        return {}
    syms=MK['index'] if isinstance(MK['index'],list) else [MK['index']]
    Ws=[w for w in (weekly(x) for x in syms) if len(w)>60]
    if not Ws: return {}
    ks=sorted(set().union(*Ws));lvl={};v=100.0
    for a,b in zip(ks,ks[1:]):
        r=[w[b]/w[a]-1 for w in Ws if a in w and b in w]
        if r: v*=1+sum(r)/len(r)
        lvl[b]=v
    ks=sorted(lvl);return {ks[i]:lvl[ks[i]]/(sum(lvl[k] for k in ks[i-40:i])/40)-1 for i in range(40,len(ks))}
def feats(C,i,p,lo,holds,spy):
    # C: closed weekly bars [ts,low,high,close,vol]; i: signal week. Returns None if history is too short.
    if i<53: return None
    b=C[i];c=b[3];k=wk(b[0])
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
    if wk(B[-1][0])==wkd(ny.date()) and week_open(ny): C=B[:-1]  # week not closed
    if len(C)<10: return []
    out=[];seen=set();cur=B[-1][3]
    for k in range(4):
        i=len(C)-1-k;last=C[i];prev=C[i-1];pre=[x[3] for x in C[i-5:i-1]];w=C[i-1:i+1];after=B[i+1:]
        lo=min(x[1] for x in w);hi=max(x[2] for x in w);wks=ny_date(last[0]).isoformat();c=last[3]
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
                out.append(dict(s=s,side='دعم',level=round(p,2),holds=L['h'],close=round(c,2),ext=round(lo,2),pen=round((1-lo/p)*100,1),wk=wks,age=k,pos=round(ps*100),hit=hit,pr=sc[0] if sc else None,grade=sc[1] if sc else None,cur=round(cur,2),chg=round((cur/c-1)*100,1),T=[round(x,2) for x in T],kind='ذيل في نفس الشمعة' if prev[3]>=p else 'رجوع بعد إغلاق تحت المستوى'))
            else:
                T=[c*0.95,c*0.946,c*0.88];mn=min([x[1] for x in after],default=9e9);hit=sum(mn<=x for x in T)
                if hit or any(x[3]>hi for x in after): continue
                out.append(dict(s=s,side='مقاومة',level=round(p,2),holds=L['h'],close=round(c,2),ext=round(hi,2),pen=round((hi/p-1)*100,1),wk=wks,age=k,pos=round(ps*100),hit=hit,cur=round(cur,2),chg=round((cur/c-1)*100,1),T=[round(x,2) for x in T],kind='ذيل في نفس الشمعة' if prev[3]<=p else 'رجوع بعد إغلاق فوق المستوى'))
    return out
# --- Self-tracking: every suggestion is logged the first day it is shown, then graded win/loss from later prices,
# whether or not the user traded it. Live results adjust the shown probability (Bayesian shrinkage toward the
# backtest rate) and pause a category whose live record turns bad; a paused category keeps being logged in the
# background and is switched back on if its record recovers.
LOGF=os.path.join(H,'log.txt')
PRIOR={'fake|A':(68,20),'fake|B':(66,20),'fake|C':(57,20),'fake4':(60,20),'ct|panic':(71,20),'ct|lo52':(78,20)}  # (expected win %, weight)
HORIZON={'fake':91,'fake4':45,'ct':88}  # calendar days before an unresolved suggestion counts as a miss
def resolve(e,tl,now):
    # returns ('win'|'loss', date) or None while still open
    d0=d.date.fromisoformat(e['d'])
    bars=[b for b in tl if d.date.fromisoformat(b[0])>d0 and (e['kind']!='fake' or wkd(d.date.fromisoformat(b[0]))!=wkd(d0))]  # weekly signals: track from the next trading week
    win=next((b[0] for b in bars if b[1]>=e['tgt']),None);loss=None
    if e['stop']:
        if e['kind']=='fake':  # stop = a closed weekly candle below the wick
            wk={}
            wb={}
            for b in bars: wb[wkd(d.date.fromisoformat(b[0]))]=b
            cw=wkd(now.date());closed=not week_open(now)
            loss=next((b[0] for k,b in sorted(wb.items()) if (k!=cw or closed) and b[3]<e['stop']),None)
        else: loss=next((b[0] for b in bars if b[3]<e['stop']),None)
    if win and (not loss or win<=loss): return 'win',win
    if loss: return 'loss',loss
    if (now.date()-d0).days>HORIZON[e['kind']]: return 'loss',now.date().isoformat()
    return None
def selflearn(fake,fake4,ccand,tails,labs):
    now=ny_now();today=now.date().isoformat()
    try: log=json.load(open(LOGF,encoding='utf8'))
    except Exception: log=[]
    have={e['id'] for e in log}
    def add(kind,s,dt,key,entry,tgt,stop,cat,pr,grade=None):
        i=f"{kind}|{s}|{dt}|{key}"
        if i in have and grade:
            for e in log:
                if e['id']==i and not e.get('grade') and 'pt' not in e: e['grade']=grade;e['pr']=pr
        if i not in have: have.add(i);log.append(dict(id=i,mk=MK['id'],kind=kind,s=s,d=dt,entry=entry,tgt=tgt,stop=stop,cat=cat,pr=pr,first=today,status='open',res=None,grade=grade))
        return i
    for f in fake:
        if f['side']=='دعم': f['cat']='fake|'+(f.get('grade') or 'B');f['lid']=add('fake',f['s'],f['wk'],f['level'],f['close'],f['T'][0],f['ext'],f['cat'],f.get('pr'),f.get('grade'))
    for f in fake4: f['cat']='fake4';f['lid']=add('fake4',f['s'],f['wk'][:10],f['level'],f['close'],f['T'][0],f['ext'],'fake4',None)
    for c in ccand:
        if c.get('act','').startswith('buy'): c['cat']='ct|'+c['k'];c['lid']=add('ct',c['s'],c['date'],c['k'],c['sig'],c['tgt'],None,c['cat'],c.get('pr'),c.get('grade'))
    mine=[e for e in log if e.get('mk','us')==MK['id']]
    for e in mine:
        if 'pt' not in e:  # the exit rule is frozen when the paper trade is opened
            lb=labs.get(e['kind']) or {};ch=lb['champ'] if lb.get('valid_ok') else DEFAULT_PT[e['kind']];g=e.get('grade')
            e['pt']=dict(T=ch['T'],S=ch['S'],maxd=MAXD[e['kind']],ok=ch['f']=='all' or (g in ('A','B') if ch['f']=='AB' else g=='A'),status='pending')
        if e['pt']['status']!='closed' and e['s'] in tails: paper(e,tails[e['s']])
    def pstat(E):
        cl=[e['pt']['ret'] for e in E if e['pt']['status']=='closed']
        return dict(n=len(E),open=sum(e['pt']['status']=='open' for e in E),pending=sum(e['pt']['status']=='pending' for e in E),closed=len(cl),win=round(100*sum(r>0 for r in cl)/len(cl)) if cl else None,avg=round(sum(cl)/len(cl),2) if cl else None,total=round(sum(cl),1) if cl else 0,
            unreal=round(sum(e['pt']['ret'] for e in E if e['pt']['status']=='open'),1))
    pp=dict(all=pstat(mine),champ=pstat([e for e in mine if e['pt']['ok']]),recent=[dict(s=e['s'],kind=e['kind'],ret=e['pt']['ret'],exit=e['pt']['exit'],entry=e['pt']['entry']) for e in sorted([e for e in mine if e['pt']['status']=='closed'],key=lambda e:e['pt']['exit'],reverse=True)[:20]])
    done=[]
    for e in mine:
        if e['status']=='open' and e['s'] in tails:
            r=resolve(e,tails[e['s']],now)
            if r: e['status'],e['res']=r;done.append(e)
    cats={}
    pri=dict(PRIOR);tm=MODEL['info'].get('test_mid') or MODEL['info'].get('test') or {}
    for g,v in tm.items():  # expected rate per grade = what the model in use achieved on this market's recent unseen signals
        if v and v[1] is not None and v[0]>=15: pri['fake|'+g]=(round(v[1]),20)
    for c in list(pri)+sorted({e['cat'] for e in mine}-set(pri)):
        pr,k=pri.get(c,(50,10))
        E=[e for e in mine if e['cat']==c];w=sum(e['status']=='win' for e in E);l=sum(e['status']=='loss' for e in E);n=w+l
        post=(pr*k+100*w)/(k+n);on=not(n>=15 and 100*w/n<45)
        cats[c]=dict(n=len(E),open=len(E)-n,w=w,l=l,rate=round(100*w/n) if n else None,prior=pr,adj=round(post),on=on)
    json.dump(log,open(LOGF,'w',encoding='utf8'),ensure_ascii=False)
    for f in fake:
        if 'cat' in f and f.get('pr') is not None: f['adj']=max(1,min(99,f['pr']+cats[f['cat']]['adj']-cats[f['cat']]['prior']))
    for x in fake4: x['adj']=cats['fake4']['adj']
    for c in ccand:
        if 'cat' in c and c.get('pr') is not None: c['adj']=max(1,min(99,c['pr']+cats[c['cat']]['adj']-cats[c['cat']]['prior']))
    ok=lambda x:'cat' not in x or cats[x['cat']]['on']
    recent=sorted([e for e in mine if e['status']!='open'],key=lambda e:e['res'],reverse=True)[:25]
    perf=dict(cats=cats,paper=pp,labs=labs,total=len(mine),recent=[dict(s=e['s'],kind=e['kind'],d=e['d'],res=e['res'],status=e['status'],entry=e['entry'],tgt=e['tgt']) for e in recent],
        today=[dict(s=e['s'],kind=e['kind'],status=e['status']) for e in done],since=min([e['first'] for e in mine],default=today))
    return [f for f in fake if ok(f)],[f for f in fake4 if ok(f)],[c for c in ccand if ok(c)],perf
# --- Continuous learning: every run rebuilds the full history of signals and their outcomes, refits each scoring
# model on everything except the most recent years, and compares it there (data it never saw) with the model in use.
# The challenger replaces the champion only if it separates wins from losses better on that recent period.
FCOLLECT=None
def levels_pit(B):
    # point-in-time levels: each has the dates it held and the date it broke, so history can be replayed honestly
    idx={b[0]:i for i,b in enumerate(B)};out=[]
    for t,p in zigzag(B):
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
def fake_hist(B):
    if len(B)<260: return
    Ls=levels_pit(B)
    for i in range(60,len(B)-14):
        t=B[i][0];last=B[i];prev=B[i-1];c=last[3];lo=min(last[1],prev[1])
        for L in Ls:
            p=L['p']
            if not(p<=c<=p*1.03) or not(p*0.92<=lo<=p*0.99): continue
            h=sum(1 for x in L['holds'] if x<t)
            if L['t0']>=t or (L['brk'] and L['brk']<=t) or h<3: continue
            if min(x[3] for x in B[i-5:i-1])>p and (prev[3]<p or last[1]<=p*0.99):
                f=feats(B,i,p,lo,h,SPY)
                if not f: continue
                y=0
                for x in B[i+1:i+14]:
                    if x[2]>=c*1.05: y=1;break
                    if x[3]<lo: break
                FW=B[i+1:i+14];FCOLLECT.append((t,None,[f[n] for n in FEATS],y,([x[2]/c-1 for x in FW],[x[1]/c-1 for x in FW],[x[3]/c-1 for x in FW],lo/c-1)))
def relearn(data,old,years,pos_idx=None):
    # returns the model to use (old or retrained) with fresh validation numbers in ['info']
    try: import numpy as np
    except Exception: return old
    keep=dict(old,info=dict(old['info'],transfer=True,retrained=False,auc_new=None,auc_old=None,total=len(data)))  # not enough local data to judge
    if len(data)<200: return keep
    now=ny_now();cutd=d.datetime(now.year-years,now.month,1,tzinfo=d.timezone.utc);cut_ts=cutd.timestamp()
    T=np.array([a[0] for a in data],float);X=np.array([a[2] for a in data],float);Y=np.array([a[3] for a in data],float)
    tr=T<cut_ts;te=~tr
    if te.sum()<60: return keep
    def auc(p,y):
        r=p.argsort().argsort()+1;n1=y.sum();n0=len(y)-n1
        return float((r[y==1].sum()-n1*(n1+1)/2)/(n1*n0)) if n1 and n0 else 0.5
    def pred(m): return 1/(1+np.exp(-(((X-np.array(m['mu']))/np.array(m['sd']))@np.array(m['w'])+m['b'])))
    ao=auc(pred(old)[te],Y[te]);an=None;new=None;use=dict(old)
    if tr.sum()>=500:
        mu=X[tr].mean(0);sd=X[tr].std(0)+1e-9;Z=(X[tr]-mu)/sd;w=np.zeros(X.shape[1]);b=0.0
        for _ in range(3000):
            p=1/(1+np.exp(-(Z@w+b)));w-=0.3*(Z.T@(p-Y[tr])/tr.sum()+0.01*w);b-=0.3*(p-Y[tr]).mean()
        new=dict(w=[float(x) for x in w],b=float(b),mu=[float(x) for x in mu],sd=[float(x) for x in sd])
        Pn=pred(new);new['cut']=[float(np.quantile(Pn[tr],1/3)),float(np.quantile(Pn[tr],2/3))]
        an=auc(Pn[te],Y[te])
        if an>ao+0.003: use=new
    P=pred(use);cut=use['cut']
    def grades(m): return {g:[int((m&sel).sum()),round(100*float(Y[m&sel].mean()),1) if (m&sel).sum() else None] for g,sel in (('C',P<cut[0]),('B',(P>=cut[0])&(P<cut[1])),('A',P>=cut[1]))}
    info=dict(n_train=int(tr.sum()) if use is new else old['info']['n_train'],n_test=int(te.sum()),base_test=round(100*float(Y[te].mean()),1),test=grades(te),
        retrained=use is new,auc_new=round(an,3) if an is not None else None,auc_old=round(ao,3),since=cutd.date().isoformat(),total=len(data))
    if pos_idx is not None:
        mid=(X[:,pos_idx]>=MID[0])&(X[:,pos_idx]<=MID[1]);info['test_mid']=grades(te&mid);info['base_test_mid']=round(100*float(Y[te&mid].mean()),1) if (te&mid).sum() else None
    use['info']=info;return use
# --- Strategy lab + paper trading. Every run replays thousands of simulated trades over all history with a grid of
# exit rules (target, stop, grade filter). The rule with the best average net result on the older data becomes the
# champion; its result on the recent years it never saw is reported next to it. New suggestions are then paper-traded
# forward with the champion rule (virtual money only: nothing is ever sent to a broker).
COST=0.002  # round-trip cost assumed per simulated trade
GRID={'ct':([0.04,0.06,0.08,0.10,0.15,None],[0.05,0.08,0.12,0.20,None],(0.06,None)),'fake':([0.03,0.05,0.08,0.12,None],['wick',0.05,0.08,0.12,None],(0.05,'wick'))}
MAXD={'ct':60,'fake':65,'fake4':30};DEFAULT_PT={'ct':dict(T=0.06,S=None,f='all'),'fake':dict(T=0.05,S='wick',f='all'),'fake4':dict(T=0.03,S='wick',f='all')}
def lab(kind,data,model,years,pos_idx=None):
    try: import numpy as np
    except Exception: return None
    if pos_idx is not None: data=[a for a in data if MID[0]<=a[2][pos_idx]<=MID[1]]
    if len(data)<300: return None
    now=ny_now();cut=d.datetime(now.year-years,now.month,1,tzinfo=d.timezone.utc).timestamp()
    T_=np.array([a[0] for a in data],float);X=np.array([a[2] for a in data],float)
    H=np.array([a[4][0] for a in data]);L=np.array([a[4][1] for a in data]);C=np.array([a[4][2] for a in data]);W=np.array([a[4][3] for a in data])
    P=1/(1+np.exp(-(((X-np.array(model['mu']))/np.array(model['sd']))@np.array(model['w'])+model['b'])));c0,c1=model['cut']
    F={'all':np.ones(len(data),bool),'AB':P>=c0,'A':P>=c1};tr=T_<cut;va=~tr;K=H.shape[1];rows=np.arange(len(data))
    def first(m):
        i=m.argmax(1);i[~m.any(1)]=K;return i
    def sim(T,S):
        ti=first(H>=T) if T else np.full(len(data),K);R=C[:,-1].copy()
        if S=='wick':
            si=first(C<W[:,None]);st=(si<ti)&(si<K);R[st]=C[rows[st],si[st]];tg=(ti<=si)&(ti<K)
        else:
            si=first(L<=-S) if S else np.full(len(data),K);st=(si<=ti)&(si<K);R[st]=-S if S else 0;tg=(ti<si)&(ti<K)
        if T: R[tg]=T
        return R-COST
    def stat(R,m): return dict(n=int(m.sum()),win=round(100*float((R[m]>0).mean())),avg=round(100*float(R[m].mean()),2)) if m.sum() else dict(n=0,win=None,avg=None)
    Ts,Ss,base=GRID[kind];res=[]
    for T in Ts:
        for S in Ss:
            R=sim(T,S)
            for f,m in F.items():
                if (m&tr).sum()>=150 and (m&va).sum()>=30: res.append(dict(T=T,S=S,f=f,tr=stat(R,m&tr),va=stat(R,m&va)))
    if not res: return None
    res.sort(key=lambda r:-r['tr']['avg']);Rb=sim(*base);good=[r for r in res if r['va']['avg']>0]
    return dict(champ=(good or res)[0],valid_ok=bool(good),top=res[:5],base=dict(T=base[0],S=base[1],f='all',tr=stat(Rb,tr),va=stat(Rb,va)),sims=len(data)*len(Ts)*len(Ss),signals=len(data),since=d.datetime.fromtimestamp(cut,d.timezone.utc).date().isoformat())
def paper(e,tl):
    # forward virtual trade: bought at the open of the first session after the suggestion was first shown
    pt=e['pt'];bars=[b for b in tl if b[0]>e['first']]
    if not bars: return
    en=bars[0][4];pt['entry']=round(en,2);T,S=pt['T'],pt['S'];r=None
    for k,b in enumerate(bars):
        if isinstance(S,float) and b[2]<=en*(1-S): r=-S
        elif T and b[1]>=en*(1+T): r=T
        elif S=='wick' and e['stop'] and b[3]<e['stop']: r=b[3]/en-1
        elif k+1>=pt['maxd']: r=b[3]/en-1
        if r is not None: pt.update(status='closed',ret=round(100*(r-COST),2),exit=b[0]);return
    pt.update(status='open',ret=round(100*(bars[-1][3]/en-1),2))
def grp(h): return '1' if h==1 else '2-3' if h<=3 else '4-6' if h<=6 else '7+'
def run_market(mid,base):
    global MK,MODEL,CMODEL,FCOLLECT,COLLECT
    MK=MARKETS[mid];MODEL,CMODEL=base;P='' if mid=='us' else mid.upper()+'_'
    SPY.clear();SPY.update(spy_map());FCOLLECT=[];COLLECT=[]
    rows=[l.split('\t') for l in open(os.path.join(H,MK['tickers']),encoding='utf8').read().splitlines() if l.strip()]
    S=[r[0].strip() for r in rows];names={r[0].strip():r[1].strip() for r in rows if len(r)>1};cev=[];cbase={};ccand=[]
    with cf.ThreadPoolExecutor(12) as ex: data=list(ex.map(get,S))
    okn=sum(1 for x in data if x)
    if okn<MK['minok'] or not SPY:
        print(P+'ERROR',f'only {okn} of {len(S)} stocks downloaded (index data: {bool(SPY)})');return None
    MODEL=relearn(FCOLLECT,MODEL,5,FEATS.index('pos'));CMODEL=relearn(COLLECT,CMODEL,3)
    labs={'fake':lab('fake',FCOLLECT,MODEL,5,FEATS.index('pos')),'ct':lab('ct',COLLECT,CMODEL,3)}
    fake=[];fake4=[];tails={}
    for s,X in zip(S,data):
        if not X or len(X[0])<260: continue
        B,ct,X4,tl=X;tails[s]=tl
        if ct:
            cev+=ct[0];ccand+=ct[2]
            for m,x in ct[1].items():
                bb=cbase.setdefault(m,[0.0,0.0,0]);bb[0]+=x[0];bb[1]+=x[1];bb[2]+=x[2]
        lv,e=track(B)
        fake4+=fakeouts4h(s,lv,X4,B);fake+=fakeouts(s,lv,B)
    fake.sort(key=lambda f:(f['side']!='دعم',-(f.get('pr') or 0),f['age']))
    cst=ct_stats(cev,cbase)
    ccand=[dict(c,vd=cst[c['k']]['vd'],dir=cst[c['k']]['dir']) for c in ccand if c['k'] in cst and cst[c['k']]['vd']!='none']
    for c in ccand:
        # what this market's own history supports: buy against the crowd, buy with the crowd (only where the
        # opposite fails and the average 60-day gain is worth it), or avoid buying
        if c['vd']=='win': c['act']='buy_contra' if c['dir']>0 else 'avoid'
        elif MK.get('with_crowd') and c['dir']<0 and cst[c['k']]['raw60']>=3: c['act']='buy_with'
    ccand=[c for c in ccand if 'act' in c]
    ccand.sort(key=lambda c:c['date'],reverse=True)
    keep=[];seen=set()
    for c in ccand:
        if c['act'].startswith('buy'):
            c['tgt']=round(c['sig']*(1+cst[c['k']]['raw60']/100),2)
            sc=cscore(c.get('f'))
            if sc: c['pr'],c['grade']=sc
            if c['mx']>=c['tgt']: continue  # already reached its target once: drop it
        if (c['s'],c['act']) in seen: continue  # newest signal per stock only
        seen.add((c['s'],c['act']));keep.append(c)
    ccand=keep
    for c in ccand: c.pop('f',None)
    fake,fake4,ccand,perf=selflearn(fake,fake4,ccand,tails,labs)
    print(P+'SUMMARY',okn,'stocks',len(FCOLLECT),'historical false-breakout signals',len(COLLECT),'historical contrarian signals')
    print(P+'MODELS',json.dumps({k:{x:m['info'].get(x) for x in ('retrained','transfer','auc_new','auc_old','n_train','n_test','since','total')} for k,m in (('fake',MODEL),('ct',CMODEL))}))
    print(P+'LAB',json.dumps({k:(v and dict(champ=v['champ'],base=v['base'],sims=v['sims'])) for k,v in labs.items()}))
    print(P+'PAPER',json.dumps(dict(all=perf['paper']['all'],champ=perf['paper']['champ'])))
    print(P+'PERF',json.dumps(dict(cats=perf['cats'],resolved_today=perf['today']),ensure_ascii=False))
    print(P+'FAKEOUTS',json.dumps(fake,ensure_ascii=False))
    print(P+'FAKEOUTS_4H',json.dumps(fake4,ensure_ascii=False))
    print(P+'CONTRARIAN_STATS',json.dumps(cst))
    print(P+'CONTRARIAN_CANDIDATES',json.dumps(ccand))
    return dict(fake=fake,fake4=fake4,h4=MK['h4'],model=MODEL['info'],cmodel=CMODEL['info'],perf=perf,ct=dict(st=cst,cand=ccand,n=len(cev)),names=names,stocks=okn)
def main(out):
    base=(MODEL,CMODEL);D={}
    for mid in MARKETS: D[mid]=run_market(mid,base)
    if not D['us']: sys.exit('ERROR: US market data could not be downloaded; not writing the page')
    tp=os.path.join(H,'template.html')
    if not os.path.exists(tp): tp=os.path.join(H,'template.txt')  # name used by the copy stored with the artifact
    html=open(tp,encoding='utf8').read().replace('__DATA__',json.dumps(D,ensure_ascii=False)).replace('__DATE__',d.date.today().isoformat())
    open(out,'w',encoding='utf8').write(html)
if __name__=='__main__': main(sys.argv[1])
