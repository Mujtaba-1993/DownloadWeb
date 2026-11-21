# DownloadWeb

- `bounce-radar/`: the stock radar (scanner `radar.py`, page `template.html`), published as a private artifact.

## Roast Room (advisor council)

Installed from github.com/nateherkai/roast-room (MIT). Skills `/roast-room` and `/newroaster` live in `.claude/skills/`, one agent per advisor in `.claude/agents/council-*.md`, the roster in `.claude/skills/roast-room/roster.json`.

- For a hard decision about the radar or a trade ("should we...", which signal to keep, how much risk), run `/roast-room`. For one opinion, `/roast-room ask <seat> ...`. Use `--quick` by default: the owner wants to save usage.
- To add an advisor, run `/newroaster <name>`. Keep `--quick` depth unless the owner asks for more.
- The room web app was not installed (this repo's `app/` is an Android app). Councils run in chat and are saved under `sessions/`.
- Seats are simulations built from public work, not the real people. Never present a seat's words as the person's unless it is a verbatim quote with a source id from that seat's brain.

## Research tools (installed from GitHub projects)

`pip install -r bounce-radar/requirements-research.txt` before any chart-pattern study.

- `trendln` (GregoryMorse/trendln, MIT): draws support and resistance lines through the bounces. Use it to draw the owner's lines instead of a hand-written rule. On his EURUSD chart it found his falling line (1.1897 to 1.1249, 8 touches).
- `stumpy` (stumpy-dev/stumpy): finds windows whose shape matches a given chart (`stumpy.mass`). Use it when the owner sends a chart and asks for similar ones.

## Mujtaba's theory (tab "نظرية مجتبى" in the radar)

The owner's own pattern, added 2026-11-21: a falling line on the small bounces; each daily close above it after the price sat below it is a buy point. Code: `mujtaba()` and `MJ_STATS` in `radar.py`, `renderMJ()` in `template.html`.

- Study (42,814 breaks, lines drawn from the past only): all breaks win 51.7%, calm breaks 53.4%, calm breaks with the S&P 500 below its 200-day average 56.6%, wild breaks 48.0%. A line that worked before does not raise the odds of its next break.
- Grades on the page: A = calm break and market below its 200-day, B = calm break and market above it, C = wild break (do not enter).
- The tab is not written to the performance log yet.
- Timeframes and currencies (studied 2026-11-21): on the 1-hour and 4-hour charts the theory is a coin flip for stocks (48.7% and 50.5%) and for 28 currency pairs (48.7% and 50.8%); currencies on the day chart 50.6%, calm breaks 52.0%. The tab "الفوركس" (`forex()` in `radar.py`, `renderFX()` in `template.html`) lists the pairs on the three timeframes and is labelled as unproven.
