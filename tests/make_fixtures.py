"""Synthetic Yahoo v8 charts for NSE symbols (IST session 9:15-15:30) to test the port."""
import json, random, datetime, sys, os
IST = datetime.timedelta(hours=5, minutes=30)
def ts(d, h, m): return int((datetime.datetime.combine(d, datetime.time(h, m)) - IST - datetime.datetime(1970,1,1)).total_seconds())
def intraday(sym, days, seed, breakout_day=None, base=1000.0):
    r = random.Random(seed); t=[];o=[];h=[];l=[];c=[];v=[]; px=base
    for d in days:
        for k in range(75):
            mins = 9*60+15+5*k; op=px
            drift = 0.0
            if d == breakout_day and 3 <= k <= 8: drift = 0.004
            px = px*(1+drift+r.gauss(0,0.0015)); hi=max(op,px)*(1+abs(r.gauss(0,0.0007))); lo=min(op,px)*(1-abs(r.gauss(0,0.0007)))
            t.append(ts(d, mins//60, mins%60)); o.append(round(op,2)); h.append(round(hi,2)); l.append(round(lo,2)); c.append(round(px,2)); v.append(r.randint(20000,90000))
    return {"chart":{"result":[{"meta":{"symbol":sym+".NS","currency":"INR","exchangeName":"NSI","regularMarketPrice":c[-1],"regularMarketVolume":sum(v[-75:]),"chartPreviousClose":base},
      "timestamp":t,"indicators":{"quote":[{"open":o,"high":h,"low":l,"close":c,"volume":v}]}}],"error":None}}
def daily(sym, end, n, seed, pattern="flat", base=500.0):
    r=random.Random(seed); t=[];c=[];o=[];h=[];l=[];v=[]; d=end; days=[]
    while len(days)<n:
        if d.weekday()<5: days.append(d)
        d-=datetime.timedelta(days=1)
    days.reverse(); px=base
    for i,dd in enumerate(days):
        step = r.gauss(0,0.01)
        if pattern=="breakout" and i==n-1: step=0.06
        if pattern=="oversold" and i>n-12: step=-0.025
        px*=1+step; t.append(ts(dd,9,15)); c.append(round(px,2)); o.append(round(px,2)); h.append(round(px*1.01,2)); l.append(round(px*0.99,2)); v.append(r.randint(1_000_000,5_000_000))
    return {"chart":{"result":[{"meta":{"symbol":sym+".NS","regularMarketPrice":c[-1],"regularMarketVolume":v[-1]},"timestamp":t,"indicators":{"quote":[{"open":o,"high":h,"low":l,"close":c,"volume":v}]}}],"error":None}}
if __name__=="__main__":
    out=sys.argv[1]; os.makedirs(out+"/intraday",exist_ok=True); os.makedirs(out+"/daily",exist_ok=True)
    day=datetime.date(2026,10,28)  # a Wednesday
    hist=[]; d=day-datetime.timedelta(days=90)
    from itertools import count
    while d<=day:
        if d.weekday()<5 and d.isoformat() not in ("2026-09-14","2026-10-02","2026-10-20"): hist.append(d)
        d+=datetime.timedelta(days=1)
    hist=hist[-60:]
    for i,(s,b) in enumerate([("RELIANCE",day),("M&M",day),("BAJAJ-AUTO",None),("TCS",None),("INFY",day)]):
        doc=intraday(s,hist,i+1,b,base=1000+300*i)
        json.dump(doc,open("%s/intraday/%s.NS.json"%(out,s),"w"))
    for i,(s,p) in enumerate([("RELIANCE","breakout"),("TCS","oversold"),("INFY","flat"),("M&M","flat")]):
        json.dump(daily(s,day,70,i+10,p),open("%s/daily/%s.NS.json"%(out,s),"w"))
    open(out+"/fo_mktlots.csv","w").write("UNDERLYING,SYMBOL,OCT-26,NOV-26,DEC-26\nDerivatives on Indices,,,,\nNIFTY 50,NIFTY,75,75,75\nNIFTY BANK,BANKNIFTY,35,35,35\nDerivatives on Individual Securities,,,,\nRELIANCE INDUSTRIES LTD,RELIANCE,500,500,500\nMAHINDRA & MAHINDRA LTD,M&M,200,200,200\nBAJAJ AUTO LIMITED,BAJAJ-AUTO,75,75,75\nTATA CONSULTANCY SERV LT,TCS,175,175,175\nINFOSYS LIMITED,INFY,400,400,400\n")
    print("ok", len(hist), "days")
