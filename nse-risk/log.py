#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Trade log for nse-risk. You place orders yourself in Zerodha Kite; this log is how
nse-risk counts today's trades and today's risk. Standard library only, no network.

    python3 log.py placed                       # the order in nse/orders.json that nse-risk passed
    python3 log.py placed --index 2             # the 2nd order in the file
    python3 log.py exit RELIANCE 18 1021.40     # you sold 18 RELIANCE at 1021.40 (stop, target or flat-by)
    python3 log.py today                        # what is logged for today

'placed' only logs an order whose exact fields nse-risk passed today (the fingerprint in
nse/state/risk.json); a changed or unchecked order is refused, so the daily limits stay honest.
Records go to nse/state/broker.json, the file check.py reads with --state.
"""

import argparse
import datetime
import hashlib
import json
import os
import sys

FIELDS = ("symbol", "side", "qty", "notional", "type", "time_in_force", "limit_price",
          "stop_price", "trail_price", "trail_percent", "extended_hours", "client_order_id",
          "order_class", "product", "take_profit_limit_price", "stop_loss_stop_price",
          "stop_loss_limit_price", "advanced_instructions")


def fingerprint(order):
    """Same function as check.py: the exact order that was checked."""
    core = {k: order[k] for k in FIELDS if k in order and order[k] is not None}
    blob = json.dumps(core, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()[:16]


def now_utc():
    return datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0, tzinfo=None)


def ist_today(utc):
    return (utc + datetime.timedelta(hours=5, minutes=30)).date().isoformat()


def load(path, default):
    if not os.path.exists(path):
        return default
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def save(path, doc):
    d = os.path.dirname(path)
    if d:
        os.makedirs(d, exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, indent=2)
        fh.write("\n")
    os.replace(tmp, path)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Log trades you placed in Kite, for nse-risk's daily limits.")
    ap.add_argument("--state", default="nse/state/broker.json")
    ap.add_argument("--now", help="pretend it is this UTC time (ISO, for tests)")
    sub = ap.add_subparsers(dest="cmd")
    p = sub.add_parser("placed", help="log the order nse-risk passed")
    p.add_argument("--orders", default="nse/orders.json")
    p.add_argument("--risk", default="nse/state/risk.json")
    p.add_argument("--index", type=int, default=1)
    p = sub.add_parser("exit", help="log a sell that closed (part of) a position")
    p.add_argument("symbol")
    p.add_argument("qty", type=int)
    p.add_argument("price", type=float)
    sub.add_parser("today", help="show today's log")
    a = ap.parse_args(argv)
    if not a.cmd:
        ap.print_help()
        return 1
    now = datetime.datetime.fromisoformat(a.now.replace("Z", "")) if a.now else now_utc()
    today = ist_today(now)
    state = load(a.state, {"orders": []})
    state.setdefault("orders", [])
    stamp = now.strftime("%Y-%m-%dT%H:%M:%SZ")

    if a.cmd == "placed":
        try:
            orders = (load(a.orders, {}) or {}).get("orders") or []
            risk = load(a.risk, {}) or {}
        except (OSError, ValueError) as e:
            print("log.py: %s" % e, file=sys.stderr)
            return 1
        if not 1 <= a.index <= len(orders):
            print("log.py: no order #%d in %s" % (a.index, a.orders), file=sys.stderr)
            return 1
        o = orders[a.index - 1]
        fp = fingerprint(o)
        verdict = next((r for r in risk.get("results", []) if r.get("fingerprint") == fp), None)
        if risk.get("date") != today or verdict is None:
            print("log.py: nse-risk has not checked this exact order today. Run check.py first.", file=sys.stderr)
            return 1
        if verdict.get("verdict") != "PASS":
            print("log.py: nse-risk BLOCKED this order (%s). Not logged." % "; ".join(verdict.get("reasons") or []),
                  file=sys.stderr)
            return 1
        plan = o.get("plan") or {}
        rec = {"status": "placed", "date": today, "at": stamp, "symbol": o["symbol"], "side": o["side"],
               "qty": o.get("qty"), "kind": verdict.get("kind"), "max_loss": verdict.get("max_loss", plan.get("max_loss")),
               "stop": o.get("stop_loss_stop_price"), "fingerprint": fp, "where": "Zerodha Kite (placed by you)"}
        state["orders"].append(rec)
        save(a.state, state)
        print("Logged: buy %s %s, max loss ₹%s at the stop. Today: %d order(s) logged."
              % (rec["qty"], rec["symbol"], rec["max_loss"],
                 sum(1 for r in state["orders"] if r.get("date") == today and r.get("status") == "placed")))
        return 0

    if a.cmd == "exit":
        rec = {"status": "filled", "date": today, "at": stamp, "symbol": a.symbol.upper(), "side": "sell",
               "qty": str(a.qty), "kind": "exit", "price": a.price, "where": "Zerodha Kite (placed by you)"}
        state["orders"].append(rec)
        save(a.state, state)
        print("Logged: sold %d %s at ₹%.2f." % (a.qty, rec["symbol"], a.price))
        return 0

    rows = [r for r in state["orders"] if r.get("date") == today]
    if not rows:
        print("Nothing logged for %s." % today)
        return 0
    risk_total = sum(float(r.get("max_loss") or 0) for r in rows if r.get("kind") == "entry" and r.get("status") == "placed")
    for r in rows:
        print("%s  %-6s %-4s %s %s%s" % (r["at"][11:16] + "Z", r["status"], r["side"], r["qty"], r["symbol"],
                                         ("  max loss ₹%s" % r["max_loss"]) if r.get("max_loss") is not None else
                                         ("  at ₹%.2f" % r["price"]) if r.get("price") else ""))
    print("Risk taken today (max losses at the stops): ₹%.2f" % risk_total)
    return 0


if __name__ == "__main__":
    sys.exit(main())
