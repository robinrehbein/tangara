#!/usr/bin/env python3
"""Erzeugt lib/Hauptplatine.pretty mit den Footprints, die nicht in den KiCad-Standardbibliotheken stehen.

1. ESP32-S31-WROOM-1 (selbst erzeugt)
   Landmuster nach Datenblatt ESP32-S31-WROOM-1 v0.5, Abb. 10-1 (Modul) und 11-1 (Landmuster); Masse aus der Zeichnung gelesen. Der Espressif-KiCad-Bibliothek
   fehlt dieses Modul (nur WROOM-3 vorhanden). Pads: 40 Randpads 1,5 x 0,9 (Raster 1,27), im Feld 20 kleine Pads 0,4 x 0,8 (Raster 0,8, Pins 42-61) und
   3 x 3 Masse-Pads 0,9 x 0,9 (Pin 41, Raster 1,4). Antennenzone: Sperrfläche (alle Kupferlagen) 18,6 x 7,6 mm.  UNGEPRUEFT gegen die Espressif-Zeichnung.
2. X2QFN-12-RWB (TUSB320, TI RWB0012A) - Landmuster nach TI-Beispiel.
3. CUI_SJ-43504-SMT-TR (Tangara-Bibliothek, CERN-OHL-S-2.0) - Pads auf 1,45 mm verschmaelert, Zapfenloecher entfernt (liegen im Randausschnitt).
4. GCT_USB4510-03-1-A_REVA, SOT65P210X110-6N (Tangara, unveraendert).
5. BATT_PADS_3 (Akkulitzen), MountingHole_1.8mm (M1,6).
"""
import os, re, shutil
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'lib', 'Hauptplatine.pretty')
os.makedirs(OUT, exist_ok=True)
for f in os.listdir(OUT): os.remove(os.path.join(OUT, f))

HEAD = '(footprint "%s"\n\t(version 20241229)\n\t(generator "tangara_make_lib")\n\t(generator_version "9.0")\n\t(layer "F.Cu")\n\t(descr "%s")\n\t(tags "%s")\n'

def prop(name, val, x, y, layer, hide=False, size=1.0):
    return (f'\t(property "{name}" "{val}"\n\t\t(at {x} {y} 0)\n\t\t(layer "{layer}")\n'
            + ('\t\t(hide yes)\n' if hide else '') +
            f'\t\t(effects\n\t\t\t(font\n\t\t\t\t(size {size} {size})\n\t\t\t\t(thickness 0.15)\n\t\t\t)\n\t\t)\n\t)\n')

def line(x0, y0, x1, y1, layer, w=0.12):
    return f'\t(fp_line\n\t\t(start {x0} {y0})\n\t\t(end {x1} {y1})\n\t\t(stroke\n\t\t\t(width {w})\n\t\t\t(type solid)\n\t\t)\n\t\t(layer "{layer}")\n\t)\n'

def rect(x0, y0, x1, y1, layer, w=0.12):
    return ''.join(line(a, b, c, d, layer, w) for a, b, c, d in
                   ((x0, y0, x1, y0), (x1, y0, x1, y1), (x1, y1, x0, y1), (x0, y1, x0, y0)))

def text(s, x, y, layer, size=0.8, rot=0):
    return (f'\t(fp_text user "{s}"\n\t\t(at {x} {y} {rot})\n\t\t(layer "{layer}")\n'
            f'\t\t(effects\n\t\t\t(font\n\t\t\t\t(size {size} {size})\n\t\t\t\t(thickness 0.12)\n\t\t\t)\n\t\t)\n\t)\n')

def pad(num, x, y, w, h, shape='roundrect', rr=0.1, rot=0, extra=''):
    r = f'\t\t(roundrect_rratio {rr})\n' if shape == 'roundrect' else ''
    return (f'\t(pad "{num}" smd {shape}\n\t\t(at {x} {y}{" " + str(rot) if rot else ""})\n\t\t(size {w} {h})\n'
            f'\t\t(layers "F.Cu" "F.Mask" "F.Paste")\n{r}{extra}\t)\n')

# ---------------------------------------------------------------- ESP32-S31-WROOM-1
def wroom1():
    s = HEAD % ('ESP32-S31-WROOM-1', 'Espressif ESP32-S31-WROOM-1, Landmuster nach Datenblatt v0.5 (selbst erzeugt, ungeprueft)', 'esp32-s31 wroom-1')
    s += prop('Reference', 'REF**', 0, -14.8, 'F.SilkS') + prop('Value', 'ESP32-S31-WROOM-1', 0, 14.5, 'F.Fab')
    s += prop('Datasheet', 'https://documentation.espressif.com/esp32-s31-wroom-1_wroom-1u_datasheet_en.pdf', 0, 0, 'F.Fab', True)
    s += '\t(attr smd)\n'
    def p(num, x, y, w, h): return pad(num, round(x, 3), round(y, 3), w, h, 'rect')
    for n in range(1, 15): s += p(n, -8.75, -5.26 + (n - 1) * 1.27, 1.5, 0.9)
    for n in range(15, 27): s += p(n, -6.985 + (n - 15) * 1.27, 12.5, 0.9, 1.5)
    for n in range(27, 41): s += p(n, 8.75, 11.25 - (n - 27) * 1.27, 1.5, 0.9)
    cx, cy = -1.5, 2.46       # Mitte des Masse-Feldes (KiCad-y nach unten)
    for n in range(42, 50): s += p(n, cx + 2.8 - (n - 42) * 0.8, cy - 2.6, 0.4, 0.8)
    for n in range(50, 56): s += p(n, cx - 2.6, cy - (1.6 - (n - 50) * 0.8), 0.8, 0.4)
    for n in range(61, 55, -1): s += p(n, cx + 2.6, cy - (1.6 - (61 - n) * 0.8), 0.8, 0.4)
    for dx in (-1.4, 0, 1.4):
        for dy in (-1.4, 0, 1.4): s += p(41, cx + dx, cy + dy, 0.9, 0.9)
    s += rect(-9.0, -12.75, 9.0, 12.75, 'F.Fab', 0.1) + rect(-9.25, -13.0, 9.25, 13.0, 'F.CrtYd', 0.05)
    s += line(-9.0, -6.75, 9.0, -6.75, 'F.SilkS', 0.12) + text('Antenne', 0, -9.8, 'F.SilkS', 0.8)
    s += text('1', -10.4, -5.26, 'F.SilkS', 0.8)
    pts = ' '.join('(xy %s %s)' % pt for pt in ((-9.3, -14.0), (9.3, -14.0), (9.3, -6.4), (-9.3, -6.4)))
    s += ('\t(zone\n\t\t(layers "F.Cu" "B.Cu" "In1.Cu" "In2.Cu")\n\t\t(name "antenna keepout")\n\t\t(hatch edge 0.508)\n\t\t(connect_pads\n\t\t\t(clearance 0)\n\t\t)\n'
          '\t\t(min_thickness 0.254)\n\t\t(keepout\n\t\t\t(tracks not_allowed)\n\t\t\t(vias not_allowed)\n\t\t\t(pads not_allowed)\n\t\t\t(copperpour not_allowed)\n\t\t\t(footprints not_allowed)\n\t\t)\n'
          '\t\t(placement\n\t\t\t(enabled no)\n\t\t\t(sheetname "")\n\t\t)\n\t\t(fill\n\t\t\t(thermal_gap 0.508)\n\t\t\t(thermal_bridge_width 0.508)\n\t\t)\n'
          '\t\t(polygon\n\t\t\t(pts ' + pts + ')\n\t\t)\n\t)\n')
    s += ')\n'
    return s

# ---------------------------------------------------------------- X2QFN-12 (TI RWB0012A, TUSB320)
def x2qfn():
    s = HEAD % ('X2QFN-12-RWB', 'TI RWB0012A X2QFN-12 1,6 x 1,6 mm, Raster 0,4 mm; Landmuster nach TI-Beispiel (Datenblatt TUSB320LAI, Abschnitt Mechanical)', 'X2QFN 12 TI RWB')
    s += prop('Reference', 'REF**', 0, -1.7, 'F.SilkS', size=0.6) + prop('Value', 'X2QFN-12-RWB', 0, 1.7, 'F.Fab', size=0.6)
    s += '\t(attr smd)\n\t(clearance 0.09)\n'
    s += pad(1, 0.2, -0.4, 0.2, 0.7, 'rect') + pad(2, -0.2, -0.4, 0.2, 0.7, 'rect')
    for i, y in enumerate((-0.6, -0.2, 0.2, 0.6)):
        s += pad(3 + i, -0.65, y, 0.5, 0.2, 'rect')
    s += pad(7, -0.2, 0.4, 0.2, 0.7, 'rect') + pad(8, 0.2, 0.4, 0.2, 0.7, 'rect')
    for i, y in enumerate((0.6, 0.2, -0.2, -0.6)):
        s += pad(9 + i, 0.65, y, 0.5, 0.2, 'rect')
    s += rect(-0.8, -0.8, 0.8, 0.8, 'F.Fab', 0.1) + rect(-1.1, -1.1, 1.1, 1.1, 'F.CrtYd', 0.05)
    s += line(-1.15, -0.95, -1.15, -0.45, 'F.SilkS', 0.12)
    s += ')\n'
    return s

# ---------------------------------------------------------------- Akku-Loetpads
def battpads():
    s = HEAD % ('BATT_PADS_3', 'Loetpads fuer 3 Akkulitzen (NTC, GND, BAT+), Raster 2,0 mm', 'battery pads')
    s += prop('Reference', 'REF**', 0, -2.2, 'F.SilkS', size=0.8) + prop('Value', 'BATT_PADS_3', 0, 2.2, 'F.Fab', size=0.8)
    s += '\t(attr smd)\n'
    for i in range(3): s += pad(i + 1, (i - 1) * 2.0, 0, 1.5, 2.0, 'rect')
    s += rect(-3.1, -1.5, 3.1, 1.5, 'F.CrtYd', 0.05) + text('+', 2.0, -2.2, 'F.SilkS', 0.8)
    s += ')\n'
    return s

# ---------------------------------------------------------------- Befestigungsloch M1,6
def hole18():
    s = HEAD % ('MountingHole_1.8mm', 'Befestigungsloch M1,6 (NPTH 1,8 mm)', 'mounting hole')
    s += prop('Reference', 'REF**', 0, -2.5, 'F.SilkS', hide=True, size=0.8) + prop('Value', 'M1.6', 0, 2.5, 'F.Fab', hide=True, size=0.8)
    s += '\t(attr exclude_from_pos_files exclude_from_bom)\n'
    s += '\t(pad "" np_thru_hole circle\n\t\t(at 0 0)\n\t\t(size 1.8 1.8)\n\t\t(drill 1.8)\n\t\t(layers "*.Cu" "*.Mask")\n\t)\n'
    s += '\t(fp_circle\n\t\t(center 0 0)\n\t\t(end 1.7 0)\n\t\t(stroke\n\t\t\t(width 0.05)\n\t\t\t(type solid)\n\t\t)\n\t\t(fill none)\n\t\t(layer "F.CrtYd")\n\t)\n'
    s += ')\n'
    return s

# ---------------------------------------------------------------- Klinke SJ-43504-SMT-TR (Tangara-Bibliothek, angepasst)
def jack():
    t = open(os.path.join(ROOT, 'quellen', 'CUI_SJ-43504-SMT-TR.kicad_mod')).read()
    t = re.sub(r'  \(pad "" np_thru_hole[^\n]*\n', '', t)
    def fix(m):
        num, x, y = m.group(1), float(m.group(2)), m.group(3)
        nx = -0.15 if x < 1 else 8.5
        return '(pad "%s" smd rect (at %s %s) (size 1.45 2)' % (num, nx, y)
    t = re.sub(r'\(pad "([1-6])" smd rect \(at ([-0-9.]+) ([-0-9.]+)\) \(size 1\.75 2\)', fix, t)
    return t

for name, fn in (('X2QFN-12-RWB', x2qfn), ('ESP32-S31-WROOM-1', wroom1), ('BATT_PADS_3', battpads), ('MountingHole_1.8mm', hole18), ('CUI_SJ-43504-SMT-TR', jack)):
    with open(os.path.join(OUT, name + '.kicad_mod'), 'w') as f:
        f.write(fn())
for fn in ('GCT_USB4510-03-1-A_REVA', 'SOT65P210X110-6N'):
    shutil.copy(os.path.join(ROOT, 'quellen', fn + '.kicad_mod'), os.path.join(OUT, fn + '.kicad_mod'))
print('Footprints geschrieben:', sorted(os.listdir(OUT)))
