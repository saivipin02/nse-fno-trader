---
name: nse-news
description: >-
  NSE News Monitor. Tracks news on every NSE stock you watch and flags what
  moves it: Yahoo Finance headlines (SYMBOL.NS), each company's NSE corporate
  announcements (financial results, board meetings, dividends, bonus and
  splits, acquisitions, management changes, credit ratings, regulatory
  actions) and how far each stock is from yesterday's close. Shows only what
  is new since the last check, newest first, in IST, tags each item (earnings,
  analyst, deal, capital, people, legal, halt/circuit, regulatory, macro) and
  never repeats one. Use when the user says "any news on RELIANCE", "why is
  this moving", "what's the news on my watchlist", "morning briefing",
  "pre-market news", "check NSE announcements", "did anything break", or
  after /nse-scanner finds setups.
argument-hint: "[--tickers SYMBOL ...] [--all] [--hours N]"
---

# nse-news

`${CLAUDE_SKILL_DIR}` is this skill's folder. Run from the folder that holds `nse/`.

```bash
python3 "${CLAUDE_SKILL_DIR}/news.py"                          # watchlist + plan + portfolio symbols
python3 "${CLAUDE_SKILL_DIR}/news.py" --tickers RELIANCE "M&M" INFY
python3 "${CLAUDE_SKILL_DIR}/news.py" --tickers TCS --all --hours 72
python3 "${CLAUDE_SKILL_DIR}/news.py" --no-nse                 # headlines only
```

Other flags: `--no-moves`, `--move-pct 3`, `--json`, `--dry-run` (leave the
seen-list alone), `--offline DIR`. Exit code 1 means nothing new.

## Sources

- Yahoo Finance headline RSS for SYMBOL.NS. Coverage of Indian stocks is
  thin; an empty feed does not mean no news.
- NSE corporate announcements, nseindia.com's own feed. NSE blocks some
  automated requests: when it does, the tool says so in a `note:` line and the
  headlines still run. Then point the user to the company's page on
  nseindia.com (Corporate filings > Announcements).
- The move: the last price against yesterday's close (Yahoo, can lag).

A `!` marks a filing that tends to move a stock: results, board meeting
outcomes, acquisitions and mergers, resignations, credit ratings, defaults,
regulatory action, buybacks, bonus, splits, dividends and record dates, pledges.

## Steps

1. Run `news.py`.
2. Read what matters first: every `!` filing, anything tagged earnings, halt,
   legal, regulatory, and every MOVING symbol.
3. Write a short brief per symbol: what happened, the source and link, the
   move, and one line on why it matters to the setup (for example "results are
   due after the close today: hold nothing past 3:15").
4. If a story changes the picture (results inside the trade, a circuit, the
   stock entering the F&O ban period, an OFS or block deal), say so before
   `/nse-entry` and `/nse-exit`. Never act on a headline alone.

## Rules

- Headlines are leads, not facts: open the filing before acting.
- Say what failed: a blocked NSE request or an empty feed is reported, not hidden.
- Never invent a headline, a filing or a date.

## Safety

Education and tooling, not financial advice. Nothing in this pack places an
order; the user places every order themselves in Zerodha Kite.
