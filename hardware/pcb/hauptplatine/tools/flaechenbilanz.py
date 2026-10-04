#!/usr/bin/env python3
"""Flaechenbilanz vor Platzierung/Routing: Courtyard-Flaeche (mit Abstandsaufschlag) aller Bauteile gegen die nutzbare Flaeche je Seite."""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pcbnew
from shapely.geometry import box, Polygon, Point
from shapely.ops import unary_union
import geom as G, netlist, layout
ROOT = G.ROOT
PARTS = {p['ref']: p for p in netlist.parts()}
FIX = layout.FIXED
def bbox_area(ref, gap=0.25):
    x0, x1, y0, y1 = G.fpgeom(PARTS[ref]['fp'])['bb']
    return (x1 - x0 + gap) * (y1 - y0 + gap)
def rect_view(ref):
    x0, x1, y0, y1 = G.fpgeom(PARTS[ref]['fp'])['bb']; st = FIX[ref]
    pts = [G.to_view(st, a, b) for a, b in ((x0, y0), (x1, y0), (x1, y1), (x0, y1))]
    return box(min(p[0] for p in pts), min(p[1] for p in pts), max(p[0] for p in pts), max(p[1] for p in pts))
f = pcbnew.FootprintLoad(os.path.join(ROOT, 'lib', 'Hauptplatine.pretty'), 'ESP32-S31-WROOM-1')
ant = []
for z in f.Zones():
    o = z.Outline(); ch = o.Outline(0)
    ant.append(Polygon([G.to_view(FIX['U15'], pcbnew.ToMM(ch.CPoint(k).x), pcbnew.ToMM(ch.CPoint(k).y)) for k in range(ch.PointCount())]))
ANT = unary_union(ant)
BOARD = layout.board_poly()
IN = BOARD.buffer(-0.7)
fixed_b = unary_union([rect_view(r) for r in FIX if FIX[r][3] == 'B'])
fixed_t = unary_union([rect_view(r) for r in FIX if FIX[r][3] == 'T'])
avail_b = IN.difference(unary_union([layout.forbidden_b(), ANT, fixed_b]))
avail_t = IN.difference(unary_union([layout.forbidden_t(), ANT, fixed_t]))
tall = [r for r in PARTS if r not in FIX and PARTS[r]['kind'] != 'H' and layout.height(PARTS[r]) > layout.TOP_MAX_H]
flat = [r for r in PARTS if r not in FIX and PARTS[r]['kind'] != 'H' and layout.height(PARTS[r]) <= layout.TOP_MAX_H]
a_tall = sum(bbox_area(r) for r in tall); a_flat = sum(bbox_area(r) for r in flat)
a_fix = {r: round(bbox_area(r), 0) for r in FIX}
print('Platine %.0f x %.0f mm, Flaeche %.0f mm2' % (layout.BOARD_W, layout.BOARD_H, BOARD.area))
print('nutzbar Rueckseite %.0f mm2, Vorderseite %.0f mm2 (Rand 0,7 mm, Sperrzonen abgezogen, feste Teile abgezogen)' % (avail_b.area, avail_t.area))
print('Bauteile: hoch (>1,0 mm, nur hinten) %d Stk %.0f mm2; flach %d Stk %.0f mm2; feste Teile %s' % (len(tall), a_tall, len(flat), a_flat, a_fix))
need = a_tall + a_flat
tot = avail_b.area + avail_t.area
print('Summe Bedarf %.0f, nutzbar %.0f, Reserve %.0f %%' % (need, tot, 100 * (tot - need) / need))
print('nur hinten + J20-Zone vorn (kein Teil unter dem Display): Reserve %.0f %%' % (100 * ((avail_b.area + avail_t.difference(box(*layout.DISPLAY).difference(box(-12, -7, 12, 0))).area) - need) / need))
print('tall:', sorted(tall))
