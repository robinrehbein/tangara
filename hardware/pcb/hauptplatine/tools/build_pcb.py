#!/usr/bin/env python3
"""Erzeugt hauptplatine.kicad_pcb.

Koordinaten wie in netlist.py: Mitte = (0,0), x rechts, y oben, Blick von der Display-Seite (Oberseite).
MODE=place   -> Platzierung + Umriss + Netze (ohne Leiterbahnen) nach $TMPDIR_PCB/pre.kicad_pcb
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
    ds = board.GetDesignSettings()
    ds.SetBoardThickness(FromMM(1.0))
nets = {}
if MODE == 'finish':
    for name, n in board.GetNetsByName().items(): nets[str(name)] = n
def net(name):
    if name not in nets:
        n = pcbnew.NETINFO_ITEM(board, name); board.Add(n); nets[name] = n
    return nets[name]

def loadfp(spec):
    lib, name = spec.split(':')
    path = os.path.join(ROOT, 'lib', 'Tangara.pretty') if lib == 'Tangara' else FPDIR + lib + '.pretty'
    fp = pcbnew.FootprintLoad(path, name)
    if fp is None: raise SystemExit('Footprint fehlt: ' + spec)
    fp.SetFPID(pcbnew.LIB_ID(lib, name))
    return fp

def rot(a, b, deg):
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    return a * c - b * s, a * s + b * c

placed = {}
def place(part, x, y, theta, side):
    """theta: Drehung der Ansicht (CCW, Blick von oben). Unterseite: Bauteil wird erst gespiegelt (Blick von unten wie Oberseite), dann gedreht."""
    fp = loadfp(part['fp'])
    fp.SetReference(part['ref']); fp.SetValue(part['value'])
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
def via(netname, x, y, dia=0.6, drill=0.3):
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

def outline():
    W, H, R = layout.BOARD_W, layout.BOARD_H, layout.BOARD_R
    x0, x1, y0, y1 = -W / 2, W / 2, -H / 2, H / 2
    L = pcbnew.Edge_Cuts
    sline(L, (x0 + R, y1), (x1 - R, y1), 0.1); sline(L, (x1, y1 - R), (x1, y0 + R), 0.1)
    sline(L, (x1 - R, y0), (x0 + R, y0), 0.1); sline(L, (x0, y0 + R), (x0, y1 - R), 0.1)
    k = R * (1 - math.sqrt(0.5))
    sarc(L, (x1 - R, y1), (x1 - k, y1 - k), (x1, y1 - R)); sarc(L, (x1, y0 + R), (x1 - k, y0 + k), (x1 - R, y0))
    sarc(L, (x0 + R, y0), (x0 + k, y0 + k), (x0, y0 + R)); sarc(L, (x0, y1 - R), (x0 + k, y1 - k), (x0 + R, y1))
    # Klickrad-Aussparung: Kreis r = 13 um (0,-27) plus Ausbuchtung nach unten (Platz fuer Stecker J1 des Moduls)
    cx, cy, r = 0.0, layout.WHEEL_Y, layout.CUT_R
    a, yb, rc = layout.NOTCH_HALF, layout.NOTCH_BOTTOM, layout.NOTCH_CORNER
    yj = cy - math.sqrt(r * r - a * a)
    sline(L, (a, yj), (a, yb + rc), 0.1); sarc(L, (a, yb + rc), (a - rc + rc * math.sqrt(0.5), yb + rc - rc * math.sqrt(0.5)), (a - rc, yb))
    sline(L, (a - rc, yb), (-a + rc, yb), 0.1)
    sarc(L, (-a + rc, yb), (-a + rc - rc * math.sqrt(0.5), yb + rc - rc * math.sqrt(0.5)), (-a, yb + rc))
    sline(L, (-a, yb + rc), (-a, yj), 0.1)
    sarc(L, (-a, yj), (0, cy + r), (a, yj))

def bsetup():
    if MODE != 'finish':
        outline()
    if MODE == 'place':
        from shapely.geometry import box as sbox
        majors = [p for p in netlist.parts() if p.get('at')]
        for part in majors:
            place(part, *part['at'])
        for ref, fp in placed.items():
            layout.placed_side[ref] = 'B' if fp.GetLayer() == B_CU else 'T'
            c = fp.GetPosition(); layout.anchor_center[ref] = P(c)
        def pad_boxes():
            out = {}
            for ref, fp in placed.items():
                side = layout.placed_side[ref]
                lst = []
                for pad in fp.Pads():
                    bb = pad.GetBoundingBox()
                    lst.append((sbox(ToMM(bb.GetLeft()) - OX, OY - ToMM(bb.GetBottom()), ToMM(bb.GetRight()) - OX, OY - ToMM(bb.GetTop())), side))
                cl = pcbnew.B_CrtYd if side == 'B' else pcbnew.F_CrtYd
                cyb = fp.GetCourtyard(cl).BBox()
                if cyb.GetWidth() > 0:
                    lst.append((sbox(ToMM(cyb.GetLeft()) - OX, OY - ToMM(cyb.GetBottom()), ToMM(cyb.GetRight()) - OX, OY - ToMM(cyb.GetTop())), side))
                out[ref] = lst
            return out
        def anchor_net(aref, apin):
            for p in placed[aref].Pads():
                if p.GetNumber() == str(apin): return p.GetNetname()
            return None
        auto = layout.auto_place(netlist.parts(), placed, padpos, pad_boxes, anchor_net)
        for part in netlist.parts():
            if part['ref'] in placed: continue
            if part['ref'] in auto: place(part, *auto[part['ref']])
            else: print('NICHT PLATZIERT', part['ref'])
bsetup()

if MODE == 'place':
    board.Save(os.path.join(TMP, 'pre.kicad_pcb'))
    for r in ('U1', 'U2', 'U3', 'U4', 'U5', 'J1', 'J2', 'J3', 'J4', 'J5', 'SW1'):
        if r in placed:
            print(r, [(p.GetNumber(), tuple(round(v, 2) for v in P(p.GetPosition()))) for p in placed[r].Pads()][:40])
    print('platziert:', len(placed))
else:
    exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'finish.py')).read())
