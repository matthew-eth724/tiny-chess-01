
import json,os,sys,urllib.request

MATE = 30000
INF = 1000000

P, N, B, R, Q, K = 1, 2, 3, 4, 5, 6
VAL = [0, 100, 325, 335, 500, 975, 0, 0, 0, 100, 325, 335, 500, 975, 0]
DIAG = (-17, -15, 15, 17)
ORTH = (-16, -1, 1, 16)
ALLK = DIAG + ORTH
OFF = [(), (), (-33, -31, -18, -14, 14, 18, 31, 33), DIAG, ORTH, ALLK, ALLK]

PAWN=(0,0,0,0,0,0,0,0,5,10,10,-20,-20,10,10,5,5,-5,-10,0,0,-10,-5,5,0,0,0,20,20,0,0,0,5,5,10,25,25,10,5,5,10,10,20,30,30,20,10,10,50,50,50,50,50,50,50,50,0,0,0,0,0,0,0,0,)
KNIGHT=(-50,-40,-30,-30,-30,-30,-40,-50,-40,-20,0,5,5,0,-20,-40,-30,5,10,15,15,10,5,-30,-30,0,15,20,20,15,0,-30,-30,5,15,20,20,15,5,-30,-30,0,10,15,15,10,0,-30,-40,-20,0,0,0,0,-20,-40,-50,-40,-30,-30,-30,-30,-40,-50,)
BISHOP=(-20,-10,-10,-10,-10,-10,-10,-20,-10,5,0,0,0,0,5,-10,-10,10,10,10,10,10,10,-10,-10,0,10,10,10,10,0,-10,-10,5,5,10,10,5,5,-10,-10,0,5,10,10,5,0,-10,-10,0,0,0,0,0,0,-10,-20,-10,-10,-10,-10,-10,-10,-20,)
ROOK=(0,0,0,5,5,0,0,0,-5,0,0,0,0,0,0,-5,-5,0,0,0,0,0,0,-5,-5,0,0,0,0,0,0,-5,-5,0,0,0,0,0,0,-5,-5,0,0,0,0,0,0,-5,5,10,10,10,10,10,10,5,0,0,0,0,0,0,0,0,)
QUEEN=(-20,-10,-10,-5,-5,-10,-10,-20,-10,0,5,0,0,0,0,-10,-10,5,5,5,5,5,0,-10,-5,0,5,5,5,5,0,-5,0,0,5,5,5,5,0,-5,-10,0,5,5,5,5,0,-10,-10,0,0,0,0,0,0,-10,-20,-10,-10,-5,-5,-10,-10,-20,)
KING=(20,30,10,0,0,10,30,20,20,20,0,0,0,0,20,20,-10,-20,-20,-20,-20,-20,-20,-10,-20,-30,-30,-40,-40,-30,-30,-20,-30,-40,-40,-50,-50,-40,-40,-30,-30,-40,-40,-50,-50,-40,-40,-30,-30,-40,-40,-50,-50,-40,-40,-30,-30,-40,-40,-50,-50,-40,-40,-30,)
KING_EG=(-50,-30,-30,-30,-30,-30,-30,-50,-30,-30,0,0,0,0,-30,-30,-30,-10,20,30,30,20,-10,-30,-30,-10,30,40,40,30,-10,-30,-30,-10,30,40,40,30,-10,-30,-30,-10,20,30,30,20,-10,-30,-30,-20,0,0,0,0,-20,-30,-50,-40,-30,-20,-20,-30,-40,-50,)
TS = [None, PAWN, KNIGHT, BISHOP, ROOK, QUEEN, KING]

PST = [None] * 15
KEG = [[0] * 128, [0] * 128]
for t in range(1, 7):
    w = [0] * 128
    bl = [0] * 128
    for sq in range(128):
        if sq & 0x88:
            continue
        f, r = sq & 7, sq >> 4
        w[sq] = TS[t][r * 8 + f] + VAL[t]
        bl[sq] = -(TS[t][(7 - r) * 8 + f] + VAL[t])
        if t == K:
            KEG[0][sq] = KING_EG[r * 8 + f]
            KEG[1][sq] = -KING_EG[(7 - r) * 8 + f]
    PST[t] = w
    PST[t + 8] = bl


TT = {}
KILL = [[0, 0] for _ in range(64)]
HIST = [[0] * 128 for _ in range(128)]
NODES = 0
LIMIT = 250000
ABORT = False

import random as _r
_r.seed(20261117)
ZP = [[_r.getrandbits(64) for _ in range(128)] for _ in range(15)]
ZS = _r.getrandbits(64)
ZC = [_r.getrandbits(64) for _ in range(16)]
ZE = [_r.getrandbits(64) for _ in range(128)]


def pf(fen):
    b = [0] * 128
    f = fen.split()
    r, fl = 7, 0
    for c in f[0]:
        if c == "/":
            r, fl = r - 1, 0
        elif "1" <= c <= "8":
            fl += int(c)
        else:
            t = "pnbrqk".index(c.lower()) + 1
            b[fl + r * 16] = t if c.isupper() else t + 8
            fl += 1
    side = 0 if f[1] == "w" else 1
    ca = 0
    for c in f[2]:
        ca |= {"K": 1, "Q": 2, "k": 4, "q": 8}.get(c, 0)
    ep = -1
    if f[3] != "-":
        ep = (ord(f[3][0]) - 97) + (int(f[3][1]) - 1) * 16
    return b, side, ca, ep
def atk(b, sq, by):
    lo = by * 8
    for o in DIAG:
        s = sq + o
        while 0 <= s < 128 and not s & 0x88:
            pc = b[s]
            if pc:
                if pc == B + lo or pc == Q + lo:
                    return True
                break
            s += o
    for o in ORTH:
        s = sq + o
        while 0 <= s < 128 and not s & 0x88:
            pc = b[s]
            if pc:
                if pc == R + lo or pc == Q + lo:
                    return True
                break
            s += o
    for o in OFF[N]:
        s = sq + o
        if 0 <= s < 128 and not s & 0x88 and b[s] == N + lo:
            return True
    for o in ALLK:
        s = sq + o
        if 0 <= s < 128 and not s & 0x88 and b[s] == K + lo:
            return True
    st = -16 if by == 0 else 16
    for o in (st - 1, st + 1):
        s = sq + o
        if 0 <= s < 128 and not s & 0x88 and b[s] == P + lo:
            return True
    return False
class Pos:
    __slots__ = ("b", "side", "castle", "ep", "king", "hist", "h")

    def __init__(self, board, side, castle, ep):
        self.b = board
        self.side = side
        self.castle = castle
        self.ep = ep
        self.king = [board.index(K), board.index(K + 8)]
        self.hist = []
        h = ZS if side else 0
        for sq in range(128):
            pc = board[sq]
            if pc:
                h ^= ZP[pc][sq]
        h ^= ZC[castle]
        if ep >= 0:
            h ^= ZE[ep]
        self.h = h

    def moves(self, caps=False):
        b = self.b
        side = self.side
        out = []
        sq = 0
        while sq < 128:
            if sq & 0x88:
                sq = (sq & 112) + 16
                continue
            pc = b[sq]
            if not pc or pc >> 3 != side:
                sq += 1
                continue
            t = pc & 7
            if t == P:
                st = 16 if side == 0 else -16
                last = 7 if side == 0 else 0
                to = sq + st
                if 0 <= to < 128 and not to & 0x88 and not b[to]:
                    if to >> 4 == last:
                        out.append((sq, to, Q))
                        out.append((sq, to, R))
                        out.append((sq, to, B))
                        out.append((sq, to, N))
                    elif not caps:
                        out.append((sq, to, 0))
                for d in (st - 1, st + 1):
                    to = sq + d
                    if not (0 <= to < 128) or to & 0x88:
                        continue
                    pc2 = b[to]
                    if pc2:
                        if pc2 >> 3 != side:
                            if to >> 4 == last:
                                out.append((sq, to, Q))
                                out.append((sq, to, R))
                                out.append((sq, to, B))
                                out.append((sq, to, N))
                            else:
                                out.append((sq, to, 0))
                    elif to == self.ep and not caps:
                        out.append((sq, to, 0))
                if not caps:
                    fr = 1 if side == 0 else 6
                    if (sq >> 4) == fr and not b[sq + st] and not b[sq + 2 * st]:
                        out.append((sq, sq + 2 * st, 0))
            elif t == N or t == K:
                for o in OFF[t]:
                    to = sq + o
                    if not (0 <= to < 128) or to & 0x88:
                        continue
                    pc2 = b[to]
                    if pc2 and pc2 >> 3 == side:
                        continue
                    if caps and not pc2:
                        continue
                    out.append((sq, to, 0))
                if t == K and self.castle:
                    out.extend(self.castles(sq, side, caps))
            else:
                for o in OFF[t]:
                    to = sq + o
                    while 0 <= to < 128 and not to & 0x88:
                        pc2 = b[to]
                        if pc2:
                            if pc2 >> 3 != side:
                                out.append((sq, to, 0))
                            break
                        if not caps:
                            out.append((sq, to, 0))
                        to += o
            sq += 1
        return out

    def castles(self, sq, side, caps):
        if caps:
            return []
        b = self.b
        e = side ^ 1
        o = []
        if side == 0 and sq == 4:
            if self.castle & 1 and not b[5] and not b[6] and b[7] == R and \
                    not atk(b, 4, e) and not atk(b, 5, e) and not atk(b, 6, e):
                o.append((4, 6, 0))
            if self.castle & 2 and not b[3] and not b[2] and not b[1] and b[0] == R and \
                    not atk(b, 4, e) and not atk(b, 3, e) and not atk(b, 2, e):
                o.append((4, 2, 0))
        elif side == 1 and sq == 116:
            if self.castle & 4 and not b[117] and not b[118] and b[119] == R + 8 and \
                    not atk(b, 116, e) and not atk(b, 117, e) and not atk(b, 118, e):
                o.append((116, 118, 0))
            if self.castle & 8 and not b[115] and not b[114] and not b[113] and b[112] == R + 8 and \
                    not atk(b, 116, e) and not atk(b, 115, e) and not atk(b, 114, e):
                o.append((116, 114, 0))
        return o

    def make(self, m):
        fr, to, promo = m
        b = self.b
        pc = b[fr]
        cap = b[to]
        ep_cap = -1
        t = pc & 7
        if t == P and to == self.ep and not cap:
            ep_cap = to + (-16 if self.side == 0 else 16)
            cap = b[ep_cap]
        self.hist.append([m, cap, self.castle, self.ep, ep_cap, self.king[0], self.king[1], self.h])
        h = self.h ^ ZS
        h ^= ZC[self.castle]
        if self.ep >= 0:
            h ^= ZE[self.ep]
        b[fr] = 0
        h ^= ZP[pc][fr]
        if ep_cap >= 0:
            h ^= ZP[cap][ep_cap]
        b[to] = (promo | (pc & 8)) if promo else pc
        h ^= ZP[b[to]][to]
        if ep_cap >= 0:
            b[ep_cap] = 0
        self.ep = ((fr + to) >> 1 if (to - fr) in (32, -32) else -1) if t == P else -1
        if t == K:
            self.king[self.side] = to
            self.castle &= ~(3 if self.side == 0 else 12)
            if to - fr == 2:
                b[fr + 1] = b[fr + 3]
                b[fr + 3] = 0
            elif fr - to == 2:
                b[fr - 1] = b[fr - 4]
                b[fr - 4] = 0
        elif t == R:
            if fr == 0: self.castle &= ~2
            elif fr == 7: self.castle &= ~1
            elif fr == 112: self.castle &= ~8
            elif fr == 119: self.castle &= ~4
        if cap and cap & 7 == R:
            if to == 0: self.castle &= ~2
            elif to == 7: self.castle &= ~1
            elif to == 112: self.castle &= ~8
            elif to == 119: self.castle &= ~4
        self.side ^= 1
        h ^= ZC[self.castle]
        if self.ep >= 0:
            h ^= ZE[self.ep]
        self.h = h

    def make_null(self):
        self.hist.append([(-1, 0, 0), 0, self.castle, self.ep, -1,
                          self.king[0], self.king[1], self.h])
        h = self.h ^ ZS
        if self.ep >= 0:
            h ^= ZE[self.ep]
        self.ep = -1
        self.side ^= 1
        self.h = h

    def unmake_null(self):
        _, cap, castle, ep, ep_cap, kw, kb, h = self.hist.pop()
        self.side ^= 1
        self.castle = castle
        self.ep = ep
        self.h = h

    def unmake(self):
        m, cap, castle, ep, ep_cap, kw, kb, h = self.hist.pop()
        fr, to, promo = m
        b = self.b
        self.side ^= 1
        pc = b[to]
        b[fr] = (P | (pc & 8)) if promo else pc
        b[to] = 0
        if pc & 7 == K and abs(to - fr) == 2:
            if to - fr == 2:
                b[fr + 3] = b[fr + 1]
                b[fr + 1] = 0
            else:
                b[fr - 4] = b[fr - 1]
                b[fr - 1] = 0
        if ep_cap >= 0:
            b[to] = 0
            b[ep_cap] = P | ((self.side ^ 1) * 8)
        else:
            b[to] = cap
        self.king[0] = kw
        self.king[1] = kb
        self.castle = castle
        self.ep = ep
        self.h = h

    def evaluate(self):
        b = self.b
        sc = np = 0
        sq = 0
        while sq < 128:
            if sq & 0x88:
                sq = (sq & 112) + 16
                continue
            pc = b[sq]
            if pc:
                t = pc & 7
                if t != K:
                    if t != P:
                        np += VAL[t]
                sc += PST[pc][sq]
            sq += 1
        ph = np if np < 6200 else 6200
        kw, kb = self.king
        sc += (PST[6][kw] * ph + KEG[0][kw] * (6200 - ph)) // 6200
        sc -= (PST[14][kb] * ph + KEG[1][kb] * (6200 - ph)) // 6200
        return sc if self.side == 0 else -sc

    def legal(self):
        for m in self.moves():
            self.make(m)
            ok = not atk(self.b, self.king[self.side ^ 1], self.side)
            self.unmake()
            if ok:
                return m
        return None


def sm(p, mv, ply, tt):
    b, hs = p.b, HIST
    k0, k1 = KILL[ply] if ply < 64 else KILL[63]

    def key(m):
        fr, to, pr = m
        c = b[to]
        s = (10 * VAL[c] - VAL[b[fr]]) if c else (8 * VAL[pr] if pr else 0)
        return (1 << 20) if m == tt else s + hs[fr][to] + (5000 if m == k0 else 4000 if m == k1 else 0)
    mv.sort(key=key, reverse=True)
    return mv


def qsearch(p, a, b, ply):
    global NODES
    NODES += 1
    st = p.evaluate()
    if st >= b or ply > 40:
        return st
    if st > a:
        a = st
    for m in sm(p, p.moves(True), ply, None):
        p.make(m)
        if atk(p.b, p.king[p.side ^ 1], p.side):
            p.unmake()
            continue
        sc = -qsearch(p, -b, -a, ply + 1)
        p.unmake()
        if sc >= b:
            return sc
        if sc > a:
            a = sc
    return a


def search(p, d, a, b, ply, null=True):
    global NODES, ABORT
    if NODES > LIMIT or ABORT:
        ABORT = True
        return 0
    if d <= 0:
        return qsearch(p, a, b, ply)
    hit = TT.get(p.h)
    tm = None
    if hit:
        f, v, hd, tm = hit
        if hd >= d and (f == 0 or (f == 1 and v >= b) or (f == 2 and v <= a)):
            return v
    chk = atk(p.b, p.king[p.side], p.side ^ 1)
    if null and not chk and d >= 3 and ply:
        p.make_null()
        sc = -search(p, d - 3, -b, -b + 1, ply + 1, False)
        p.unmake_null()
        if ABORT:
            return 0
        if sc >= b:
            return sc
    mv = p.moves()
    lg = 0
    best = -INF
    bm = None
    a0 = a
    sm(p, mv, ply, tm)
    for m in mv:
        cap = p.b[m[1]] or m[2]
        p.make(m)
        if atk(p.b, p.king[p.side ^ 1], p.side):
            p.unmake()
            continue
        lg += 1
        red = 0
        if d >= 3 and lg > 3 and not cap and not chk:
            red = 1 if lg < 8 else 2
        if lg == 1:
            sc = -search(p, d - 1, -b, -a, ply + 1)
        else:
            sc = -search(p, d - 1 - red, -a - 1, -a, ply + 1, False)
            if not ABORT and a < sc < b:
                sc = -search(p, d - 1, -b, -a, ply + 1, False)
        p.unmake()
        if ABORT:
            return 0
        if sc > best:
            best, bm = sc, m
        if sc > a:
            a = sc
        if a >= b:
            if not cap:
                if ply < 64 and KILL[ply][0] != m:
                    KILL[ply][1], KILL[ply][0] = KILL[ply][0], m
                HIST[m[0]][m[1]] += d * d
            break
    if not lg:
        return -MATE + ply if chk else 0
    TT[p.h] = (2 if best <= a0 else 1 if best >= b else 0, best, d, bm)
    return best


def pick(f, nb):
    global NODES, LIMIT, ABORT
    NODES = 0
    LIMIT = nb
    ABORT = False
    if len(TT) > 300000:
        TT.clear()
    p = Pos(*pf(f))
    bm = None
    for d in range(1, 40):
        sc = search(p, d, -INF, INF, 0)
        h = TT.get(p.h)
        if not ABORT and h and h[3]:
            bm = h[3]
        if ABORT or sc > MATE - 200:
            break
    return bm if bm else p.legal()

BG = "abcdefgh"


def uc(m):
    return (BG[m[0] & 7] + str((m[0] >> 4) + 1) + BG[m[1] & 7]
            + str((m[1] >> 4) + 1) + ("nbrq"[m[2] - 2] if m[2] else ""))


def post(p, body):
    r = urllib.request.Request(ENV + p, data=json.dumps(body).encode(),
                               headers={"content-type": "application/json"})
    return json.load(urllib.request.urlopen(r))


def main():
    nb = int(os.environ.get("MAKEFUN_NODES", "60000"))
    while True:
        g = post("/game", {})
        if g["status"] == "done":
            break
        while g["status"] == "your_move":
            mv = uc(pick(g["fen"], nb))
            g = post("/move", {"game": g["game"], "move": mv if mv in g["legal_moves"] else g["legal_moves"][0]})
ENV = os.environ.get("MAKEFUN_ENV_URL")
if ENV:
    main()
