#!/usr/bin/env python3
"""Rev. 3b, Stufe 4: USB-HS-Paar (USB_DP/USB_DN) als gekoppeltes Paar neu verlegen (Review H5).
Auf F.Cu ueber der GND-Flaeche In1: Breite W, Abstand S (Kante-Kante); Hauptstrecke (ca. 71 mm) aus EINER Mittellinie (A* mit Breite 2W+S, Kurvenstrafe,
nur 0/45/90 Grad) per Parallelversatz in zwei Bahnen zerlegt, daher gleich lang (Differenz < 0,1 mm). Fremde F.Cu-Bahnen, die gekreuzt werden, werden
entfernt und danach (auf anderen Lagen) neu verlegt. Einzeln geroutet sind nur Fan-out oben (R102/R103) und Anschluss unten (J6/U5, B.Cu mit Vias).
argv: Eingabe Ausgabe [W] [S]"""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rt, rtedit
import pcbnew
from pcbnew import FromMM, ToMM
from rt import P, V
from shapely.geometry import LineString, Point, box
E = rtedit.Edit(sys.argv[1]); OUT = sys.argv[2]
W = float(sys.argv[3]) if len(sys.argv) > 3 else 0.2
S = float(sys.argv[4]) if len(sys.argv) > 4 else 0.15
PITCH = W + S; WC = 2 * W + S
b, R = E.b, E.R
J6BOX = box(7.4, -42.6, 10.4, -39.9)

# ---- 1) alte USB-Bahnen entfernen; nur die lokalen Verbindungen an den USB-C-Pads (J6 A6/B6 bzw. A7/B7) bleiben
n = 0
for it in list(rt.collect_net(b, 'USB_DP')) + list(rt.collect_net(b, 'USB_DN')):
    if it.kind == 'pad': continue
    if J6BOX.contains(it.geom.centroid) and (it.kind == 'via' or J6BOX.contains(Point(*P(it.obj.GetStart()))) and J6BOX.contains(Point(*P(it.obj.GetEnd())))): continue
    rt.remove_item(b, it.obj); n += 1
print('entfernt:', n); R.refresh()
for net in ('USB_DP', 'USB_DN'): print('  bleibt', net, len([i for i in rt.collect_net(b, net) if i.kind != 'pad']), 'Objekte (lokal an J6)')

# ---- 2) Hauptstrecke
TOP = (2.55, 31.0)
BOT = (5.31, -33.6)
def exact_ok(DP, DN, ignore_nets=()):
    """Exakte Pruefung der beiden Polylinien gegen alle Fremdobjekte auf F.Cu und gegen die Kontur."""
    g1 = LineString(DP).buffer(W / 2, 4); g2 = LineString(DN).buffer(W / 2, 4)
    bad = []
    for it in R.items:
        if it.net in ('USB_DP', 'USB_DN') or 0 not in it.lays or it.kind == 'keepout' and False: continue
        if it.net in ignore_nets: continue
        for nm, gg in (('DP', g1), ('DN', g2)):
            d = it.geom.distance(gg)
            if d < 0.135: bad.append((nm, it.kind, it.net, round(d, 3)))
    return bad

soft = [it for it in R.items if it.kind == 'track' and 0 in it.lays and it.net not in ('USB_DP', 'USB_DN')]
pts = None
for clr in (0.15, 0.18, 0.21, 0.25, 0.3):
    pts = R.center_route('__PAIR__', TOP, BOT, WC, 0, clr=clr, softgeoms=[it.geom for it in soft], avoid=[it.obj for it in soft], res=0.05, turn=14.0, quiet=True)
    if not pts: continue
    cl = LineString(pts)
    left = cl.offset_curve(PITCH / 2, join_style=2, mitre_limit=2.0); right = cl.offset_curve(-PITCH / 2, join_style=2, mitre_limit=2.0)
    if left.geom_type != 'LineString' or right.geom_type != 'LineString': print('  Versatz zerfaellt (clr %.2f)' % clr); continue
    lc, rc = list(left.coords), list(right.coords)
    if lc[0][0] > rc[0][0]: lc, rc = rc, lc
    DP, DN = lc, rc
    if DP[0][1] < DP[-1][1]: DP = DP[::-1]
    if DN[0][1] < DN[-1][1]: DN = DN[::-1]
    # Kreuzungen (weiche Bahnen) zunaechst ausnehmen
    body = cl.buffer(WC / 2 + 0.2)
    crossed = {}
    for it in soft:
        if it.geom.intersects(body): crossed.setdefault(it.net, []).append(it.obj)
    skip = [it.geom for it in soft if it.geom.intersects(body)]
    g1 = LineString(DP).buffer(W / 2, 4); g2 = LineString(DN).buffer(W / 2, 4)
    bad = []
    for it in R.items:
        if it.net in ('USB_DP', 'USB_DN') or 0 not in it.lays: continue
        if it.kind == 'track' and it.obj in sum(crossed.values(), []): continue
        for nm, gg in (('DP', g1), ('DN', g2)):
            d = it.geom.distance(gg)
            if d < 0.135: bad.append((nm, it.kind, it.net, round(d, 3)))
    print('  clr %.2f: Mittellinie %.1f mm, %d Ecken, Verletzungen %d %s' % (clr, cl.length, len(pts), len(bad), bad[:4]))
    if not bad: break
else:
    raise SystemExit('kein sauberer Pfad')
print('Mittellinie:', [(round(x, 1), round(y, 1)) for x, y in pts])
ripped = set()
for net, objs in crossed.items():
    for t in objs: rt.remove_item(b, t)
    ripped.add(net); print('  gekreuzt/entfernt:', net, len(objs), 'Segmente')
R.refresh()
def lenof(c): return sum(math.dist(a, b2) for a, b2 in zip(c[:-1], c[1:]))
print('gekoppelte Strecke: DP %.2f mm, DN %.2f mm (W=%.2f, S=%.2f)' % (lenof(DP), lenof(DN), W, S))
ni = {'USB_DP': b.FindNet('USB_DP'), 'USB_DN': b.FindNet('USB_DN')}
def add_poly(net, c, w=W, lay=pcbnew.F_Cu):
    for a, c2 in zip(c[:-1], c[1:]):
        if math.dist(a, c2) < 1e-6: continue
        t = pcbnew.PCB_TRACK(b); t.SetStart(V(*a)); t.SetEnd(V(*c2)); t.SetWidth(FromMM(w)); t.SetLayer(lay); t.SetNet(ni[net]); b.Add(t)
add_poly('USB_DP', DP); add_poly('USB_DN', DN)
R.refresh()
TRUNK_END = {'USB_DP': DP[-1], 'USB_DN': DN[-1]}

# ---- 3) Fan-out oben: R102.1 -> Anfang DP, R103.1 -> Anfang DN; unten: Anschluss an die J6-Cluster und die U5-Pads
def route_to_point(net, src_items, xy, widths, layers):
    pt = Point(*xy)
    dst = [it for it in R.items if it.net == net and it.kind == 'track' and 0 in it.lays and it.geom.distance(pt) < 0.02]
    for w in widths:
        r = R.route(net, src_items, dst, w=w, layers=layers, allow_vias=len(layers) > 1, margin=3.0, quiet=True, via_cost=8)
        if r: return w
    return None
for net, pad in (('USB_DP', ('R102', '1')), ('USB_DN', ('R103', '1'))):
    cl_ = R.clusters(net); me = [c for c in cl_ if any(it.kind == 'pad' and it.obj == pad for it in c)][0]
    top_pt = (DP if net == 'USB_DP' else DN)[0]
    print('  Fan-out oben', net, route_to_point(net, me, top_pt, (W, 0.15, 0.127), (0,))); R.refresh()
# ESD-Abgriffe an U5 (kurze Stichleitungen) vor dem Anschluss an J6
for net, u5 in (('USB_DP', ('U5', '3')), ('USB_DN', ('U5', '1'))):
    cl_ = R.clusters(net); me = [c for c in cl_ if any(it.kind == 'pad' and it.obj == u5 for it in c)][0]
    print('  ESD-Abgriff', net, route_to_point(net, me, TRUNK_END[net], (0.2, 0.15, 0.127), (0, 2))); R.refresh()
for net, j6 in (('USB_DP', ('J6', 'A6')), ('USB_DN', ('J6', 'A7'))):
    cl_ = R.clusters(net); me = [c for c in cl_ if any(it.kind == 'pad' and it.obj == j6 for it in c)][0]
    print('  J6-Cluster -> Paarende', net, route_to_point(net, me, TRUNK_END[net], (0.2, 0.15, 0.127), (0, 2))); R.refresh()
for net in ('USB_DP', 'USB_DN'):
    left_ = None
    for w in (0.2, 0.15, 0.127):
        left_ = R.connect_all(net, w=w, layers=(0, 2), margin=3.0, via_cost=8)
        if left_ == 0: break
    print('  Rest', net, 'Cluster', left_); R.refresh()
for net in ('USB_DP', 'USB_DN'):
    L = sum(ToMM(t.GetLength()) for t in b.GetTracks() if t.GetNetname() == net and t.Type() != pcbnew.PCB_VIA_T)
    nv = sum(1 for t in b.GetTracks() if t.GetNetname() == net and t.Type() == pcbnew.PCB_VIA_T)
    print(net, 'Gesamtlaenge %.2f mm, %d Vias' % (L, nv))
for net in sorted(ripped):
    left_ = None
    for w in (0.25, 0.127):
        left_ = R.connect_all(net, w=w, layers=(0, 1, 2), margin=8.0)
        if left_ == 0: break
    print('  neu verbunden', net, 'Rest-Cluster', left_); R.refresh()
E.save(OUT)
