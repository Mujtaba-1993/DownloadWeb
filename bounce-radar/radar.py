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
            for a,l,h,c in zip(r['timestamp'],q['low'],q['high'],q['close']):
                if not(l and h and c): continue
                Dd.append((a,l,h,c))
                k=d.datetime.fromtimestamp(a,d.timezone.utc).isocalendar()[:2]
                if k in W: x=W[k];W[k]=[x[0],min(x[1],l),max(x[2],h),c]
                else: W[k]=[a,l,h,c]
            return list(W.values()),Dd
        except Exception: pass
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
def fakeouts(s,lv,B):
    # weekly false breakout: within the last 2 closed weeks price traded 1-8% through a strong level (>=3 holds)
    # and the latest closed weekly candle closed back inside the zone. Backtest (S&P 500, all history):
    # weekly 47.5% hit +8% before closing below the wick vs 42.2% stopped; daily only 36.2% vs 49.7%.
    ny=d.datetime.now(d.timezone.utc)-d.timedelta(hours=5)
    lw=(d.datetime.fromtimestamp(B[-1][0],d.timezone.utc)-d.timedelta(hours=5)).date()
    if lw.isocalendar()[:2]==ny.date().isocalendar()[:2] and (ny.weekday()<4 or (ny.weekday()==4 and (ny.hour,ny.minute)<(16,15))): B=B[:-1]  # week not closed
    if len(B)<6: return []
    out=[];last=B[-1];prev=B[-2];before=B[-4][3];w=B[-2:]
    wk=(d.datetime.fromtimestamp(last[0],d.timezone.utc)-d.timedelta(hours=5)).date().isoformat()
    for L in lv:
        p=L['p']
        if not L['a'] or L['h']<3: continue
        lo=min(x[1] for x in w);hi=max(x[2] for x in w)
        if before>p and p<=last[3]<=p*(1+TOL) and p*0.92<=lo<=p*0.99 and (prev[3]<p or last[1]<=p*0.99):
            out.append(dict(s=s,side='دعم',level=round(p,2),holds=L['h'],close=round(last[3],2),ext=round(lo,2),pen=round((1-lo/p)*100,1),wk=wk,kind='ذيل في نفس الشمعة' if prev[3]>=p else 'رجوع بعد إغلاق تحت المستوى'))
        if before<p and p*(1-TOL)<=last[3]<=p and p*1.01<=hi<=p*1.08 and (prev[3]>p or last[2]>=p*1.01):
            out.append(dict(s=s,side='مقاومة',level=round(p,2),holds=L['h'],close=round(last[3],2),ext=round(hi,2),pen=round((hi/p-1)*100,1),wk=wk,kind='ذيل في نفس الشمعة' if prev[3]<=p else 'رجوع بعد إغلاق فوق المستوى'))
    return out
def grp(h): return '1' if h==1 else '2-3' if h<=3 else '4-6' if h<=6 else '7+'
def main(out):
    S=open(os.path.join(H,'tickers.txt')).read().split();ev=[];cand=[]
    with cf.ThreadPoolExecutor(12) as ex: data=list(ex.map(get,S))
    fake=[]
    for s,X in zip(S,data):
        if not X or len(X[0])<260: continue
        B,Dd=X
        lv,e=track(B)
        fake+=fakeouts(s,lv,B);ev+=e;last=B[-1][3];sma=sum(x[3] for x in B[-41:-1])/40
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
    html=open(os.path.join(H,'template.html'),encoding='utf8').read().replace('__DATA__',json.dumps(dict(st=st,cur=cur,fake=fake),ensure_ascii=False)).replace('__DATE__',d.date.today().isoformat()).replace('__N__',str(len(ev)//1000))
    open(out,'w',encoding='utf8').write(html)
    print(len([x for x in data if x]),'stocks',len(ev),'events',len(cur),'candidates')
    print('FAKEOUTS',json.dumps(fake,ensure_ascii=False))
if __name__=='__main__': main(sys.argv[1])
