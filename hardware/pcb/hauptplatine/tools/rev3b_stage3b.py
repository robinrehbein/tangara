#!/usr/bin/env python3
"""Rev. 3b, Stufe 3b: Bahnen der Leistungsnetze segmentweise verbreitern, soweit Platz ist (exakte Abstandspruefung gegen den Bestand, Review H3).
argv: Eingabe Ausgabe."""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rt, rtedit
import pcbnew
from pcbnew import FromMM, ToMM
from rt import P
from shapely.geometry import LineString, Point
from shapely.strtree import STRtree
E = rtedit.Edit(sys.argv[1]); OUT = sys.argv[2]
b, R = E.b, E.R
TARGET = {'BOOST_SW': 0.5, 'SYS_POWER': 0.5, 'VBAT': 0.5, 'VBUS': 0.4, 'VBUS_SW': 0.4, 'V5_HOST': 0.4}
STEPS = (0.6, 0.5, 0.45, 0.4, 0.35, 0.3, 0.27)
NEED = 0.131
EDGE = rt.layout.board_poly().boundary


def stats(net):
    d = {}
    for t in b.GetTracks():
        if t.GetNetname() == net and t.Type() != pcbnew.PCB_VIA_T:
            k = (t.GetLayerName(), round(ToMM(t.GetWidth()), 3)); d[k] = d.get(k, 0) + ToMM(t.GetLength())
    return {k: round(v, 1) for k, v in sorted(d.items())}


def trunk_segments(net, p1, p2):
    """Bahnstuecke auf dem kuerzesten Kupferweg zwischen zwei Pads eines Netzes (Dijkstra ueber Item-Kontakte)."""
    import heapq
    its = rt.collect_net(b, net)
    idx = {id(it): i for i, it in enumerate(its)}
    src = [i for i, it in enumerate(its) if it.kind == 'pad' and it.obj == p1]
    dst = [i for i, it in enumerate(its) if it.kind == 'pad' and it.obj == p2]
    if not src or not dst: return []
    adj = {i: [] for i in range(len(its))}
    for i in range(len(its)):
        for j in range(i + 1, len(its)):
            if its[i].lays & its[j].lays and its[i].geom.intersects(its[j].geom): adj[i].append(j); adj[j].append(i)
    def wt(it): return ToMM(it.obj.GetLength()) if it.kind == 'track' else 0.0
    dist = {src[0]: 0}; prev = {}; pq = [(0, src[0])]
    while pq:
        d, i = heapq.heappop(pq)
        if d > dist.get(i, 1e18): continue
        if i == dst[0]: break
        for j in adj[i]:
            nd = d + wt(its[j]) + 0.001
            if nd < dist.get(j, 1e18): dist[j] = nd; prev[j] = i; heapq.heappush(pq, (nd, j))
    if dst[0] not in prev and dst[0] != src[0]: return []
    out = []; i = dst[0]
    while i in prev:
        if its[i].kind == 'track': out.append(its[i].obj)
        i = prev[i]
    return out


def widen_list(net, segs, target):
    R.refresh()
    others = [it for it in R.items if it.net != net]
    trees = {}
    for l in (0, 1, 2):
        g = [it.geom for it in others if l in it.lays]
        trees[l] = (STRtree(g), g)
    n = 0
    for t in sorted(segs, key=lambda t: -t.GetLength()):
        if t.GetLayer() not in rt.LIDX: continue
        l = rt.LIDX[t.GetLayer()]; cur = ToMM(t.GetWidth()); a, c = P(t.GetStart()), P(t.GetEnd())
        for w in STEPS:
            if w > target + 1e-9 or w <= cur + 1e-9: continue
            g = LineString([a, c]).buffer(w / 2, 4)
            if g.distance(EDGE) < 0.31: continue
            tree, geoms = trees[l]
            if all(geoms[i].distance(g) >= NEED for i in tree.query(g.buffer(NEED + 0.01))):
                t.SetWidth(FromMM(w)); n += 1; break
    return n


def widen(net, target):
    R.refresh()
    others = [it for it in R.items if it.net != net and it.kind != 'keepout' or it.kind == 'keepout']
    trees = {}
    for l in (0, 1, 2):
        g = [it.geom for it in others if l in it.lays]
        trees[l] = (STRtree(g), g)
    n = 0
    segs = [t for t in b.GetTracks() if t.GetNetname() == net and t.Type() != pcbnew.PCB_VIA_T and t.GetLayer() in rt.LIDX]
    segs.sort(key=lambda t: -t.GetLength())
    for t in segs:
        l = rt.LIDX[t.GetLayer()]
        cur = ToMM(t.GetWidth())
        a, c = P(t.GetStart()), P(t.GetEnd())
        for w in STEPS:
            if w > target + 1e-9 or w <= cur + 1e-9: continue
            g = LineString([a, c]).buffer(w / 2, 4)
            if g.distance(EDGE) < 0.31: continue
            tree, geoms = trees[l]
            ok = True
            for i in tree.query(g.buffer(NEED + 0.01)):
                if geoms[i].distance(g) < NEED: ok = False; break
            if ok:
                t.SetWidth(FromMM(w)); n += 1; break
    return n


for net in TARGET: print('vorher', net, stats(net))
for net, tg in TARGET.items():
    print(net, 'verbreitert:', widen(net, tg))
# 3V3-Zuleitung vom LDO U4 (Pin 1) zum Modul (U15 Pin 2): Hauptweg verbreitern
tr = trunk_segments('3V3', ('U4', '1'), ('U15', '2'))
print('3V3-Hauptweg U4.1 -> U15.2:', len(tr), 'Segmente, Laenge %.1f mm' % sum(ToMM(t.GetLength()) for t in tr))
print('3V3 Hauptweg verbreitert:', widen_list('3V3', tr, 0.5))
tr = trunk_segments('3V3', ('U4', '1'), ('U15', '2'))
print('3V3-Hauptweg nachher (Breiten):', sorted({round(ToMM(t.GetWidth()), 3) for t in tr}), 'min', min(ToMM(t.GetWidth()) for t in tr) if tr else None)
E.save(OUT)
for net in TARGET: print('nachher', net, stats(net))
