#!/usr/bin/env python3
"""Eigener Gitter-Router (A*, 2 Lagen) für das Klickrad-Modul. Freerouting kam mit den dicht liegenden Pads nicht zum Ziel.
Eingabe: <pre.kicad_pcb> (platziert, ohne Leiterbahnen) -> Ausgabe: <routed.kicad_pcb>.
Aufruf: route.py pre.kicad_pcb routed.kicad_pcb
Regeln: Bahn 0,15 mm (Strom und LRA 0,2), Abstand 0,15 mm, Via 0,6/0,3. B.Cu überall, F.Cu nur im Innenkreis zwischen Taste und Rad."""
import sys, math, heapq, itertools
import numpy as np
import pcbnew
from pcbnew import FromMM, ToMM, VECTOR2I
from shapely.geometry import Point, Polygon, box, LineString
from shapely.ops import unary_union
from PIL import Image, ImageDraw
from scipy import ndimage

OX = OY = 100.0
RES = 0.05            # Rastermaß mm
HALF = 16.0
N = int(2 * HALF / RES)
CLR = 0.13
VIA_D, VIA_DR = 0.6, 0.3
WIDTH = {'GND': 0.2, '3V3': 0.2, 'LRA_P': 0.2, 'LRA_N': 0.2}
DEFW = 0.15
GND_RING = (3.3, 5.5)     # GND-Fläche auf F.Cu (Zone, in finish.py)
F_RMIN, F_RMAX = 2.5 + 0.15, 6.3 - 0.15
import os
ORDER = ['3V3', 'SDA', 'K2', 'KB', 'KG', 'K1', 'K0', 'E0', 'E1', 'E2', 'EB', 'EG', 'SCL', 'CHANGE', 'EN', 'REG', 'RESET', 'LRA_P', 'LRA_N', 'GND']
if os.environ.get('ORDER'): ORDER = os.environ['ORDER'].split(',')

def bpt(p): return (ToMM(p.x) - OX, OY - ToMM(p.y))
def cell(x, y): return (int(round((x + HALF) / RES)), int(round((HALF - y) / RES)))   # (col,row), Zeile 0 = oben
def xy(c, r): return (c * RES - HALF, HALF - r * RES)

board = pcbnew.LoadBoard(sys.argv[1])
BCU, FCU = pcbnew.B_Cu, pcbnew.F_Cu
objs = {0: [], 1: []}      # Lage -> Liste (Netz, shapely-Geometrie) Kupfer
terms = {}                 # Netz -> Liste von Terminals (Lage, (x,y), Geometrie)
holes = []
for fp in board.GetFootprints():
    for p in fp.Pads():
        net = p.GetNetname()
        if p.GetAttribute() == pcbnew.PAD_ATTRIB_NPTH:
            holes.append(Point(*bpt(p.GetPosition())).buffer(ToMM(p.GetDrillSize().x) / 2 + 0.25)); continue
        bb = p.GetBoundingBox(); g = box(*[ToMM(v) for v in (bb.GetLeft(), bb.GetTop(), bb.GetRight(), bb.GetBottom())])
        g = box(ToMM(bb.GetLeft()) - OX, OY - ToMM(bb.GetBottom()), ToMM(bb.GetRight()) - OX, OY - ToMM(bb.GetTop()))
        if p.IsOnLayer(FCU) and fp.GetLayer() == FCU:      # Touch-Flächen: echte Form über Effective Polygon
            poly = p.GetEffectivePolygon(FCU)
            pts = [bpt(poly.CVertex(i)) for i in range(poly.FullPointCount())] if poly.OutlineCount() else None
            if pts: g = Polygon(pts).buffer(0)
            objs[1].append((net, g)); continue
        if p.IsOnLayer(BCU):
            objs[0].append((net, g))
            if net: terms.setdefault(net, []).append((0, bpt(p.GetPosition()), g, f'{fp.GetReference()}.{p.GetNumber()}'))
for t in board.GetTracks():
    if t.Type() == pcbnew.PCB_VIA_T:
        c = bpt(t.GetPosition()); g = Point(*c).buffer(ToMM(t.GetWidth(BCU)) / 2)
        for l in (0, 1): objs[l].append((t.GetNetname(), g))
        terms.setdefault(t.GetNetname(), []).append((0, c, g, 'via'))
fixedgeo = {}
for t in board.GetTracks():
    if t.Type() == pcbnew.PCB_VIA_T: continue
    a, b2, w_ = bpt(t.GetStart()), bpt(t.GetEnd()), ToMM(t.GetWidth())
    fixedgeo.setdefault(t.GetNetname(), []).append((0 if t.GetLayer() == BCU else 1, LineString([a, b2]).buffer(w_ / 2), w_))
edge = Point(0, 0).buffer(HALF * 2).difference(Point(0, 0).buffer(15.7))
ring_f = Point(0, 0).buffer(HALF * 2).difference(Point(0, 0).buffer(F_RMAX).difference(Point(0, 0).buffer(F_RMIN)))

for n_, lst_ in fixedgeo.items():
    for la_, g_, w_ in lst_:
        objs[la_].append((n_, g_))
        terms.setdefault(n_, [])
def raster(geoms):
    out = np.zeros((N, N), dtype=bool)
    for g in geoms:
        for pg in (g.geoms if hasattr(g, 'geoms') else [g]):
            if pg.is_empty or pg.geom_type != 'Polygon': continue
            im = Image.new('1', (N, N), 0); d = ImageDraw.Draw(im)
            d.polygon([((x + HALF) / RES, (HALF - y) / RES) for x, y in pg.exterior.coords], fill=1)
            for ring in pg.interiors:
                d.polygon([((x + HALF) / RES, (HALF - y) / RES) for x, y in ring.coords], fill=0)
            out |= np.array(im, dtype=bool)
    return out

routed = []   # (Netz, Lage, Geometrie, Breite)

def blocked(net, w):
    """Maske unzulässiger Rasterpunkte (Leiterbahnmitte) je Lage für Netz `net`, Bahnbreite w."""
    m = []
    for l in (0, 1):
        gs = [g.buffer(CLR + w / 2 + 0.02) for n, g in objs[l] if n != net or not n]
        gs += [g.buffer(CLR + w / 2 + 0.02) for n, la, g, ww in routed if la == l and n != net]
        gs += [h.buffer(w / 2) for h in holes]
        gs.append(edge.buffer(w / 2))
        if l == 1: gs.append(ring_f)
        m.append(raster(gs))
    return m

def viablocked(net):
    m = []
    for l in (0, 1):
        gs = [g.buffer(CLR + VIA_D / 2 + 0.02) for n, g in objs[l] if n != net or not n]
        gs += [g.buffer(CLR + VIA_D / 2 + 0.02) for n, la, g, ww in routed if la == l and n != net]
        gs += [h.buffer(VIA_D / 2) for h in holes]
        gs.append(edge.buffer(VIA_D / 2))
        if l == 1: gs.append(ring_f)
        m.append(raster(gs))
    return m[0] | m[1]

SOFT = 25
DIRS = [(1, 0, 1.0), (-1, 0, 1.0), (0, 1, 1.0), (0, -1, 1.0), (1, 1, 1.4142), (1, -1, 1.4142), (-1, 1, 1.4142), (-1, -1, 1.4142)]
def astar(starts, goals, blk, vblk, soft=None, allow_via=True):
    """starts/goals: Mengen (lage, c, r). Liefert Pfad als Liste von (lage, c, r)."""
    goalset = set(goals)
    gc = np.array([[c, r] for l, c, r in goals]); cx, cy = gc.mean(axis=0)
    def h(c, r): return 1.0 * max(abs(c - cx), abs(r - cy)) * 0.9
    pq = []; best = {}; prev = {}
    cnt = itertools.count()
    for s in starts:
        best[s] = 0; heapq.heappush(pq, (h(s[1], s[2]), next(cnt), 0, s)); prev[s] = None
    VIA_COST = 12
    while pq:
        f, _, g, cur = heapq.heappop(pq)
        if g > best.get(cur, 1e18): continue
        if cur in goalset:
            path = []; s = cur
            while s: path.append(s); s = prev[s]
            return path[::-1]
        l, c, r = cur
        for dc, dr, cost in DIRS:
            nc, nr = c + dc, r + dr
            if not (0 <= nc < N and 0 <= nr < N): continue
            if blk[l][nr, nc] and (l, nc, nr) not in goalset: continue
            if dc and dr and (blk[l][r, nc] or blk[l][nr, c]) and (l, nc, nr) not in goalset: continue
            ng = g + cost + (SOFT if (soft is not None and soft[l][nr, nc]) else 0)
            ns = (l, nc, nr)
            if ng < best.get(ns, 1e18):
                best[ns] = ng; prev[ns] = cur; heapq.heappush(pq, (ng + h(nc, nr), next(cnt), ng, ns))
        if allow_via and not vblk[r, c]:
            ns = (1 - l, c, r)
            if not blk[1 - l][r, c]:
                ng = g + VIA_COST
                if ng < best.get(ns, 1e18):
                    best[ns] = ng; prev[ns] = cur; heapq.heappush(pq, (ng + h(c, r), next(cnt), ng, ns))
    return None

def cells_of(geom, layer, shrink=0.0):
    g = geom.buffer(-shrink) if shrink else geom
    if g.is_empty: g = geom
    minx, miny, maxx, maxy = g.bounds
    out = set()
    c0, r1 = cell(minx, miny); c1, r0 = cell(maxx, maxy)
    for c in range(c0, c1 + 1):
        for r in range(r0, r1 + 1):
            if g.contains(Point(*xy(c, r))): out.add((layer, c, r))
    return out

def simplify(path):
    pts = [(l, ) + xy(c, r) for l, c, r in path]
    segs = []; cur = [pts[0]]
    for a, b in zip(pts[:-1], pts[1:]):
        if a[0] != b[0]:
            segs.append(('via', a)); 
            if len(cur) > 1: segs.append(('trk', cur))
            cur = [b]
        else:
            cur.append(b)
    if len(cur) > 1: segs.append(('trk', cur))
    out = []
    for kind, data in segs:
        if kind == 'via': out.append(('via', data[1], data[2])); continue
        # kollineare Punkte entfernen
        keep = [data[0]]
        for i in range(1, len(data) - 1):
            a, b, c = keep[-1], data[i], data[i + 1]
            if abs((b[1] - a[1]) * (c[2] - b[2]) - (b[2] - a[2]) * (c[1] - b[1])) > 1e-6: keep.append(b)
        keep.append(data[-1]); out.append(('trk', keep))
    return out

items = {}   # Netz -> Liste PCB-Objekte
geo = {}     # Netz -> Liste (Lage, Geometrie, Breite)

def add_track(net, layer, pts, w):
    nt = board.FindNet(net)
    for a, b in zip(pts[:-1], pts[1:]):
        t = pcbnew.PCB_TRACK(board); t.SetStart(VECTOR2I(FromMM(OX + a[0]), FromMM(OY - a[1]))); t.SetEnd(VECTOR2I(FromMM(OX + b[0]), FromMM(OY - b[1])))
        t.SetWidth(FromMM(w)); t.SetLayer(BCU if layer == 0 else FCU); t.SetNet(nt); board.Add(t); items.setdefault(net, []).append(t)
    geo.setdefault(net, []).append((layer, LineString([(p[0], p[1]) for p in pts]).buffer(w / 2), w))

def add_via(net, x, y):
    v = pcbnew.PCB_VIA(board); v.SetPosition(VECTOR2I(FromMM(OX + x), FromMM(OY - y))); v.SetWidth(FromMM(VIA_D)); v.SetDrill(FromMM(VIA_DR))
    v.SetViaType(pcbnew.VIATYPE_THROUGH); v.SetNet(board.FindNet(net)); board.Add(v); items.setdefault(net, []).append(v)
    g = Point(x, y).buffer(VIA_D / 2)
    geo.setdefault(net, []).append((0, g, VIA_D)); geo.setdefault(net, []).append((1, g, VIA_D))

def rip(net):
    for it in items.pop(net, []): board.Remove(it)
    geo.pop(net, None)

def masks(net, w):
    """hart: feste Hindernisse + verlegte Vias; weich: verlegte Leiterbahnen anderer Netze."""
    hard, via_h, soft = [], [], []
    for l in (0, 1):
        fixed = [g.buffer(CLR + w / 2 + 0.02) for n, g in objs[l] if n != net or not n]
        fixed += [h.buffer(w / 2) for h in holes] + [edge.buffer(w / 2)]
        if l == 1: fixed.append(ring_f)
        vias = [g.buffer(CLR + w / 2 + 0.02) for n, lst in geo.items() if n != net for la, g, ww in lst if la == l and ww == VIA_D]
        trk = [g.buffer(CLR + w / 2 + 0.02) for n, lst in geo.items() if n != net for la, g, ww in lst if la == l and ww != VIA_D]
        hard.append(raster(fixed + vias)); soft.append(raster(trk))
        vf = [g.buffer(CLR + VIA_D / 2 + 0.02) for n, g in objs[l] if n != net or not n] + [h.buffer(VIA_D / 2) for h in holes] + [edge.buffer(VIA_D / 2)]
        if l == 1: vf.append(ring_f)
        vf += [g.buffer(CLR + VIA_D / 2 + 0.02) for n, lst in geo.items() if n != net for la, g, ww in lst if la == l]
        via_h.append(raster(vf))
    return hard, via_h[0] | via_h[1], soft

def route_net(net, allow_soft):
    """Verlegt alle Terminals von `net`. Rückgabe: (fehlende Terminals, gekreuzte Netze)."""
    rip(net)
    ts = list(terms.get(net, []))
    if len(ts) < 2: return [], set()
    w = WIDTH.get(net, DEFW)
    hard, vblk, soft = masks(net, w)
    blk = [hard[l] | soft[l] for l in (0, 1)]
    def tcells(t):
        c = cells_of(t[2], t[0], 0.05) or {(t[0],) + cell(*t[1])}
        if t[3] == 'via': c |= cells_of(t[2], 1, 0.05)
        return c
    tree = tcells(ts[0]); rest = ts[1:]; missing = []; crossed = set()
    if net == 'GND':    # GND-Ring auf F.Cu (Kupferfläche zwischen Taste und Rad) als Anschlussfläche, nur Zellen ohne fremdes Kupfer
        rg = Point(0, 0).buffer(GND_RING[1]).difference(Point(0, 0).buffer(GND_RING[0]))
        rc = {c_ for c_ in cells_of(rg, 1, 0.0) if not (hard[1] | soft[1])[c_[2], c_[1]]}
        tree |= rc
    for la_, g_, w_ in fixedgeo.get(net, []): tree |= cells_of(g_, la_)
    for t_ in list(rest):
        if tcells(t_) & tree: rest.remove(t_); tree |= tcells(t_)
    while rest:
        cx = np.mean([c for l, c, r in tree]); cy = np.mean([r for l, c, r in tree])
        rest.sort(key=lambda t: (cell(*t[1])[0] - cx) ** 2 + (cell(*t[1])[1] - cy) ** 2)
        t = rest.pop(0)
        starts = tcells(t)
        path = astar(starts, tree, blk, vblk)
        if not path and allow_soft:
            path = astar(starts, tree, hard, vblk, soft=soft)
            if path:
                for l, c, r in path:
                    for n, lst in geo.items():
                        if n == net: continue
                        if any(la == l and g.buffer(CLR + w / 2).contains(Point(*xy(c, r))) and ww != VIA_D for la, g, ww in lst): crossed.add(n)
        if not path: missing.append(t[3]); continue
        for kind, *data in simplify(path):
            if kind == 'trk': add_track(net, data[0][0][0], [(p[1], p[2]) for p in data[0]], w)
        for a, b in zip(path[:-1], path[1:]):
            if a[0] != b[0]: add_via(net, *xy(a[1], a[2]))
        for cc in path: tree.add(cc)
        if crossed: break
    return missing, crossed

stubfail = []
def gnd_stubs():
    global stubfail
    # ---- GND-Stummel: jedes GND-Pad bekommt eine kurze Leiterbahn (ca. 1,7 mm), die das GND-Gitter (B.Cu) kreuzt und so sicher anbindet
    stubfail[:] = []
    hard, vblk, soft = masks('GND', DEFW)
    blkg = [hard[l] | soft[l] for l in (0, 1)]
    for t in terms.get('GND', []):
        if t[3] == 'via': continue
        sc = cell(*t[1]); starts = cells_of(t[2], 0, 0.05) or {(0,) + sc}
        goals = set()
        for r_ in range(int(1.6 / RES), int(1.8 / RES)):
            for ang in range(0, 360, 2):
                c = sc[0] + int(round(r_ * math.cos(math.radians(ang)))); rr = sc[1] + int(round(r_ * math.sin(math.radians(ang))))
                if 0 <= c < N and 0 <= rr < N and not blkg[0][rr, c]: goals.add((0, c, rr))
        path = astar(starts, goals, blkg, vblk, allow_via=False) if goals else None
        if not path:
            stubfail.append(t[3]); print('STUMMEL fehlt', t[3]); continue
        for kind, *data in simplify(path):
            if kind == 'trk': add_track('GND', 0, [(p[1], p[2]) for p in data[0]], DEFW)
        blkg = [(hard[l] | raster([g.buffer(CLR + DEFW / 2 + 0.02) for n, lst in geo.items() if n != 'GND' for la, g, ww in lst if la == l])) for l in (0, 1)]

queue = list(ORDER); failed = {}; guard = 0; rips = {}
while queue and guard < 120:
    guard += 1
    net = queue.pop(0)
    miss, crossed = route_net(net, allow_soft=False)
    if miss:
        rip(net)
        miss, crossed = route_net(net, allow_soft=True)
        if crossed and any(rips.get(n, 0) >= 3 for n in crossed):
            rip(net); miss = ['Kreuzung nicht lösbar']; crossed = set()
        if crossed:
            for n in crossed: rips[n] = rips.get(n, 0) + 1
            # gekreuzte Netze entfernen, dieses Netz endgültig verlegen, dann die entfernten wieder anstellen
            for n in crossed: rip(n)
            miss, crossed2 = route_net(net, allow_soft=False)
            for n in crossed:
                if n not in queue: queue.insert(0, n)
    if miss:
        failed[net] = miss
        print('FEHLT', net, miss, flush=True)
    else:
        failed.pop(net, None)
    print('Netz', net, 'fertig' if not miss else 'unvollständig', 'Warteschlange', queue, flush=True)
fl = [(n, m) for n, ms in failed.items() for m in ms]
for n, m in fl: print('FEHLT', n, m)
board.Save(sys.argv[2])
print('fehlende Verbindungen:', len(fl), fl)
pass
