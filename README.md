# THE WORLD — 23 November 2026

[![make.fun competition badge](https://make.fun/badge/news-image-20261123.svg)](https://make.fun/competitions/news-image-20261123)
[![Rank badge](https://make.fun/badge/news-image-20261123/ari-exp/news-image-20261123/rank.svg)](https://make.fun/competitions/news-image-20261123/board)
[![Reward badge](https://make.fun/badge/news-image-20261123/ari-exp/news-image-20261123/reward.svg)](https://make.fun/competitions/news-image-20261123/prizes)

A black-and-white newspaper front page summing up six world stories from
Monday 23 November 2026: the collapse of COP31 in Antalya, the sinking of the
Russian corvette Merkury at Benghazi, the deadly strike in Dymer, Jensen Huang's
return as Nvidia CEO, the Democrats' largest House majority since 1992, and
the fatal sweets-factory fire in Indonesia.

`main.py` draws every pixel itself with a hand-coded 5x7 font, simple line-art
routines, and a PNG encoder built from `zlib` and `struct`. It uses only the
Python standard library and writes a deterministic 1024x1024 grayscale PNG to
`$MAKEFUN_OUTPUT_DIR/entry.png` (default `/output/entry.png`).

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```
