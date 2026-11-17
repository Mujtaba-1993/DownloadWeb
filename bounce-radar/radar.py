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
            q=r['indicators']['quote'][0];W={}
            for a,l,h,c in zip(r['timestamp'],q['low'],q['high'],q['close']):
                if not(l and h and c): continue
                k=d.datetime.fromtimestamp(a,d.timezone.utc).isocalendar()[:2]
                if k in W: x=W[k];W[k]=[x[0],min(x[1],l),max(x[2],h),c]
                else: W[k]=[a,l,h,c]
            return list(W.values())
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
def grp(h): return '1' if h==1 else '2-3' if h<=3 else '4-6' if h<=6 else '7+'
def main(out):
    S=open(os.path.join(H,'tickers.txt')).read().split();ev=[];cand=[]
    with cf.ThreadPoolExecutor(12) as ex: data=list(ex.map(get,S))
    for s,B in zip(S,data):
        if not B or len(B)<260: continue
        lv,e=track(B);ev+=e;last=B[-1][3];sma=sum(x[3] for x in B[-41:-1])/40
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
    html=open(os.path.join(H,'template.html'),encoding='utf8').read().replace('__DATA__',json.dumps(dict(st=st,cur=cur),ensure_ascii=False)).replace('__DATE__',d.date.today().isoformat()).replace('__N__',str(len(ev)//1000))
    open(out,'w',encoding='utf8').write(html)
    print(len([x for x in data if x]),'stocks',len(ev),'events',len(cur),'candidates')
if __name__=='__main__': main(sys.argv[1])
