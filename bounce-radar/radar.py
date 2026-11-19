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
            I=get4h(s)
            return list(W.values()),ct,(I[0] if I and MK['h4'] else None),[(ny_date(x[0]).isoformat(),x[2],x[3],x[4],x[1]) for x in Dd[-150:]],patterns(s,Dd)+(I[1] if I else []),gaps(s,Dd),dips(s,Dd),schools(s,Dd),pullbacks(s,Dd),tlines(s,Dd)
        except Exception: pass
def get4h(s):
    # One hourly download (about 250 days). Returns (4-hour bars for the weekly-level false breakouts, intraday pattern signals).
    # 4-hour bars = the two halves of the session; only closed bars are used.
    import time
    for _ in range(3):
        try:
            now=int(time.time());u=f"https://query1.finance.yahoo.com/v8/finance/chart/{urllib.parse.quote(s)}?period1={now-250*86400}&period2={now}&interval=1h"
            r=json.load(urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'}),timeout=40))['chart']['result'][0]
            q=r['indicators']['quote'][0];off=r['meta']['gmtoffset'];split=MK['split'];W={};H1=[]
            for a,o,h,l,c,v in zip(r['timestamp'],q['open'],q['high'],q['low'],q['close'],q['volume']):
                if not(o and l and h and c): continue
                H1.append((a,o,h,l,c,v or 0));loc=a+off;k=(loc//86400,0 if (loc%86400)<split else 1)
                if k in W: x=W[k];W[k]=[x[0],x[1],max(x[2],h),min(x[3],l),c,x[5]+(v or 0)]
                else: W[k]=[a,o,h,l,c,v or 0]
            if not H1: return None
            ks=sorted(W);H4=[tuple(W[k]) for k in ks];cur=H1[-1][4];nl=now+off;dl={}
            for a,o,h,l,c,v in H1[-150:]:   # per-session high / low / last, for the live price refresh
                k=d.datetime.fromtimestamp(a+off,d.timezone.utc).date().isoformat();x=dl.get(k);dl[k]=[max(x[0],h),min(x[1],l),c] if x else [h,l,c]
            end=ks[-1][0]*86400+(split if ks[-1][1]==0 else MK['close'][0]*3600+MK['close'][1]*60)
            if nl<end: H4=H4[:-1]
            if H1[-1][0]+3600>now: H1=H1[:-1]
            pts=patterns(s,H4,'h4')+patterns(s,H1,'h1')
            if pts:   # daily candles for the chart of an intraday signal, built from the hourly download
                Dy={}
                for a,o,h,l,c,v in H1:
                    k=(a+off)//86400
                    if k in Dy: x=Dy[k];Dy[k]=[x[0],max(x[1],h),min(x[2],l),c]
                    else: Dy[k]=[o,h,l,c]
                ch=[[round(v,2) for v in Dy[k]] for k in sorted(Dy)][-90:]
                for p in pts: p['chart']=ch
            for p in pts: p['cur']=round(cur,2);p['chg']=round((cur/p['close']-1)*100,1)
            pts=[p for p in pts if p['stop']<cur<p['tgt']]
            return ([[x[0],x[3],x[2],x[4]] for x in H4],cur,off),pts,dl
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
            if any(x[3]<lo for x in after) or cur<lo or max([x[2] for x in after]+[cur,b[2]])>=c*1.03: continue  # the signal candle's own high counts too
            t=d.datetime.fromtimestamp(b[0]+off,d.timezone.utc)
            out.append(dict(s=s,side='دعم',level=round(p,2),holds=L['h'],close=round(c,2),ext=round(lo,2),pen=round((1-lo/p)*100,1),wk=t.strftime('%Y-%m-%d ')+('صباحاً' if t.hour<13 else 'مساءً'),age=k,hit=0,pos=round(ps*100),cur=round(cur,2),chg=round((cur/c-1)*100,1),T=[round(c*1.03,2),round(c*1.05,2),round(c*1.08,2)],kind='4 ساعات'))
    return out
# --- Markets. Everything below runs once per market; MK is the market being processed.
# wd: days to shift so the trading week groups correctly (Saudi week is Sunday-Thursday).
MARKETS={'us':dict(id='us',tickers='tickers.txt',index='SPY',wd=0,tz='America/New_York',off=-5,close=(16,15),split=13*3600+1800,h4=True,minok=450),
         'sa':dict(id='sa',tickers='tickers_sa.txt',index=['1120.SR','1010.SR','2010.SR','7010.SR','1150.SR','1211.SR','2280.SR','1050.SR','1060.SR','4030.SR','2020.SR','1140.SR'],wd=1,tz='Asia/Riyadh',off=3,close=(15,30),split=12*3600+1800,h4=False,minok=200,with_crowd=True)}
MK=MARKETS['us']
def _tz():
    try:
        from zoneinfo import ZoneInfo
        return ZoneInfo(MK['tz'])
    except Exception: return d.timezone(d.timedelta(hours=MK['off']))
# --- Chart-pattern false breakdowns. A pattern is two trendlines through the last 3 confirmed pivot highs and lows.
# Signal: a daily close below the lower line, then within 5 sessions a close back inside. Only the two shapes whose
# "return inside" trade was profitable in both halves of history and in both markets are reported:
# falling wedge and falling channel. Target = the pattern's upper line, stop = a close below the breakdown low.
# --- Gap down in an already beaten-down stock (more than 30% below its 52-week high, opens 2%+ lower).
# GAP_STATS: what followed such gaps since 2015, by gap size: dd50/dd75/dd90 = typical / deep / extreme further fall
# within 20 sessions from the next open, dlow = session of the low, r20 = median 20-session return, fill = gap closed.
GAP_STATS={"us": {"2-4%": {"trig": 34, "r20": 5.0, "r20m": 6.2, "pos": 66, "dd50": -7.7, "dd75": -13.6, "dd90": -20.8, "fill": 66, "up": 7.1, "trade": 3.2, "n": 2443}, "4-7%": {"trig": 43, "r20": 6.6, "r20m": 7.7, "pos": 69, "dd50": -8.2, "dd75": -14.6, "dd90": -22.2, "fill": 66, "up": 9.1, "trade": 5.0, "n": 890}, "7%+": {"trig": 65, "r20": 11.5, "r20m": 14.2, "pos": 75, "dd50": -9.1, "dd75": -15.5, "dd90": -24.0, "fill": 58, "up": 17.8, "trade": 11.9, "n": 695}}, "sa": {"2-4%": {"trig": 37, "r20": 1.2, "r20m": 1.8, "pos": 55, "dd50": -5.9, "dd75": -11.1, "dd90": -17.4, "fill": 59, "up": 6.2, "trade": 1.6, "n": 1049}, "4-7%": {"trig": 48, "r20": 1.6, "r20m": 3.2, "pos": 56, "dd50": -5.5, "dd75": -10.4, "dd90": -15.8, "fill": 60, "up": 7.3, "trade": 2.8, "n": 544}, "7%+": {"trig": 60, "r20": 4.5, "r20m": 5.5, "pos": 64, "dd50": -5.7, "dd75": -9.9, "dd90": -15.5, "fill": 51, "up": 12.4, "trade": 4.7, "n": 518}}}
GAP_CMP={"us": {"now": {"trig": 78, "r20": 5.6, "r20m": 6.6, "pos": 64, "dd50": -8.1, "dd75": -15.2, "dd90": -24.4, "fill": 80, "up": 4.7, "trade": 2.5, "n": 7970}, "conf": {"trig": 39, "r20": 6.2, "r20m": 7.9, "pos": 68, "dd50": -8.0, "dd75": -14.2, "dd90": -21.7, "fill": 64, "up": 8.8, "trade": 5.1, "n": 4028}}, "sa": {"now": {"trig": 78, "r20": 2.2, "r20m": 3.8, "pos": 58, "dd50": -6.1, "dd75": -11.5, "dd90": -19.6, "fill": 74, "up": 4.0, "trade": 1.7, "n": 3783}, "conf": {"trig": 44, "r20": 2.0, "r20m": 3.0, "pos": 57, "dd50": -5.7, "dd75": -10.6, "dd90": -16.8, "fill": 57, "up": 7.3, "trade": 2.6, "n": 2111}}}
def gaps(s,Dd):
    # Shown only once ALL conditions are complete: the stock is more than 30% below its 52-week high, gapped down 2%+,
    # at least 3 sessions have passed, the gap is still open, and a session has closed higher than the one before it
    # (the first such close is the confirmation). Entry = the open after the confirmation; target = the gap closing.
    # This rule was the best of six tested: average trade +5.1% (US) against +2.5% for buying right after the gap.
    now=ny_now()
    if Dd and ny_date(Dd[-1][0])==now.date() and (now.hour,now.minute)<MK['close']: Dd=Dd[:-1]
    n=len(Dd)
    if n<300: return []
    c=[x[4] for x in Dd];cur=c[-1]
    for i in range(n-4,n-14,-1):   # gap day: 3 to 12 sessions ago
        pc=c[i-1];g=Dd[i][1]/pc-1
        if g>-0.02 or pc>=0.7*max(c[i-253:i-1]): continue
        k=next((k for k in range(i+3,min(i+11,n)) if c[k]>c[k-1]),None)   # confirmation session
        if k is None or n-1-k>2: return []                                # not confirmed yet, or confirmed too long ago
        if max(x[2] for x in Dd[i:])>=pc: return []                       # gap already closed: target reached
        b='2-4%' if g>-0.04 else '4-7%' if g>-0.07 else '7%+';st=GAP_STATS[MK['id']].get(b)
        if not st: return []
        ref=Dd[k+1][1] if k+1<n else c[k]
        if ref>=pc or cur>=pc: return []
        return [dict(s=s,date=ny_date(Dd[i][0]).isoformat(),conf=ny_date(Dd[k][0]).isoformat(),gap=round(g*100,1),b=b,pc=round(pc,2),ref=round(ref,2),cur=round(cur,2),chg=round((cur/ref-1)*100,1),age=n-1-k,
            low=round(min(x[3] for x in Dd[i:]),2),typ=round(ref*(1+st['dd50']/100),2),deep=round(ref*(1+st['dd75']/100),2),ext=round(ref*(1+st['dd90']/100),2),up=round((pc/cur-1)*100,1))]
    return []
# --- The single best "trader strategy" (study of 13 popular strategies over all history of both markets, Nov 2026).
# Trend-following entries (breakouts, moving-average and MACD crosses) won only 32-46% of trades and did not beat
# simply holding the stocks; light dip-buying (RSI, Bollinger) was no better than holding. The one rule that beat
# holding in both halves of history and in both markets: buy a DEEP fast fall.
# Rule: the close is 25%+ below the highest high of the previous 20 sessions (first such close, no signal in the
# 20 sessions before, no split/data glitch inside the window). Buy the next open, sell at +10%, no stop (every stop
# tested made it worse), sell at the close of session 60 if the target was not reached.
# DIP_STATS: net of 0.2% cost. days = median sessions to the target, al = average losing trade, worst = worst 5% of
# trades, dd50/75/90 = typical / deep / extreme fall after entry, ex = average gain over holding the whole market
# for the same days, up/dn = signal above / below the 200-day average, stop15 = the same rule with a 15% stop.
DIP=dict(depth=0.25,win=20,tgt=0.10,maxd=60,fresh=10)
DIP_STATS={"us": {"n": 5235, "win": 83, "avg": 4.1, "pf": 2.04, "days": 8, "al": -23.0, "worst": -30.9, "ex": 0.7, "dd50": -8.5, "dd75": -21.0, "dd90": -39.1, "since": 2000, "up": {"n": 602, "win": 86, "avg": 4.7, "pf": 2.28}, "dn": {"n": 4633, "win": 83, "avg": 4.0, "pf": 2.01}, "per": [["2000–2007", {"n": 1738, "win": 83, "avg": 3.3, "pf": 1.71}], ["2008–2013", {"n": 1655, "win": 81, "avg": 3.4, "pf": 1.75}], ["2014–2019", {"n": 361, "win": 85, "avg": 5.5, "pf": 3.06}], ["2020–2026", {"n": 1481, "win": 84, "avg": 5.4, "pf": 3.04}]], "stop15": {"win": 65, "avg": 0.8}}, "sa": {"n": 1044, "win": 81, "avg": 4.7, "pf": 2.51, "days": 9, "al": -16.6, "worst": -21.9, "ex": 2.1, "dd50": -8.5, "dd75": -16.4, "dd90": -27.0, "since": 2011, "up": {"n": 167, "win": 81, "avg": 3.9, "pf": 2.01}, "dn": {"n": 877, "win": 81, "avg": 4.8, "pf": 2.63}, "per": [["2011–2013", {"n": 96, "win": 80, "avg": 4.7, "pf": 2.64}], ["2014–2019", {"n": 535, "win": 83, "avg": 5.0, "pf": 2.65}], ["2020–2026", {"n": 413, "win": 80, "avg": 4.2, "pf": 2.31}]], "stop15": {"win": 70, "avg": 2.0}}}
# The comparison behind the choice: [strategy, side (w = with the crowd/trend, c = against it), trades, win %,
# average trade %, average sessions held, profit factor, average gain over holding the market for the same days].
DIP_CMP={"us":[["hi52","w",10290,38,1.2,38,1.36,-0.5],["trend","w",9711,36,0.8,28,1.22,-0.4],["turtle20","w",47707,42,0.9,28,1.28,-0.7],["turtle55","w",23791,42,1.6,51,1.42,-0.9],["golden","w",8431,46,10.5,197,2.6,-2.0],["ma2050","w",31945,43,2.4,54,1.61,-0.7],["macd","w",27073,40,0.5,15,1.23,-0.4],["bbup","w",47096,39,0.3,17,1.12,-0.5],["ma50pb","w",31155,46,0.7,23,1.23,-0.5],["rsi2","c",79104,64,0.2,5,1.23,-0.2],["rsi30","c",17740,69,1.6,18,1.55,0.0],["bbdn","c",25934,70,0.8,12,1.43,-0.1],["deep","c",5235,83,4.1,22,2.04,0.7]],
 "sa":[["hi52","w",2026,37,2.9,35,1.7,1.2],["trend","w",2512,34,1.5,20,1.38,0.4],["turtle20","w",8602,37,1.7,28,1.47,0.0],["turtle55","w",3961,39,3.0,50,1.66,0.5],["golden","w",1887,32,4.4,145,1.49,3.0],["ma2050","w",7104,35,1.8,45,1.41,0.5],["macd","w",4342,34,0.4,15,1.13,0.0],["bbup","w",7532,37,1.4,17,1.49,0.2],["ma50pb","w",4310,40,0.5,20,1.14,0.5],["rsi2","c",14050,58,-0.1,5,0.92,0.1],["rsi30","c",6409,57,-0.4,20,0.89,0.3],["bbdn","c",3925,60,-0.2,13,0.94,0.4],["deep","c",1044,81,4.7,24,2.51,2.1]]}
def dips(s,Dd):
    # Live signals of the rule above from the last DIP['fresh'] closed sessions whose +10% target has not been touched.
    now=ny_now()
    if Dd and ny_date(Dd[-1][0])==now.date() and (now.hour,now.minute)<MK['close']: Dd=Dd[:-1]
    n=len(Dd)
    if n<300: return []
    c=[x[4] for x in Dd];h=[x[2] for x in Dd];W=DIP['win'];th=DIP['depth'];lim=0.115 if MK['id']=='sa' else 0.6;st=DIP_STATS[MK['id']]
    dep=lambda i:1-c[i]/max(h[i-W:i])
    last=-999;sig=None
    for i in range(n-130,n):
        if dep(i)<th or dep(i-1)>=th: continue
        if any(abs(c[j]/c[j-1]-1)>lim for j in range(i-W,i+1)): continue   # split or data glitch, not a real fall
        if i-last<W: continue
        last=i;sig=i
    if sig is None or n-1-sig>DIP['fresh']: return []
    i=sig;ref=Dd[i+1][1] if i+1<n else c[i]
    if abs(ref/c[i]-1)>lim: return []
    tgt=ref*(1+DIP['tgt']);cur=c[-1]
    if i+1<n and max(h[i+1:])>=tgt: return []   # target already reached
    return [dict(s=s,date=ny_date(Dd[i][0]).isoformat(),hi=round(max(h[i-W:i]),2),depth=round(dep(i)*100,1),sig=round(c[i],2),ref=round(ref,2),cur=round(cur,2),chg=round((cur/ref-1)*100,1),
        tgt=round(tgt,2),up=round((tgt/cur-1)*100,1),age=n-1-i,left=DIP['maxd']-(n-1-i),up200=c[i]>sum(c[i-199:i+1])/200,
        typ=round(ref*(1+st['dd50']/100),2),deep=round(ref*(1+st['dd75']/100),2),ext=round(ref*(1+st['dd90']/100),2))]
# --- "All schools" confluence (study, Nov 2026). Twelve bullish conditions, one per trading school, were scored on
# every stock-day of both markets: trend (Dow / moving averages), Fibonacci retracement, classic support, RSI, MACD,
# Japanese candles, volume (Wyckoff), Bollinger bands, market regime, relative strength, liquidity sweep (smart
# money / ICT) and Ichimoku. Findings: (1) simply counting how many schools agree predicts nothing: the 20-session
# return is the same for 3 schools as for 10, because trend schools and reversal schools contradict each other;
# (2) the one coherent combination that held up in both halves of US history is the pullback every school would
# sign: a strong stock in a rising market (trend + market + relative strength) that pulls back (RSI at or below 40
# and turning up, a 38-79% Fibonacci retracement, a touch of the lower Bollinger band) and sweeps the 10-session low
# before closing back above it. Buy the next open, sell at +8%, no stop (stops made it worse), out at session 40.
# (3) On the Saudi market the same combination LOSES, so nothing is suggested there.
# The live market filters use the market index (weekly) where the study used an equal-weight index of the stocks.
SCH=dict(tgt=0.08,maxd=40,fresh=10,need=('trend','market','relstr','rsi','sweep','fib','boll'))
SCH_NAMES=['trend','fib','support','rsi','macd','candle','volume','boll','market','relstr','sweep','ichimoku']
SCH_STATS={"us": {"on": True, "n": 2372, "win": 69, "avg": 2.1, "pf": 1.79, "days": 18, "al": -8.7, "worst": -15.2, "ex": 0.4, "dd50": -5.1, "dd75": -10.2, "dd90": -17.8, "since": 2000, "per": [["2000–2007", {"n": 635, "win": 67, "avg": 1.6, "pf": 1.5}], ["2008–2013", {"n": 473, "win": 73, "avg": 3.0, "pf": 2.38}], ["2014–2019", {"n": 573, "win": 68, "avg": 2.0, "pf": 1.83}], ["2020–2026", {"n": 691, "win": 70, "avg": 2.1, "pf": 1.74}]], "sc": [["7", {"n": 60, "win": 67, "avg": 0.8, "pf": 1.19}], ["8", {"n": 543, "win": 71, "avg": 2.6, "pf": 2.03}], ["9", {"n": 825, "win": 69, "avg": 2.0, "pf": 1.76}], ["10", {"n": 944, "win": 69, "avg": 2.0, "pf": 1.73}]], "stop8": {"win": 59, "avg": 1.0},
  "count": [[3, 1.1, 56], [4, 1.0, 56], [5, 1.0, 56], [6, 1.0, 56], [7, 1.0, 56], [8, 1.3, 57], [9, 1.4, 58], [10, 1.0, 56]], "base": [1.2, 57]},
 "sa": {"on": False, "n": 260, "win": 57, "avg": -0.6, "pf": 0.87, "days": 16, "al": -10.9, "worst": -20.1, "ex": 0.6, "dd50": -8.1, "dd75": -14.4, "dd90": -22.2, "since": 2011, "per": [["2014–2019", {"n": 97, "win": 62, "avg": 0.1, "pf": 1.03}], ["2020–2026", {"n": 143, "win": 52, "avg": -1.6, "pf": 0.7}]], "sc": [["8", {"n": 88, "win": 59, "avg": 0.2, "pf": 1.06}], ["9", {"n": 84, "win": 58, "avg": -0.4, "pf": 0.92}], ["10", {"n": 77, "win": 53, "avg": -1.6, "pf": 0.71}]], "stop8": {"win": 44, "avg": -1.2},
  "count": [[3, 0.2, 47], [4, 0.5, 48], [5, 0.5, 48], [6, 0.6, 48], [7, 0.5, 48], [8, 0.3, 46], [9, -0.7, 43], [10, -1.8, 42]], "base": [0.3, 47]}}
SPYR={}   # market index: 26-week return per trading week (filled by spy_map)
def schools(s,Dd):
    # Live signals of the confluence above: all SCH['need'] schools true on one of the last SCH['fresh'] closed
    # sessions (first such session in 10), target not touched yet. Each signal lists every school that agreed.
    st=SCH_STATS[MK['id']]
    if not st['on']: return []
    now=ny_now()
    if Dd and ny_date(Dd[-1][0])==now.date() and (now.hour,now.minute)<MK['close']: Dd=Dd[:-1]
    if len(Dd)<420: return []
    D=Dd[-420:];n=len(D);t=[x[0] for x in D];o=[x[1] for x in D];h=[x[2] for x in D];l=[x[3] for x in D];c=[x[4] for x in D];v=[x[5] for x in D]
    lim=0.115 if MK['id']=='sa' else 0.6
    ag=al=0.0;r=[50.0]*n
    for i in range(1,n):
        ch=c[i]-c[i-1];g=max(ch,0);ls=max(-ch,0)
        if i<=14: ag+=g/14;al+=ls/14
        else: ag=(ag*13+g)/14;al=(al*13+ls)/14
        r[i]=100-100/(1+ag/al) if al>0 else 100.0
    e12=e26=c[0];sg=0.0;hs=[0.0]*n
    for i in range(1,n):
        e12+=2/13*(c[i]-e12);e26+=2/27*(c[i]-e26);m=e12-e26;sg+=2/10*(m-sg);hs[i]=m-sg
    K=5;piv=[(j,l[j]) for j in range(K,n-K) if l[j]==min(l[j-K:j+K+1])]+[(j,h[j]) for j in range(K,n-K) if h[j]==max(h[j-K:j+K+1])]
    sma=lambda i,k:sum(c[i-k+1:i+1])/k
    def bl(i):
        w=c[i-19:i+1];m=sum(w)/20;return m-2*(sum((x-m)**2 for x in w)/20)**.5
    def at(i):
        if any(abs(c[j]/c[j-1]-1)>lim for j in range(i-20,i+1)): return None
        f={};k=wk(t[i]);ma200=sma(i,200)
        f['rsi']=min(r[i],r[i-1],r[i-2])<=40 and r[i]>r[i-1]
        l10=min(l[i-10:i]);f['sweep']=l[i]<l10<c[i]
        if not(f['rsi'] and f['sweep']): return f   # cheap exit: both are required
        f['trend']=c[i]>ma200 and sma(i,50)>ma200
        w=h[i-59:i+1];hi=max(w);am=i-59+w.index(hi);lo=min(l[max(0,am-59):am+1])
        f['fib']=hi/lo-1>=0.15 and am<i-2 and 0.382<=(hi-c[i])/(hi-lo)<=0.786
        f['support']=any(j+10<=i<j+250 and abs(l[i]/p-1)<=0.02 and c[i]>p for j,p in piv)
        f['macd']=(hs[i]>hs[i-1] and hs[i-1]<=hs[i-2] and hs[i]<0) or (hs[i]>0 and hs[i-1]<=0)
        body=abs(c[i]-o[i]);rg=max(h[i]-l[i],1e-9);lw=min(o[i],c[i])-l[i]
        f['candle']=(lw>=2*body and (c[i]-l[i])/rg>=0.66) or (c[i]>o[i] and c[i-1]<o[i-1] and c[i]>=o[i-1] and o[i]<=c[i-1]) or c[i]>h[i-1]
        f['volume']=v[i]>=1.2*sum(v[i-49:i+1])/50 and c[i]>o[i]
        f['boll']=min(l[j]-bl(j) for j in (i-2,i-1,i))<=0 and c[i]>bl(i)
        f['market']=SPY.get(k,-1)>0
        f['relstr']=c[i]/c[i-126]-1>SPYR.get(k,9)
        mid=lambda a,b,q:(max(h[a-q+1:a+1])+min(l[a-q+1:a+1]))/2 if b else 0
        ten=mid(i,1,9);kij=mid(i,1,26);j=i-26
        f['ichimoku']=c[i]>max((mid(j,1,9)+mid(j,1,26))/2,mid(j,1,52)) and ten>=kij
        return f
    last=-99;sig=None
    for i in range(n-45,n):
        f=at(i)
        if not f or not all(f.get(x) for x in SCH['need']) or i-last<10: continue
        last=i;sig=(i,f)
    if not sig or n-1-sig[0]>SCH['fresh']: return []
    i,f=sig;ref=o[i+1] if i+1<n else c[i]
    if abs(ref/c[i]-1)>lim: return []
    tgt=ref*(1+SCH['tgt']);cur=c[-1]
    if i+1<n and max(h[i+1:])>=tgt: return []
    ok=[x for x in SCH_NAMES if f.get(x)]
    return [dict(s=s,date=ny_date(t[i]).isoformat(),sig=round(c[i],2),ref=round(ref,2),cur=round(cur,2),chg=round((cur/ref-1)*100,1),tgt=round(tgt,2),up=round((tgt/cur-1)*100,1),
        age=n-1-i,left=SCH['maxd']-(n-1-i),ok=ok,cnt=len(ok),rsi=round(r[i]),low=round(l[i],2),
        typ=round(ref*(1+st['dd50']/100),2),deep=round(ref*(1+st['dd75']/100),2),ext=round(ref*(1+st['dd90']/100),2))]
PAT_STATS={"us": {"d": {"falling_wedge": {"n": 573, "far": 81, "stopd": 19, "rew": 3.9, "risk": 5.3, "exp": 1.93}, "down_channel": {"n": 1065, "far": 54, "stopd": 41, "rew": 11.2, "risk": 6.0, "exp": 3.0}}, "h4": {"falling_wedge": {"n": 68, "far": 71, "stopd": 29, "rew": 2.9, "risk": 2.9, "exp": 1.39}, "down_channel": {"n": 133, "far": 47, "stopd": 50, "rew": 7.9, "risk": 3.3, "exp": 1.92}}, "h1": {"falling_wedge": {"n": 198, "far": 79, "stopd": 21, "rew": 1.6, "risk": 1.9, "exp": 0.79}, "down_channel": {"n": 446, "far": 56, "stopd": 43, "rew": 4.0, "risk": 1.8, "exp": 1.22}}}, "sa": {"d": {"falling_wedge": {"n": 142, "far": 73, "stopd": 27, "rew": 3.7, "risk": 4.8, "exp": 1.31}, "down_channel": {"n": 304, "far": 52, "stopd": 44, "rew": 10.4, "risk": 6.2, "exp": 3.03}}, "h4": {"falling_wedge": {"n": 65, "far": 60, "stopd": 40, "rew": 2.9, "risk": 3.1, "exp": 0.49}, "down_channel": {"n": 119, "far": 57, "stopd": 42, "rew": 5.9, "risk": 3.5, "exp": 2.05}}, "h1": {"falling_wedge": {"n": 138, "far": 72, "stopd": 28, "rew": 1.2, "risk": 2.2, "exp": 0.23}, "down_channel": {"n": 268, "far": 46, "stopd": 50, "rew": 4.3, "risk": 2.2, "exp": 1.13}}}}
PAT_ALL={"us": {"d": {"n": 16713, "far": 39, "stopd": 43, "exp": 0.16}, "h4": {"n": 1764, "far": 37, "stopd": 50, "exp": 0.04}, "h1": {"n": 5713, "far": 41, "stopd": 45, "exp": -0.03}}, "sa": {"d": {"n": 2104, "far": 41, "stopd": 46, "exp": 0.11}, "h4": {"n": 761, "far": 38, "stopd": 53, "exp": 0.04}, "h1": {"n": 1995, "far": 40, "stopd": 47, "exp": -0.05}}}
# per timeframe: line-fit tolerance, breakout margin, minimum slope to call a line falling, minimum width,
# and how many closed bars back a "returned inside" signal still counts as fresh
PCFG={'d':dict(tol=0.025,brk=0.01,F=0.03,wmin=0.02,fresh=6),'h4':dict(tol=0.02,brk=0.005,F=0.03,wmin=0.02,fresh=4),'h1':dict(tol=0.015,brk=0.004,F=0.02,wmin=0.012,fresh=7)}
# --- Pullback from the peak (study, Nov 2026). Question tested: does each stock repeat a "signature" fall (a fixed or
# near-fixed % drop) before it reverses? Answer: no. Out of sample, 25% of falls end within 15% of the stock's own
# median fall, against 24% for a memoryless random process; the stock's own median predicts the next fall no better
# than one number for all stocks; and at a given absolute depth it makes no difference whether that depth equals
# the stock's usual fall. What does matter is absolute depth together with trend: on US history a first close 12%
# or more below the swing high (8% zigzag) while the close is still above its 200-day average beat the equal-weight
# market by about 1% over 20 sessions in every period since 1980. Rule kept: buy the next open, +8% target, -8%
# stop, out at session 40. Hourly and 4-hour versions (2 years of data) showed no edge of their own after costs:
# small intraday falls of 3-8% lose, and only falls of 12%+ (the daily rule again) are positive. On the Saudi
# market the rule loses with a stop, so nothing is suggested there. Shown in its own tab, not in the trade blotter.
PB=dict(th=0.08,dep=0.12,cap=0.22,tgt=0.08,stop=0.08,maxd=40,fresh=5)
PB_STATS={'us':dict(on=True,n=17249,win=58,avg=1.17,pf=1.35,ex=0.95,t=5.4,dd50=-8.4,dd75=-16.2,since=1980,per=[['1980–1999',dict(n=5162,win=58,avg=1.12,pf=1.33,ex=0.94)],['2000–2007',dict(n=3841,win=57,avg=0.96,pf=1.28,ex=0.85)],['2008–2013',dict(n=2394,win=60,avg=1.45,pf=1.45,ex=0.83)],['2014–2019',dict(n=1459,win=61,avg=1.54,pf=1.51,ex=0.48)],['2020–2026',dict(n=4052,win=58,avg=1.16,pf=1.34,ex=1.28)]],sig=[25.4,23.6]),
          'sa':dict(on=False,n=3323,win=50,avg=-0.23,pf=0.95,ex=0.52,t=1.6,dd50=-9.6,dd75=-17.2,since=2008,per=[['2008–2013',dict(n=683,win=47,avg=-0.80,pf=0.83,ex=-0.60)],['2014–2019',dict(n=891,win=52,avg=-0.02,pf=1.00,ex=0.74)],['2020–2026',dict(n=1744,win=50,avg=-0.11,pf=0.97,ex=0.85)]],sig=[23.2,22.5])}
# Per timeframe, stocks above the daily 200-day average: [fall from peak, cases, win % (equal target and stop), excess
# over the market after costs %, t-stat, first half, second half]. Daily horizon 20 sessions; 4h 20 bars; 1h 35 bars.
PB_TF={'us':{'d':[['4–8%',48790,55,-0.08,-0.8,None,None],['8–12%',47042,56,0.46,3.2,None,None],['12–16%',18435,58,0.88,5.9,None,None],['16–22%',6678,59,1.86,5.9,None,None]],
             'h4':[['5–8%',8266,51,0.17,1.1,0.68,-0.22],['8–12%',3963,53,0.21,0.7,1.1,-0.34],['12–16%',1033,53,1.1,0.8,1.58,0.81],['16%+',402,55,0.76,0.9,1.36,0.51]],
             'h1':[['3–5%',27529,50,-0.14,-0.7,-0.09,-0.2],['5–8%',14378,52,0.08,0.7,0.0,0.16],['8–12%',4734,52,0.18,1.0,-0.06,0.41],['12%+',1101,53,0.75,2.0,0.57,0.93]]},
       'sa':{'d':[['4–8%',5759,51,0.35,0.0,None,None],['8–12%',6691,50,0.11,0.6,None,None],['12–16%',3211,51,0.35,1.3,None,None],['16–22%',1565,51,2.04,1.1,None,None]],
             'h4':[['5–8%',1955,46,1.8,0.9,4.41,0.25],['8–12%',921,44,0.65,0.9,0.12,0.93],['12–16%',200,40,-0.87,-0.3,0.41,-1.34],['16%+',70,57,-0.17,0.6,None,-0.63]],
             'h1':[['3–5%',5806,43,-0.58,-1.1,-0.77,-0.39],['5–8%',3246,44,1.09,1.3,2.42,-0.18],['8–12%',943,42,-0.35,-0.3,-0.86,0.1],['12%+',148,47,4.21,0.5,11.14,-2.18]]}}
def pullbacks(s,Dd):
    # Live signals of the rule above from the last PB['fresh'] closed sessions whose target and stop are both untouched.
    if not PB_STATS[MK['id']]['on']: return []
    now=ny_now()
    if Dd and ny_date(Dd[-1][0])==now.date() and (now.hour,now.minute)<MK['close']: Dd=Dd[:-1]
    Dd=Dd[-700:];n=len(Dd)
    if n<300: return []
    o=[x[1] for x in Dd];h=[x[2] for x in Dd];l=[x[3] for x in Dd];c=[x[4] for x in Dd];th=PB['th']
    ma=lambda i:sum(c[i-199:i+1])/200
    trend=1;H=h[0];Hi=0;L=l[0];fired=False;sig=None
    for i in range(1,n):
        if abs(c[i]/c[i-1]-1)>0.5: trend=1;H=h[i];Hi=i;fired=False;continue   # split or data glitch
        if trend==1:
            if h[i]>=H: H=h[i];Hi=i;fired=False
            elif l[i]<=H*(1-th): trend=-1;L=l[i]
        else:
            if l[i]<=L: L=l[i]
            elif h[i]>=L*(1+th): trend=1;H=h[i];Hi=i;fired=False;continue
        if fired or i<260: continue
        dep=1-c[i]/H
        if dep<PB['dep']: continue
        fired=True
        if dep<PB['cap'] and c[i]>ma(i): sig=(i,H,Hi,dep)
    if sig is None or n-1-sig[0]>PB['fresh']: return []
    i,H,Hi,dep=sig;ref=o[i+1] if i+1<n else c[i];tgt=ref*(1+PB['tgt']);stop=ref*(1-PB['stop']);cur=c[-1]
    if i+1<n and (max(h[i+1:])>=tgt or min(l[i+1:])<=stop): return []
    a0=n-120
    return [dict(s=s,date=ny_date(Dd[i][0]).isoformat(),hi=round(H,2),hidate=ny_date(Dd[Hi][0]).isoformat(),depth=round(dep*100,1),sig=round(c[i],2),ref=round(ref,2),cur=round(cur,2),chg=round((cur/ref-1)*100,1),
        tgt=round(tgt,2),stop=round(stop,2),age=n-1-i,left=PB['maxd']-(n-1-i),ma=round(ma(n-1),2),vl=PB['fresh']-(n-1-i),vu='s',
        chart=[[round(o[j],2),round(h[j],2),round(l[j],2),round(c[j],2)] for j in range(a0,n)],mal=[round(ma(j),2) for j in range(a0,n)],pk=[max(Hi-a0,0),round(H,2)],sg=i-a0)]
# --- Trend trap: an ascending trendline is broken (a close below it) and within 5 sessions the price closes back
# above it. Studied on every US stock since 1980 (see TL_STATS). Daily only: the 1-hour version loses money.
TL=dict(K=5,tol=0.012,brk=0.004,R=5,minspan=30,maxspan=260,stale=90,fresh=3,rr=2.0,maxd=40,buf=0.002)
TL_STATS=dict(n=35634,back=45,back25=65,win=42,avg=0.63,pf=1.25,days=14,since=1980,ex=dict(sig=0.65,brk=0.65,touch=0.48),
    recent=dict(n=12662,win=42,avg=0.60,pf=1.24,ex=0.26,since=2014),
    per=[['1980–1999',10150,43,0.77,0.87],['2000–2007',6178,42,0.66,1.14],['2008–2013',5420,43,0.50,0.50],['2014–2019',5541,44,0.67,0.29],['2020–2026',7121,40,0.55,0.23]],
    tf=[['يومي',35634,45,42,0.63,1.25,'منذ 1980'],['4 ساعات',3474,39,40,0.26,1.12,'سنتان'],['ساعة',10137,35,38,-0.10,0.92,'سنتان']],
    rob=[1.18,1.27],model=dict(all=1.24,top=1.33,wtop=47))
def tlines(s,Dd):
    now=ny_now()
    if Dd and ny_date(Dd[-1][0])==now.date() and (now.hour,now.minute)<MK['close']: Dd=Dd[:-1]
    Dd=Dd[-520:];n=len(Dd)
    if n<300: return []
    o=[x[1] for x in Dd];h=[x[2] for x in Dd];l=[x[3] for x in Dd];c=[x[4] for x in Dd];K=TL['K'];tol=TL['tol'];PL=[];line=None;st=None;sig=None
    def best(i):
        bst=None
        for bi in range(len(PL)-1,max(len(PL)-4,0),-1):
            xb,pb=PL[bi]
            for ai in range(bi-1,max(bi-11,-1),-1):
                xa,pa=PL[ai]
                if i-xa>TL['maxspan']: break
                if i-xa<TL['minspan'] or xb-xa<K*2 or pb<=pa: continue
                m=(pb-pa)/(xb-xa);b=pa-m*xa
                if not c[i]>b+m*i or any(l[x]<(b+m*x)*(1-tol) for x in range(xa,i+1)): continue
                T=[(x,p) for x,p in PL[ai:] if abs(p-(b+m*x))<=tol*(b+m*x)];key=(len(T),i-xa)
                if bst is None or key>bst[0]: bst=(key,dict(m=m,b=b,xa=xa,T=T,last=T[-1][0],born=i))
        return bst and bst[1]
    for i in range(2*K,n):
        j=i-K
        if l[j]==min(l[j-K:j+K+1]):
            PL.append((j,l[j]))
            if st is None:
                nl=best(i)
                if nl: line=nl
        if line is None: continue
        y=line['b']+line['m']*i
        if st is None:
            if i-line['last']>TL['stale'] or y<=0: line=None
            elif c[i]<y*(1-TL['brk']) and i>line['born']: st=(i,l[i])
        else:
            i0,ext=st;ext=min(ext,l[i]);st=(i0,ext)
            if c[i]>y: sig=(i,i0,ext,line);line=None;st=None
            elif i-i0>=TL['R']: line=None;st=None
    if sig is None or n-1-sig[0]>TL['fresh']: return []
    i,i0,ext,L=sig;ref=o[i+1] if i+1<n else c[i];risk=1-ext/ref+TL['buf']
    if not 0.003<risk<=0.15: return []
    stop=ref*(1-risk);tgt=ref*(1+TL['rr']*risk);cur=c[-1]
    if i+1<n and (max(h[i+1:])>=tgt or min(l[i+1:])<=stop): return []
    ln=lambda x:L['b']+L['m']*x;a0=max(0,L['xa']-8,n-170);r=lambda v:round(v,2);xs=max(L['xa'],a0)
    return [dict(s=s,date=ny_date(Dd[i][0]).isoformat(),bdate=ny_date(Dd[i0][0]).isoformat(),ref=r(ref),cur=r(cur),chg=round((cur/ref-1)*100,1),stop=r(stop),tgt=r(tgt),rew=round(TL['rr']*risk*100,1),risk=round(risk*100,1),
        touches=len(L['T']),span=i-L['xa'],below=i-i0,depth=round((1-ext/ln(i0))*100,1),age=n-1-i,left=TL['maxd']-(n-1-i),vl=TL['fresh']-(n-1-i),vu='s',
        geo=dict(bars=[[r(o[k]),r(h[k]),r(l[k]),r(c[k])] for k in range(a0,n)],line=[[xs-a0,r(ln(xs))],[n-1-a0,r(ln(n-1))]],T=[[x-a0,r(p)] for x,p in L['T'] if x>=a0],brk=[i0-a0,r(ext)],ret=i-a0))]
def _geo(Dd,pat,i0,i,ext):
    # What the page needs to draw a pattern signal on its own timeframe: the bars, the two fitted lines, the six
    # pivots they were fitted to, the bar that closed below the lower line and the bar that closed back inside.
    n=len(Dd);a0=max(0,pat['x0']-6,n-170);r=lambda v:round(v,2);u=lambda x:pat['bu']+pat['mu']*x;lo=lambda x:pat['bl']+pat['ml']*x;x0=max(pat['x0'],a0)
    return dict(bars=[[r(x[1] or x[4]),r(x[2]),r(x[3]),r(x[4])] for x in Dd[a0:]],up=[[x0-a0,r(u(x0))],[n-1-a0,r(u(n-1))]],lo=[[x0-a0,r(lo(x0))],[n-1-a0,r(lo(n-1))]],
        ph=[[j-a0,r(p)] for j,p in pat['A'] if j>=a0],pl=[[j-a0,r(p)] for j,p in pat['B'] if j>=a0],brk=[i0-a0,r(ext)],ret=i-a0)
def patterns(s,Dd,tf='d'):
    # Dd rows: (ts,open,high,low,close,volume). Intraday callers pass closed bars only.
    cfg=PCFG[tf];now=ny_now()
    if tf=='d' and Dd and ny_date(Dd[-1][0])==now.date() and (now.hour,now.minute)<MK['close']: Dd=Dd[:-1]
    Dd=Dd[-460:];n=len(Dd)
    if n<300: return []
    K=5;h=[x[2] for x in Dd];l=[x[3] for x in Dd];c=[x[4] for x in Dd];PH=[];PL=[];pat=None;st=None;out=[]
    def fit(P):
        k=len(P);mx=sum(p[0] for p in P)/k;my=sum(p[1] for p in P)/k;sxx=sum((p[0]-mx)**2 for p in P)
        m=sum((p[0]-mx)*(p[1]-my) for p in P)/sxx;b=my-m*mx
        return m,b,max(abs(p[1]-(m*p[0]+b))/p[1] for p in P)
    for i in range(K*2,n):
        j=i-K;newp=False
        if h[j]==max(h[j-K:j+K+1]): PH.append((j,h[j]));newp=True
        if l[j]==min(l[j-K:j+K+1]): PL.append((j,l[j]));newp=True
        if st is None and newp and len(PH)>=3 and len(PL)>=3:
            A=PH[-3:];B=PL[-3:];x0=min(A[0][0],B[0][0])
            if 25<=i-x0<=150:
                mu,bu,du=fit(A);ml,bl,dl=fit(B)
                if du<=cfg['tol'] and dl<=cfg['tol']:
                    u0,u1,l0,l1=mu*x0+bu,mu*i+bu,ml*x0+bl,ml*i+bl
                    if min(u0,u1,l0,l1)>0 and u1>l1 and u0>l0:
                        mid=(u0+l0)/2;cu=(u1-u0)/mid;cl=(l1-l0)/mid;w0=(u0-l0)/mid;w1=(u1-l1)/mid
                        if w1>=cfg['wmin'] and w0<=0.6 and cu<=-cfg['F'] and cl<=-cfg['F'] and l1<c[i]<u1:
                            pat=dict(typ='falling_wedge' if w1<0.7*w0 else 'down_channel',mu=mu,bu=bu,ml=ml,bl=bl,born=i,x0=x0,A=A,B=B)
                        else: pat=None
        if pat is None: continue
        u=pat['bu']+pat['mu']*i;lo=pat['bl']+pat['ml']*i
        if st is None:
            if i-pat['born']>40 or u<=lo: pat=None
            elif c[i]<lo*(1-cfg['brk']) and i>pat['born']: st=(i,l[i])
            elif c[i]>u*(1+cfg['brk']): pat=None
        else:
            i0,ext=st;ext=min(ext,l[i]);st=(i0,ext)
            if c[i]>lo:
                if i>=n-cfg['fresh']:   # a fresh signal: returned inside within the last few closed bars
                    e=c[i];alive=True;tg=u
                    for jj in range(i+1,n):
                        if h[jj]>=pat['bu']+pat['mu']*jj or c[jj]<ext: alive=False;break
                    cur=c[-1];tgn=pat['bu']+pat['mu']*(n-1)
                    if alive and tg>e*1.01 and tgn>cur*1.01:
                        out.append(dict(s=s,tf=tf,typ=pat['typ'],date=ny_date(Dd[i][0]).isoformat() if tf=='d' else d.datetime.fromtimestamp(Dd[i][0],_tz()).strftime('%Y-%m-%d %H:%M'),close=round(e,2),cur=round(cur,2),chg=round((cur/e-1)*100,1),tgt=round(tg,2),stop=round(ext,2),rew=round((tg/e-1)*100,1),risk=round((1-ext/e)*100,1),age=n-1-i,geo=_geo(Dd,pat,i0,i,ext)))
                pat=None;st=None
            elif i-i0>=5: pat=None;st=None
    return out
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
    cd=[dict(s=s,k=k,date=ny_date(t[i]).isoformat(),sig=round(c[i],2),cur=round(cur,2),chg=round((cur/c[i]-1)*100,1),mx=round(max([x[2] for x in full[i+1:]]+[cur]),2),age=n-1-i,f=cf.get((k,i))) for k,i in cand]
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
DAYS=[]
def spy_map():
    # market regime per trading week: the market index relative to its 40-week average.
    # MK['index'] is one symbol, or a basket of leading stocks averaged equally when no index history is available.
    def weekly(sym):
        u="https://query1.finance.yahoo.com/v8/finance/chart/"+urllib.parse.quote(sym)+"?period1=0&period2=4000000000&interval=1d"
        for _ in range(3):
            try:
                r=json.load(urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'}),timeout=40))['chart']['result'][0]
                W={};dd=[]
                for a,c in zip(r['timestamp'],r['indicators']['quote'][0]['close']):
                    if c: W[wk(a)]=c;dd.append(ny_date(a))
                if len(dd)>len(DAYS): DAYS[:]=dd   # longest history = the market's trading calendar
                return W
            except Exception: pass
        return {}
    SPYR.clear();syms=MK['index'] if isinstance(MK['index'],list) else [MK['index']]
    Ws=[w for w in (weekly(x) for x in syms) if len(w)>60]
    if not Ws: return {}
    ks=sorted(set().union(*Ws));lvl={};v=100.0
    for a,b in zip(ks,ks[1:]):
        r=[w[b]/w[a]-1 for w in Ws if a in w and b in w]
        if r: v*=1+sum(r)/len(r)
        lvl[b]=v
    ks=sorted(lvl);SPYR.update({ks[i]:lvl[ks[i]]/lvl[ks[i-26]]-1 for i in range(26,len(ks))})
    return {ks[i]:lvl[ks[i]]/(sum(lvl[k] for k in ks[i-40:i])/40)-1 for i in range(40,len(ks))}
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
                if hit or last[2]>=T[0] or any(x[3]<lo for x in after): continue  # reached a target already (even inside the signal candle), or stopped out
                sc=score(feats(C,i,p,lo,L['h'],SPY))
                out.append(dict(s=s,side='دعم',level=round(p,2),holds=L['h'],close=round(c,2),ext=round(lo,2),pen=round((1-lo/p)*100,1),wk=wks,age=k,pos=round(ps*100),hit=hit,pr=sc[0] if sc else None,grade=sc[1] if sc else None,cur=round(cur,2),chg=round((cur/c-1)*100,1),T=[round(x,2) for x in T],kind='ذيل في نفس الشمعة' if prev[3]>=p else 'رجوع بعد إغلاق تحت المستوى'))
            else:
                T=[c*0.95,c*0.946,c*0.88];mn=min([x[1] for x in after],default=9e9);hit=sum(mn<=x for x in T)
                if hit or last[1]<=T[0] or any(x[3]>hi for x in after): continue
                out.append(dict(s=s,side='مقاومة',level=round(p,2),holds=L['h'],close=round(c,2),ext=round(hi,2),pen=round((hi/p-1)*100,1),wk=wks,age=k,pos=round(ps*100),hit=hit,cur=round(cur,2),chg=round((cur/c-1)*100,1),T=[round(x,2) for x in T],kind='ذيل في نفس الشمعة' if prev[3]<=p else 'رجوع بعد إغلاق فوق المستوى'))
    return out
# --- Self-tracking: every suggestion is logged the first day it is shown, then graded win/loss from later prices,
# whether or not the user traded it. Live results adjust the shown probability (Bayesian shrinkage toward the
# backtest rate) and pause a category whose live record turns bad; a paused category keeps being logged in the
# background and is switched back on if its record recovers.
LOGF=os.path.join(H,'log.txt')
PRIOR={'fake|A':(68,20),'fake|B':(66,20),'fake|C':(57,20),'fake4':(60,20),'ct|panic':(71,20),'ct|lo52':(78,20)}  # (expected win %, weight)
HORIZON={'sch':60,'dip':88,'gap':30,'fake':91,'fake4':45,'ct':88,'pat':60,'pat4':30,'pat1':14,'tl':60}  # calendar days before an unresolved suggestion counts as a miss
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
def selflearn(fake,fake4,ccand,tails,labs,pats=(),gps=(),dps=(),scs=(),tls=()):
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
    for g in gps: g['cat']='gap|'+g['b'];g['lid']=add('gap',g['s'],g['conf'],g['b'],g['ref'],g['pc'],None,g['cat'],None)
    for x in scs: x['cat']='sch';x['lid']=add('sch',x['s'],x['date'],'all',x['ref'],x['tgt'],None,'sch',None)
    for x in dps: x['cat']='dip';x['lid']=add('dip',x['s'],x['date'],'deep',x['ref'],x['tgt'],None,'dip',None)
    for p in pats:
        kd={'d':'pat','h4':'pat4','h1':'pat1'}[p['tf']];p['cat']=kd+'|'+p['typ'];p['lid']=add(kd,p['s'],p['date'][:10],p['typ']+'|'+p['date'][10:],p['close'],p['tgt'],p['stop'],p['cat'],None)
    for x in tls: x['cat']='tl';x['lid']=add('tl',x['s'],x['date'],'up',x['ref'],x['tgt'],x['stop'],'tl',None)
    for f in fake4: f['cat']='fake4';f['lid']=add('fake4',f['s'],f['wk'][:10],f['level'],f['close'],f['T'][0],f['ext'],'fake4',None)
    for c in ccand:
        if c.get('act','').startswith('buy'): c['cat']='ct|'+c['k'];c['lid']=add('ct',c['s'],c['date'],c['k'],c['sig'],c['tgt'],None,c['cat'],c.get('pr'),c.get('grade'))
    mine=[e for e in log if e.get('mk','us')==MK['id']]
    for e in mine:
        if 'pt' not in e or e['pt']['status']=='pending':  # the exit rule is frozen once the paper trade is actually entered
            lb=labs.get(e['kind']) or {};ch=lb['champ'] if lb.get('valid_ok') else DEFAULT_PT[e['kind']];g=e.get('grade')
            if e['kind'].startswith('pat') or e['kind']=='tl': ch=dict(ch,T=round(e['tgt']/e['entry']-1,4))  # target = the pattern's upper line
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
    pri=dict(PRIOR);pri['tl']=(TL_STATS['win'],20);pri['dip']=(DIP_STATS[MK['id']]['win'],20)
    if SCH_STATS[MK['id']]['on']: pri['sch']=(SCH_STATS[MK['id']]['win'],20)
    for b,v in GAP_STATS[MK['id']].items(): pri['gap|'+b]=(v['fill'],20)   # expected: the gap closes within 20 sessions
    for tf,kd in (('d','pat'),('h4','pat4'),('h1','pat1')):  # expected hit rate of each pattern on this market and timeframe
        for typ,v in PAT_STATS[MK['id']].get(tf,{}).items(): pri[kd+'|'+typ]=(round(100*v['far']/max(1,v['far']+v['stopd'])),20)
    tm=MODEL['info'].get('test_mid') or MODEL['info'].get('test') or {}
    for g,v in tm.items():  # expected rate per grade = what the model in use achieved on this market's recent unseen signals
        if v and v[1] is not None and v[0]>=15: pri['fake|'+g]=(round(v[1]),20)
    for c in list(pri)+sorted({e['cat'] for e in mine}-set(pri)):
        pr,k=pri.get(c,(50,10))
        E=[e for e in mine if e['cat']==c];w=sum(e['status']=='win' for e in E);l=sum(e['status']=='loss' for e in E);n=w+l
        post=(pr*k+100*w)/(k+n);on=not(n>=15 and 100*w/n<(34 if c=='tl' else 45))   # the trend trap aims at twice its risk: it breaks even near 34%
        cats[c]=dict(n=len(E),open=len(E)-n,w=w,l=l,rate=round(100*w/n) if n else None,prior=pr,adj=round(post),on=on)
    json.dump(log,open(LOGF,'w',encoding='utf8'),ensure_ascii=False)
    for f in fake:
        if 'cat' in f and f.get('pr') is not None: f['adj']=max(1,min(99,f['pr']+cats[f['cat']]['adj']-cats[f['cat']]['prior']))
    for x in fake4: x['adj']=cats['fake4']['adj']
    for p in pats: p['adj']=cats[p['cat']]['adj']
    for g in gps: g['adj']=cats[g['cat']]['adj']
    for x in tls: x['adj']=cats['tl']['adj']
    for x in dps: x['adj']=cats['dip']['adj']
    for x in scs: x['adj']=cats['sch']['adj']
    for c in ccand:
        if 'cat' in c and c.get('pr') is not None: c['adj']=max(1,min(99,c['pr']+cats[c['cat']]['adj']-cats[c['cat']]['prior']))
    ok=lambda x:'cat' not in x or cats[x['cat']]['on']
    recent=sorted([e for e in mine if e['status']!='open'],key=lambda e:e['res'],reverse=True)[:25]
    perf=dict(cats=cats,paper=pp,labs=labs,total=len(mine),recent=[dict(s=e['s'],kind=e['kind'],d=e['d'],res=e['res'],status=e['status'],entry=e['entry'],tgt=e['tgt']) for e in recent],
        today=[dict(s=e['s'],kind=e['kind'],status=e['status']) for e in done],since=min([e['first'] for e in mine],default=today))
    return [f for f in fake if ok(f)],[f for f in fake4 if ok(f)],[c for c in ccand if ok(c)],[p for p in pats if ok(p)],[g for g in gps if ok(g)],perf,[x for x in dps if ok(x)],[x for x in scs if ok(x)]
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
MAXD={'tl':40,'sch':40,'dip':60,'gap':20,'ct':60,'fake':65,'fake4':30,'pat':40,'pat4':20,'pat1':7};DEFAULT_PT={'tl':dict(T=None,S='wick',f='all'),'sch':dict(T=SCH['tgt'],S=None,f='all'),'dip':dict(T=DIP['tgt'],S=None,f='all'),'gap':dict(T=None,S=None,f='all'),'pat':dict(T=None,S='wick',f='all'),'pat4':dict(T=None,S='wick',f='all'),'pat1':dict(T=None,S='wick',f='all'),'ct':dict(T=0.06,S=None,f='all'),'fake':dict(T=0.05,S='wick',f='all'),'fake4':dict(T=0.03,S='wick',f='all')}
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
def plab(data,model,weekly,years=3,span=8):
    # Portfolio lab for "buy the fallen stock" signals: a real portfolio with limited slots, not an average per trade.
    # Rules are ranked on the older window by yearly return / worst drawdown; the winner is then reported on the
    # most recent years, which neither it nor the scoring model was fitted on, next to an equal-weight buy-and-hold
    # of the same stocks (the fair benchmark, since the stock list is today's survivors).
    import math
    if len(data)<400 or len(DAYS)<1500: return None
    di={x:i for i,x in enumerate(DAYS)};now=ny_now().date();cutd=d.date(now.year-years,now.month,1);a0=d.date(cutd.year-span,cutd.month,1)
    days_i=[i for i,x in enumerate(DAYS) if x>=a0]
    if not days_i: return None
    start=days_i[0];mid=next((i for i,x in enumerate(DAYS) if x>=cutd),None);end=len(DAYS)-1
    if mid is None or mid-start<500 or end-mid<250: return None
    sig={}
    for t,k,f,y,(H,L,C,_) in data:
        i=di.get(ny_date(t))
        if i is not None and i>=start-1:
            z=model['b']+sum(model['w'][j]*((f[j]-model['mu'][j])/model['sd'][j]) for j in range(len(f)))
            sig.setdefault(i,[]).append((1/(1+math.exp(-z)),C,L))
    thr={'all':0,'AB':model['cut'][0],'A':model['cut'][1]};cost=COST/2
    def run(N,f,stop,a,b):
        cash=1.0;pos=[];eq=[];n=0
        for i in range(a,b+1):
            keep=[]
            for p in pos:
                k=i-p[0]
                if k>=1 and stop and p[3][k-1]<=-stop: cash+=p[1]*(1-stop)*(1-cost);continue
                if k>=59: cash+=p[1]*(1+p[2][59])*(1-cost)
                else: keep.append(p)
            pos=keep;val=cash+sum(p[1]*(1+p[2][max(i-p[0]-1,0)]) if i>p[0] else p[1] for p in pos)
            for pr,C,L in sorted(sig.get(i-1,[]),key=lambda x:-x[0]):
                if len(pos)>=N or pr<thr[f]: break
                amt=min(val/N,cash)
                if amt<=0: break
                cash-=amt;pos.append([i,amt*(1-cost),C,L]);n+=1
            eq.append(cash+sum(p[1]*(1+p[2][min(i-p[0],59)]) for p in pos))
        yrs=(DAYS[b]-DAYS[a]).days/365.25;pk=0;dd=0
        for v in eq: pk=max(pk,v);dd=min(dd,v/pk-1)
        return dict(cagr=round((max(eq[-1],1e-9)**(1/yrs)-1)*100,1),maxdd=round(dd*100),n=n)
    res=[]
    for f in ('all','AB','A'):
        for N in (10,20):
            for stop in (None,0.12,0.20):
                tr=run(N,f,stop,start,mid-1)
                if tr['n']>=40: res.append(dict(T=None,S=stop,f=f,N=N,tr=tr,va=run(N,f,stop,mid,end)))
    if not res: return None
    res.sort(key=lambda r:-(r['tr']['cagr']/max(1,-r['tr']['maxdd'])))
    base=next((r for r in res if (r['f'],r['N'],r['S'])==('all',10,None)),res[-1])
    # fair benchmark over the recent window, from weekly closes
    cut_ts=d.datetime(cutd.year,cutd.month,cutd.day,tzinfo=d.timezone.utc).timestamp();acc={}
    for B in weekly:
        x=[b for b in B if b[0]>=cut_ts]
        if len(x)>years*40 and x[0][0]<cut_ts+21*86400:
            for b in x: v=acc.setdefault(wk(b[0]),[0.0,0]);v[0]+=b[3]/x[0][3];v[1]+=1
    ks=sorted(k for k,v in acc.items() if v[1]>=20);bench=None
    if len(ks)>50:
        ew=[acc[k][0]/acc[k][1] for k in ks];pk=0;dd=0
        for v in ew: pk=max(pk,v);dd=min(dd,v/pk-1)
        bench=dict(cagr=round((ew[-1]**(1/((DAYS[end]-cutd).days/365.25))-1)*100,1),maxdd=round(dd*100))
    return dict(port=True,champ=res[0],valid_ok=res[0]['va']['cagr']>0,base=base,bench=bench,sims=sum(r['tr']['n']+r['va']['n'] for r in res),signals=len(data),since=cutd.isoformat(),start=a0.isoformat())
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
def validity(fake,fake4,ccand,pats,gps,dps,scs):
    # Every suggestion carries how long it stays valid for a NEW entry: vl = units left after today, vu = unit
    # (w weeks, s sessions, b4 / b1 = 4-hour / 1-hour bars). It is removed when that runs out, when its target is
    # touched, or when its own cancel condition (a close below the stop, where the setup has one) is met.
    for f in fake: f['vl']=3-f['age'];f['vu']='w'
    for f in fake4: f['vl']=(9-f['age'])//2;f['vu']='s'
    for g in gps: g['vl']=2-g['age'];g['vu']='s'
    for p in pats: p['vl']=PCFG[p['tf']]['fresh']-1-p['age'];p['vu']={'d':'s','h4':'b4','h1':'b1'}[p['tf']]
    for c in ccand: c['vl']=10-c.get('age',0);c['vu']='s'
    for x in dps: x['vl']=DIP['fresh']-x['age'];x['vu']='s'
    for x in scs: x['vl']=SCH['fresh']-x['age'];x['vu']='s'
def grp(h): return '1' if h==1 else '2-3' if h<=3 else '4-6' if h<=6 else '7+'
def run_market(mid,base):
    global MK,MODEL,CMODEL,FCOLLECT,COLLECT
    MK=MARKETS[mid];MODEL,CMODEL=base;P='' if mid=='us' else mid.upper()+'_'
    DAYS.clear();SPY.clear();SPY.update(spy_map());FCOLLECT=[];COLLECT=[]
    rows=[l.split('\t') for l in open(os.path.join(H,MK['tickers']),encoding='utf8').read().splitlines() if l.strip()]
    S=[r[0].strip() for r in rows];names={r[0].strip():r[1].strip() for r in rows if len(r)>1};cev=[];cbase={};ccand=[]
    with cf.ThreadPoolExecutor(12) as ex: data=list(ex.map(get,S))
    okn=sum(1 for x in data if x)
    if okn<MK['minok'] or not SPY:
        print(P+'ERROR',f'only {okn} of {len(S)} stocks downloaded (index data: {bool(SPY)})');return None
    MODEL=relearn(FCOLLECT,MODEL,5,FEATS.index('pos'));CMODEL=relearn(COLLECT,CMODEL,3)
    labs={'fake':lab('fake',FCOLLECT,MODEL,5,FEATS.index('pos')),'ct':plab(COLLECT,CMODEL,[x[0] for x in data if x])}
    fake=[];fake4=[];tails={};pats=[];gps=[];dps=[];scs=[];pbs=[];tls=[]
    for s,X in zip(S,data):
        if not X or len(X[0])<260: continue
        B,ct,X4,tl,pts,gp,dp,sc_,pb_,tl_=X;tails[s]=tl;pats+=pts;gps+=gp;dps+=dp;scs+=sc_;pbs+=pb_;tls+=tl_
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
    pats.sort(key=lambda p:({'d':0,'h4':1,'h1':2}[p['tf']],p['age'],-p['rew']/max(p['risk'],0.1)))
    gps.sort(key=lambda g:(g['age'],g['gap']))
    dps.sort(key=lambda x:(x['age'],-x['depth']))
    scs.sort(key=lambda x:(x['age'],-x['cnt']))
    pbs.sort(key=lambda x:(x['age'],-x['depth']))
    fake,fake4,ccand,pats,gps,perf,dps,scs=selflearn(fake,fake4,ccand,tails,labs,pats,gps,dps,scs,tls)
    validity(fake,fake4,ccand,pats,gps,dps,scs)
    tls=[x for x in tls if perf['cats'].get('tl',{}).get('on',True)];tls.sort(key=lambda x:(x['age'],-x['touches']))
    for x in tls: x['lim']=round(min(x['ref']*1.02,x['tgt']*0.995),2);x['missed']=x['cur']>x['lim']
    print(P+'SUMMARY',okn,'stocks',len(FCOLLECT),'historical false-breakout signals',len(COLLECT),'historical contrarian signals')
    print(P+'MODELS',json.dumps({k:{x:m['info'].get(x) for x in ('retrained','transfer','auc_new','auc_old','n_train','n_test','since','total')} for k,m in (('fake',MODEL),('ct',CMODEL))}))
    print(P+'LAB',json.dumps({k:(v and dict(champ=v['champ'],base=v['base'],sims=v['sims'])) for k,v in labs.items()}))
    print(P+'PAPER',json.dumps(dict(all=perf['paper']['all'],champ=perf['paper']['champ'])))
    print(P+'PERF',json.dumps(dict(cats=perf['cats'],resolved_today=perf['today']),ensure_ascii=False))
    print(P+'FAKEOUTS',json.dumps(fake,ensure_ascii=False))
    print(P+'FAKEOUTS_4H',json.dumps(fake4,ensure_ascii=False))
    print(P+'PATTERNS',json.dumps([{k:v for k,v in x.items() if k not in ('chart','geo')} for x in pats]))
    print(P+'GAPS',json.dumps(gps))
    print(P+'DIPS',json.dumps(dps))
    print(P+'SCHOOLS',json.dumps(scs))
    print(P+'PULLBACKS',json.dumps([{k:v for k,v in x.items() if k not in ('chart','mal')} for x in pbs]))
    print(P+'TREND_TRAP',json.dumps([{k:v for k,v in x.items() if k!='geo'} for x in tls]))
    print(P+'CONTRARIAN_STATS',json.dumps(cst))
    print(P+'CONTRARIAN_CANDIDATES',json.dumps(ccand))
    need={x['s'] for x in fake+fake4+gps+dps+scs+ccand+[p for p in pats if p['tf']=='d']}
    charts={x:[[round(b[4],2),round(b[1],2),round(b[2],2),round(b[3],2)] for b in tails[x][-90:]] for x in need if x in tails}
    M=dict(charts=charts,fake=fake,fake4=fake4,gaps=gps,dips=dps,dstats=DIP_STATS[mid],schools=scs,sstats=SCH_STATS[mid],dcmp=DIP_CMP[mid],gstats=GAP_STATS[mid],gcmp=GAP_CMP[mid],tl=tls,tlstats=TL_STATS,tlon=perf['cats'].get('tl',{}).get('on',True),pb=pbs,pbstats=PB_STATS[mid],pbtf=PB_TF[mid],pats=pats,pstats=PAT_STATS[mid],pall=PAT_ALL[mid],h4=MK['h4'],model=MODEL['info'],cmodel=CMODEL['info'],perf=perf,ct=dict(st=cst,cand=ccand,n=len(cev)),names=names,stocks=okn)
    M['trades']=build_trades(M)
    print(P+'TRADES',json.dumps([{k:v for k,v in t.items() if k not in ('chart','geo')} for t in M['trades'][:12]],ensure_ascii=False))
    return M
HIDE=('fake','fake4','pat4','pat1')   # dropped from the blotter by the review panel: break-even after costs or tiny samples. Still tracked in the background.
FALL=('dip','ct','gap')                # one correlated bet: buying stocks that have just fallen
def build_trades(M):
    # One ranked blotter of every buy setup whose conditions are complete.
    # - Setups whose study has NO stop (deep dip, all-schools, gap) are shown as "no stop" and sized from the loss of
    #   the worst 5% of their historical trades, not from an untested stop; their expected value uses the average loser.
    # - lim = the highest price worth paying (2% above the signal's reference price). Above it the row is "missed".
    # - Fall-buying setups are one bet: the best 3 are shown and share ONE risk budget, the rest are folded.
    T=[];ch=M.get('charts',{});lc=((M.get('perf') or {}).get('labs') or {}).get('ct') or {};champ=lc.get('champ') if lc.get('port') and lc.get('valid_ok') else None
    ds=M.get('dstats') or {};ss=M.get('sstats') or {}
    def add(kind,x,entry,stop,tgt,conf,date,d,base=None,ref=None,loss=None,al=None,exitby=None,fam=None):
        if kind in HIDE: return
        # A target defined as a % from the signal price is re-based to the latest price when the stock has fallen
        # since: the stated confidence was measured for that % move, not for a longer one.
        if base and entry and tgt and entry<base:
            t2=entry*tgt/base
            if t2<tgt: d=dict(d,tgt0=round(tgt,2));tgt=t2
        if loss: stop=entry*(1-loss/100)
        if not(entry and stop and tgt) or not(stop<entry<tgt): return
        rew=(tgt/entry-1)*100;risk=(1-stop/entry)*100;p=(conf or 50)/100;ev=p*rew-(1-p)*(al or risk)
        lim=round(min(ref*1.02,tgt*0.995),2) if ref else None
        T.append(dict(kind=kind,fam=fam or ('fall' if kind in FALL else kind),s=x['s'],entry=round(entry,2),stop=round(stop,2),tgt=round(tgt,2),rew=round(rew,1),risk=round(risk,1),rr=round(rew/risk,2),conf=conf,ev=round(ev,2),er=round(ev/risk,2),
            date=date,d=d,vl=x.get('vl'),vu=x.get('vu'),lim=lim,missed=bool(lim and entry>lim),nostop=bool(loss),exitby=exitby,chart=x.get('chart') or ch.get(x['s']),geo=x.get('geo')))
    for f in M.get('fake',[]):
        if f['side']=='دعم': add('fake',f,f['cur'],f['ext'],f['T'][0],f.get('adj') or f.get('pr'),f['wk'],dict(level=f['level'],grade=f.get('grade'),pos=f.get('pos'),holds=f.get('holds'),pen=f.get('pen')),f['close'])
    for f in M.get('fake4',[]): add('fake4',f,f['cur'],f['ext'],f['T'][0],f.get('adj'),f['wk'],dict(level=f['level'],pos=f.get('pos'),holds=f.get('holds'),pen=f.get('pen')))
    for p in M.get('pats',[]): add({'d':'pat','h4':'pat4','h1':'pat1'}[p['tf']],p,p['cur'],p['stop'],p['tgt'],p.get('adj'),p['date'],dict(typ=p['typ']),ref=p['close'])
    for g in M.get('gaps',[]): add('gap',g,g['cur'],None,g['pc'],g.get('adj'),g['conf'],dict(gap=g['gap'],gapdate=g['date'],typ=g['typ'],ext=g['ext']),g['ref'],g['ref'],loss=max(5,(1-g['ext']/g['cur'])*100),al=max(3,(1-g['deep']/g['cur'])*100),exitby=20-g.get('age',0))
    for x in M.get('dips',[]): add('dip',x,x['cur'],None,x['tgt'],x.get('adj'),x['date'],dict(depth=x.get('depth'),hi=x.get('hi'),typ=x['typ'],ext=x['ext'],left=x.get('left')),x['ref'],x['ref'],loss=abs(ds.get('worst',-31)),al=abs(ds.get('al',-23)),exitby=x.get('left'))
    for x in M.get('schools',[]): add('sch',x,x['cur'],None,x['tgt'],x.get('adj'),x['date'],dict(cnt=x.get('cnt'),ok=x.get('ok'),rsi=x.get('rsi'),typ=x['typ'],ext=x['ext'],left=x.get('left')),x['ref'],x['ref'],loss=abs(ss.get('worst',-15)),al=abs(ss.get('al',-9)),exitby=x.get('left'))
    for c in (M.get('ct') or {}).get('cand',[]):
        if not c.get('act','').startswith('buy'): continue
        g=c.get('grade')
        if champ and g and not(champ['f']=='all' or (g!='C' if champ['f']=='AB' else g=='A')): continue
        add('ct',c,c['cur'],c['cur']*(1-((champ or {}).get('S') or 0.20)),c.get('tgt'),c.get('adj') or c.get('pr'),c['date'],dict(k=c['k'],act=c['act'],grade=g,sig=c['sig']),c['sig'],c['sig'],fam=None if c['act']=='buy_contra' else 'with')
    T=[t for t in T if t['ev']>0];T.sort(key=lambda t:(t['missed'],-t['er']))
    seen=set();U=[]
    for t in T:   # one row per stock: its best setup
        if t['s'] not in seen: seen.add(t['s']);U.append(t)
    live=[t for t in U if t['fam']=='fall' and not t['missed']];k=min(3,len(live))
    for n,t in enumerate(live): t['fold']=n>=3;t['share']=k;t['cluster']=len(live)
    return U
DATAF=os.path.join(H,'data.txt')   # last full result, so the light intraday refresh can rebuild the page
def render(D,out):
    tp=os.path.join(H,'template.html')
    if not os.path.exists(tp): tp=os.path.join(H,'template.txt')  # name used by the copy stored with the artifact
    json.dump(D,open(DATAF,'w',encoding='utf8'),ensure_ascii=False)
    open(out,'w',encoding='utf8').write(open(tp,encoding='utf8').read().replace('__DATA__',json.dumps(D,ensure_ascii=False)).replace('__DATE__',D.get('date') or d.date.today().isoformat()))
def live_prices(M,px):
    # Light refresh: bring every listed suggestion of this market to the latest price and drop the ones whose
    # target was touched (or, for 4-hour false breakouts, whose wick was lost) since the last full run.
    # px: symbol -> (latest price, {session date: [high, low, last]}). New signals still need the full daily run.
    def hi_after(s,day): return max([v[0] for k,v in px[s][1].items() if k>day],default=0)
    def upd(L,ref,tgt,since,extra=None):
        keep=[]
        for x in L:
            if x['s'] in px:
                cur=px[x['s']][0];t=tgt(x)
                if t and max(cur,hi_after(x['s'],since(x)))>=t: continue
                if extra and extra(x,cur): continue
                x['cur']=round(cur,2);x['chg']=round((cur/ref(x)-1)*100,1)
                if 'up' in x and t: x['up']=round((t/cur-1)*100,1)
            keep.append(x)
        L[:]=keep
    upd(M.get('dips',[]),lambda x:x['ref'],lambda x:x['tgt'],lambda x:x['date'])
    upd(M.get('schools',[]),lambda x:x['ref'],lambda x:x['tgt'],lambda x:x['date'])
    upd(M.get('gaps',[]),lambda x:x['ref'],lambda x:x['pc'],lambda x:x['conf'])
    upd(M.get('pb',[]),lambda x:x['ref'],lambda x:x['tgt'],lambda x:x['date'],lambda x,cur:cur<=x['stop'])
    upd(M.get('tl',[]),lambda x:x['ref'],lambda x:x['tgt'],lambda x:x['date'],lambda x,cur:cur<=x['stop'])
    for x in M.get('tl',[]): x['missed']=x['cur']>x['lim']
    upd(M.get('fake',[]),lambda x:x['close'],lambda x:x['T'][0] if x['side']=='دعم' else None,lambda x:(d.date.fromisoformat(x['wk'])+d.timedelta(days=6)).isoformat())
    upd(M.get('fake4',[]),lambda x:x['close'],lambda x:x['T'][0],lambda x:x['wk'][:10],lambda x,cur:cur<x['ext'])
    for c in (M.get('ct') or {}).get('cand',[]):
        if c['s'] in px:
            cur=px[c['s']][0];c['cur']=round(cur,2);c['chg']=round((cur/c['sig']-1)*100,1);c['mx']=round(max(c.get('mx',0),cur,hi_after(c['s'],c['date'])),2)
    if M.get('ct'): M['ct']['cand']=[c for c in M['ct']['cand'] if not(c.get('tgt') and c['mx']>=c['tgt'])]
def intraday(out,mid):
    # Light refresh while a market is open: the 1-hour and 4-hour pattern signals of that market are rescanned and
    # every listed suggestion gets its latest price (see live_prices). Models, studies, paper trades and new daily
    # signals stay as the last full run left them.
    global MK
    if mid not in ACTIVE: print('INTRADAY',mid,'market is switched off; nothing to do');return
    MK=MARKETS[mid];D=json.load(open(DATAF,encoding='utf8'));D={k:v for k,v in D.items() if k not in MARKETS or k in ACTIVE}
    if not D.get(mid): sys.exit('ERROR: no full data for this market yet; run the daily update first')
    S=[l.split('\t')[0].strip() for l in open(os.path.join(H,MK['tickers']),encoding='utf8').read().splitlines() if l.strip()]
    with cf.ThreadPoolExecutor(12) as ex: res=list(ex.map(get4h,S))
    okn=sum(1 for r in res if r)
    if okn<MK['minok']: sys.exit(f'ERROR: only {okn} of {len(S)} stocks downloaded; page left unchanged')
    pats=[p for r in res if r for p in r[1]]
    live_prices(D[mid],{s:(r[0][1],r[2]) for s,r in zip(S,res) if r})
    try: log=json.load(open(LOGF,encoding='utf8'))
    except Exception: log=[]
    have={e['id'] for e in log};today=ny_now().date().isoformat();cats=D[mid]['perf']['cats'];new=[]
    for p in pats:
        kd={'h4':'pat4','h1':'pat1'}[p['tf']];p['cat']=kd+'|'+p['typ'];p['lid']=f"{kd}|{p['s']}|{p['date'][:10]}|{p['typ']}|{p['date'][10:]}"
        v=PAT_STATS[mid].get(p['tf'],{}).get(p['typ']);p['adj']=(cats.get(p['cat']) or {}).get('adj') or (round(100*v['far']/max(1,v['far']+v['stopd'])) if v else 50)
        if (cats.get(p['cat']) or {}).get('on') is False: continue
        if p['lid'] not in have:
            have.add(p['lid']);new.append(p)
            log.append(dict(id=p['lid'],mk=mid,kind=kd,s=p['s'],d=p['date'][:10],entry=p['close'],tgt=p['tgt'],stop=p['stop'],cat=p['cat'],pr=None,first=today,status='open',res=None,grade=None))
    json.dump(log,open(LOGF,'w',encoding='utf8'),ensure_ascii=False)
    pats=[p for p in pats if (cats.get(p['cat']) or {}).get('on') is not False]
    pats.sort(key=lambda p:({'h4':1,'h1':2}[p['tf']],p['age'],-p['rew']/max(p['risk'],0.1)))
    validity([],[],[],pats,[],[],[])
    D[mid]['pats']=[p for p in D[mid].get('pats',[]) if p['tf']=='d']+pats;D['built']=d.datetime.now(d.timezone.utc).isoformat(timespec='seconds');D[mid]['intraday_at']=ny_now().strftime('%Y-%m-%d %H:%M')
    D[mid]['trades']=build_trades(D[mid])
    for m in MARKETS:   # study tables of the pullback tab, also for data saved before that tab existed
        if D.get(m): D[m]['pbstats']=PB_STATS[m];D[m]['pbtf']=PB_TF[m];D[m].setdefault('pb',[])
    render(D,out)
    print('INTRADAY',mid,okn,'stocks',len(pats),'live signals',json.dumps({k:len(D[mid].get(k,[])) for k in ('dips','schools','gaps','fake','fake4')}))
    print('NEW',json.dumps([{k:v for k,v in x.items() if k not in ('chart','geo')} for x in new]))
ACTIVE=('us',)   # the Saudi market was dropped at the owner's request; its code stays but is not run or shown
def main(out):
    base=(MODEL,CMODEL);D={}
    for mid in ACTIVE: D[mid]=run_market(mid,base)
    if not D['us']: sys.exit('ERROR: US market data could not be downloaded; not writing the page')
    D['date']=d.date.today().isoformat();D['built']=d.datetime.now(d.timezone.utc).isoformat(timespec='seconds')
    render(D,out)
if __name__=='__main__':
    if len(sys.argv)>3 and sys.argv[2]=='--intraday': intraday(sys.argv[1],sys.argv[3])
    else: main(sys.argv[1])
