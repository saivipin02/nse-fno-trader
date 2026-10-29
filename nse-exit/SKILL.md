---
name: nse-exit
description: >-
  NSE Exit Planner. Sets the stop and the target before you enter, so you
  know when to get out. Reads the entry from nse-entry (or a price you give),
  puts the stop at the opening-range midpoint by default (or the range low,
  your price, a percent, or a multiple of the ATR), rounds the stop DOWN and
  the target UP to NSE's tick for that price (0.01 / 0.05 / 0.10 / 0.50 / 1 /
  5), and sets the target at 2R (or 1R, or your price). Refuses a stop at or
  above the entry, a target at or below it, or a stop too tight to survive the
  spread. Flat by 15:15 IST by default, before Zerodha's MIS auto square-off.
  Writes nse/plan.json. Long side only. Use when the user says "where's my
  stop", "set my stop and target", "plan the exit", "when do I get out",
  "stop loss", "what's my R", "risk reward", or right after /nse-entry triggers.
argument-hint: "[--stop or-mid|or-low|price:X|pct:X|atr:K] [--target 2R|1R|price:X]"
---

# nse-exit

`${CLAUDE_SKILL_DIR}` is this skill's folder. Run from the folder that holds `nse/`.

```bash
python3 "${CLAUDE_SKILL_DIR}/exit.py" plan --write                         # from nse/entry.json
python3 "${CLAUDE_SKILL_DIR}/exit.py" plan --stop or-low --target 1.5R --write
python3 "${CLAUDE_SKILL_DIR}/exit.py" plan --symbol INFY --entry 1520 --stop pct:1 --write
python3 "${CLAUDE_SKILL_DIR}/exit.py" show                                 # today's plan
```

Other flags: `--or-high/--or-low` (plan without nse/entry.json), `--time
"10:15 AM"`, `--flat-by 15:15`, `--now`, `--offline`, `--json`.

## The rules it applies

- Stop: opening-range midpoint for an ORB (default), or `or-low`, `price:X`,
  `pct:X` under the entry, `atr:K` times the 14-bar ATR. Rounded DOWN to the
  NSE tick, away from the entry.
- Target: 2R by default (twice the risk above the entry), or `1R`, `1.5R`,
  `price:X`. Rounded UP to the NSE tick.
- NSE tick by price (from 15 April 2025): under ₹250 ₹0.01; ₹250 to 1,000
  ₹0.05; to 5,000 ₹0.10; to 10,000 ₹0.50; to 20,000 ₹1; above ₹5. NSE sets
  each stock's tick from its price band, so for a stock right at a band edge
  Kite's tick wins: if Kite rejects a price, re-plan with `price:X` on its tick.
- Refusals: a stop at or above the entry, a target at or below it, a stop
  closer than 0.05 % of the price.
- Flat by 15:15 IST (config `flat_by`): out by then, win or lose. Zerodha
  auto squares off equity MIS positions at about 3:25 PM and charges ₹50 + GST
  per order for it.

## Steps

1. Run it right after `/nse-entry` triggers. Before that, `--entry PRICE`
   plans ahead at the level you expect.
2. Use the default stop for an opening-range breakout unless the user names
   another. A level setup needs one: ask.
3. Run `exit.py plan --write`. Read back the entry, the stop and its rule,
   the target, the risk a share, reward:risk and flat by.
4. If it refuses, say the reason and the fix. Never loosen anything on your own.
5. Say once that the stop is a plan, not a guarantee: a gap or a circuit can
   fill past it.
6. Hand off to `/nse-timemachine` to replay the plan, then `/nse-budget`.

## Rules

- The stop and target are set before the entry, never after.
- Never move a stop further from the entry once the trade is on.
- Plain numbers only. Never a P&L or a return. A 2R target is not a prediction.
- Long side only.

## Safety

Education and tooling, not financial advice. Nothing in this pack places an
order; the user places every order themselves in Zerodha Kite.
