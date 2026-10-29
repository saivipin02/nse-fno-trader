---
name: nse-risk
description: >-
  NSE Risk Manager. Checks every proposed trade against your limits before
  you place it in Zerodha Kite, and keeps the trade log that makes the daily
  limits work. Blocks: no stop, a loss at the stop over your max loss per
  trade (measured from the higher of the plan's entry and a fresh price),
  reward:risk under your minimum, today's total risk over your daily loss
  limit, too many trades today, entries outside your IST window or when NSE is
  closed (weekends, NSE holidays), a price off NSE's tick, part shares, a
  product other than MIS/CNC, blocked symbols, order size, position cap, cash
  buffer, margin and short sales. Prints PASS or BLOCK with the reason. Also
  fetches fresh prices (quote.py) and logs trades you placed (log.py). Use
  when the user says "check my order", "is this safe", "risk check", "can I
  take this trade", "how much have I risked today", "I placed it", "I got out",
  or before placing anything in Kite, always.
argument-hint: "[check | quote SYMBOL | log placed | log exit SYMBOL QTY PRICE | log today]"
---

# nse-risk

`${CLAUDE_SKILL_DIR}` is this skill's folder. Run from the folder that holds `nse/`.

```bash
python3 "${CLAUDE_SKILL_DIR}/quote.py" --from-orders        # fresh prices -> nse/prices.json
python3 "${CLAUDE_SKILL_DIR}/check.py"                       # PASS / BLOCK, writes nse/state/risk.json
python3 "${CLAUDE_SKILL_DIR}/log.py" placed                  # after the user placed it in Kite
python3 "${CLAUDE_SKILL_DIR}/log.py" exit RELIANCE 18 1021.40   # after they sold
python3 "${CLAUDE_SKILL_DIR}/log.py" today                   # today's trades and risk
```

check.py reads nse/orders.json (from `/nse-budget`), nse/config.json,
nse/prices.json, nse/portfolio.json (optional: `{"cash": ..., "positions":
[...]}`) and nse/state/broker.json (the log). Exit code 0 when every order
passes, 1 when any is blocked.

## What blocks an entry

stop missing or on the wrong side; loss at the stop over `max_loss_per_trade_inr`;
reward:risk under `min_reward_risk`; today's logged risk plus this one over
`max_daily_loss_inr`; `max_trades_per_day` reached; the same buy already
logged today; before `no_entries_before` or after `no_entries_after` (IST) or
NSE closed; a limit, stop or target price not on NSE's tick for that price; a
product other than MIS or CNC; part shares; a blocked symbol; under
`min_order_inr` or over `max_order_inr`; over `max_position_pct`; dipping into
the cash buffer or needing margin. Getting out (an exit) is never blocked by
a day limit.

## The log

The user places orders themselves, so the daily limits only work if each
trade is logged. `log.py placed` logs the order in nse/orders.json ONLY if
check.py passed that exact order today (it matches a fingerprint of the
order's fields); an edited or unchecked order is refused. Ask the user to tell
you when they placed it and when they got out, and log both.

## Steps

1. If the price may have moved since the plan, run `quote.py --from-orders`.
2. Run `check.py`. Tell the user, order by order: the max loss at the stop,
   reward:risk, and how much of today's limits it uses. For a BLOCK, give the
   reason and the fix (fewer shares, a closer stop from `/nse-exit`, wait for
   the window, or skip it). Never change a limit yourself.
3. On PASS, show the three Kite orders from nse/orders.json and remind the
   user: place the stop and target once the buy fills, cancel the other when
   one fills, and be flat by the flat-by time (Zerodha squares MIS off at
   about 3:25 PM and charges for it).
4. When the user says they placed it: `log.py placed`. When they got out:
   `log.py exit SYMBOL QTY PRICE`.
5. If the order changes in any way, check it again.

## Rules

- A PASS means the order fits the user's own rules. It is not a recommendation.
- Every number comes from the config, the order, the prices or the log.
- Yahoo's NSE prices are free and can lag; the price in Kite is the one that
  fills, and an SL-M stop can fill worse than its trigger in a fast market or
  past a circuit.
- Brokerage and taxes are not included in any number.

## Safety

Education and tooling, not financial advice, and not a SEBI-registered
adviser's view. Nothing in this pack places an order; the user places every
order themselves in Zerodha Kite.
