# tiny-chess-01

[![make.fun · tiny-chess-01](https://make.fun/badge/tiny-chess-01.svg)](https://make.fun/bounty/tiny-chess-01?utm_source=github&utm_medium=readme&utm_campaign=tiny-chess-01)
[![rank](https://make.fun/badge/tiny-chess-01/matthew-eth724/tiny-chess-01/rank.svg)](https://make.fun/bounty/tiny-chess-01/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=tiny-chess-01)
[![reward](https://make.fun/badge/tiny-chess-01/matthew-eth724/tiny-chess-01/reward.svg)](https://make.fun/bounty/tiny-chess-01?utm_source=github&utm_medium=readme&utm_campaign=tiny-chess-01)

An entry for make.fun's [Build the strongest chess engine in 4 KB of Python](https://make.fun/bounty/tiny-chess-01) bounty.

A 0x88 negamax engine in **4,072 bytes** of `main.py` (Python 3.13, stdlib only) — the payload is
LZMA-packed and unpacked at startup. PVS with a Zobrist-keyed transposition table, late-move
reductions, null-move pruning, killers and history, quiescence, and a tapered evaluation.

Move generation is verified exact against python-chess on the standard perft suite (52M nodes).
Search runs on a fixed node budget, never a clock, so replay is byte-for-byte deterministic.

## Run

```sh
python3 main.py
```

It plays through make.fun's game protocol, requesting a game and posting one move per turn.

SPDX-License-Identifier: MIT
