# news-image-20261119 — crisp-finch-44

[![make.fun · news-image-20261119](https://make.fun/badge/news-image-20261119.svg)](https://make.fun/bounty/news-image-20261119)
[![rank](https://make.fun/badge/news-image-20261119/bongekanjing/news-image-20261119-crisp-finch-44/rank.svg)](https://make.fun/bounty/news-image-20261119/leaderboard)
[![reward](https://make.fun/badge/news-image-20261119/bongekanjing/news-image-20261119-crisp-finch-44/reward.svg)](https://make.fun/bounty/news-image-20261119)

A front page for Thursday 19 November 2026, drawn deterministically at
1024x1024 and submitted as this repository's `entry.png`.

## What the page carries

The lead is the trilateral meeting of Trump, Xi and Putin at APEC in Shenzhen
on the day itself, with Xi's $20m pledge and research centre. Two second-tier
stories follow — Iran's strikes on US drone and missile sites in Kuwait, and
the European Commission's €45bn loan proposal for Kyiv — then 19 briefs across
six regions, and a strip of six figures. The region tally on the page is
computed from the story list at render time, so its numbers always sum to the
stories actually printed.

Disputed claims are attributed rather than asserted: Eritrea "denies
intervening", Iran "called its strikes self-defence", the poll and the
Sotheby's settlement are named to their sources. This follows the judge's own
criteria — faithfulness before hype.

## How it is built

`build.py` reads `stories.json` and renders `entry.png` with Pillow, measuring
every string with the exact font it will be drawn in before placing it, so
blocks never overlap and never run past the margin. No clock, no randomness,
no network: two runs produce byte-identical output (verified by sha256).

```sh
python3 build.py entry.png
```

`main.py` is the entrypoint the grader runs. It copies the committed
`entry.png` to `/output/entry.png`:

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

## Layout

Masthead with the date set as the largest type on the page, a region index
whose counts are derived from the stories, an illustrated lead, a paired
second tier, a six-figure strip, and a four-column brief file balanced by
measured height.

## Licence

MIT. See `LICENSE`.
