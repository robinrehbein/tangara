#!/usr/bin/env python3
"""Engpassbreite (Maximin-Pfad) zwischen Anschlusspaaren der Leistungsnetze: widest.py <pcb>"""
import sys, heapq
sys.path.insert(0, '.')
import rt, pcbnew
from pcbnew import ToMM
PAIRS = {
    'SYS_POWER': [(('U10', '1'), ('U4', '6')), (('U10', '1'), ('U20', '3')), (('U10', '1'), ('U17', '26')), (('U10', '20'), ('R4', '2')), (('U20', '3'), ('L20', '1'))],
    'VBAT': [(('BT1', '3'), ('U10', '14')), (('BT1', '3'), ('U22', '2')), (('U10', '14'), ('C25', '1'))],
    'VBUS': [(('J6', 'A4_B9'), ('Q1', '2')), (('J6', 'A4_B9'), ('U21', '1')), (('J6', 'B4_A9'), ('Q1', '2'))],
    'VBUS_SW': [(('Q1', '3'), ('U10', '2')), (('Q1', '3'), ('U10', '18'))],
    'V5_HOST': [(('U20', '6'), ('U21', '6')), (('U20', '6'), ('C112', '1'))],
    'BOOST_SW': [(('U20', '5'), ('L20', '2'))],
    '3V3': [(('U4', '1'), ('U15', '2')), (('U4', '1'), ('J20', '23')), (('U4', '1'), ('U34', '4')), (('U4', '1'), ('J21', '1'))],
}
def widest(b, net, p1, p2):
    its = rt.collect_net(b, net)
    n = len(its)
    adj = {i: [] for i in range(n)}
    for i in range(n):
        for j in range(i + 1, n):
            if its[i].lays & its[j].lays and its[i].geom.intersects(its[j].geom): adj[i].append(j); adj[j].append(i)
    def w(it): return ToMM(it.obj.GetWidth()) if it.kind == 'track' else 9.9
    src = [i for i, it in enumerate(its) if it.kind == 'pad' and it.obj == p1]
    dst = [i for i, it in enumerate(its) if it.kind == 'pad' and it.obj == p2]
    if not src or not dst: return None
    best = {src[0]: 9.9}; pq = [(-9.9, src[0])]
    while pq:
        d, i = heapq.heappop(pq)
        if -d < best.get(i, 0): continue
        if i == dst[0]: return -d
        for j in adj[i]:
            nd = min(-d, w(its[j]))
            if nd > best.get(j, 0): best[j] = nd; heapq.heappush(pq, (-nd, j))
    return 0.0
if __name__ == '__main__':
    b = rt.load(sys.argv[1])
    for net, pairs in PAIRS.items():
        for p1, p2 in pairs:
            r = widest(b, net, p1, p2)
            print('%-10s %s.%s -> %s.%s: Engpass %s mm' % (net, p1[0], p1[1], p2[0], p2[1], r if r is None else round(r, 3)))
