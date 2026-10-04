"""J21 (Molex 503480) auf x = 0 verschieben, Footprint tauschen (Pads an der Muendung, Pin 1 rechts), alte Bahnen/Vias entfernen."""
import sys, os
os.environ.setdefault('KICAD9_FOOTPRINT_DIR', '/usr/share/kicad/footprints')
import pcbnew
from pcbnew import VECTOR2I, FromMM, ToMM
b = pcbnew.LoadBoard(sys.argv[1])
V = lambda x, y: VECTOR2I(FromMM(100 + x), FromMM(100 - y))
old = b.FindFootprintByReference('J21')
nets = {p.GetNumber(): p.GetNet() for p in old.Pads()}
ob = old.GetBoundingBox(False)
x0, x1 = ToMM(ob.GetLeft()) - 100 - 0.3, ToMM(ob.GetRight()) - 100 + 0.3
y0, y1 = 100 - ToMM(ob.GetBottom()) - 0.3, 100 - ToMM(ob.GetTop()) + 0.3
rm = []
for t in b.GetTracks():
    pts = [t.GetPosition()] if t.Type() == pcbnew.PCB_VIA_T else [t.GetStart(), t.GetEnd()]
    if any(x0 <= ToMM(p.x) - 100 <= x1 and y0 <= 100 - ToMM(p.y) <= y1 for p in pts): rm.append(t)
for t in rm: b.Remove(t)
print('entfernt', len(rm))
b.Remove(old)
fp = pcbnew.FootprintLoad(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0]))), 'lib', 'Hauptplatine.pretty'), 'Molex_503480-0600')
fp.SetFPID(pcbnew.LIB_ID('Hauptplatine', 'Molex_503480-0600')); fp.SetReference('J21'); fp.SetValue('503480-0600')
b.Add(fp); fp.SetPosition(V(0.0, -46.2)); fp.SetOrientationDegrees(0)
for p in fp.Pads():
    n = p.GetNumber()
    p.SetNet(nets['MP'] if n == 'MP' else nets[n])
fp.Reference().SetVisible(False); fp.Value().SetVisible(False)
pcbnew.SaveBoard(sys.argv[2], b)
