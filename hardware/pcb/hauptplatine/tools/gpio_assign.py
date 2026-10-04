#!/usr/bin/env python3
"""GPIO-Zuordnung S31 nach Platzierung: ordnet jedem Signal (netlist.GPIO_SIGNALS) einen freien IO-Pin zu, der moeglichst nah an den
Zielpads liegt (Hungarian-Verfahren). Schreibt tools/gpio_map.json (Signal -> IOx). Randbedingungen: LP-GPIO IO0-IO7 fuer Weck-/Halte-Signale."""
import os, sys, json, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from scipy.optimize import linear_sum_assignment
import geom as G, netlist
HERE = os.path.dirname(os.path.abspath(__file__))
PARTS = {p['ref']: p for p in netlist.parts()}
pl = json.load(open(os.path.join(HERE, 'placement.json')))
LP = {'IO%d' % i for i in range(8)}
LP_SIG = {'SYS_PWR_EN', 'KEY_LOCK_MCU', 'WHEEL_INT'}
BAD = set(netlist.NO_GPIO)
name2pad = {v: k for k, v in netlist.S31.items() if v.startswith('IO') and v not in BAD}
def padpos(ref, pad):
    p = PARTS[ref]; g = G.fpgeom(p['fp']); st = pl[ref]
    for n, x, y, *_ in g['pads']:
        if str(n) == str(pad): return G.to_view(st, x, y)
    return None
sig_t = {}
for s in netlist.GPIO_SIGNALS:
    pts = []
    for r, p in PARTS.items():
        if r == 'U15': continue
        for pad, net in p['pins'].items():
            if net == s:
                q = padpos(r, pad)
                if q: pts.append(q)
    sig_t[s] = pts
    if not pts: print('WARN kein Ziel fuer', s)
ios = sorted(name2pad)
cost = np.zeros((len(netlist.GPIO_SIGNALS), len(ios)))
for i, s in enumerate(netlist.GPIO_SIGNALS):
    for j, io in enumerate(ios):
        q = padpos('U15', name2pad[io])
        c = sum(math.dist(q, t) for t in sig_t[s]) if sig_t[s] else 0
        if s in LP_SIG and io not in LP: c += 1e4
        if s not in LP_SIG and io in LP: c += 15
        cost[i, j] = c
r, c = linear_sum_assignment(cost)
m = {netlist.GPIO_SIGNALS[i]: ios[j] for i, j in zip(r, c)}
json.dump(m, open(os.path.join(HERE, 'gpio_map.json'), 'w'), indent=1)
print(m, 'Summe', round(cost[r, c].sum(), 1))
