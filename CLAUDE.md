# DownloadWeb

- `bounce-radar/`: the stock radar (scanner `radar.py`, page `template.html`), published as a private artifact.

## Roast Room (advisor council)

Installed from github.com/nateherkai/roast-room (MIT). Skills `/roast-room` and `/newroaster` live in `.claude/skills/`, one agent per advisor in `.claude/agents/council-*.md`, the roster in `.claude/skills/roast-room/roster.json`.

- For a hard decision about the radar or a trade ("should we...", which signal to keep, how much risk), run `/roast-room`. For one opinion, `/roast-room ask <seat> ...`. Use `--quick` by default: the owner wants to save usage.
- To add an advisor, run `/newroaster <name>`. Keep `--quick` depth unless the owner asks for more.
- The room web app was not installed (this repo's `app/` is an Android app). Councils run in chat and are saved under `sessions/`.
- Seats are simulations built from public work, not the real people. Never present a seat's words as the person's unless it is a verbatim quote with a source id from that seat's brain.
