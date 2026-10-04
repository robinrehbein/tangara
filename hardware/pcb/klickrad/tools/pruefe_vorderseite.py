#!/usr/bin/env python3
"""Prüft: Auf F.Cu liegen außer den Touch-Flächen nur Leiterbahnen im Innenring 2,65 ... 6,15 mm (zwischen Taste und Rad) und die sechs Elektroden-Vias."""
import math, os, sys, pcbnew
from pcbnew import ToMM
b = pcbnew.LoadBoard(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'klickrad.kicad_pcb'))
bad = 0; n_f = 0
for t in b.GetTracks():
    if t.Type() == pcbnew.PCB_VIA_T: continue
    if t.GetLayer() != pcbnew.F_Cu: continue
    n_f += 1
    for p in (t.GetStart(), t.GetEnd()):
        r = math.hypot(ToMM(p.x) - 100, 100 - ToMM(p.y))
        if not (2.6 <= r <= 6.2): bad += 1; print('F.Cu-Leiterbahn außerhalb des Innenrings bei r =', round(r, 2))
print('F.Cu-Leiterbahnen:', n_f, 'außerhalb:', bad)
sys.exit(1 if bad else 0)
