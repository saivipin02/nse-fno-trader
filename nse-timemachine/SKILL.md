---
name: nse-timemachine
description: >-
  NSE Time Machine. Replays a planned NSE intraday trade before you risk a
  rupee: 10,000 simulated sessions plus every past time the setup fired.
  Takes the plan from nse-exit (entry, stop, target), rebuilds the rest of
  the day 10,000 times from the stock's own 5-minute bars over the last 60
  days (full 9:15 to 3:30 IST sessions, 75 bars each), and re-runs the same
  rule on every past session. Prints the odds of target first, stop first or
  neither, where the price sits at the end, the average R, the history, and
  one honest verdict. Use when the user says "run the time machine", "replay
  this trade", "what are the odds", "simulate this trade", "monte carlo",
  "backtest this setup", "is this a coin flip", or after /nse-exit, before /nse-budget.
argument-hint: "[--until 15:15] [--seed N]"
---

# nse-timemachine

`${CLAUDE_SKILL_DIR}` is this skill's folder. Run from the folder that holds `nse/`.

```bash
python3 "${CLAUDE_SKILL_DIR}/timemachine.py" run --until 15:15 --write    # nse/plan.json, out by your flat-by
python3 "${CLAUDE_SKILL_DIR}/timemachine.py" run --symbol TCS --entry 3400 --stop 3380 --target 3440 --entry-time "10:15 AM"
python3 "${CLAUDE_SKILL_DIR}/timemachine.py" chart                         # the price band, as text
```

Other flags: `--replays 10000`, `--seed 19`, `--window 2` (draw from the same
time of day plus or minus 2 bars), `--offline FILE`, `--now`, `--json`.

## How it works

1. One request for 60 days of 5-minute bars (Yahoo, SYMBOL.NS). Only FULL
   sessions before the plan's date count: all 75 bars from 9:15 to 3:30 IST.
   NSE holidays, short or broken days and today are left out.
2. Each replay builds the rest of the day bar by bar, each bar drawn whole
   (its move from the bar before, its high and low) from the stock's own bars
   at the same time of day. It checks the stop and target on every bar; when
   one bar touches both, the stop counts first.
3. The history replay runs the same rule (opening range, stop rule, the same
   R target) on every one of those real sessions.
4. The verdict weighs the target's R: at 2R the target only has to come first
   a third of the time to break even.

## Steps

1. Make sure nse/plan.json is today's plan from `/nse-exit`.
2. Run `timemachine.py run --until 15:15 --write` (use the plan's flat-by time).
3. Tell the user, in order: the four odds, the price range at the end, the
   average R, the history line, then the verdict line and any line under it
   exactly as printed. Say the seed.
4. If it is a coin flip or close to break-even, say so plainly.
5. Say once that it is built from the last 60 days and is not a prediction:
   results, news, F&O ban periods and circuits can do things those days never
   did. Check `/nse-news` before going on.
6. If the user still wants the trade, hand off to `/nse-budget`.

## Rules

- Every number comes from the run. Never round a coin flip up into an edge.
- Repeat the verdict lines, do not rewrite them.
- Simulated odds are not predictions or promises. Brokerage, STT and other
  charges are not in the R numbers; on a small move they matter.
- Always say the seed.

## Safety

Education and tooling, not financial advice. Nothing in this pack places an
order; the user places every order themselves in Zerodha Kite.
