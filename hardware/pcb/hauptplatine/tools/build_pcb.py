#!/usr/bin/env python3
"""Erzeugt hauptplatine.kicad_pcb.

Koordinaten wie in netlist.py: Mitte = (0,0), x rechts, y oben, Blick von der Display-Seite (Oberseite).
MODE=place   -> Platzierung (tools/placement.json) + Umriss + Netze (ohne Leiterbahnen) nach $TMPDIR_PCB/pre.kicad_pcb
MODE=finish  -> laedt $LOADFROM (Platzierung + Routing), fuegt Zonen, Beschriftung, Keepouts hinzu und speichert hauptplatine.kicad_pcb
"""
import math, os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('KICAD9_FOOTPRINT_DIR', '/usr/share/kicad/footprints')
import pcbnew
from pcbnew import VECTOR2I, FromMM, ToMM
import netlist, layout
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OX, OY = 100.0, 100.0
FPDIR = '/usr/share/kicad/footprints/'
def V(x, y): return VECTOR2I(FromMM(OX + x), FromMM(OY - y))
def P(p): return (ToMM(p.x) - OX, OY - ToMM(p.y))

MODE = os.environ.get('MODE', 'place')
TMP = os.environ.get('TMPDIR_PCB', '/tmp/hp')
os.makedirs(TMP, exist_ok=True)
board = pcbnew.LoadBoard(os.environ['LOADFROM']) if MODE == 'finish' else pcbnew.BOARD()
F_CU, B_CU, IN1, IN2 = pcbnew.F_Cu, pcbnew.B_Cu, pcbnew.In1_Cu, pcbnew.In2_Cu
if MODE != 'finish':
    board.SetCopperLayerCount(4)
    board.SetLayerType(pcbnew.In1_Cu, pcbnew.LT_POWER)
    ds = board.GetDesignSettings()
    ds.SetBoardThickness(FromMM(layout.BOARD_T))
nets = {}
if MODE == 'finish':
    for name, n in board.GetNetsByName().items(): nets[str(name)] = n
def net(name):
    if name not in nets:
        n = pcbnew.NETINFO_ITEM(board, name); board.Add(n); nets[name] = n
    return nets[name]

def loadfp(spec):
    lib, name = spec.split(':')
    path = os.path.join(ROOT, 'lib', 'Hauptplatine.pretty') if lib == 'Hauptplatine' else FPDIR + lib + '.pretty'
    fp = pcbnew.FootprintLoad(path, name)
    if fp is None: raise SystemExit('Footprint fehlt: ' + spec)
    fp.SetFPID(pcbnew.LIB_ID(lib, name))
    return fp

def rot(a, b, deg):
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    return a * c - b * s, a * s + b * c

placed = {}
NC = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'nc_nets.json')))
def place(part, x, y, theta, side):
    """theta: Drehung der Ansicht (CCW, Blick von oben). Unterseite: Bauteil wird erst gespiegelt (Blick von unten wie Oberseite), dann gedreht."""
    fp = loadfp(part['fp'])
    fp.SetReference(part['ref']); fp.SetValue(part['value'])
    for g in list(fp.GraphicalItems()):
        if g.GetLayer() == pcbnew.Edge_Cuts: fp.Remove(g)   # Tangara-Footprints (Klinke/USB) enthalten Edge.Cuts-Konturen: hier unerwuenscht
    board.Add(fp)
    fp.SetPosition(V(0, 0))
    ref_pad = None
    for p in fp.Pads():
        q = p.GetPosition()
        if abs(q.x) + abs(q.y) > FromMM(0.2) and abs(q.x) > FromMM(0.1) and abs(q.y) > FromMM(0.1):
            ref_pad = p; break
    if ref_pad is None: ref_pad = list(fp.Pads())[0]
    qu, qv = ToMM(ref_pad.GetPosition().x) - OX, -(ToMM(ref_pad.GetPosition().y) - OY)   # lokal, y oben
    padkey = ref_pad.GetNumber()
    if side == 'B':
        fp.Flip(V(0, 0), pcbnew.FLIP_DIRECTION_LEFT_RIGHT)
        eu, ev = rot(-qu, qv, theta)
        for o in (0, 90, 180, 270, -90):
            fp.SetOrientationDegrees(o)
            for p in fp.Pads():
                if p.GetNumber() == padkey:
                    gx, gy = P(p.GetPosition())
                    break
            if abs(gx - eu) < 0.01 and abs(gy - ev) < 0.01: break
        else: raise SystemExit('Orientierung nicht gefunden: ' + part['ref'])
    else:
        fp.SetOrientationDegrees(theta)
    fp.SetPosition(V(x, y))
    for pad in fp.Pads():
        nm = part['pins'].get(pad.GetNumber())
        if nm: pad.SetNet(net(nm))
    placed[part['ref']] = fp
    return fp

def padpos(ref, num):
    return [P(p.GetPosition()) for p in placed[ref].Pads() if p.GetNumber() == str(num)]

def track(netname, layer, pts, w=0.15):
    for a, b in zip(pts[:-1], pts[1:]):
        t = pcbnew.PCB_TRACK(board); t.SetStart(V(*a)); t.SetEnd(V(*b)); t.SetWidth(FromMM(w)); t.SetLayer(layer)
        if netname: t.SetNet(net(netname))
        board.Add(t)
def via(netname, x, y, dia=0.45, drill=0.2):
    v = pcbnew.PCB_VIA(board); v.SetPosition(V(x, y)); v.SetWidth(FromMM(dia)); v.SetDrill(FromMM(drill))
    v.SetViaType(pcbnew.VIATYPE_THROUGH)
    if netname: v.SetNet(net(netname))
    board.Add(v)
def sline(layer, a, b, w=0.12):
    s = pcbnew.PCB_SHAPE(board); s.SetShape(pcbnew.SHAPE_T_SEGMENT); s.SetStart(V(*a)); s.SetEnd(V(*b)); s.SetLayer(layer); s.SetWidth(FromMM(w)); board.Add(s)
def sarc(layer, start, mid, end, w=0.1):
    s = pcbnew.PCB_SHAPE(board); s.SetShape(pcbnew.SHAPE_T_ARC); s.SetStart(V(*start)); s.SetArcGeometry(V(*start), V(*mid), V(*end))
    s.SetLayer(layer); s.SetWidth(FromMM(w)); board.Add(s)
def scircle(layer, c, r, w=0.12):
    s = pcbnew.PCB_SHAPE(board); s.SetShape(pcbnew.SHAPE_T_CIRCLE); s.SetCenter(V(*c)); s.SetEnd(V(c[0] + r, c[1])); s.SetLayer(layer); s.SetWidth(FromMM(w)); board.Add(s)
def text(layer, s, x, y, h=0.9, mirror=False, rot_deg=0, bold=False):
    t = pcbnew.PCB_TEXT(board); t.SetText(s); t.SetPosition(V(x, y)); t.SetLayer(layer)
    t.SetTextSize(VECTOR2I(FromMM(h), FromMM(h))); t.SetTextThickness(FromMM(max(h / 6, 0.15))); t.SetMirrored(mirror)
    t.SetTextAngleDegrees(rot_deg); board.Add(t)


def zone(layer, pts, netname, prio=0, clearance=0.2, minw=0.2, keepout=None, layers=None, holes=(), thermal=False):
    z = pcbnew.ZONE(board); z.SetLayer(layer)
    if layers:
        ls = pcbnew.LSET()
        for l in layers: ls.AddLayer(l)
        z.SetLayerSet(ls)
    if netname and not keepout: z.SetNet(net(netname))
    o = z.Outline(); o.NewOutline()
    for x, y in pts: o.Append(FromMM(OX + x), FromMM(OY - y))
    for h in holes:
        o.NewHole()
        for x, y in h: o.Append(FromMM(OX + x), FromMM(OY - y), 0, 0)
    z.SetAssignedPriority(prio); z.SetMinThickness(FromMM(minw)); z.SetLocalClearance(FromMM(clearance))
    z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL if thermal else pcbnew.ZONE_CONNECTION_FULL)
    if thermal:
        z.SetThermalReliefGap(FromMM(0.25)); z.SetThermalReliefSpokeWidth(FromMM(0.3))
    z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
    if keepout:
        z.SetIsRuleArea(True)
        z.SetDoNotAllowTracks('tracks' in keepout); z.SetDoNotAllowVias('vias' in keepout)
        z.SetDoNotAllowPads(False); z.SetDoNotAllowCopperPour('pour' in keepout); z.SetDoNotAllowFootprints('fp' in keepout)
    board.Add(z); return z

def circle_pts(c, r, n=48):
    return [(c[0] + r * math.cos(2 * math.pi * i / n), c[1] + r * math.sin(2 * math.pi * i / n)) for i in range(n)]

def board_pts(inset=0.0, n=8):
    W, H, R = layout.BOARD_W / 2 - inset, layout.BOARD_H / 2 - inset, max(layout.BOARD_R - inset, 0.2)
    pts = []
    for cx, cy, a0 in ((W - R, H - R, 0), (-W + R, H - R, 90), (-W + R, -H + R, 180), (W - R, -H + R, 270)):
        for i in range(n + 1):
            a = math.radians(a0 + 90 * i / n); pts.append((cx + R * math.cos(a), cy + R * math.sin(a)))
    return pts

def outline():
    """Plattenkontur 37 x 84 (Ecken r = 5) mit Randausschnitten fuer Klinke, USB-C und Klickrad-Kabelschlitz (layout.board_poly)."""
    poly = layout.board_poly()
    L = pcbnew.Edge_Cuts
    geoms = list(poly.geoms) if hasattr(poly, 'geoms') else [poly]
    for g in geoms:
        for ring in [g.exterior] + list(g.interiors):
            pts = list(ring.coords)
            for a, b in zip(pts[:-1], pts[1:]):
                if math.dist(a, b) > 1e-4: sline(L, (round(a[0], 4), round(a[1], 4)), (round(b[0], 4), round(b[1], 4)), 0.1)

HOLES = layout.HOLES
RING_W = float(os.environ.get('RING_W', '0.35'))
def edge_ring():
    """Sperrring (keine Leiterbahnen/Vias) entlang aller Kanten fuer den Router (die DSN kennt den Randabstand nicht). Pads bleiben erreichbar."""
    from shapely.geometry import box as sb
    bp = layout.board_poly()
    ring = bp.difference(bp.buffer(-RING_W))
    padgeom = []
    for fp in placed.values():
        for pad in fp.Pads():
            bb = pad.GetBoundingBox()
            padgeom.append(sb(ToMM(bb.GetLeft()) - OX - 0.1, OY - ToMM(bb.GetBottom()) - 0.1, ToMM(bb.GetRight()) - OX + 0.1, OY - ToMM(bb.GetTop()) + 0.1))
    from shapely.ops import unary_union as uu
    ring = ring.difference(uu(padgeom))
    geoms = list(ring.geoms) if hasattr(ring, 'geoms') else [ring]
    for g in geoms:
        if g.is_empty or g.area < 1e-4: continue
        z = zone(F_CU, list(g.exterior.coords)[:-1], None, keepout=('tracks', 'vias'), layers=[F_CU, IN1, IN2, B_CU],
                 holes=[list(i.coords)[:-1] for i in g.interiors])
        z.SetZoneName('edge_ring')
def run_place():
    outline()
    pl = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'placement.json')))
    for part in netlist.parts():
        r = part['ref']
        if part['kind'] == 'H':
            hx, hy = part['hole_at']; place(part, hx, hy, 0, 'T'); continue
        x, y, th, side = layout.FIXED.get(r) or pl[r]
        place(part, x, y, th, side)
    zone(IN1, board_pts(0.3), 'GND', prio=1, clearance=0.2)
    from previa import previa
    previa(board, OX, OY, layout.board_poly().buffer(-0.45))
    board.Save(os.path.join(TMP, 'pre_nr.kicad_pcb'))
    edge_ring()
    board.Save(os.path.join(TMP, 'pre.kicad_pcb'))
    print('platziert:', len(placed))

if MODE == 'place':
    run_place()
else:
    exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'finish.py')).read())
