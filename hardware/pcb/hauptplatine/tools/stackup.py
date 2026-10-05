#!/usr/bin/env python3
"""Traegt den Referenz-Lagenaufbau in hauptplatine.kicad_pcb ein (Review H5: im Projekt war kein Aufbau hinterlegt).
Werte: PCBWay-Lagenaufbau-Seite (https://www.pcbway.com/multi-layer-laminated-structure.html), 4 Lagen, 1,0 mm, aussen 1 oz / innen 1 oz, Restkupfer innen > 60 %:
Prepreg 7628 RC46 % (0,196 mm, nach dem Pressen 0,1855 mm, DK 4,74), Kern 0,43 mm (DK 4,6), Endstaerke 1,01 mm +-10 %.
NICHT von PCBWay fuer diese Bestellung bestaetigt: bei der Impedanzanfrage kann PCBWay einen anderen Aufbau (z. B. 2116/1080) waehlen. Aufruf: stackup.py <pcb>"""
import sys, re
path = sys.argv[1]
t = open(path).read()
st = '''		(stackup
			(layer "F.SilkS" (type "Top Silk Screen"))
			(layer "F.Paste" (type "Top Solder Paste"))
			(layer "F.Mask" (type "Top Solder Mask") (thickness 0.01))
			(layer "F.Cu" (type "copper") (thickness 0.035))
			(layer "dielectric 1" (type "prepreg") (thickness 0.1855) (material "7628 RC46%") (epsilon_r 4.74) (loss_tangent 0.02))
			(layer "In1.Cu" (type "copper") (thickness 0.035))
			(layer "dielectric 2" (type "core") (thickness 0.43) (material "FR4 Core") (epsilon_r 4.6) (loss_tangent 0.02))
			(layer "In2.Cu" (type "copper") (thickness 0.035))
			(layer "dielectric 3" (type "prepreg") (thickness 0.1855) (material "7628 RC46%") (epsilon_r 4.74) (loss_tangent 0.02))
			(layer "B.Cu" (type "copper") (thickness 0.035))
			(layer "B.Mask" (type "Bottom Solder Mask") (thickness 0.01))
			(layer "B.Paste" (type "Bottom Solder Paste"))
			(layer "B.SilkS" (type "Bottom Silk Screen"))
			(copper_finish "ENIG")
			(dielectric_constraints no)
		)
'''
t = re.sub(r'\t\t\(stackup\n.*?\n\t\t\)\n', '', t, flags=re.S)
assert '(setup\n' in t
t = t.replace('(setup\n', '(setup\n' + st, 1)
open(path, 'w').write(t)
print('Lagenaufbau eingetragen')
