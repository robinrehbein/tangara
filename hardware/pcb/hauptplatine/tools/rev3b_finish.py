#!/usr/bin/env python3
"""Rev. 3b, Abschluss: Zonen fuellen, nach ../hauptplatine.kicad_pcb speichern, Lagenaufbau eintragen, placement.json um die neuen Bauteile ergaenzen.
argv: Eingabe"""
import os, sys, json, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rt
import pcbnew
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
b = pcbnew.LoadBoard(sys.argv[1])
pcbnew.ZONE_FILLER(b).Fill(b.Zones())
out = os.path.join(ROOT, 'hauptplatine.kicad_pcb')
pcbnew.SaveBoard(out, b)
subprocess.run([sys.executable, os.path.join(HERE, 'stackup.py'), out], check=True)
pl = json.load(open(os.path.join(HERE, 'placement.json')))
fps = {f.GetReference(): f for f in b.GetFootprints()}
for ref in ('J20', 'Q21', 'Q22', 'R250', 'SW2', 'SW3'):
    f = fps[ref]; x, y = rt.P(f.GetPosition())
    pl[ref] = [round(x, 2), round(y, 2), round(f.GetOrientationDegrees()) % 360, 'B' if f.GetLayerName() == 'B.Cu' else 'T']
json.dump(pl, open(os.path.join(HERE, 'placement.json'), 'w'), indent=1)
print('gespeichert', out)
