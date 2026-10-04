#!/usr/bin/env python3
"""Erzeugt die Projektbibliothek: lib/Klickrad.pretty (Touch-Elektroden, Befestigungsloch) und lib/Klickrad.kicad_sym (AT42QT2120 von Tangara)."""
import os, re, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wheel_geometry as G
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'lib', 'Klickrad.pretty')
TANGARA_SYM = '/home/user/tangara-ref/tangara-hw/tangara-faceplate/faceplate-symbols.kicad_sym'
os.makedirs(OUT, exist_ok=True)

# Lage der Durchkontaktierungen (Mitte der Pads) -> von layout.py ebenfalls benutzt
def pad_points():
    b = G.build()
    pts = {}
    want = {0: 172.0, 1: 10.0, 2: 55.0}      # Winkel der Durchkontaktierungen (Frontansicht)
    taken = []
    for k in (1, 0, 2):
        pts[('W', k)] = G.inner_point(b['wheel'][k], 6.5, 12.0, want[k], margin=0.33, span=100, taken=taken)
        assert pts[('W', k)], k
        taken.append(pts[('W', k)])
    pts[('B', 0)] = (0.45, 3.1)                       # Mitteltaste: Via oberhalb von U1/R4 (r = 2,98 < 3,5 - 0,3)
    return pts

def poly_pad(num, cx, cy, poly, name_layer='F.Cu'):
    coords = list(poly.exterior.coords)[:-1]
    s = ' '.join('(xy %.4f %.4f)' % (x - cx, -(y - cy)) for x, y in coords)   # KiCad-Footprint: y nach unten
    return (f'\t(pad "{num}" smd custom (at {cx:.4f} {-cy:.4f}) (size 0.3 0.3) (layers "{name_layer}")\n'
            f'\t\t(options (clearance outline) (anchor circle))\n'
            f'\t\t(primitives (gr_poly (pts {s}) (width 0) (fill yes))))\n')

def fp_head(name, descr):
    return (f'(footprint "{name}"\n\t(version 20241229)\n\t(generator "make_lib.py")\n\t(layer "F.Cu")\n\t(descr "{descr}")\n'
            f'\t(attr smd exclude_from_pos_files exclude_from_bom)\n'
            f'\t(property "Reference" "REF**" (at 0 0 0) (layer "F.SilkS") (hide yes) (effects (font (size 1 1) (thickness 0.15))))\n'
            f'\t(property "Value" "{name}" (at 0 0 0) (layer "F.Fab") (hide yes) (effects (font (size 1 1) (thickness 0.15))))\n'
            f'\t(property "Footprint" "" (at 0 0 0) (layer "F.Fab") (hide yes) (effects (font (size 1 1) (thickness 0.15))))\n')

def make(vias):
    b = G.build()
    t = fp_head('qtouch-wheel', 'Interpolierter Touch-Wheel (3 Elektroden, 3 Ringe) nach Tangara qtouch-wheel, auf r = 6,3 ... 12,3 mm skaliert. Pad k = KEY k. Lötstopplack bleibt geschlossen.')
    for k in range(3):
        cx, cy = vias[('W', k)]
        t += poly_pad(k + 1, cx, cy, b['wheel'][k])
    open(OUT + '/qtouch-wheel.kicad_mod', 'w').write(t + ')\n')
    t = fp_head('qtouch-button', 'Kapazitive Mitteltaste (Scheibe), nach Tangara qtouch-button, Radius %.1f mm' % G.BTN_R)
    cx, cy = vias[('B', 0)]
    t += poly_pad(1, cx, cy, b['button'])
    open(OUT + '/qtouch-button.kicad_mod', 'w').write(t + ')\n')
    t = fp_head('qtouch-guard', 'Guard-Kanal: drei Kreisbögen außen zwischen den Befestigungslöchern, innen durch zwei schmale Stege verbunden (Tangara: Ring r = 22,2 mm), ein Pad')
    cx, cy = vias[('G', 0)]
    t += poly_pad(1, cx, cy, b['guard'])
    open(OUT + '/qtouch-guard.kicad_mod', 'w').write(t + ')\n')
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

def make_symbols():
    t = open(TANGARA_SYM).read()
    i = t.index('(symbol "AT42QT2120"')
    d, k = 0, i
    while True:
        c = t[k]
        if c == '(': d += 1
        elif c == ')':
            d -= 1
            if d == 0: break
        elif c == '"': k = t.index('"', k + 1)
        k += 1
    sym = t[i:k + 1]
    sym = sym.replace('(property "Footprint" "MODULE"', '(property "Footprint" "Package_DFN_QFN:VQFN-20-1EP_3x3mm_P0.45mm_EP1.55x1.55mm"')
    sym = sym.replace('(property "Datasheet" "DOCUMENTATION"', '(property "Datasheet" "https://ww1.microchip.com/downloads/en/DeviceDoc/Atmel-9634-AT42-QTouch-Sensor-AT42QT2120_Datasheet.pdf"')
    out = ('(kicad_symbol_lib (version 20220914) (generator kicad_symbol_editor)\n'
           '  ' + sym + '\n)\n')
    open(os.path.join(ROOT, 'lib', 'Klickrad.kicad_sym'), 'w').write(out)

if __name__ == '__main__':
    import json
    b = G.build(); vias = {k: v for k, v in pad_points().items() if v}
    from shapely.geometry import Point
    vias[('G', 0)] = (round(14.2 * math.cos(math.radians(150)), 2), round(14.2 * math.sin(math.radians(150)), 2))     # Guard-Via oben links (nahe R5)
    assert b['guard'].contains(Point(*vias[('G', 0)]))
    json.dump({f'{k[0]}{k[1]}': v for k, v in vias.items()}, open(os.path.join(ROOT, 'tools', 'vias_touch.json'), 'w'), indent=1)
    make(vias); make_symbols(); __import__("subprocess").run(["kicad-cli", "sym", "upgrade", os.path.join(ROOT, "lib", "Klickrad.kicad_sym")], check=False, capture_output=True); print('ok', vias)
