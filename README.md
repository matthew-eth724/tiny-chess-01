# tiny-chess-01

A chess engine in at most 4,096 bytes of Python (LZMA-packed by `makefun compress`).

`main.py` is the entry: a 0x88 move generator with exact perft, tapered
piece-square evaluation, and a PVS search with a Zobrist transposition table,
null-move pruning, late-move reductions, killers/history ordering and
quiescence. It reads `MAKEFUN_ENV_URL` and plays through the env's
`/game` and `/move` endpoints under a fixed node budget, so replays are
deterministic.

`src.py` is the readable source `main.py` is packed from.
