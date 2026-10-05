#!/usr/bin/env python3
"""NICHT VERWENDET (Versuch, in rev3b_make.sh nicht enthalten): Auf den Aussenlagen waren die In2-Stuecke von SYS_POWER nicht mit >= 0,25 mm ersetzbar (6 Cluster blieben unverbunden); stattdessen Stufe 3b/3c.
Rev. 3b, Stufe 3: Leistungsnetze (SYS_POWER, VBUS, VBUS_SW, VBAT, V5_HOST, BOOST_SW, 3V3-Zuleitung) von In2 auf die Aussenlagen holen und verbreitern (Review H3).
argv: Eingabe Ausgabe. 1) In2-Bahnen der Netze entfernen, Cluster mit >= 0,3 mm neu verbinden (Rueckfall 0,25); 2) alle Segmente soweit verbreitern, wie der Platz reicht."""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rt, rtedit
import pcbnew
from pcbnew import FromMM, ToMM
from rt import P
from shapely.geometry import LineString, Point
E = rtedit.Edit(sys.argv[1]); OUT = sys.argv[2]
b, R = E.b, E.R
TARGET = {'SYS_POWER': 0.5, 'VBAT': 0.5, 'VBUS': 0.4, 'VBUS_SW': 0.4, 'V5_HOST': 0.4, 'BOOST_SW': 0.4}
MINW = {'SYS_POWER': 0.3, 'VBAT': 0.3, 'VBUS': 0.3, 'VBUS_SW': 0.3, 'V5_HOST': 0.3, 'BOOST_SW': 0.3}


def stats(net):
    d = {}
    for t in b.GetTracks():
        if t.GetNetname() == net and t.Type() != pcbnew.PCB_VIA_T:
            k = (t.GetLayerName(), round(ToMM(t.GetWidth()), 3)); d[k] = d.get(k, 0) + ToMM(t.GetLength())
    return {k: round(v, 1) for k, v in sorted(d.items())}


for net in list(TARGET) + ['3V3']:
    print('vorher', net, stats(net))

# ---- 1) In2-Bahnen der Leistungsnetze entfernen und ueber Aussenlagen neu verbinden
for net in ('SYS_POWER', 'VBUS', 'VBAT', '3V3'):
    n = 0
    for t in list(b.GetTracks()):
        if t.GetNetname() == net and t.Type() != pcbnew.PCB_VIA_T and t.GetLayer() == pcbnew.In2_Cu:
            rt.remove_item(b, t); n += 1
    R.refresh()
    print(net, 'In2-Segmente entfernt:', n)
    # Vias, die nur noch In2 beruehrten, entfernen; danach Cluster verbinden
    print('  prune', rt.prune_dangling(b, net)); R.refresh()
    for w in ((0.5, 0.4, 0.3, 0.25) if net != '3V3' else (0.4, 0.3, 0.25)):
        left = R.connect_all(net, w=w, layers=(0, 2), margin=6.0, via_cost=25, clr_steps=(0.0, 0.04))
        print('  connect_all w=%.2f Rest-Cluster %d' % (w, left))
        if left == 0: break
    if left:
        for w in (0.25, 0.2, 0.127):
            left = R.connect_all(net, w=w, layers=(0, 1, 2), margin=10.0)
            print('  Fallback w=%.3f (mit In2) Rest-Cluster %d' % (w, left))
            if left == 0: break
    print('  prune', rt.prune_dangling(b, net)); R.refresh()
E.save(OUT)
for net in list(TARGET) + ['3V3']:
    print('nachher', net, stats(net))
