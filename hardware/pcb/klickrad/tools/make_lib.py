#!/usr/bin/env python3
"""Erzeugt die lokale Footprint-Bibliothek lib/Klickrad.pretty
(QFN ohne Exposed Pad, 12 Touch-Segmente, Befestigungsloch, LRA-Markierung)."""
import math, re, os
from shapely.geometry import Polygon
from shapely import affinity
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'lib', 'Klickrad.pretty')
os.makedirs(OUT, exist_ok=True)
KF = '/usr/share/kicad/footprints/'

R_IN, R_OUT, GAP, NSEG = 6.5, 12.8, 0.4, 12
VIA_R = 7.6
def seg_angle(k): return 15.0 + 30.0 * k       # Segmentmitte (Grad, 0 = rechts, CCW)

def strip_pads(txt, drop):
    out, i = [], 0
    while True:
        j = txt.find('\n\t(pad ', i)
        if j < 0: out.append(txt[i:]); break
        out.append(txt[i:j])
        d, k = 0, j + 1
        while True:
            c = txt[k]
            if c == '(': d += 1
            elif c == ')':
                d -= 1
                if d == 0: break
            elif c == '"':
                k = txt.index('"', k + 1)
            k += 1
        blk = txt[j:k + 1]
        m = re.match(r'\n\t\(pad "([^"]*)"', blk)
        if not (m and m.group(1) in drop): out.append(blk)
        i = k + 1
    return ''.join(out)

def make_qfn():
    t = open(KF + 'Package_DFN_QFN.pretty/QFN-20-1EP_3x3mm_P0.4mm_EP1.65x1.65mm.kicad_mod').read()
    t = strip_pads(t, {'', '21'})
    t = t.replace('QFN-20-1EP_3x3mm_P0.4mm_EP1.65x1.65mm', 'QFN-20_3x3mm_P0.4mm_noEP')
    t = re.sub(r'\(model .*?\n\t\)\n', '', t, flags=re.S)
    open(OUT + '/QFN-20_3x3mm_P0.4mm_noEP.kicad_mod', 'w').write(t)

def sector(a0, a1, r0, r1, n=10):
    pts = [(r1 * math.cos(math.radians(a0 + (a1 - a0) * i / n)), r1 * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]
    pts += [(r0 * math.cos(math.radians(a1 - (a1 - a0) * i / n)), r0 * math.sin(math.radians(a1 - (a1 - a0) * i / n))) for i in range(n + 1)]
    return Polygon(pts)

def make_segments():
    for k in range(NSEG):
        a = seg_angle(k)
        poly = sector(a - 15, a + 15, R_IN - GAP / 2, R_OUT + GAP / 2).buffer(-GAP / 2, join_style=2, mitre_limit=5)
        cx, cy = VIA_R * math.cos(math.radians(a)), VIA_R * math.sin(math.radians(a))
        pts = ' '.join('(xy %.4f %.4f)' % (x - cx, -(y - cy)) for x, y in list(poly.exterior.coords)[:-1])
        txt = f'''(footprint "SEG{k+1}"
	(version 20241229)
	(generator "make_lib.py")
	(layer "F.Cu")
	(descr "Touch-Segment {k+1}, Mitte {a:.0f} Grad, Kupfer ohne Lötstopplack-Öffnung")
	(attr smd exclude_from_pos_files exclude_from_bom)
	(property "Reference" "SEG{k+1}" (at 0 0 0) (layer "F.SilkS") (hide yes) (effects (font (size 1 1) (thickness 0.15))))
	(property "Value" "Touch" (at 0 0 0) (layer "F.Fab") (hide yes) (effects (font (size 1 1) (thickness 0.15))))
	(property "Footprint" "" (at 0 0 0) (layer "F.Fab") (hide yes) (effects (font (size 1 1) (thickness 0.15))))
	(pad "1" smd custom (at 0 0) (size 0.6 0.6) (layers "F.Cu")
		(options (clearance outline) (anchor circle))
		(primitives (gr_poly (pts {pts}) (width 0) (fill yes))))
)
'''
        open(OUT + f'/SEG{k+1}.kicad_mod', 'w').write(txt)

def make_misc():
    open(OUT + '/MountingHole_2.2mm_NPTH.kicad_mod', 'w').write('''(footprint "MountingHole_2.2mm_NPTH"
	(version 20241229)
	(generator "make_lib.py")
	(layer "F.Cu")
	(attr exclude_from_pos_files exclude_from_bom)
	(property "Reference" "H" (at 0 -2 0) (layer "F.SilkS") (hide yes) (effects (font (size 1 1) (thickness 0.15))))
	(property "Value" "M2" (at 0 2 0) (layer "F.Fab") (hide yes) (effects (font (size 1 1) (thickness 0.15))))
	(pad "" np_thru_hole circle (at 0 0) (size 2.2 2.2) (drill 2.2) (layers "*.Cu" "*.Mask"))
)
''')

if __name__ == '__main__':
    make_qfn(); make_segments(); make_misc(); print('ok')
