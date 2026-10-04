"""Entfernt kurze Bahnreste, die der DRC als 'track_dangling' meldet (nur ungesperrte, < 0,2 mm) und uebergebene Netz-Stummel (NET@x,y)."""
import sys, os, re
os.environ.setdefault('KICAD9_FOOTPRINT_DIR', '/usr/share/kicad/footprints')
import pcbnew
b = pcbnew.LoadBoard(sys.argv[1]); rpt = open(sys.argv[3]).read()
pos = [(float(x) - 100, 100 - float(y)) for x, y in re.findall(r'\[track_dangling\].*?\n.*?\n\s*@\(([\d.]+) mm, ([\d.]+) mm\)', rpt)]
extra = [tuple(float(v) for v in a.split(',')) for a in sys.argv[4:]]
n = 0
for t in list(b.GetTracks()):
    if t.Type() == pcbnew.PCB_VIA_T or t.IsLocked(): continue
    s = (pcbnew.ToMM(t.GetStart().x) - 100, 100 - pcbnew.ToMM(t.GetStart().y)); e = (pcbnew.ToMM(t.GetEnd().x) - 100, 100 - pcbnew.ToMM(t.GetEnd().y))
    L = pcbnew.ToMM(t.GetLength())
    hit = any(abs(p[0] - q[0]) < 0.02 and abs(p[1] - q[1]) < 0.02 for p in pos for q in (s, e))
    hit2 = any(abs(p[0] - q[0]) < 0.06 and abs(p[1] - q[1]) < 0.06 for p in extra for q in (s, e))
    if (hit and L < 0.5) or hit2: b.Remove(t); n += 1
print('entfernt', n)
pcbnew.SaveBoard(sys.argv[2], b)
