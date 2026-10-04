#!/usr/bin/env python3
"""Mini-Maze-Router fuer einzelne Restverbindungen: maze.py <in.kicad_pcb> <out.kicad_pcb> NETZ:REF.PAD:REF.PAD ...
Raster 0,05 mm, Lagen F/In2/B, Via-Wechsel, Hindernisse = Kupfer fremder Netze + Abstand. Ziel: Pad B (oder Netz 'GND': beliebiges GND-Pad/Track in der Naehe)."""
import sys, os, math, heapq
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('KICAD9_FOOTPRINT_DIR', '/usr/share/kicad/footprints')
import numpy as np, shapely
from shapely.geometry import box, Point, LineString, Polygon
from shapely.ops import unary_union
import pcbnew
from pcbnew import VECTOR2I, FromMM, ToMM
import layout
OX, OY = 100.0, 100.0
V = lambda x, y: VECTOR2I(FromMM(OX + x), FromMM(OY - y))
P = lambda p: (ToMM(p.x) - OX, OY - ToMM(p.y))
R = 0.05; W = 0.127; CLR = 0.127; VD, VH = 0.45, 0.2
LAYS = [pcbnew.F_Cu, pcbnew.In2_Cu, pcbnew.B_Cu]
b = pcbnew.LoadBoard(sys.argv[1])
EDGE = layout.board_poly().buffer(-0.35)
def items(net):
    obs = [[], [], []]
    for fp in b.GetFootprints():
        for z in fp.Zones():
            ch = z.Outline().Outline(0); pg = Polygon([P(ch.CPoint(i)) for i in range(ch.PointCount())])
            for o in obs: o.append((pg, 0.3))
        for pad in fp.Pads():
            if pad.GetNetname() == net: continue
            bb = pad.GetBoundingBox(); g = box(ToMM(bb.GetLeft()) - OX, OY - ToMM(bb.GetBottom()), ToMM(bb.GetRight()) - OX, OY - ToMM(bb.GetTop()))
            for i, l in enumerate(LAYS):
                if pad.IsOnLayer(l) or pad.GetAttribute() in (pcbnew.PAD_ATTRIB_NPTH, pcbnew.PAD_ATTRIB_PTH): obs[i].append((g, CLR + W / 2))
    for t in b.GetTracks():
        if t.GetNetname() == net: continue
        if t.Type() == pcbnew.PCB_VIA_T:
            g = Point(*P(t.GetPosition())).buffer(ToMM(t.GetWidth(pcbnew.F_Cu)) / 2)
            for o in obs: o.append((g, CLR + W / 2))
        else:
            g = LineString([P(t.GetStart()), P(t.GetEnd())]).buffer(ToMM(t.GetWidth()) / 2)
            for i, l in enumerate(LAYS):
                if t.GetLayer() == l: obs[i].append((g, CLR + W / 2))
    return obs
class _FakePad:
    def __init__(self, x, y): self.x, self.y = x, y
    def GetPosition(self): return V(self.x, self.y)
def padgeom(ref, num):
    if ref.startswith('@'):
        x, y = float(ref[1:]), float(num.split('/')[0]); lay = {'F': 0, 'B': 2, 'I': 1}[num.split('/')[1]]
        return box(x - 0.1, y - 0.1, x + 0.1, y + 0.1), lay, _FakePad(x, y)
    fp = b.FindFootprintByReference(ref)
    for p in fp.Pads():
        if p.GetNumber() == num:
            bb = p.GetBoundingBox()
            lay = 0 if (p.IsOnLayer(pcbnew.F_Cu) and fp.GetLayer() == pcbnew.F_Cu) else 2
            return box(ToMM(bb.GetLeft()) - OX, OY - ToMM(bb.GetBottom()), ToMM(bb.GetRight()) - OX, OY - ToMM(bb.GetTop())), lay, p
def route(net, a, c):
    ga, la, pa = padgeom(*a); gb, lb, pb = padgeom(*c)
    obs = items(net)
    cx0 = min(ga.bounds[0], gb.bounds[0]) - 5; cx1 = max(ga.bounds[2], gb.bounds[2]) + 5
    cy0 = min(ga.bounds[1], gb.bounds[1]) - 5; cy1 = max(ga.bounds[3], gb.bounds[3]) + 5
    nx = int((cx1 - cx0) / R); ny = int((cy1 - cy0) / R)
    xs = cx0 + (np.arange(nx) + 0.5) * R; ys = cy0 + (np.arange(ny) + 0.5) * R
    XX, YY = np.meshgrid(xs, ys, indexing='ij')
    free = []; viafree = np.ones((nx, ny), bool)
    for i in range(3):
        blocked = ~shapely.contains_xy(EDGE, XX, YY)
        for g, d in obs[i]:
            if g.distance(box(cx0, cy0, cx1, cy1)) > 0.5: continue
            blocked |= shapely.contains_xy(g.buffer(d, 4), XX, YY)
        free.append(~blocked)
        vb = ~shapely.contains_xy(EDGE.buffer(-0.1), XX, YY)
        for g, d in obs[i]:
            if g.distance(box(cx0, cy0, cx1, cy1)) > 0.5: continue
            vb |= shapely.contains_xy(g.buffer(d + (VD - W) / 2, 4), XX, YY)
        viafree &= ~vb
    sa = shapely.contains_xy(ga.buffer(0.0), XX, YY); sb = shapely.contains_xy(gb.buffer(0.0), XX, YY)
    for i in range(3):
        if i == la: free[i] |= sa
        if i == lb: free[i] |= sb
    free[la] |= shapely.contains_xy(ga, XX, YY) & True
    start = [(i0, j0) for i0, j0 in zip(*np.nonzero(sa))]
    goal = sb
    dist = {}; pq = []
    for s in start:
        dist[(la,) + s] = 0; heapq.heappush(pq, (0, (la,) + s, None))
    prev = {}
    end = None
    while pq:
        d, n, pv = heapq.heappop(pq)
        if n in prev: continue
        prev[n] = pv
        l, i, j = n
        if l == lb and goal[i, j]: end = n; break
        for di, dj, cst in ((1,0,1),(-1,0,1),(0,1,1),(0,-1,1),(1,1,1.41),(1,-1,1.41),(-1,1,1.41),(-1,-1,1.41)):
            ni, nj = i + di, j + dj
            if 0 <= ni < nx and 0 <= nj < ny and free[l][ni, nj]:
                nn = (l, ni, nj); nd = d + cst
                if nd < dist.get(nn, 1e18): dist[nn] = nd; heapq.heappush(pq, (nd, nn, n))
        if viafree[i, j]:
            for l2 in range(3):
                if l2 != l and free[l2][i, j]:
                    nn = (l2, i, j); nd = d + 25
                    if nd < dist.get(nn, 1e18): dist[nn] = nd; heapq.heappush(pq, (nd, nn, n))
    if end is None: print('KEIN WEG', net, a, c); return False
    path = []; n = end
    while n is not None: path.append(n); n = prev[n]
    path.reverse()
    netinfo = b.FindNet(net)
    pts = [(l, float(xs[i]), float(ys[j])) for l, i, j in path]
    # Segmente je Lage, Vias bei Lagenwechsel
    seg = [pts[0]]
    def flush(seg):
        if len(seg) < 2: return
        # Geraden zusammenfassen
        out = [seg[0]]
        for k in range(1, len(seg) - 1):
            a0, a1, a2 = out[-1], seg[k], seg[k + 1]
            if abs((a1[1]-a0[1])*(a2[2]-a1[2]) - (a1[2]-a0[2])*(a2[1]-a1[1])) > 1e-9: out.append(a1)
        out.append(seg[-1])
        for p, q in zip(out[:-1], out[1:]):
            t = pcbnew.PCB_TRACK(b); t.SetStart(V(p[1], p[2])); t.SetEnd(V(q[1], q[2])); t.SetWidth(FromMM(W)); t.SetLayer(LAYS[p[0]]); t.SetNet(netinfo); b.Add(t)
    for p in pts[1:]:
        if p[0] != seg[-1][0]:
            flush(seg)
            v = pcbnew.PCB_VIA(b); v.SetPosition(V(p[1], p[2])); v.SetWidth(FromMM(VD)); v.SetDrill(FromMM(VH)); v.SetViaType(pcbnew.VIATYPE_THROUGH); v.SetNet(netinfo); b.Add(v)
            seg = [p]
        else: seg.append(p)
    flush(seg)
    ca = P(pa.GetPosition()); cb = P(pb.GetPosition())
    for (lay, pt, ctr) in ((pts[0][0], pts[0], ca), (pts[-1][0], pts[-1], cb)):
        if math.dist((pt[1], pt[2]), ctr) > 1e-3:
            t = pcbnew.PCB_TRACK(b); t.SetStart(V(pt[1], pt[2])); t.SetEnd(V(*ctr)); t.SetWidth(FromMM(W)); t.SetLayer(LAYS[lay]); t.SetNet(netinfo); b.Add(t)
    print('geroutet', net, a, c, 'Punkte', len(pts)); return True
ok = True
for spec in sys.argv[3:]:
    net, a, c = spec.split(':')
    def sp(t):
        if t.startswith('@'):
            q = t.split(';'); return (q[0], q[1] + '/' + q[2])
        return tuple(t.split('.', 1))
    ok &= route(net, sp(a), sp(c))
pcbnew.SaveBoard(sys.argv[2], b)
