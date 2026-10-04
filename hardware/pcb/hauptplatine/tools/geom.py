"""Footprint-Geometrie-Helfer (ohne Seiteneffekte)."""
import os, sys, math
os.environ.setdefault('KICAD9_FOOTPRINT_DIR', '/usr/share/kicad/footprints')
import pcbnew
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def rot(a, b, deg):
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    return a * c - b * s, a * s + b * c

# ---------------------------------------------------------------- Footprint-Geometrie
_cache = {}
def fpgeom(spec):
    if spec in _cache: return _cache[spec]
    lib, name = spec.split(':')
    path = os.path.join(ROOT, 'lib', 'Hauptplatine.pretty') if lib == 'Hauptplatine' else '/usr/share/kicad/footprints/%s.pretty' % lib
    f = pcbnew.FootprintLoad(path, name)
    if f is None: raise SystemExit('Footprint fehlt: ' + spec)
    pads = []
    for p in f.Pads():
        q = p.GetPosition()
        pads.append((p.GetNumber(), pcbnew.ToMM(q.x), pcbnew.ToMM(q.y), p.GetAttribute() in (pcbnew.PAD_ATTRIB_PTH,), pcbnew.ToMM(p.GetSizeX()), pcbnew.ToMM(p.GetSizeY())))
    cy = f.GetCourtyard(pcbnew.F_CrtYd).BBox()
    if cy.GetWidth() > 0:
        bb = (pcbnew.ToMM(cy.GetLeft()), pcbnew.ToMM(cy.GetRight()), pcbnew.ToMM(cy.GetTop()), pcbnew.ToMM(cy.GetBottom()))
    else:
        xs = [p[1] - p[4] / 2 for p in pads] + [p[1] + p[4] / 2 for p in pads]; ys = [p[2] - p[5] / 2 for p in pads] + [p[2] + p[5] / 2 for p in pads]
        bb = (min(xs) - 0.25, max(xs) + 0.25, min(ys) - 0.25, max(ys) + 0.25)
    _cache[spec] = dict(pads=pads, bb=bb)
    return _cache[spec]

def to_view(state, x_fp, y_fp):
    x, y, th, side = state
    u, v = x_fp, -y_fp
    if side == 'B': u = -u
    a, b = rot(u, v, th)
    return (x + a, y + b)

