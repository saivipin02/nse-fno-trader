#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Latest NSE prices for nse-risk and nse-budget. Standard library only.

    python3 quote.py RELIANCE M&M            # prints and writes nse/prices.json
    python3 quote.py --from-orders           # every symbol in nse/orders.json
    python3 quote.py RELIANCE --no-write --json

Reads Yahoo Finance's free chart endpoint (SYMBOL.NS, 1-minute bars, today). The
price is the last traded price Yahoo reports (regularMarketPrice) with its own
time (regularMarketTime). Yahoo's NSE quotes are free, unofficial and can lag;
nse-risk only uses a price under 15 minutes old.

prices.json: {"as_of": UTC, "prices": {SYM: price}, "detail": {SYM: {"time": UTC,
"fetched": UTC, "source": "yahoo"}}}. Symbols not asked for are kept.
"""

import argparse
import datetime
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

UA = "Mozilla/5.0 (compatible; nse-fno-trader/1.0)"
HOSTS = ("https://query2.finance.yahoo.com", "https://query1.finance.yahoo.com")


def yahoo_symbol(sym):
    s = sym.upper()
    return s if s.endswith((".NS", ".BO")) else s + ".NS"


def iso(utc):
    return utc.strftime("%Y-%m-%dT%H:%M:%SZ")


def fetch(sym):
    path = "/v8/finance/chart/%s?range=1d&interval=1m" % urllib.parse.quote(yahoo_symbol(sym))
    last = None
    for host in HOSTS:
        try:
            req = urllib.request.Request(host + path, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=20) as r:
                doc = json.loads(r.read().decode("utf-8", "replace"))
            res = (doc.get("chart") or {}).get("result") or []
            if not res:
                raise ValueError(((doc.get("chart") or {}).get("error") or {}).get("description", "no data"))
            meta = res[0].get("meta") or {}
            p, t = meta.get("regularMarketPrice"), meta.get("regularMarketTime")
            if p is None:
                raise ValueError("no price in Yahoo's answer")
            when = datetime.datetime(1970, 1, 1) + datetime.timedelta(seconds=int(t)) if t else None
            return float(p), when
        except urllib.error.HTTPError as e:
            last = "HTTP %d" % e.code
            if e.code == 429:
                time.sleep(3)
            continue
        except (urllib.error.URLError, OSError, ValueError) as e:
            last = str(getattr(e, "reason", e))
            continue
    raise RuntimeError("no quote for %s (%s)" % (sym, last))


def main(argv=None):
    ap = argparse.ArgumentParser(description="Latest NSE prices -> nse/prices.json")
    ap.add_argument("symbols", nargs="*")
    ap.add_argument("--from-orders", nargs="?", const="nse/orders.json", metavar="PATH")
    ap.add_argument("--out", default="nse/prices.json")
    ap.add_argument("--no-write", action="store_true")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    syms = [s.upper() for s in a.symbols]
    if a.from_orders:
        try:
            with open(a.from_orders, encoding="utf-8") as fh:
                doc = json.load(fh)
            syms += [str(o.get("symbol", "")).upper() for o in (doc.get("orders") or []) if o.get("symbol")]
        except (OSError, ValueError) as e:
            print("quote.py: cannot read %s: %s" % (a.from_orders, e), file=sys.stderr)
            return 1
    syms = list(dict.fromkeys(s for s in syms if s))
    if not syms:
        print("quote.py: which symbols? quote.py RELIANCE, or --from-orders", file=sys.stderr)
        return 1
    now = datetime.datetime.utcnow().replace(microsecond=0)
    got, errors = {}, {}
    for k, s in enumerate(syms):
        if k:
            time.sleep(0.3)
        try:
            got[s] = fetch(s)
        except RuntimeError as e:
            errors[s] = str(e)
    if not a.no_write and got:
        old = {}
        if os.path.exists(a.out):
            try:
                with open(a.out, encoding="utf-8") as fh:
                    old = json.load(fh)
            except (OSError, ValueError):
                old = {}
        prices, detail = dict(old.get("prices") or {}), dict(old.get("detail") or {})
        for s, (p, t) in got.items():
            prices[s] = p
            detail[s] = {"time": iso(t) if t else None, "fetched": iso(now), "source": "yahoo"}
        d = os.path.dirname(a.out)
        if d:
            os.makedirs(d, exist_ok=True)
        with open(a.out, "w", encoding="utf-8") as fh:
            json.dump({"as_of": iso(now), "prices": prices, "detail": detail}, fh, indent=2)
            fh.write("\n")
    if a.json:
        print(json.dumps({"prices": {s: p for s, (p, _) in got.items()},
                          "times": {s: iso(t) if t else None for s, (_, t) in got.items()}, "errors": errors}, indent=2))
    else:
        for s, (p, t) in got.items():
            ist = (t + datetime.timedelta(hours=5, minutes=30)).strftime("%H:%M:%S IST") if t else "time unknown"
            print("%-12s ₹%s  (%s, Yahoo, can lag)" % (s, "{:,.2f}".format(p), ist))
        for s, e in errors.items():
            print("%-12s %s" % (s, e))
        if got and not a.no_write:
            print("Wrote %s." % a.out)
    return 0 if got and not errors else 1


if __name__ == "__main__":
    sys.exit(main())
