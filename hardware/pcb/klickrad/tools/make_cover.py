#!/usr/bin/env python3
"""FR4-Abdeckung (0,6 mm) für das Klickrad-Modul nach Vorbild tangara-hw/touchwheel-cover (cool tech zone, CERN-OHL-S-2.0).
Nur Umriss (Edge.Cuts) und Siebdruck (F.SilkS), kein Kupfer. Koordinaten: Mitte = (0, 0), Vorderansicht, y nach oben."""
import math, os, sys
import pcbnew
from pcbnew import VECTOR2I, FromMM
from shapely.geometry import Point
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTD = os.path.join(ROOT, 'abdeckung')
OX, OY = 100.0, 100.0
def V(x, y): return VECTOR2I(FromMM(OX + x), FromMM(OY - y))
b = pcbnew.BOARD()
b.SetCopperLayerCount(2)
b.GetDesignSettings().SetBoardThickness(FromMM(0.6))
def seg(layer, a, c, w):
    s = pcbnew.PCB_SHAPE(b); s.SetShape(pcbnew.SHAPE_T_SEGMENT); s.SetStart(V(*a)); s.SetEnd(V(*c)); s.SetLayer(layer); s.SetWidth(FromMM(w)); b.Add(s)
def circ(layer, r, w, c=(0, 0)):
    s = pcbnew.PCB_SHAPE(b); s.SetShape(pcbnew.SHAPE_T_CIRCLE); s.SetCenter(V(*c)); s.SetEnd(V(c[0] + r, c[1])); s.SetLayer(layer); s.SetWidth(FromMM(w)); b.Add(s)
def poly(layer, pts, filled=True, w=0.0):
    s = pcbnew.PCB_SHAPE(b); s.SetShape(pcbnew.SHAPE_T_POLY); s.SetFilled(filled); s.SetLayer(layer); s.SetWidth(FromMM(w))
    s.SetPolyPoints([V(*p) for p in pts]); b.Add(s)
def text(layer, s, x, y, h, thick, rot=0):
    t = pcbnew.PCB_TEXT(b); t.SetText(s); t.SetPosition(V(x, y)); t.SetLayer(layer)
    t.SetTextSize(VECTOR2I(FromMM(h), FromMM(h))); t.SetTextThickness(FromMM(thick)); t.SetTextAngleDegrees(rot); b.Add(t)

SILK = pcbnew.F_SilkS
# ---- Umriss: Ø 30 mit drei Aussparungen (Schraubenköpfe der Platine bei r = 14,6 mm, 90/210/330 Grad) -> Platinenschrauben bleiben frei
R = 15.0; NOTCH = 2.1
shape = Point(0, 0).buffer(R, 256)
for a in (90, 210, 330):
    shape = shape.difference(Point(14.6 * math.cos(math.radians(a)), 14.6 * math.sin(math.radians(a))).buffer(NOTCH, 64))
pts = list(shape.exterior.coords)
for p, q in zip(pts[:-1], pts[1:]): seg(pcbnew.Edge_Cuts, p, q, 0.1)
# ---- Siebdruck (nach Tangara: Kreis für die Mitteltaste, Ring-Markierungen, Symbole an den vier Richtungen)
circ(SILK, 5.8, 0.2)                # Mitteltaste Ø 11,6 (wie die gedruckte Abdeckung)
circ(SILK, 12.4, 0.15)              # Außenkante des Touch-Rads (Elektroden r = 6,3 ... 12,3)
def tri(cx, cy, size, ang):   # gefülltes Dreieck, Spitze in Richtung ang (Grad)
    a = math.radians(ang); h = size
    tip = (cx + h * 0.5 * math.cos(a), cy + h * 0.5 * math.sin(a))
    bx, by = cx - h * 0.5 * math.cos(a), cy - h * 0.5 * math.sin(a)
    n = (-math.sin(a), math.cos(a))
    return [tip, (bx + n[0] * h * 0.5, by + n[1] * h * 0.5), (bx - n[0] * h * 0.5, by - n[1] * h * 0.5)]
RS = 9.35   # Symbolradius = Mitte des Rings
text(SILK, 'MENU', 0, RS, 1.5, 0.2)
# links: |<<
poly(SILK, tri(-RS - 0.2, 0, 1.6, 180)); poly(SILK, tri(-RS + 1.2, 0, 1.6, 180)); seg(SILK, (-RS - 1.2, -0.8), (-RS - 1.2, 0.8), 0.25)
# rechts: >>|
poly(SILK, tri(RS + 0.2, 0, 1.6, 0)); poly(SILK, tri(RS - 1.2, 0, 1.6, 0)); seg(SILK, (RS + 1.2, -0.8), (RS + 1.2, 0.8), 0.25)
# unten: >||
poly(SILK, tri(-0.9, -RS, 1.6, 0)); seg(SILK, (0.4, -RS - 0.8), (0.4, -RS + 0.8), 0.25); seg(SILK, (1.2, -RS - 0.8), (1.2, -RS + 0.8), 0.25)
text(SILK, 'v2', 0, -13.4, 0.8, 0.15)
b.Save(os.path.join(OUTD, 'klickrad-abdeckung.kicad_pcb'))
print('ok', OUTD)
