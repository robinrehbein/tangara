#!/usr/bin/env python3
"""Handnachbesserung der Router-Ausgabe (tools/routed.kicad_pcb): fehlende Teilstücke von Hand ergänzen. Aufruf: fix_routing.py datei.kicad_pcb"""
import sys, pcbnew
from pcbnew import FromMM, VECTOR2I
FIX = [   # Stücke
    ('3V3', 'B.Cu', [(0.45, -5.11), (0.95, -5.05)], 0.2),           # R6-Pad 1 -> Via
    ('3V3', 'F.Cu', [(0.95, -5.05), (1.95, -5.05)], 0.2),           # Brücke auf F.Cu über das SDA-Signal (Lücke im Router-Ergebnis)
]
VIAS = [('3V3', 0.95, -5.05), ('3V3', 1.95, -5.05)]
b = pcbnew.LoadBoard(sys.argv[1])
for net, lay, pts, w in FIX:
    for a, c in zip(pts[:-1], pts[1:]):
        t = pcbnew.PCB_TRACK(b); t.SetStart(VECTOR2I(FromMM(100 + a[0]), FromMM(100 - a[1]))); t.SetEnd(VECTOR2I(FromMM(100 + c[0]), FromMM(100 - c[1])))
        t.SetWidth(FromMM(w)); t.SetLayer(b.GetLayerID(lay)); t.SetNet(b.FindNet(net)); b.Add(t)
for net, x, y in VIAS:
    v = pcbnew.PCB_VIA(b); v.SetPosition(VECTOR2I(FromMM(100 + x), FromMM(100 - y))); v.SetWidth(FromMM(0.6)); v.SetDrill(FromMM(0.3)); v.SetViaType(pcbnew.VIATYPE_THROUGH); v.SetNet(b.FindNet(net)); b.Add(v)
b.Save(sys.argv[1])
