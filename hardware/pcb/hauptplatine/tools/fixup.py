"""Nachbesserung: Vias zu nah an der Kante nach innen schieben (samt Bahnenden)."""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('KICAD9_FOOTPRINT_DIR', '/usr/share/kicad/footprints')
import pcbnew
from pcbnew import VECTOR2I, FromMM, ToMM
from shapely.geometry import Point
import layout
b = pcbnew.LoadBoard(sys.argv[1])
bp = layout.board_poly(); bd = bp.boundary
P = lambda p: (ToMM(p.x) - 100, 100 - ToMM(p.y))
V = lambda x, y: VECTOR2I(FromMM(100 + x), FromMM(100 - y))
n = 0
for v in [t for t in b.GetTracks() if t.Type() == pcbnew.PCB_VIA_T]:
    c = P(v.GetPosition())
    if bd.distance(Point(*c)) >= 0.58: continue
    best = None
    for r in (0.1, 0.2, 0.3, 0.4, 0.5):
        for a in range(0, 360, 30):
            q = (c[0] + r * math.cos(math.radians(a)), c[1] + r * math.sin(math.radians(a)))
            if bp.contains(Point(*q)) and bd.distance(Point(*q)) >= 0.58: best = q; break
        if best: break
    if not best: continue
    for t in b.GetTracks():
        if t.Type() == pcbnew.PCB_VIA_T: continue
        for end, set_ in ((t.GetStart(), t.SetStart), (t.GetEnd(), t.SetEnd)):
            if math.dist(P(end), c) < 2e-3: set_(V(*best))
    v.SetPosition(V(*best)); n += 1
print('Vias verschoben', n)
pcbnew.SaveBoard(sys.argv[2], b)
