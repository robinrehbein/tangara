#!/usr/bin/env python3
"""Erzeugt klickrad.kicad_pcb v2, 2 Lagen (Koordinaten: Frontansicht, x rechts, y oben, Ursprung = Platinenmitte)."""
import math, os, sys, json
import pcbnew
from pcbnew import VECTOR2I, FromMM, ToMM
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import netlist, make_lib, sx
ROOT = netlist.ROOT
OX, OY = 100.0, 100.0
FP = '/usr/share/kicad/footprints/'
def V(x, y): return VECTOR2I(FromMM(OX + x), FromMM(OY - y))
def P(p): return (ToMM(p.x) - OX, OY - ToMM(p.y))

MODE = os.environ.get('MODE', 'place')
board = pcbnew.LoadBoard(os.environ['LOADFROM']) if MODE == 'finish' else pcbnew.BOARD()
B_CU, F_CU = pcbnew.B_Cu, pcbnew.F_Cu
if MODE != 'finish': board.SetCopperLayerCount(2)
nets = {}
if MODE == 'finish':
    for name, n in board.GetNetsByName().items():
        nets[str(name)] = n
def net(name):
    if name not in nets:
        n = pcbnew.NETINFO_ITEM(board, name); board.Add(n); nets[name] = n
    return nets[name]

def loadfp(spec):
    lib, name = spec.split(':')
    path = os.path.join(ROOT, 'lib', 'Klickrad.pretty') if lib == 'Klickrad' else FP + lib + '.pretty'
    fp = pcbnew.FootprintLoad(path, name)
    fp.SetFPID(pcbnew.LIB_ID(lib, name))
    return fp

placed = {}
def place(part, x, y, side='B', rot=0):
    fp = loadfp(part['fp'])
    fp.SetReference(part['ref']); fp.SetValue(part['value'])
    board.Add(fp)
    fp.SetPosition(V(x, y))
    if side == 'B': fp.Flip(V(x, y), pcbnew.FLIP_DIRECTION_LEFT_RIGHT)
    fp.SetOrientationDegrees((180 + rot) if side == 'B' else rot)
    lib, sname = part['sym'].split(':')
    pn = {t[0]: t[1] for t in sx.pins(sx.sym(lib, sname))}
    for pad in fp.Pads():
        num = pad.GetNumber()
        if num in part['pins']:
            nm = part['pins'][num]
            if nm is None: nm = f"unconnected-({part['ref']}-{pn[num]}-Pad{num})"
            pad.SetNet(net(nm))
    if part.get('dnp'): fp.SetDNP(True)
    if part.get('nobom'): pass
    for item in (fp.Reference(), fp.Value()):
        pass
    placed[part['ref']] = fp
    return fp

def pad(ref, num):
    for p in placed[ref].Pads():
        if p.GetNumber() == str(num): return P(p.GetPosition())

def track(netname, layer, pts, w=0.15):
    for a, b in zip(pts[:-1], pts[1:]):
        t = pcbnew.PCB_TRACK(board); t.SetStart(V(*a)); t.SetEnd(V(*b)); t.SetWidth(FromMM(w))
        t.SetLayer(layer)
        if netname: t.SetNet(net(netname))
        board.Add(t)
def via(netname, x, y, dia=0.6, drill=0.3):
    v = pcbnew.PCB_VIA(board); v.SetPosition(V(x, y)); v.SetWidth(FromMM(dia)); v.SetDrill(FromMM(drill))
    v.SetViaType(pcbnew.VIATYPE_THROUGH)
    if netname: v.SetNet(net(netname))
    board.Add(v)

def line(layer, a, b, w=0.12):
    s = pcbnew.PCB_SHAPE(board); s.SetShape(pcbnew.SHAPE_T_SEGMENT); s.SetStart(V(*a)); s.SetEnd(V(*b))
    s.SetLayer(layer); s.SetWidth(FromMM(w)); board.Add(s)
def circle(layer, c, r, w=0.12):
    s = pcbnew.PCB_SHAPE(board); s.SetShape(pcbnew.SHAPE_T_CIRCLE); s.SetCenter(V(*c)); s.SetEnd(V(c[0] + r, c[1]))
    s.SetLayer(layer); s.SetWidth(FromMM(w)); board.Add(s)
def text(layer, s, x, y, h=0.8, mirror=False, rot=0):
    t = pcbnew.PCB_TEXT(board); t.SetText(s); t.SetPosition(V(x, y)); t.SetLayer(layer)
    t.SetTextSize(pcbnew.VECTOR2I(FromMM(h), FromMM(h))); t.SetTextThickness(FromMM(max(h / 6, 0.15))); t.SetMirrored(mirror)
    t.SetTextAngleDegrees(rot); board.Add(t)
def rect(layer, x0, y0, x1, y1, w=0.12):
    for a, b in (((x0, y0), (x1, y0)), ((x1, y0), (x1, y1)), ((x1, y1), (x0, y1)), ((x0, y1), (x0, y0))): line(layer, a, b, w)

def disc(r, n=96):
    return [(r * math.cos(2 * math.pi * i / n), r * math.sin(2 * math.pi * i / n)) for i in range(n)]
def zone(layer, pts, netname, prio=0, hatch=False, keepout=False, hole=None, layers=None):
    z = pcbnew.ZONE(board); z.SetLayer(layer)
    if layers:
        ls = pcbnew.LSET()
        for l in layers: ls.AddLayer(l)
        z.SetLayerSet(ls)
    if not keepout: z.SetNet(net(netname))
    o = z.Outline(); o.NewOutline()
    for x, y in pts: o.Append(FromMM(OX + x), FromMM(OY - y))
    if hole:
        o.NewHole()
        for x, y in hole: o.Append(FromMM(OX + x), FromMM(OY - y), 0, 0)
    z.SetAssignedPriority(prio); z.SetMinThickness(FromMM(0.2)); z.SetLocalClearance(FromMM(0.2))
    z.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL); z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
    if hatch:
        z.SetFillMode(pcbnew.ZONE_FILL_MODE_HATCH_PATTERN)
        z.SetHatchThickness(FromMM(0.3)); z.SetHatchGap(FromMM(0.7)); z.SetHatchOrientation(pcbnew.EDA_ANGLE(45, pcbnew.DEGREES_T))
        z.SetHatchSmoothingLevel(0); z.SetHatchHoleMinArea(0.3)
    if keepout:
        z.SetIsRuleArea(True); z.SetDoNotAllowFootprints(True); z.SetDoNotAllowTracks(False); z.SetDoNotAllowVias(False)
        z.SetDoNotAllowPads(False); z.SetDoNotAllowCopperPour(False)
    board.Add(z); return z

exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'layout.py')).read())
