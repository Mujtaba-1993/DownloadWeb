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
- Paper trades are automatic since 2026-11-21: every fresh break is written to the log as kind `mj` (categories `mj|A`, `mj|B`, `mj|C`) and every launch-line touch as kind `lp`; entry at the next open, target and stop two daily ranges away. The owner starts real money only after grade A has about 20 closed paper trades near the studied rate.
- Timeframes and currencies (studied 2026-11-21): on the 1-hour and 4-hour charts the theory is a coin flip for stocks (48.7% and 50.5%) and for 28 currency pairs (48.7% and 50.8%); currencies on the day chart 50.6%, calm breaks 52.0%. The tab "الفوركس" (`forex()` in `radar.py`, `renderFX()` in `template.html`) lists the pairs on the three timeframes and is labelled as unproven.

## Day-trader skills (installed 2026-11-21)

From github.com/Jakeschincariol/day-trader-skill (MIT, commit 3d0f4ef), copied into `.claude/skills/trader-*`: scanner, news, entry, exit, budget, risk, timemachine, alerts, analyst, pelosi, broker. They read free public data (Yahoo, Nasdaq Trader, SEC EDGAR, House Clerk) and write their files under `trader/`.

- `trader-broker` only prepares order tickets. No broker is connected (the owner trades in the Sahm app); never place an order.
- `trader-analyst` and the SEC part of `trader-news` need a contact e-mail in `SEC_USER_AGENT`. Do not put the owner's e-mail there; he can set it himself.
- Launch line (added 2026-11-21, `launch()` and `LP_STATS` in `radar.py`, `renderLP()` in `template.html`, shown inside the Mujtaba tab): line through the bottoms that started a big rise (8 daily ranges); buy when the price returns to it. Study: 11,651 returns, 51.0% worked, 48.2% when the market is below its 200-day. Labelled as unproven.

## Claude's paper account (tab "تداول Claude" in the radar)

The owner asked (2026-11-21) that Claude learn trading from zero and trade by itself. No real money and no broker: it is a virtual $10,000 account computed from the tool's own paper trades by `claude_book()` and the `BOOK` rules in `radar.py`, shown by `renderBook()` in `template.html`. It needs no extra scheduled run.

- Rules v1: only setup types whose studied rate is 55% or more and that the tool has not paused; risk 1% of the account per trade (5% of the account when there is no stop); at most 10% per position, 10 open positions and 3 new positions a day; no adding after a loss.
- The tab also lists the lessons learned and the schools to study next (momentum, post-earnings drift, trend following, short-term reversal, Wyckoff and volume, macro news, money management). When the owner asks to continue: study one school, test it on the data first, then change `BOOK` and the lessons list, and bump `BOOK['v']`.
- Social-media methods (tested 2026-11-21 on daily bars of liquid US stocks since 2012, coded from their published rules, not from watching videos): Minervini trend template breakout 49.8%, Qullamaggie flag breakout 50.3%, Rayner Teo 50-day pullback 51.4%, ICT liquidity sweep 52.5%, ICT fair value gap 52.6%, gap-and-go daily proxy 51.0%. None beats a random entry (about 51%). The intraday methods (Ross Cameron, ICT) were only approximated on daily bars.
- Reading videos (2026-11-21): YouTube blocks this machine (`youtube-transcript-api` and `yt-dlp` both fail with an IP block; do not try to get around it). The Firecrawl connector reads the transcript of some videos: `firecrawl_scrape` with `formats: ["query"]` and a question (5 credits each); it worked on 2 of 4 videos tried. Rules read from the videos and tested on daily bars since 2012, result in units of the risked amount: Rayner Teo 50-day pullback +0.06 (31,928 trades), Ross Cameron momentum day bought the next day -0.03 (his method is intraday), Minervini VCP breakout +0.21 (1,311 trades, positive in all four periods) against +0.12 for any day in a stock that passes the same trend template.
- Seven more videos found and read by a subagent through Firecrawl (2026-11-21), rules tested as stated on daily bars of liquid US stocks since 2012; holding the same stocks returns +0.078% a day: Connors RSI-2 below 5 above the 200-day, exit above the 5-day average, wins 64.8%, +0.42% a trade, +0.082% a day (no better than holding); Turtle 55-day high +0.024% a day; Trading Rush MACD +0.028%; Oliver Kell (Arabic video) +0.028%; Darvas box +0.019%; Adam Khoo 50-day pullback -0.019%; Humbled Trader gap swing -0.017%. When the owner says to look for videos, find them yourself (he will not send links): delegate the search and reading to a subagent with a tight brief and return only the rules.
- Fixed 2026-11-24: suggestions on stocks outside the S&P 500 list (most insider buys) were never entered or graded because the scanner only kept price bars for the index. `run_market` now downloads the bars of those symbols before `selflearn` (output line `EXTRA`). A full run during market hours is only for testing in a scratch copy: publish the light `--intraday us` run instead and let the evening run do the full one.

## Gap with a patient entry (tab "الفجوات" in the radar)

The owner's idea (2026-11-24): for the down-gap signal, do not buy at once; place the buy order at the usual further fall under the signal price (`dd50` of the gap size, about -7.7%) and wait up to 20 sessions; target = the gap closes, no stop, out 20 sessions after the fill. Code: `gapwait()` and `GAPW_STATS` in `radar.py` (computed from the `gap` entries of the log on every full run, so it needs no state of its own), `renderGW()` in `template.html`.

- Study on 54,648 signals (US stocks of $5 or more, since 2007): buying at once averages +1.5% a trade; waiting fills 55% of the signals and averages +5.3% a trade (+2.9% per signal against +1.5%), better in all four periods, weakest since 2023 (+0.8% against -0.3%). The 45% that never come down are missed, and they were the best ones bought at once (+10.0%).
- The tab lists ONLY the stocks that already fell to the entry price (owner, 2026-11-24: «بس اطلع لي الاسهم الي نزلت ٧.٧٪»). Do not show the stocks still waiting to come down.
