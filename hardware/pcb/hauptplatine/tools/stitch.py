#!/usr/bin/env python3
"""GND-Nachbesserung: setzt fuer GND-Pads, die laut DRC nicht an die GND-Flaeche (In1) angebunden sind, eine Via mit kurzer Bahn an freier Stelle.
Aufruf: python3 stitch.py <in.kicad_pcb> <drc.rpt> <out.kicad_pcb>   (Platine muss Zonen gefuellt haben; danach neu fuellen + DRC)"""
import sys, os, re, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('KICAD9_FOOTPRINT_DIR', '/usr/share/kicad/footprints')
import pcbnew
from pcbnew import VECTOR2I, FromMM, ToMM
from shapely.geometry import box, Point, LineString
from shapely.ops import unary_union
from shapely.strtree import STRtree
import layout
OX, OY = 100.0, 100.0
def V(x, y): return VECTOR2I(FromMM(OX + x), FromMM(OY - y))
def P(p): return (ToMM(p.x) - OX, OY - ToMM(p.y))
src, rpt, out = sys.argv[1:4]
b = pcbnew.LoadBoard(src)
LAY = {'F': pcbnew.F_Cu, 'I1': pcbnew.In1_Cu, 'I2': pcbnew.In2_Cu, 'B': pcbnew.B_Cu}
CLR, W, VD, VH = 0.16, 0.15, 0.45, 0.2
obs = {k: [] for k in LAY}
for fp in b.GetFootprints():
    for pad in fp.Pads():
        bb = pad.GetBoundingBox(); g = box(ToMM(bb.GetLeft()) - OX, OY - ToMM(bb.GetBottom()), ToMM(bb.GetRight()) - OX, OY - ToMM(bb.GetTop()))
        if pad.GetNetname() == 'GND':
            continue
        npth = pad.GetAttribute() == pcbnew.PAD_ATTRIB_NPTH
        for k, l in LAY.items():
            if npth or pad.IsOnLayer(l): obs[k].append(g)
    for z in fp.Zones():
        o = z.Outline(); ch = o.Outline(0)
        from shapely.geometry import Polygon
        pg = Polygon([P(ch.CPoint(i)) for i in range(ch.PointCount())])
        for k in LAY: obs[k].append(pg)
for t in b.GetTracks():
    if t.GetNetname() == 'GND': continue
    if t.Type() == pcbnew.PCB_VIA_T:
        g = Point(*P(t.GetPosition())).buffer(ToMM(t.GetWidth(pcbnew.F_Cu)) / 2)
        for k in LAY: obs[k].append(g)
    else:
        g = LineString([P(t.GetStart()), P(t.GetEnd())]).buffer(ToMM(t.GetWidth()) / 2)
        for k, l in LAY.items():
            if t.GetLayer() == l: obs[k].append(g)
EDGE = layout.board_poly().buffer(-0.45)
ANTSKIP = None
union = {k: unary_union(v) for k, v in obs.items()}
want = []
txt = open(rpt).read()
for blk in re.split(r'\n(?=\[)', txt):
    if blk.startswith('[unconnected_items]'):
        for m in re.finditer(r'Pad (\S+) \[GND\] of (\S+) on', blk): want.append((m.group(2), m.group(1)))
want = sorted(set(want)); print('GND-Pads zu verbinden:', len(want))
net = b.FindNet('GND')
done = fail = 0
for ref, num in want:
    fp = b.FindFootprintByReference(ref)
    pads = [p for p in fp.Pads() if p.GetNumber() == num and p.GetNetname() == 'GND']
    if not pads: continue
    pad = pads[0]; c = P(pad.GetPosition())
    side = 'F' if pad.IsOnLayer(pcbnew.F_Cu) and fp.GetLayer() == pcbnew.F_Cu else 'B'
    if pad.GetAttribute() == pcbnew.PAD_ATTRIB_PTH: side = 'F'
    bb = pad.GetBoundingBox(); hw = max(ToMM(bb.GetWidth()), ToMM(bb.GetHeight())) / 2
    ok = False
    for r in (hw + 0.45, hw + 0.6, hw + 0.8, hw + 1.1, hw + 1.5, hw + 2.0):
        for a in range(0, 360, 15):
            q = (c[0] + r * math.cos(math.radians(a)), c[1] + r * math.sin(math.radians(a)))
            vg = Point(*q).buffer(VD / 2 + CLR)
            if not EDGE.contains(Point(*q)): continue
            if any(vg.intersects(union[k]) for k in LAY): continue
            tg = LineString([c, q]).buffer(W / 2 + CLR)
            if tg.intersects(union[side]): continue
            # Bahn darf auch keine GND-fremden Pads der eigenen Seite beruehren -> in union enthalten
            t = pcbnew.PCB_TRACK(b); t.SetStart(V(*c)); t.SetEnd(V(*q)); t.SetWidth(FromMM(W)); t.SetLayer(LAY[side]); t.SetNet(net); b.Add(t)
            v = pcbnew.PCB_VIA(b); v.SetPosition(V(*q)); v.SetWidth(FromMM(VD)); v.SetDrill(FromMM(VH)); v.SetViaType(pcbnew.VIATYPE_THROUGH); v.SetNet(net); b.Add(v)
            for k in LAY:
                pass
            ok = True; break
        if ok: break
    if ok: done += 1
    else: fail += 1; print('kein Platz:', ref, num)
print('gesetzt', done, 'ohne Platz', fail)
pcbnew.SaveBoard(out, b)
