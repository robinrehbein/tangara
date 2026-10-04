#!/usr/bin/env python3
"""Erzeugt lib/Hauptplatine.pretty mit den Footprints, die nicht in den KiCad-Standardbibliotheken stehen.

1. S31-ESP32-S3-Plus-SMD
   Quelle: Seeed Studio "New_S31_Series_Footprints.zip" (XIAO-ESP32-S3-Plus-SMD.kicad_mod), Pad-Positionen 1:1
   uebernommen (Kopie der Originaldatei in quellen/). Aenderungen gegenueber dem Original:
   * nur die Randpads 1-23 und die Akkupads 32 (VBAT) / 33 (GND) bleiben; Pads 24-31 (acht Test-/USB-/JTAG-Pads
     auf der Modulunterseite) und Pad 34 (Zweck unklar) entfallen: sie werden nicht verloetet
   * Akkupads auf die Padgroesse der Modulunterseite (2,03 x 1,02 mm laut Seeed-PCB) verkleinert
   * Bezeichnungen, Silkscreen, Courtyard neu; Originaldatei ist im KiCad-10-Format, daher neu geschrieben
   Koordinaten: Footprint-Ursprung = Modulmitte, USB-C an +x, Modul 21,0 x 17,8 mm (Pads x -10,4 ... +10,55).

2. FPC-AXE534124 (Panasonic AXE5, 34 Kontakte, 0,4 mm, Gegenstueck auf dem Display-FPC).
   ACHTUNG: Landmuster NICHT nach Herstellerzeichnung, sondern aus den Eckdaten abgeleitet (Panasonic-Produktseite:
   Korpus 9,30 mm lang, 2,50 mm breit, 0,77 hoch, empfohlene Leiterplattenbreite 2,90 mm). Vor Bestellung gegen die
   Panasonic-Zeichnung pruefen!
"""
import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'lib', 'Hauptplatine.pretty')
os.makedirs(OUT, exist_ok=True)

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

# ---------------------------------------------------------------- FPC-Buchse
def fpc34():
    s = HEAD % ('FPC-AXE534124', 'Panasonic AXE534124 34 Pol 0,4 mm Board-to-FPC-Buchse, Landmuster ABGELEITET (ungeprueft)',
                'FPC 34 0.4mm Panasonic AXE5')
    s += prop('Reference', 'REF**', 0, -3.5, 'F.SilkS') + prop('Value', 'AXE534124', 0, 3.5, 'F.Fab')
    s += prop('Datasheet', 'https://industry.panasonic.com/global/en/products/control/connector/base-fpc/number/axe534124', 0, 0, 'F.Fab', True)
    s += '\t(attr smd)\n'
    pitch, ypad, pw, ph = 0.4, 1.10, 0.20, 0.70
    for k in range(17):
        x = -3.2 + pitch * k
        s += pad(2 * k + 1, x, -ypad, pw, ph, 'rect')     # ungerade Pins: obere Reihe (y negativ = oben auf dem Blatt)
        s += pad(2 * k + 2, x, ypad, pw, ph, 'rect')      # gerade Pins: untere Reihe
    for i, (x, y) in enumerate(((-4.30, -1.45), (4.30, -1.45), (-4.30, 1.45), (4.30, 1.45))):
        s += pad(35 + i, x, y, 0.6, 0.9, 'rect')          # Schirm-/Halte-Laschen -> GND
    s += rect(-4.65, -1.25, 4.65, 1.25, 'F.Fab', 0.1)
    s += rect(-4.95, -2.2, 4.95, 2.2, 'F.CrtYd', 0.05)
    s += line(-5.05, -2.0, -5.05, 2.0, 'F.SilkS', 0.12)
    s += text('1', -3.2, -2.6, 'F.SilkS', 0.8)
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
    s += line(-1.15, -0.95, -1.15, -0.45, 'F.SilkS', 0.12)   # Pin-1-Seite (oben rechts liegt Pin 1; Marke links oben)
    s += ')\n'
    return s

import shutil
def copy_tangara():
    """Footprints aus der Tangara-Hardware (CERN-OHL-S-2.0) unveraendert uebernehmen."""
    for fn in ('CUI_SJ-3506-SMT', 'GCT_USB4510-03-1-A_REVA', 'SON40P300X300X80-13N', 'SOT65P210X110-6N'):
        shutil.copy(os.path.join(ROOT, 'quellen', fn + '.kicad_mod'), os.path.join(OUT, fn + '.kicad_mod'))

def copy_espressif():
    """ESP32-S31-WROOM-3 aus github.com/espressif/kicad-libraries (CC-BY-SA 4.0 mit Ausnahme fuer Designs); KiCad-10-Format -> KiCad-9-Format."""
    src = os.path.join(ROOT, 'quellen', 'Espressif_ESP32-S31-WROOM-3_original.kicad_mod')
    t = open(src).read()
    t = t.replace('(version 20260206)', '(version 20241229)').replace('(generator_version "10.0")', '(generator_version "9.0")')
    t = re.sub(r'\n\t\(duplicate_pad_numbers_are_jumpers[^\n]*', '', t)
    t = re.sub(r'\n\t\t\(unlocked yes\)', '', t)
    open(os.path.join(OUT, 'ESP32-S31-WROOM-3.kicad_mod'), 'w').write(t)

import re
for name, fn in (('FPC-AXE534124', fpc34), ('X2QFN-12-RWB', x2qfn)):
    with open(os.path.join(OUT, name + '.kicad_mod'), 'w') as f:
        f.write(fn())
copy_tangara(); copy_espressif()
print('Footprints geschrieben:', sorted(os.listdir(OUT)))
