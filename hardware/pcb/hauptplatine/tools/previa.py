"""GND-Vorverdrahtung: setzt vor dem Routing an jedes GND-Pad eine (gesperrte) Via mit kurzer Bahn zur GND-Flaeche In1.
Der Autorouter nutzt die GND-Flaeche nicht selbst (Freerouting 1.9.0 legt keine Plane-Vias an), deshalb wird das hier geskriptet."""
import math
import pcbnew
from pcbnew import VECTOR2I, FromMM, ToMM
from shapely.geometry import box, Point, LineString, Polygon
from shapely.ops import unary_union

def previa(b, OX=100.0, OY=100.0, edge_poly=None, via_d=0.45, via_h=0.2, w=0.15, clr=0.16, lock=True):
    V = lambda x, y: VECTOR2I(FromMM(OX + x), FromMM(OY - y))
    P = lambda p: (ToMM(p.x) - OX, OY - ToMM(p.y))
    LAY = {'F': pcbnew.F_Cu, 'B': pcbnew.B_Cu}
    obs = {'F': [], 'B': []}      # Hindernisse je Seite (Pads fremder Netze, Vias)
    allv = []
    for fp in b.GetFootprints():
        for z in fp.Zones():
            ch = z.Outline().Outline(0); pg = Polygon([P(ch.CPoint(i)) for i in range(ch.PointCount())])
            for k in obs: obs[k].append(pg)
    net = b.FindNet('GND')
    pads = []
    U = {}
    for fp in b.GetFootprints():
        for pad in fp.Pads():
            bb = pad.GetBoundingBox(); g = box(ToMM(bb.GetLeft()) - OX, OY - ToMM(bb.GetBottom()), ToMM(bb.GetRight()) - OX, OY - ToMM(bb.GetTop()))
            if pad.GetNetname() == 'GND' and pad.GetAttribute() == pcbnew.PAD_ATTRIB_SMD:
                pads.append((fp, pad, g)); continue
            npth = pad.GetAttribute() == pcbnew.PAD_ATTRIB_NPTH
            for k, l in LAY.items():
                if npth or pad.IsOnLayer(l): obs[k].append(g)
    U = {k: unary_union(v) for k, v in obs.items()}
    placed = []
    n = 0; fail = []
    for fp, pad, g in pads:
        side = 'F' if pad.IsOnLayer(pcbnew.F_Cu) else 'B'
        c = P(pad.GetPosition()); cc = P(fp.GetPosition())
        bb = pad.GetBoundingBox(); wpad = ToMM(bb.GetWidth()); hpad = ToMM(bb.GetHeight())
        cands = []
        if min(wpad, hpad) > 1.8:      # grosse Pads (Exposed Pad): Vias im Pad
            for dx in (-0.9, 0.0, 0.9):
                for dy in (-0.9, 0.0, 0.9):
                    if abs(dx) < wpad / 2 - 0.3 and abs(dy) < hpad / 2 - 0.3: cands.append(((c[0] + dx, c[1] + dy), 0))
        else:
            out = math.atan2(c[1] - cc[1], c[0] - cc[0])
            hw = max(wpad, hpad) / 2
            for r in (hw + 0.45, hw + 0.6, hw + 0.8, hw + 1.1):
                for da in (0, 20, -20, 40, -40, 60, -60, 90, -90, 120, -120, 150, -150, 180):
                    a = out + math.radians(da)
                    cands.append(((c[0] + r * math.cos(a), c[1] + r * math.sin(a)), 1))
        ok = False
        for q, tr in cands:
            pt = Point(*q)
            if edge_poly is not None and not edge_poly.contains(pt): continue
            vg = pt.buffer(via_d / 2 + clr)
            if any(vg.intersects(U[k]) for k in U): continue
            if any(math.dist(q, pv) < via_d + 0.2 for pv in placed): continue
            if tr:
                tg = LineString([c, q]).buffer(w / 2 + clr)
                if tg.intersects(U[side]): continue
                t = pcbnew.PCB_TRACK(b); t.SetStart(V(*c)); t.SetEnd(V(*q)); t.SetWidth(FromMM(w)); t.SetLayer(LAY[side]); t.SetNet(net); t.SetLocked(lock); b.Add(t)
            v = pcbnew.PCB_VIA(b); v.SetPosition(V(*q)); v.SetWidth(FromMM(via_d)); v.SetDrill(FromMM(via_h)); v.SetViaType(pcbnew.VIATYPE_THROUGH); v.SetNet(net); v.SetLocked(lock); b.Add(v)
            placed.append(q)
            vc = Point(*q).buffer(via_d / 2)
            for k in U: U[k] = U[k].union(vc)
            if tr: U[side] = U[side].union(LineString([c, q]).buffer(w / 2))
            ok = True
            if not tr: n += 1; continue    # EP: mehrere Vias
            break
        if ok: n += 1 if not cands or cands[0][1] else 0
        elif not ok: fail.append(fp.GetReference() + '.' + pad.GetNumber())
    print('GND-Vorverdrahtung: Pads', len(pads), 'Vias', len(placed), 'ohne Platz', fail)
