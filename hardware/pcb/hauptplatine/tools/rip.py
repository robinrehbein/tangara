import sys, os
os.environ.setdefault('KICAD9_FOOTPRINT_DIR', '/usr/share/kicad/footprints')
import pcbnew
b = pcbnew.LoadBoard(sys.argv[1])
f = lambda p: (pcbnew.ToMM(p.x) - 100, 100 - pcbnew.ToMM(p.y))
rm = []
for t in b.GetTracks():
    if t.IsLocked(): continue
    n = t.GetNetname(); p = f(t.GetStart()); q = f(t.GetEnd())
    inbox = all(3.0 <= v[0] <= 8.0 and 0.2 <= v[1] <= 4.6 for v in (p, q))
    if inbox and n in ('GND', '3V3'): rm.append(t)
for t in rm: b.Remove(t)
print('entfernt', len(rm))
pcbnew.SaveBoard(sys.argv[2], b)
