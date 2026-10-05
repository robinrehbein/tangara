#!/usr/bin/env python3
"""Rev. 3b, Stufe 1: Netzaenderungen, neue Bauteile und J20-Tausch auf der fertig gerouteten Platine (Review B1, B2, B3, H1, H4, H7).
Eingabe: tools/routing/stand_vor_review_fixes.kicad_pcb (Stand Rev. 3 nach Router und Nacharbeit); Ausgabe: Pfad in argv[1].
Die Netzlisten-Aenderungen stehen in netlist.py (Quelle fuer Schaltplan/Stueckliste); hier werden dieselben Aenderungen auf der Platine nachgezogen,
betroffene Verbindungen werden mit rt.py (Raster-A*) neu gezogen."""
import os, sys, math, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rt, rtedit, netlist, layout
import pcbnew
from pcbnew import FromMM, ToMM
from rt import V, P
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'routing', 'stand_vor_review_fixes.kicad_pcb')
OUT = sys.argv[1] if len(sys.argv) > 1 else '/tmp/claude-0/stage1.kicad_pcb'
FPDIR = '/usr/share/kicad/footprints/'
E = rtedit.Edit(SRC)
b, R, FPS, parts = E.b, E.R, E.FPS, E.parts
net_new = E.net


def renet(ref, num, new): return E.renet(ref, num, new)


touched = set()
# ---------------------------------------------------------------------------------------------- Netzaenderungen
print('Netzaenderungen')
for ref, num, new in (('U30', '7', 'PCA_EN'), ('C257', '1', 'PCA_EN'),                                   # B1 PCA9306: VREF2 = EN
                      ('R43', '1', 'GND'), ('R36', '1', 'VBUS_SW'),                                      # B3 Lader: SEL = GND, PROG2 an VBUS_SW
                      ('U15', '48', 'unconnected-(U15-NC_48-Pad48)'), ('U15', '49', 'unconnected-(U15-NC_49-Pad49)')):   # keine GPIO-Verbindung
    touched |= {renet(ref, num, new), new}
touched.discard('')

# ---------------------------------------------------------------------------------------------- H1: Reset-Sicherung Q21, Q22, R250
print('neue Bauteile')
sp = E.place_near('Q21', (-12.2, -32.6))
E.place_near('Q22', sp[:2])
E.place_near('R250', sp[:2])

# ---------------------------------------------------------------------------------------------- H4: J20 -> Molex 503480-3000
print('J20')
E.drop_fp('J20')
E.new_fp('J20', 0.0, -0.65, 0, 'T')
R.refresh()

# ---------------------------------------------------------------------------------------------- Werte / DNP
for ref in ('R39', 'C257', 'R247', 'R43', 'R36'):
    FPS[ref].SetValue(parts[ref]['value'])
for ref in ('R1', 'R57'):
    FPS[ref].SetDNP(True)

# ---------------------------------------------------------------------------------------------- Aufraeumen
for net in sorted(touched):
    if net.startswith('unconnected'): continue
    print('  prune', net, rt.prune_dangling(b, net))
R.refresh()
E.apply_nc()
conn_pad = E.conn_pad


print('Verbinden')
for ref, num in (('Q22', '2'), ('Q21', '2'), ('R43', '1')):        # GND zuerst (enge Pads)
    conn_pad('GND', ref, num, widths=(0.2, 0.127), layers=(0, 1, 2), margin=6.0)
for net in ('PCA_EN', 'RST_G'):
    print('  connect_all', net, 'Rest-Cluster', R.connect_all(net, w=0.127, layers=(0, 2), margin=6.0))
conn_pad('DAC_RESET_N', 'Q21', '3', layers=(0, 1, 2), margin=8.0)
conn_pad('VBUS_SW', 'R36', '1', widths=(0.3, 0.2, 0.127), layers=(0, 2))
conn_pad('SYS_POWER', 'R250', '1', widths=(0.3, 0.2, 0.127), layers=(0, 2))
conn_pad('3V3', 'Q22', '1', widths=(0.25, 0.127), layers=(0, 2))
# J20: alte GND-Stummel an den Hirose-Haltern entfernen, neue Halter-Pads (Nagelpads) an die GND-Vias anbinden
for t in list(b.GetTracks()):
    if t.Type() != pcbnew.PCB_VIA_T and t.GetNetname() == 'GND' and t.GetLayer() == pcbnew.F_Cu:
        for e in (P(t.GetStart()), P(t.GetEnd())):
            if abs(abs(e[0]) - 9.15) < 0.05 and abs(e[1] + 1.9) < 0.05: rt.remove_item(b, t); break
R.refresh()
for xy in ((-8.04, -1.85), (8.04, -1.85)):
    r = R.connect_xy('GND', xy, w=0.2, layers=(0, 2)) or R.connect_xy('GND', xy, w=0.127, layers=(0, 2))
    print('  GND J20-MP', xy, 'ok' if r else 'FEHLT')
R.refresh()
r = R.connect_xy('GND', (-5.45 - 0.0, -36.95), w=0.127, layers=(0, 1, 2), quiet=False) if False else None
print('  connect_all 3V3 Rest', R.connect_all('3V3', w=0.25, layers=(0, 2)))
E.save(OUT)
print('gespeichert', OUT)
