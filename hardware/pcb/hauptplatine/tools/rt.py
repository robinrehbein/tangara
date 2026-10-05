#!/usr/bin/env python3
"""Routing-Bibliothek fuer die Review-Korrekturen (Rev. 3b): Raster-A*-Router mit beliebiger Leiterbahnbreite, Netz-Cluster,
Entfernen/Verbinden von Pads, Pruefung per kicad-cli. Ergaenzt maze.py (das nur 0,127 mm breite Einzelverbindungen zieht).

Koordinaten wie netlist.py: Mitte (0,0), x rechts, y oben (Blick auf die Oberseite). Routbare Lagen: F.Cu (0), In2 (1), B.Cu (2); In1 ist die GND-Flaeche.
"""
import os, sys, math, heapq, subprocess, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('KICAD9_FOOTPRINT_DIR', '/usr/share/kicad/footprints')
os.environ.setdefault('KICAD9_SYMBOL_DIR', '/usr/share/kicad/symbols')
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage
from shapely.geometry import box, Point, LineString, Polygon
from shapely.ops import unary_union
import pcbnew
from pcbnew import VECTOR2I, FromMM, ToMM
import layout

OX, OY = 100.0, 100.0
V = lambda x, y: VECTOR2I(FromMM(OX + x), FromMM(OY - y))
P = lambda p: (ToMM(p.x) - OX, OY - ToMM(p.y))
LAYS = [pcbnew.F_Cu, pcbnew.In2_Cu, pcbnew.B_Cu]
LIDX = {pcbnew.F_Cu: 0, pcbnew.In2_Cu: 1, pcbnew.B_Cu: 2}
RES = 0.05
CLR = 0.15            # Planungsabstand (DRC-Minimum 0,127)
EDGE_CLR = 0.32       # Kupfer-Kante (DRC 0,3)
VD, VH = 0.45, 0.2


def load(path):
    return pcbnew.LoadBoard(path)


# ---------------------------------------------------------------------------------------------- Bestand
class Item:
    __slots__ = ('net', 'lays', 'geom', 'kind', 'obj')
    def __init__(self, net, lays, geom, kind, obj=None):
        self.net, self.lays, self.geom, self.kind, self.obj = net, lays, geom, kind, obj


def pad_geom(pad):
    bb = pad.GetBoundingBox()
    return box(ToMM(bb.GetLeft()) - OX, OY - ToMM(bb.GetBottom()), ToMM(bb.GetRight()) - OX, OY - ToMM(bb.GetTop()))


def collect(b):
    """Alle Kupferobjekte als Item (Netzname, Lagenindizes, shapely-Geometrie)."""
    items = []
    for fp in b.GetFootprints():
        for pad in fp.Pads():
            lays = set()
            for l in LAYS:
                if pad.IsOnLayer(l): lays.add(LIDX[l])
            if pad.GetAttribute() in (pcbnew.PAD_ATTRIB_PTH,): lays = {0, 1, 2}
            if pad.GetAttribute() == pcbnew.PAD_ATTRIB_NPTH:
                lays = {0, 1, 2}
            if not lays: continue
            net = pad.GetNetname() if pad.GetAttribute() != pcbnew.PAD_ATTRIB_NPTH else None
            g = pad_geom(pad)
            if fp.GetReference().startswith('FID'): g = g.buffer(0.5)     # Passermarke: 0,6 mm Freiraum (Regel pad clearance)
            items.append(Item(net, lays, g, 'pad', (fp.GetReference(), pad.GetNumber())))
    for t in b.GetTracks():
        if t.Type() == pcbnew.PCB_VIA_T:
            items.append(Item(t.GetNetname(), {0, 1, 2}, Point(*P(t.GetPosition())).buffer(ToMM(t.GetWidth(pcbnew.F_Cu)) / 2, 8), 'via', t))
        else:
            if t.GetLayer() not in LIDX: continue
            a, c = P(t.GetStart()), P(t.GetEnd())
            items.append(Item(t.GetNetname(), {LIDX[t.GetLayer()]}, LineString([a, c]).buffer(ToMM(t.GetWidth()) / 2, 4), 'track', t))
    for z in b.Zones():
        if z.GetIsRuleArea():
            ch = z.Outline().Outline(0)
            g = Polygon([P(ch.CPoint(i)) for i in range(ch.PointCount())])
            lays = {LIDX[l] for l in LAYS if z.IsOnLayer(l)}
            items.append(Item(None, lays, g, 'keepout', z))
    return items


def board_free_poly(w):
    """Zulaessiger Bereich fuer die Mittellinie einer Bahn der Breite w."""
    return layout.board_poly().buffer(-(EDGE_CLR + w / 2))


# ---------------------------------------------------------------------------------------------- Raster
class Grid:
    def __init__(self, bounds, res=RES):
        self.res = res
        self.x0, self.y0 = bounds[0], bounds[1]
        self.W = int(math.ceil((bounds[2] - bounds[0]) / res)); self.H = int(math.ceil((bounds[3] - bounds[1]) / res))
    def px(self, x): return (x - self.x0) / self.res
    def py(self, y): return (y - self.y0) / self.res
    def xy(self, i, j): return (float(self.x0 + (i + 0.5) * self.res), float(self.y0 + (j + 0.5) * self.res))
    def cell(self, x, y): return (int((x - self.x0) / self.res), int((y - self.y0) / self.res))
    def draw(self, geom, arr):
        """Zeichnet eine shapely-Geometrie in ein bool-Array [j, i]."""
        if geom.is_empty: return
        gs = list(geom.geoms) if hasattr(geom, 'geoms') else [geom]
        img = Image.fromarray(arr.astype(np.uint8) * 255)
        d = ImageDraw.Draw(img)
        for g in gs:
            if g.geom_type != 'Polygon': continue
            d.polygon([(self.px(x) - 0.5, self.py(y) - 0.5) for x, y in g.exterior.coords], fill=255)
            for r in g.interiors:
                d.polygon([(self.px(x) - 0.5, self.py(y) - 0.5) for x, y in r.coords], fill=0)
        arr[:] = np.asarray(img) > 0
    def mask(self, geoms):
        arr = np.zeros((self.H, self.W), bool)
        img = Image.new('L', (self.W, self.H), 0); d = ImageDraw.Draw(img)
        for geom in geoms:
            if geom.is_empty: continue
            gs = list(geom.geoms) if hasattr(geom, 'geoms') else [geom]
            for g in gs:
                if g.geom_type != 'Polygon': continue
                d.polygon([(self.px(x) - 0.5, self.py(y) - 0.5) for x, y in g.exterior.coords], fill=255)
                for r in g.interiors:
                    d.polygon([(self.px(x) - 0.5, self.py(y) - 0.5) for x, y in r.coords], fill=0)
        return np.asarray(img) > 0


class Router:
    def __init__(self, b, items=None):
        self.b = b
        self.items = items if items is not None else collect(b)

    def refresh(self):
        self.items = collect(self.b)

    # ---------------------------------------------------------------- Cluster
    def clusters(self, net, ignore=()):
        its = [it for it in self.items if it.net == net and it.kind != 'keepout' and it.obj not in ignore]
        n = len(its); par = list(range(n))
        def f(x):
            while par[x] != x: par[x] = par[par[x]]; x = par[x]
            return x
        for i in range(n):
            for j in range(i + 1, n):
                if its[i].lays & its[j].lays and its[i].geom.intersects(its[j].geom):
                    par[f(i)] = f(j)
        cl = {}
        for i in range(n): cl.setdefault(f(i), []).append(its[i])
        return list(cl.values())

    # ---------------------------------------------------------------- Routen
    def _route_once(self, net, src, dst, w=0.127, layers=(0, 2), via_cost=30.0, lay_w=(1.0, 1.3, 1.0), margin=4.0, clr=CLR, vd=VD,
              avoid=(), allow_vias=True, extra_obst=(), bounds=None, window_free=None, commit=True, quiet=False, region=None, soft=None, soft_cost=12.0, turn_pen=0.0, max_exp=None):
        """src/dst: Liste von Item (Quelle/Ziel-Kupfer). Gibt Pfad [(lage, x, y)] zurueck und schreibt Bahnen/Vias (commit)."""
        sg = unary_union([it.geom for it in src]); dg = unary_union([it.geom for it in dst])
        if bounds is None:
            bx = [sg.bounds, dg.bounds]
            bounds = (min(a[0] for a in bx) - margin, min(a[1] for a in bx) - margin, max(a[2] for a in bx) + margin, max(a[3] for a in bx) + margin)
            bb = layout.board_poly().bounds
            bounds = (max(bounds[0], bb[0]), max(bounds[1], bb[1]), min(bounds[2], bb[2]), min(bounds[3], bb[3]))
        g = Grid(bounds)
        W, H = g.W, g.H
        raw = [np.zeros((H, W), bool) for _ in range(3)]
        rawall = np.zeros((H, W), bool)
        win = box(*bounds).buffer(2.0)
        # Hindernisse (andere Netze) je Lage
        per = [[], [], []]; perall = []
        for it in self.items:
            if it.net == net and it.kind != 'keepout': continue
            if it.obj in avoid: continue
            if not it.geom.intersects(win): continue
            for l in it.lays: per[l].append(it.geom)
            perall.append(it.geom)
        for g2 in extra_obst:
            for l in range(3): per[l].append(g2)
            perall.append(g2)
        for l in range(3): raw[l] = g.mask(per[l])
        rawall = g.mask(perall)
        r_track = (clr + w / 2) / g.res; r_via = (clr + vd / 2) / g.res
        inside_edge = g.mask([board_free_poly(w) if region is None else region.buffer(-w / 2)])
        free = []
        for l in range(3):
            if l not in layers: free.append(np.zeros((H, W), bool)); continue
            d = ndimage.distance_transform_edt(~raw[l])
            free.append((d >= r_track - 0.5) & inside_edge)
        dall = ndimage.distance_transform_edt(~rawall)
        viaok = (dall >= r_via - 0.5) & g.mask([layout.board_poly().buffer(-(EDGE_CLR + vd / 2))])
        # Quellen/Ziele je Lage
        smask = [np.zeros((H, W), bool) for _ in range(3)]; dmask = [np.zeros((H, W), bool) for _ in range(3)]
        for it in src:
            m = g.mask([it.geom])
            for l in it.lays:
                if l in layers: smask[l] |= m
        for it in dst:
            m = g.mask([it.geom])
            for l in it.lays:
                if l in layers: dmask[l] |= m
        for l in layers:
            free[l] |= smask[l] | dmask[l]
        softc = [np.zeros((H, W), np.float32) for _ in range(3)]
        if soft:
            for l, geoms in soft.items():
                m = g.mask([x.buffer(clr + w / 2) for x in geoms if x.intersects(win)])
                softc[l][m] = soft_cost
        # Ziel-Heuristik: Abstand zur naechsten Ziel-Zelle (egal welche Lage)
        anyd = dmask[0] | dmask[1] | dmask[2]
        if not anyd.any():
            if not quiet: print('  Ziel ausserhalb des Fensters / nicht auf erlaubter Lage', net)
            return None
        hdist = ndimage.distance_transform_edt(~anyd)
        # A*
        INF = 1e18
        N = 3 * H * W
        dist = np.full(N, INF, np.float64)
        prev = np.full(N, -1, np.int64)
        pq = []
        flatsoft = [f.ravel() for f in softc]; flatfree = [f.ravel() for f in free]; flatd = [m.ravel() for m in dmask]; flath = hdist.ravel(); flatvia = viaok.ravel()
        for l in layers:
            for idx in np.flatnonzero(smask[l].ravel()):
                n = l * H * W + idx; dist[n] = 0; heapq.heappush(pq, (flath[idx], n))
        end = -1
        HW = H * W
        nbr = ((1, 0, 1.0), (-1, 0, 1.0), (0, 1, 1.0), (0, -1, 1.0), (1, 1, 1.4142), (1, -1, 1.4142), (-1, 1, 1.4142), (-1, -1, 1.4142))
        done = np.zeros(N, bool)
        lw = lay_w
        nexp = 0
        while pq:
            f, n = heapq.heappop(pq)
            if done[n]: continue
            done[n] = True
            nexp += 1
            if max_exp and nexp > max_exp: break
            l = n // HW; idx = n - l * HW
            if flatd[l][idx]: end = n; break
            j = idx // W; i = idx - j * W
            d0 = dist[n]
            for di, dj, c in nbr:
                ni, nj = i + di, j + dj
                if 0 <= ni < W and 0 <= nj < H:
                    ii = nj * W + ni
                    if flatfree[l][ii]:
                        m = l * HW + ii; nd = d0 + c * lw[l] + flatsoft[l][ii]
                        if nd < dist[m]:
                            dist[m] = nd; prev[m] = n; heapq.heappush(pq, (nd + flath[ii], m))
            if allow_vias and flatvia[idx]:
                for l2 in layers:
                    if l2 != l and flatfree[l2][idx]:
                        m = l2 * HW + idx; nd = d0 + via_cost
                        if nd < dist[m]:
                            dist[m] = nd; prev[m] = n; heapq.heappush(pq, (nd + flath[idx], m))
        if end < 0:
            if not quiet: print('  KEIN WEG', net)
            return None
        path = []; n = end
        while n >= 0:
            l = n // HW; idx = n - l * HW; j = idx // W; i = idx - j * W
            x, y = g.xy(i, j); path.append((l, x, y)); n = prev[n]
        path.reverse()
        path = self._clean(path)
        return path

    def route(self, net, src, dst, w=0.127, clr=CLR, vd=VD, commit=True, quiet=False, clr_steps=(0.0, 0.03, 0.06, 0.1, 0.15), **kw):
        """Wie _route_once, prueft das Ergebnis exakt (shapely) gegen den Bestand und wiederholt mit groesserem Planungsabstand."""
        for extra in clr_steps:
            p = self._route_once(net, src, dst, w=w, clr=clr + extra, vd=vd, quiet=True, **kw)
            if p is None:
                continue
            p = self._anchor(p, src, dst)
            for eps in (0.06, 0.04, 0.02):
                q = self._simplify(p, eps)
                if len(q) < len(p) and not self.check_path(net, q, w, vd):
                    p = q; break
            bad = self.check_path(net, p, w, vd)
            if not bad:
                if commit: self.write(net, p, w, vd)
                return p
        if not quiet: print('  KEIN (sauberer) WEG', net, 'w=%.3f' % w)
        return None

    def check_path(self, net, path, w, vd=VD, need=0.131, hole=0.351):
        """Gibt Liste der Verletzungen zurueck (leer = ok)."""
        geoms = []
        for p, q in zip(path[:-1], path[1:]):
            if p[0] == q[0] and math.dist(p[1:], q[1:]) > 1e-9:
                geoms.append(({p[0]}, LineString([p[1:], q[1:]]).buffer(w / 2, 4), 'track'))
        for p, q in zip(path[:-1], path[1:]):
            if p[0] != q[0]: geoms.append(({0, 1, 2}, Point(p[1], p[2]).buffer(vd / 2, 8), 'via'))
        if not geoms: return []
        edge = layout.board_poly().boundary
        bad = []
        for lays, g, kind in geoms:
            if g.distance(edge) < EDGE_CLR - 0.01 + (0.0): bad.append(('edge', kind)); continue
            gb = g.buffer(0.45)
            for it in self.items:
                if it.net == net and it.kind != 'keepout': continue
                if not (it.lays & lays): continue
                if not it.geom.intersects(gb): continue
                d = it.geom.distance(g)
                if kind == 'via' and it.kind == 'via':
                    pass
                if d < need - 1e-6: bad.append((it.kind, it.net, round(d, 3)))
                elif kind == 'via' and d < hole - 0.2 + 0.2 - 1e-6 and False: pass
        return bad

    @staticmethod
    def _simplify(path, eps):
        """Douglas-Peucker je Lagenabschnitt (Via-Positionen bleiben); Treppenstufen des Rasters verschwinden."""
        runs = []; cur = [path[0]]
        for p in path[1:]:
            if p[0] != cur[-1][0]:
                runs.append(cur); cur = [p]
            else: cur.append(p)
        runs.append(cur)
        out = []
        for r in runs:
            if len(r) > 2:
                ls = LineString([(p[1], p[2]) for p in r]).simplify(eps, preserve_topology=False)
                r = [(r[0][0], x, y) for x, y in ls.coords]
            out.extend(r)
        return out

    @staticmethod
    def _anchor_point(pt, items):
        """Naechster Punkt im Kupfer (Pad-Mitte, Bahn-Mittellinie, Via-Mitte) der Items zu pt."""
        best = None
        for it in items:
            if it.kind == 'pad':
                c = it.geom.centroid
                q = (c.x, c.y)
                # bei grossen Pads naechster Punkt statt Mitte, wenn pt schon im Pad liegt
                if it.geom.contains(Point(*pt)) and it.geom.area > 4.0: q = pt
            elif it.kind == 'via':
                c = it.geom.centroid; q = (c.x, c.y)
            elif it.kind == 'track':
                t = it.obj; a, c2 = P(t.GetStart()), P(t.GetEnd())
                ls = LineString([a, c2]); pr = ls.project(Point(*pt)); q = ls.interpolate(pr).coords[0]
            else: continue
            d = math.dist(pt, q)
            if best is None or d < best[0]: best = (d, q)
        return best[1] if best else pt

    def _anchor(self, path, src, dst):
        a = self._anchor_point(path[0][1:], src); c = self._anchor_point(path[-1][1:], dst)
        path = list(path)
        if math.dist(a, path[0][1:]) > 1e-6: path.insert(0, (path[0][0], a[0], a[1]))
        if math.dist(c, path[-1][1:]) > 1e-6: path.append((path[-1][0], c[0], c[1]))
        return path

    @staticmethod
    def _clean(path):
        """Kollineare Punkte zusammenfassen; Lagenwechsel bleiben als Punktpaare gleicher Position erhalten."""
        out = [path[0]]
        for k in range(1, len(path) - 1):
            a, c, d = out[-1], path[k], path[k + 1]
            if a[0] == c[0] == d[0]:
                if abs((c[1] - a[1]) * (d[2] - c[2]) - (c[2] - a[2]) * (d[1] - c[1])) < 1e-9: continue
            out.append(c)
        out.append(path[-1])
        return out

    def write(self, net, path, w, vd=VD):
        ni = self.b.FindNet(net)
        seg = [path[0]]
        def flush(seg):
            for p, q in zip(seg[:-1], seg[1:]):
                if math.dist(p[1:], q[1:]) < 1e-6: continue
                t = pcbnew.PCB_TRACK(self.b); t.SetStart(V(p[1], p[2])); t.SetEnd(V(q[1], q[2])); t.SetWidth(FromMM(w)); t.SetLayer(LAYS[p[0]]); t.SetNet(ni); self.b.Add(t)
        for p in path[1:]:
            if p[0] != seg[-1][0]:
                flush(seg)
                v = pcbnew.PCB_VIA(self.b); v.SetPosition(V(p[1], p[2])); v.SetWidth(FromMM(vd)); v.SetDrill(FromMM(VH)); v.SetViaType(pcbnew.VIATYPE_THROUGH); v.SetNet(ni); self.b.Add(v)
                seg = [p]
            else: seg.append(p)
        flush(seg)

    # ---------------------------------------------------------------- Pad-/Netzbearbeitung
    def pad(self, ref, num):
        for it in self.items:
            if it.kind == 'pad' and it.obj == (ref, str(num)): return it
        raise KeyError((ref, num))

    def connect_pad_to_net(self, net, ref, num, **kw):
        """Verbindet das Pad (bzw. dessen Cluster) mit dem naechsten anderen Cluster desselben Netzes."""
        cl = self.clusters(net)
        me = [c for c in cl if any(it.kind == 'pad' and it.obj == (ref, str(num)) for it in c)]
        if not me: raise KeyError((ref, num))
        others = [it for c in cl if c is not me[0] for it in c]
        if not others: return None
        p = self.route(net, me[0], others, **kw)
        if p: self.refresh()
        return p

    def connect_xy(self, net, xy, **kw):
        """Wie connect_pad_to_net, aber das Pad/Via/Bahnstueck wird ueber eine Koordinate gewaehlt (Pads mit gleicher Nummer, z. B. MP)."""
        cl = self.clusters(net)
        pt = Point(*xy)
        me = [c for c in cl if any(it.geom.contains(pt) or it.geom.distance(pt) < 1e-6 for it in c)]
        if not me: raise KeyError(xy)
        others = [it for c in cl if c is not me[0] for it in c]
        if not others: return None
        p = self.route(net, me[0], others, **kw)
        if p: self.refresh()
        return p

    def connect_all(self, net, **kw):
        """Verbindet alle Cluster des Netzes (kleinster zuerst zum Rest). Gibt Zahl der verbleibenden Cluster zurueck."""
        for _ in range(60):
            cl = self.clusters(net)
            if len(cl) <= 1: return 0
            cl.sort(key=lambda c: sum(it.geom.area for it in c))
            ok = False
            for c in cl[:3]:
                others = [it for c2 in cl if c2 is not c for it in c2]
                p = self.route(net, c, others, **kw)
                if p: ok = True; self.refresh(); break
            if not ok: return len(cl)
        return len(self.clusters(net))


# ---------------------------------------------------------------------------------------------- Netz-/Pad-Umbau
GRAVE = []
def remove_item(b, t):
    GRAVE.append(t)
    b.Remove(t)


def tracks_of(b, net):
    return [t for t in b.GetTracks() if t.GetNetname() == net]


def touches_pad(t, pad_xy, tol=0.0):
    """Endpunkt von t im Pad-Rechteck?"""
    pass


def collect_net(b, net):
    """Wie collect, aber nur Pads/Bahnen/Vias eines Netzes (schnell)."""
    items = []
    for fp in b.GetFootprints():
        for pad in fp.Pads():
            if pad.GetNetname() != net: continue
            lays = {LIDX[l] for l in LAYS if pad.IsOnLayer(l)}
            if pad.GetAttribute() == pcbnew.PAD_ATTRIB_PTH: lays = {0, 1, 2}
            if lays: items.append(Item(net, lays, pad_geom(pad), 'pad', (fp.GetReference(), pad.GetNumber())))
    for t in b.GetTracks():
        if t.GetNetname() != net: continue
        if t.Type() == pcbnew.PCB_VIA_T:
            items.append(Item(net, {0, 1, 2}, Point(*P(t.GetPosition())).buffer(ToMM(t.GetWidth(pcbnew.F_Cu)) / 2, 8), 'via', t))
        elif t.GetLayer() in LIDX:
            items.append(Item(net, {LIDX[t.GetLayer()]}, LineString([P(t.GetStart()), P(t.GetEnd())]).buffer(ToMM(t.GetWidth()) / 2, 4), 'track', t))
    return items


def prune_dangling(b, net):
    """Entfernt Bahnstuecke (ein Ende ohne Kontakt) und Vias (Kontakt auf < 2 Lagen) eines Netzes, bis nichts mehr uebrig ist. Nicht fuer GND (Flaeche)."""
    if net == 'GND': return 0
    its = collect_net(b, net)
    removed = 0
    while True:
        changed = False
        for it in list(its):
            if it.kind == 'pad': continue
            others = [o for o in its if o is not it and (o.lays & it.lays) and o.geom.intersects(it.geom)]
            if it.kind == 'track':
                t = it.obj; bad = False
                for e in (P(t.GetStart()), P(t.GetEnd())):
                    pt = Point(*e).buffer(1e-3)
                    if not any(o.geom.intersects(pt) for o in others): bad = True
                if bad:
                    remove_item(b, t); its.remove(it); removed += 1; changed = True
            else:
                lcnt = sum(1 for l in (0, 1, 2) if any(l in o.lays and o.kind != 'via' for o in others))
                if lcnt < 2:
                    remove_item(b, it.obj); its.remove(it); removed += 1; changed = True
        if not changed: break
    return removed


def run_drc(path, out, parity=True):
    args = ['kicad-cli', 'pcb', 'drc', '--severity-all', '-o', out, path]
    if parity: args.insert(5, '--schematic-parity')
    r = subprocess.run(args, capture_output=True, text=True)
    t = open(out).read()
    kinds = {}
    for m in re.finditer(r'^\[(\w+)\]', t, re.M): kinds[m.group(1)] = kinds.get(m.group(1), 0) + 1
    return kinds, t


def drc_items(txt):
    """Liefert Liste (art, text, [(x,y)...]) aus dem DRC-Bericht (Koordinaten im Brett-System: Mitte 0,0)."""
    out = []
    blocks = re.split(r'\n(?=\[)', txt)
    for bl in blocks:
        m = re.match(r'\[(\w+)\]: ([^\n]*)', bl)
        if not m: continue
        pts = [(float(a) - OX, OY - float(c)) for a, c in re.findall(r'@\(([-\d.]+) mm, ([-\d.]+) mm\)', bl)]
        out.append((m.group(1), m.group(2), pts, bl))
    return out


# ---------------------------------------------------------------------------------------------- Platzsuche
def courtyard_geoms(b, side_layer):
    out = []
    for fp in b.GetFootprints():
        try:
            cy = fp.GetCourtyard(side_layer)
        except Exception:
            continue
        if cy is None or cy.OutlineCount() == 0: continue
        ch = cy.Outline(0)
        out.append(Polygon([P(ch.GetPoint(i)) for i in range(ch.PointCount())]))
    return out


def find_spot(b, side, w, h, near, items=None, margin=0.3, res=0.1, search=12.0, keep_fn=None, nbest=5, extra_block=()):
    """Sucht freie Plaetze fuer ein Rechteck w x h (mm, Pads + Rand) auf Seite 'T'/'B' (Bauteilseite) in der Naehe von 'near'.
    Gibt Liste [(x, y, abstand)] zurueck, naechste zuerst. Blockiert: Kupfer anderer Objekte auf der Seite, Vias, Durchsteckpads, Kontur, Courtyards, Sperrzonen."""
    items = items or collect(b)
    l = 0 if side == 'T' else 2
    lay = pcbnew.F_Cu if side == 'T' else pcbnew.B_Cu
    bounds = (near[0] - search - w, near[1] - search - h, near[0] + search + w, near[1] + search + h)
    bb = layout.board_poly().bounds
    bounds = (max(bounds[0], bb[0]), max(bounds[1], bb[1]), min(bounds[2], bb[2]), min(bounds[3], bb[3]))
    g = Grid(bounds, res)
    geoms = [it.geom for it in items if (l in it.lays) and it.kind != 'keepout' or (it.kind == 'keepout' and l in it.lays)]
    geoms += courtyard_geoms(b, lay)
    geoms += list(extra_block)
    blocked = g.mask(geoms)
    d = ndimage.distance_transform_edt(~blocked) * res
    free_pt = (d >= margin)
    outside = ~g.mask([layout.board_poly().buffer(-0.8)])
    free_pt &= ~outside
    # Rechteck frei <=> alle Zellen frei: Summentabelle
    S = np.zeros((g.H + 1, g.W + 1), np.int64)
    S[1:, 1:] = np.cumsum(np.cumsum((~free_pt).astype(np.int64), 0), 1)
    wi, hi = int(math.ceil(w / res)), int(math.ceil(h / res))
    res_list = []
    for j in range(0, g.H - hi):
        for i in range(0, g.W - wi):
            if S[j + hi, i + wi] - S[j, i + wi] - S[j + hi, i] + S[j, i] == 0:
                cx, cy = g.x0 + (i + wi / 2) * res, g.y0 + (j + hi / 2) * res
                res_list.append((cx, cy, math.hypot(cx - near[0], cy - near[1])))
    res_list.sort(key=lambda r: r[2])
    return res_list[:nbest * 50:1][:nbest]


def _center_route(self, net, s_xy, q_xy, w, layer, clr=CLR, res=0.1, turn=6.0, soft_cost=25.0, softgeoms=(), avoid=(), bounds=None, quiet=False, diag_only45=True):
    """Einlagige Wegsuche fuer eine breite Mittellinie (gekoppeltes Paar): 8 Richtungen, Kurvenstrafe, optional 'weiche' Hindernisse
    (Bahnen anderer Netze, die gekreuzt werden duerfen; Kosten soft_cost je Zelle). Gibt Polylinie [(x, y)] zurueck (nur 0/45/90 Grad)."""
    bb = layout.board_poly().bounds if bounds is None else bounds
    g = Grid(bb, res)
    W, H = g.W, g.H
    per = []
    soft_set = set(id(o) for o in avoid)
    for it in self.items:
        if it.net == net and it.kind != 'keepout': continue
        if layer not in it.lays: continue
        if it.obj is not None and id(it.obj) in soft_set: continue
        per.append(it.geom)
    raw = g.mask(per)
    d = ndimage.distance_transform_edt(~raw) * res
    free = (d >= clr + w / 2 - res / 2) & g.mask([board_free_poly(w)])
    softc = np.zeros((H, W), np.float32)
    if softgeoms:
        softc[g.mask([x.buffer(clr + w / 2) for x in softgeoms])] = soft_cost
    si, sj = g.cell(*s_xy); qi, qj = g.cell(*q_xy)
    free[max(sj - 2, 0):sj + 3, max(si - 2, 0):si + 3] = True
    free[max(qj - 2, 0):qj + 3, max(qi - 2, 0):qi + 3] = True
    dirs = [(1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1)]
    cst = [1.0, 1.4142, 1.0, 1.4142, 1.0, 1.4142, 1.0, 1.4142]
    INF = 1e18
    N = H * W * 8
    dist = np.full(N, INF, np.float64); prev = np.full(N, -1, np.int64); done = np.zeros(N, bool)
    ff = free.ravel(); fs = softc.ravel()
    gi, gj = np.meshgrid(np.arange(W), np.arange(H))
    hh = (np.hypot(gi - qi, gj - qj)).ravel()
    pq = []
    s0 = sj * W + si
    for k in range(8):
        dist[s0 * 8 + k] = 0; heapq.heappush(pq, (hh[s0], s0 * 8 + k))
    end = -1
    while pq:
        f, n = heapq.heappop(pq)
        if done[n]: continue
        done[n] = True
        idx, k = divmod(n, 8)
        j, i = divmod(idx, W)
        if abs(i - qi) <= 1 and abs(j - qj) <= 1: end = n; break
        d0 = dist[n]
        for k2 in ((k - 1) % 8, k, (k + 1) % 8, (k - 2) % 8, (k + 2) % 8):
            di, dj = dirs[k2]; ni, nj = i + di, j + dj
            if not (0 <= ni < W and 0 <= nj < H): continue
            ii = nj * W + ni
            if not ff[ii]: continue
            turnc = 0.0 if k2 == k else (turn if k2 in ((k - 1) % 8, (k + 1) % 8) else turn * 2.5)
            nd = d0 + cst[k2] + turnc + fs[ii]
            m = ii * 8 + k2
            if nd < dist[m]: dist[m] = nd; prev[m] = n; heapq.heappush(pq, (nd + hh[ii], m))
    if end < 0:
        if not quiet: print('  KEIN WEG (Mittellinie)')
        return None
    pts = []; n = end
    while n >= 0:
        idx, k = divmod(n, 8); j, i = divmod(idx, W); x, y = g.xy(i, j); pts.append((x, y, k)); n = prev[n]
    pts.reverse()
    # Richtungsaenderungen -> Eckpunkte
    out = [pts[0][:2]]
    for a, c in zip(pts[1:-1], pts[2:]):
        if c[2] != a[2]: out.append(a[:2])
    out.append(pts[-1][:2])
    out[0] = tuple(s_xy); out[-1] = tuple(q_xy)
    return out


Router.center_route = _center_route
