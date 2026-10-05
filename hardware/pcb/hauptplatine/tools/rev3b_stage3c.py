#!/usr/bin/env python3
"""Rev. 3b, Stufe 3c: schmale Teilstrecken auf den Hauptwegen der Leistungsnetze gezielt neu verlegen (Review H3).
Je Anschlusspaar wird der Weg mit der geringsten Laenge unterhalb der Zielbreite gesucht, die schmalen Abschnitte entfernt und mit der groessten
moeglichen Breite (Raster-A*, exakte Abstandspruefung) neu verbunden; gelingt das nicht besser als vorher, wird der Zustand wiederhergestellt.
argv: Eingabe Ausgabe"""
import os, sys, math, heapq
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rt, rtedit, widest
import pcbnew
from pcbnew import FromMM, ToMM
from rt import P, V
E = rtedit.Edit(sys.argv[1]); OUT = sys.argv[2]
b, R = E.b, E.R
TARGET = {'SYS_POWER': 0.5, 'VBAT': 0.5, 'VBUS': 0.4, 'VBUS_SW': 0.4, 'V5_HOST': 0.4, 'BOOST_SW': 0.4, '3V3': 0.5}
PAIRS = dict(widest.PAIRS)
PAIRS['3V3'] = [(('U4', '1'), ('U15', '2'))]       # nur die Zuleitung zum Modul
LAYERS = (0, 1, 2)


def best_path(net, p1, p2, target):
    its = rt.collect_net(b, net)
    n = len(its); adj = {i: [] for i in range(n)}
    for i in range(n):
        for j in range(i + 1, n):
            if its[i].lays & its[j].lays and its[i].geom.intersects(its[j].geom): adj[i].append(j); adj[j].append(i)
    def cost(it):
        if it.kind != 'track': return 0.0
        L = ToMM(it.obj.GetLength()); wd = ToMM(it.obj.GetWidth())
        return L * (3.0 if wd < target - 1e-6 else 0.0) + L * 0.001 + 1e-4
    src = [i for i, it in enumerate(its) if it.kind == 'pad' and it.obj == p1]; dst = [i for i, it in enumerate(its) if it.kind == 'pad' and it.obj == p2]
    if not src or not dst: return None, its
    dist = {src[0]: 0}; prev = {}; pq = [(0, src[0])]
    while pq:
        d, i = heapq.heappop(pq)
        if d > dist.get(i, 1e18): continue
        if i == dst[0]: break
        for j in adj[i]:
            nd = d + cost(its[j])
            if nd < dist.get(j, 1e18): dist[j] = nd; prev[j] = i; heapq.heappush(pq, (nd, j))
    if dst[0] not in prev: return None, its
    chain = []; i = dst[0]
    while True:
        chain.append(its[i])
        if i == src[0]: break
        i = prev[i]
    chain.reverse()
    return chain, its


def snapshot(t):
    return (P(t.GetStart()), P(t.GetEnd()), t.GetWidth(), t.GetLayer(), t.GetNetname())


def restore(snaps):
    for a, c, w, l, net in snaps:
        t = pcbnew.PCB_TRACK(b); t.SetStart(V(*a)); t.SetEnd(V(*c)); t.SetWidth(w); t.SetLayer(l); t.SetNet(b.FindNet(net)); b.Add(t)


def snapshot_net(net):
    """Alle Bahnen und Vias des Netzes als Daten (SWIG-Proxies sind nicht stabil, daher keine id()-Vergleiche)."""
    tr, vi = [], []
    for t in b.GetTracks():
        if t.GetNetname() != net: continue
        if t.Type() == pcbnew.PCB_VIA_T: vi.append((P(t.GetPosition()), t.GetWidth(pcbnew.F_Cu), t.GetDrill()))
        else: tr.append(snapshot(t))
    return tr, vi


def restore_net(net, snap):
    for t in [t for t in b.GetTracks() if t.GetNetname() == net]: rt.remove_item(b, t)
    tr, vi = snap
    restore(tr)
    for pos, w, dr in vi:
        v = pcbnew.PCB_VIA(b); v.SetPosition(V(*pos)); v.SetWidth(w); v.SetDrill(dr); v.SetViaType(pcbnew.VIATYPE_THROUGH); v.SetNet(b.FindNet(net)); b.Add(v)


def improve(net, p1, p2):
    tg = TARGET[net]
    chain, its = best_path(net, p1, p2, tg)
    if not chain: return 'kein Weg'
    runs = []; cur = []
    for it in chain:
        if it.kind == 'track' and ToMM(it.obj.GetWidth()) < tg - 1e-6: cur.append(it)
        else:
            if cur: runs.append(cur); cur = []
    if cur: runs.append(cur)
    msgs = []
    for run in runs:
        L = sum(ToMM(i.obj.GetLength()) for i in run)
        wmin = min(ToMM(i.obj.GetWidth()) for i in run)
        if L < 0.3: continue
        snaps = [snapshot(i.obj) for i in run]
        snap = snapshot_net(net)
        for i in run: rt.remove_item(b, i.obj)
        R.refresh()
        got = None
        for w in (tg, 0.45, 0.4, 0.35, 0.3, 0.27):
            if w <= wmin + 1e-6: break
            if w > tg + 1e-9: continue
            n_added = len(list(b.GetTracks()))
            left = R.connect_all(net, w=w, layers=LAYERS, margin=4.0, via_cost=15, clr_steps=(0.0, 0.03), max_exp=int(float(os.environ.get('MAXEXP', '300000'))))
            if left == 0: got = w; break
        if got is None:
            # Wiederherstellen: neu hinzugekommene Bahnen/Vias entfernen, alte zurueck
            restore_net(net, snap); R.refresh()
            msgs.append('Abschnitt %.1f mm (min %.2f) unveraendert' % (L, wmin))
        else:
            R.refresh()
            msgs.append('Abschnitt %.1f mm: %.2f -> %.2f mm' % (L, wmin, got))
    return '; '.join(msgs) if msgs else 'ok (keine schmalen Abschnitte)'


for net in os.environ.get('NETS', 'VBUS_SW,VBUS,VBAT').split(','):
    for p1, p2 in PAIRS.get(net, []):
        print('%-10s %s.%s -> %s.%s: %s' % (net, p1[0], p1[1], p2[0], p2[1], improve(net, p1, p2)), flush=True)
    print('  Reste entfernt (Stummel):', rt.prune_dangling(b, net), flush=True); R.refresh()
    print('  Cluster', net, len(R.clusters(net)), flush=True)
    E.save(OUT)
E.save(OUT)
