#!/usr/bin/env python3
"""Rev. 3b, Stufe 2: BOOT-/EN-Taster SW2/SW3 auf der Rueckseite im linken Randstreifen (Review H8). argv: Eingabe Ausgabe."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rt, rtedit, layout
from shapely.geometry import box
E = rtedit.Edit(sys.argv[1]); OUT = sys.argv[2]
bay = box(*layout.BATT).buffer(0.5)
# linker Randstreifen auf der Rueckseite (ausserhalb des Akkufachs), Taster hochkant (Pads untereinander)
a = E.place_near('SW2', (-18.0, 16.0), theta=90, extra_block=[bay], search=10, margin=0.25)
b2 = E.place_near('SW3', (-18.0, a[1] - 7.0), theta=90, extra_block=[bay], search=10, margin=0.25)
E.R.refresh()
for net, ref in (('GND', 'SW2'), ('GND', 'SW3')):
    E.conn_pad(net, ref, '2', widths=(0.2, 0.127), layers=(0, 1, 2), margin=6.0)
for net, ref in (('BOOT', 'SW2'), ('ESP_EN', 'SW3')):
    E.conn_pad(net, ref, '1', widths=(0.127,), layers=(0, 1, 2), margin=6.0, via_cost=20)
E.save(OUT)
print('gespeichert', OUT, [(r, [round(v, 2) for v in a_[:2]]) for r, a_ in (('SW2', a), ('SW3', b2))])
