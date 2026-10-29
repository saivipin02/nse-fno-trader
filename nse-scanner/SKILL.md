---
name: nse-scanner
description: >-
  NSE F&O Chart Scanner. Builds the list of NSE stocks that have futures and
  options (NSE's own fo_mktlots.csv, index contracts left out, about 200
  names), runs a pre-market scan of daily closes (20-day closing-high
  breakout, bull flag, reclaimed the 20-day average, oversold, oversold
  bounce) and an intraday opening-range breakout scan on 5-minute bars
  (9:15 to 9:30 IST range), then writes nse/watchlist.json for nse-news and
  nse-entry. Free Yahoo data (SYMBOL.NS). Use when the user says "scan F&O
  stocks", "scan NSE", "find me setups", "what is breaking out", "opening
  range breakouts", "bull flags", "oversold stocks", "pre-market scan",
  "build my watchlist", "what should I look at today", or at the start of an
  Indian trading day before /nse-news.
argument-hint: "[universe | daily | orb] [--at HH:MM]"
---

# nse-scanner

The first step of an NSE intraday trade. It reads the charts of every F&O
stock and lists the ones that match a rule. A scan is a list of charts that
match a rule, not a list of stocks to buy, and a setup is not a prediction.
Most people who trade intraday lose money; SEBI's own studies say so. The
scanner does not change that.

`${CLAUDE_SKILL_DIR}` is this skill's folder. Run everything from the folder
where the user keeps their `nse/` files (the scripts read and write `nse/...`
relative to it).

```bash
python3 "${CLAUDE_SKILL_DIR}/scan.py" universe                       # -> nse/universe.txt (F&O stocks)
python3 "${CLAUDE_SKILL_DIR}/scan.py" daily                          # before 9:15 IST -> nse/watchlist.json
python3 "${CLAUDE_SKILL_DIR}/scan.py" daily --symbols RELIANCE,INFY,"M&M"
python3 "${CLAUDE_SKILL_DIR}/scan.py" orb                            # after 9:35 IST -> nse/watchlist.json
python3 "${CLAUDE_SKILL_DIR}/scan.py" orb --at 10:15                 # cut the clock at 10:15 IST
```

Flags: `--min-price`, `--min-volume` (both 0 by default: NSE's F&O list is
already its liquid list), `--or-minutes 15`, `--max-confirm 200`,
`--now "2026-10-28 10:15"` (India time) to pin the clock, `--offline PATH`,
`--no-write`, `--show N`, `--json`. Exit code 0 when the scan found
something, 1 when it found nothing or could not run (one plain line says why).

## The universe

`universe` reads NSE's F&O lot-size file
(nsearchives.nseindia.com/content/fo/fo_mktlots.csv) and keeps the rows under
"Derivatives on Individual Securities"; NIFTY, BANKNIFTY, FINNIFTY,
MIDCPNIFTY and NIFTYNXT50 are left out. If that file cannot be read it tries
NSE's "SECURITIES IN F&O" list. NSE blocks some automated requests; if both
fail, ask the user to download fo_mktlots.csv from nseindia.com and run
`scan.py universe --offline fo_mktlots.csv`. The list changes when NSE adds or
drops F&O stocks, so re-run `universe` once a month. Each line of
`nse/universe.txt` is `SYMBOL|Name|lot size`.

## The daily scan (before the open)

Daily closes from Yahoo (SYMBOL.NS), 20 symbols a request. Today's bar is
left out until 3:30 PM IST. Setups, on closes only:

| setup | the rule |
| --- | --- |
| `breakout_20d` | the last close is above every close of the 20 sessions before it |
| `bull_flag` | up more than 10 % over the 10 sessions before the last 5, then the last 5 closes inside a 5 % range |
| `reclaim_ma20` | the close before was under its 20-day average, the last close is above it |
| `oversold` | RSI 14 (Wilder) under 30 |
| `oversold_bounce` | RSI 14 was under 30 yesterday and today closed up |

## The opening-range breakout scan (during the session)

The opening range is the first 15 minutes: the 9:15, 9:20 and 9:25 bars. A hit
is the first completed 5-minute bar to CLOSE above the range high; the first
one possible closes at 9:35 AM. Before then, on a weekend or NSE holiday,
after 3:30 PM, or after `no_entries_after` (14:45 by default, in
nse/config.json) it prints one line and writes nothing. A chart with a missing
bar (a halt, an upper or lower circuit, no trades) is not used.

## Steps

1. Once a month: `scan.py universe`.
2. Before 9:15 IST: `scan.py daily`. Tell the user the counts and the top few
   by setup.
3. After 9:35 IST (10:00 to 10:15 is common): `scan.py orb`. Say how many
   charts broke their range and when; a later hit is closer to the price now.
4. The user picks one. Hand on: `/nse-news SYMBOL`, then `/nse-entry SYMBOL`.
   Never pick for them.

## Data and limits

- Yahoo's NSE data is free, unofficial and can lag by a few minutes. Bars are
  5-minute bars, never tick by tick, never real time.
- NSE holidays: 2026 only (nseindia.com). NSE publishes the 2027 list in
  December; until then a 2027 date is treated as a normal weekday, so check
  nseindia.com. The Diwali Muhurat session is not covered.
- Partial results are said as partial. Never round a partial scan up to "every F&O stock".

## Rules

- Say what was scanned: how many symbols, how many charts came back, how
  many were usable, and the time of the data.
- Say "matched a rule", never "a buy", "a winner" or "a good trade".
- Never print a P&L, a return or a profit figure.
- A hit is stale once the price has moved on. Re-run before acting on it.

## Safety

- Education and tooling, not financial advice, and not a SEBI-registered
  research analyst's view.
- Nothing in this pack places an order. The user places every order
  themselves in Zerodha Kite.
- Cash-segment shares only (MIS intraday or CNC). No futures, options, short
  selling or MIS leverage beyond the cash in the budget unless the user's
  config allows it and the user confirms.
