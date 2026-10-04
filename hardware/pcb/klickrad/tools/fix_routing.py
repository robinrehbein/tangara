#!/usr/bin/env python3
"""Handnachbesserung der Router-Ausgabe (tools/routed.kicad_pcb): fehlende Teilstücke von Hand ergänzen. Aufruf: fix_routing.py datei.kicad_pcb"""
import sys, pcbnew
from pcbnew import FromMM, VECTOR2I
FIX = [
]
VIAS = []
REMOVE_VIAS = [(3.55, -2.3), (2.35, -3.0), (4.95, -2.4)]    # doppelte GND-Vias (Bohrungsabstand < 0,5 mm), das jeweils andere Via des Paares bleibt
REMOVE_TRACK_NEAR = [(14.3, -1.65)]                           # GND-Stichleitung mit offenem Ende
b = pcbnew.LoadBoard(sys.argv[1])
for net, lay, pts, w in FIX:
    for a, c in zip(pts[:-1], pts[1:]):
        t = pcbnew.PCB_TRACK(b); t.SetStart(VECTOR2I(FromMM(100 + a[0]), FromMM(100 - a[1]))); t.SetEnd(VECTOR2I(FromMM(100 + c[0]), FromMM(100 - c[1])))
        t.SetWidth(FromMM(w)); t.SetLayer(b.GetLayerID(lay)); t.SetNet(b.FindNet(net)); b.Add(t)
import math
for t in list(b.GetTracks()):
    p = t.GetPosition() if t.Type() == pcbnew.PCB_VIA_T else None
    if p is not None:
        for (x, y) in REMOVE_VIAS:
            if math.hypot(p.x / 1e6 - 100 - x, 100 - p.y / 1e6 - y) < 0.06: b.RemoveNative(t); break
    elif t.GetNetname() == 'GND':
        mx, my = (t.GetStart().x + t.GetEnd().x) / 2e6 - 100, 100 - (t.GetStart().y + t.GetEnd().y) / 2e6
        if any(math.hypot(mx - x, my - y) < 0.7 for (x, y) in REMOVE_TRACK_NEAR): b.RemoveNative(t)
for net, x, y in VIAS:
    v = pcbnew.PCB_VIA(b); v.SetPosition(VECTOR2I(FromMM(100 + x), FromMM(100 - y))); v.SetWidth(FromMM(0.6)); v.SetDrill(FromMM(0.3)); v.SetViaType(pcbnew.VIATYPE_THROUGH); v.SetNet(b.FindNet(net)); b.Add(v)
b.Save(sys.argv[1])
