---
name: nse-entry
description: >-
  NSE Entry Timer. Watches an NSE stock bar by bar and says the moment to get
  in. Reads free Yahoo 5-minute (or 1-minute) bars for SYMBOL.NS, builds the
  opening range (9:15 to 9:30 IST by default) and calls the entry on the first
  completed bar that CLOSES above the range high, or above a level you give
  it, with an optional volume check. Says waiting and how far, triggered with
  the time and price, expired, or not open yet, and writes nse/entry.json for
  /nse-exit. Long side only. Never places an order. Use when the user says
  "tell me when to get in", "watch RELIANCE", "has it broken out", "did it
  break the opening range", "entry signal", "time my entry", "check my
  watchlist", or after /nse-scanner and /nse-news, before /nse-exit.
argument-hint: "SYMBOL [--setup orb|level] [--level PRICE]"
---

# nse-entry

`${CLAUDE_SKILL_DIR}` is this skill's folder. Run from the folder that holds `nse/`.

```bash
python3 "${CLAUDE_SKILL_DIR}/entry.py" check RELIANCE                  # one look, now
python3 "${CLAUDE_SKILL_DIR}/entry.py" check "M&M" --write             # and save a trigger to nse/entry.json
python3 "${CLAUDE_SKILL_DIR}/entry.py" check INFY --setup level --level 1520
python3 "${CLAUDE_SKILL_DIR}/entry.py" watch RELIANCE --until 14:45    # one line per closed bar
python3 "${CLAUDE_SKILL_DIR}/entry.py" watchlist                       # every hit in nse/watchlist.json
```

Quote symbols with `&` (`"M&M"`) in the shell. Other flags: `--or-minutes 15`,
`--interval 5m|1m`, `--min-volume-x 1.5`, `--now "2026-10-28 10:15"` (India
time), `--offline PATH`, `--json`.

## The rule

- Opening range: the first 15 minutes, the 9:15, 9:20 and 9:25 five-minute
  bars. Its high is the trigger level for `--setup orb`.
- Triggered: the first COMPLETED bar after the range whose close is above the
  level. The earliest possible trigger is the 9:30 bar, closing at 9:35 AM.
  The entry price is that close.
- Waiting: no close above yet; it says how far the last close is from the level.
- Expired: no trigger by `no_entries_after` (14:45 IST by default, in
  nse/config.json). A trigger before `no_entries_before` (09:30) is reported
  but not taken.
- Not open yet / market closed: before 9:15, after 3:30 PM, weekends and NSE
  holidays (2026 list; check nseindia.com for 2027 dates).

## Steps

1. Get the symbol from the user, or run `entry.py watchlist` after
   `/nse-scanner`. Check `/nse-news` for it first.
2. Run `entry.py check SYMBOL`. Tell the user the status in one line.
3. To wait, run `entry.py watch SYMBOL --until 14:45` in the background. It
   wakes just after each bar closes, prints one line per bar, exits 0 on the
   trigger (writing nse/entry.json) or 1 when the setup expires. Keep the
   computer awake while it watches.
4. On a trigger, say the time and price, and that nothing was placed. If the
   trigger is more than a bar old, say that a late entry is a different trade.
5. Hand off to `/nse-exit` to set the stop and target BEFORE anything is bought.

## Rules

- Bar by bar, on free Yahoo bars for NSE. They are unofficial and can lag a
  few minutes. Say so when a minute matters; the price in Kite is the real one.
- A signal is information, not an order, and not a promise.
- Long side only.
- One trigger per setup per day: the first close above.
- Never call an entry early because a bar looks like it will close above.
- A stock hitting its upper circuit can trigger and then not be buyable: say so if the chart shows a flat top.

## Safety

Education and tooling, not financial advice. Nothing in this pack places an
order; the user places every order themselves in Zerodha Kite.
