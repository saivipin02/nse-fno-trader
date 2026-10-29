---
name: nse-budget
description: >-
  NSE Budget Manager. Sizes an NSE intraday trade to your rupee budget and
  your max loss per trade. Reads the plan from nse-exit (entry, stop, target),
  finds the whole shares that fit inside four limits (max loss per trade,
  position cap, max order, cash after your buffer), says which limit decided
  it, and writes the proposed trade to nse/orders.json together with the same
  trade as three Zerodha Kite orders (BUY, SL-M stop, LIMIT target, product
  MIS). A stop too far away for your max loss is a plain refusal. Nothing is
  placed. Use when the user says "how many shares", "size this trade", "how
  much should I buy", "I have 1 lakh", "I only want to risk ₹1,000 a trade",
  "set my rules", "keep 10% in cash", or after /nse-exit or /nse-timemachine.
argument-hint: "[--budget RUPEES] [--limit [PRICE]] [--write]"
---

# nse-budget

`${CLAUDE_SKILL_DIR}` is this skill's folder. Run from the folder that holds `nse/`.

```bash
python3 "${CLAUDE_SKILL_DIR}/size.py"                    # nse/plan.json + nse/config.json, prints only
python3 "${CLAUDE_SKILL_DIR}/size.py" --write            # and write nse/orders.json
python3 "${CLAUDE_SKILL_DIR}/size.py" --limit --write    # a LIMIT entry at the plan's entry
python3 "${CLAUDE_SKILL_DIR}/size.py" --budget 50000
```

## Your rules: nse/config.json

On first use, copy `${CLAUDE_SKILL_DIR}/config.example.json` to
`nse/config.json` and ASK the user for every money number; never assume them.

| key | example | meaning |
| --- | --- | --- |
| `budget` | 100000 | rupees set aside for trading (not your whole account) |
| `cash_buffer_pct` | 10 | kept in cash, never used |
| `max_position_pct` | 75 | most of the budget in one stock |
| `max_order_inr` | 100000 | largest single order |
| `min_order_inr` | 500 | smallest order worth placing |
| `max_loss_per_trade_inr` | 1000 | loss at the stop, per trade |
| `max_daily_loss_inr` | 3000 | all of today's losses at the stops together |
| `max_trades_per_day` | 3 | new entries a day |
| `min_reward_risk` | 1.0 | target distance / stop distance |
| `no_entries_before` / `no_entries_after` | "09:30" / "14:45" | IST entry window |
| `flat_by` | "15:15" | out of every intraday trade by then |
| `product` | "MIS" | MIS (intraday) or CNC (delivery) |
| `blocked` | [] | symbols never to trade (for example ones in the F&O ban period) |

The sizing uses your cash, not MIS leverage: Zerodha lets you take an MIS
position bigger than your cash, this pack does not size for that.

## How many shares

shares = floor of the smallest of: max loss / risk a share; budget x
max_position_pct / entry; max order / entry; (budget minus the buffer) /
entry. A market order is sized at the higher of the plan's entry and a fresh
price in nse/prices.json (under 15 minutes old, from `/nse-risk`'s
`quote.py`), because a price that ran up means a bigger loss at the same stop.

## The Kite orders

```
1. BUY  qty SYMBOL  MARKET (or LIMIT price)   product MIS, NSE
2. SELL qty SYMBOL  SL-M trigger = stop       place once 1 fills
3. SELL qty SYMBOL  LIMIT price = target      place once 1 fills
```

Kite does not link 2 and 3 for regular intraday orders: when one fills, the
user must cancel the other, or a stray order is left. Tell them that every
time. By `flat_by` they sell whatever is still open.

## Steps

1. Make sure nse/config.json exists and the user set the money numbers.
2. Run `size.py --write`. Read back: shares, cost, max loss at the stop, which
   limit decided the size, and the three Kite orders.
3. If it refuses, say the reason and the fix (a closer stop from `/nse-exit`,
   or skip the trade). Never raise a limit yourself.
4. Hand off to `/nse-risk` before anything is placed.

## Rules

- Proposals only. Nothing here touches Kite or any broker.
- Never size money the user has not said is for this.
- Every number comes from the config, the plan or the prices.
- No projections: never say what a trade will make.
- Brokerage, STT, exchange charges, stamp duty and GST are not included.

## Safety

Education and tooling, not financial advice. The user places every order
themselves in Zerodha Kite.
