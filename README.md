# nse-fno-trader

Seven Claude skills for intraday trading in **NSE F&O stocks** (the cash shares
of the ~200 stocks that have futures and options), with orders placed by you in
**Zerodha Kite**. An adaptation of Jake Schincariol's
[day-trader-skill](https://github.com/Jakeschincariol/day-trader-skill) (MIT),
rebuilt for Indian markets.

| skill | what it does |
| --- | --- |
| `/nse-scanner` | builds the F&O stock list from NSE, scans daily setups and 9:15–9:30 opening-range breakouts |
| `/nse-news` | Yahoo headlines + NSE corporate announcements + today's move, only what is new |
| `/nse-entry` | watches a stock bar by bar, calls the first 5-minute close above the range high |
| `/nse-exit` | sets stop and target before entry, rounded to NSE's tick, flat by 15:15 IST |
| `/nse-timemachine` | 10,000 replays of the rest of the day from the stock's own last 60 days |
| `/nse-budget` | sizes in rupees to your max loss, writes three Kite orders (BUY, SL-M, LIMIT target, MIS) |
| `/nse-risk` | PASS/BLOCK against your limits, fresh quotes, and the trade log for daily limits |

A day: `nse-scanner daily` before 9:15 → `nse-news` → `nse-scanner orb` after
9:35 → `nse-entry` → `nse-exit` → `nse-timemachine` → `nse-budget` →
`nse-risk` → you place the orders in Kite → `log.py placed` → out by 15:15 →
`log.py exit`.

## What changed from the US pack

- India time (fixed UTC+5:30), NSE session 9:15 to 15:30, NSE 2026 holidays.
  The 2027 list is not published yet: update `NSE_HOLIDAYS` in each script in December.
- Universe: NSE's `fo_mktlots.csv`, index contracts dropped.
- Yahoo symbols `SYMBOL.NS` (`M&M` and `BAJAJ-AUTO` handled).
- Prices in rupees and on NSE's tick (0.01 / 0.05 / 0.10 / 0.50 / 1 / 5 by price band).
- Defaults: entries 09:30 to 14:45, flat by 15:15 (Zerodha squares MIS off at ~15:25).
- News: NSE corporate announcements instead of SEC filings.
- Orders: Zerodha Kite tickets instead of Alpaca; no broker connection, nothing is ever placed.
- Dropped: alerts, broker, earnings analyst (SEC-only), Congress tracker (US-only).

## Network

The scripts need to reach `query1/query2.finance.yahoo.com`,
`feeds.finance.yahoo.com`, `www.nseindia.com` and `nsearchives.nseindia.com`.
Where those are blocked (some sandboxes allow only package registries), run
the skills where they are allowed, for example on your own computer.

## Tests

```bash
python3 -m unittest discover -s tests
```

Runs the whole pipeline on synthetic NSE data, no network.

## Not advice

Education and tooling, not investment advice and not a SEBI-registered
adviser's or research analyst's view. SEBI's own study found that most
individual intraday traders lose money. Brokerage, STT, exchange charges,
stamp duty and GST are not in any number here. Yahoo's NSE data is free,
unofficial and can lag.
