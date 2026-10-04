#!/usr/bin/env python3
"""Erzeugt lib/Tangara.pretty mit den Footprints, die nicht in den KiCad-Standardbibliotheken stehen.

1. XIAO-ESP32-S3-Plus-SMD
   Quelle: Seeed Studio "New_XIAO_Series_Footprints.zip" (XIAO-ESP32-S3-Plus-SMD.kicad_mod), Pad-Positionen 1:1
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
OUT = os.path.join(ROOT, 'lib', 'Tangara.pretty')
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

# ---------------------------------------------------------------- XIAO
def xiao():
    s = HEAD % ('XIAO-ESP32-S3-Plus-SMD', 'Seeed XIAO ESP32S3 Plus als SMD-Modul (Randpads + Akkupads), Quelle: Seeed New_XIAO_Series_Footprints',
                'XIAO ESP32S3 Plus Seeed')
    s += prop('Reference', 'REF**', 0, -10.5, 'F.SilkS') + prop('Value', 'XIAO-ESP32-S3-Plus-SMD', 0, 10.5, 'F.Fab')
    s += prop('Datasheet', 'https://wiki.seeedstudio.com/xiao_esp32s3_getting_started/', 0, 0, 'F.Fab', True)
    s += '\t(attr smd)\n'
    # Randpads (Seeed: 2,032 x 0,95 rotiert; hier direkt als 0,95 x 2,032)
    xs = [7.62, 5.08, 2.54, 0, -2.54, -5.08, -7.62]
    for i, x in enumerate(xs):                      # Pads 1-7  (D0..D6)  y = -8,255
        s += pad(i + 1, x, -8.255, 0.95, 2.032)
    for i, x in enumerate(xs):                      # Pads 8-14 (D7..D10, 3V3, GND, 5V)  x laeuft von -7,62 nach +7,62
        s += pad(8 + i, -x, 8.255, 0.95, 2.032)
    for i, x in enumerate((6.35, 3.81, 1.27, -1.27, -3.81, -6.35)):   # Pads 15-20 (D11..D16)  y = -8,655
        s += pad(15 + i, x, -8.655, 0.95, 1.232)
    for i, x in enumerate((-6.35, -3.81, -1.27)):   # Pads 21-23 (D19, D18, D17)  y = +8,655
        s += pad(21 + i, x, 8.655, 0.95, 1.232)
    # Akkupads auf der Modulunterseite (Seeed-PCB: BAT+ -0,99/5,03 und GND 1,01/5,03, je 2,03 x 1,02, im Modulrahmen)
    s += pad(32, -5.03, -0.994, 2.2, 1.1)
    s += pad(33, -5.03, 1.006, 2.2, 1.1)
    # Umriss Modul
    s += rect(-10.414, -8.89, 10.541, 8.89, 'F.Fab', 0.1)
    s += rect(-10.6, -9.5, 10.75, 9.5, 'F.CrtYd', 0.05)
    s += line(10.541, -4.5, 12.05, -4.0, 'F.Fab') + line(12.05, -4.0, 12.05, 4.0, 'F.Fab') + line(12.05, 4.0, 10.541, 4.5, 'F.Fab')
    s += rect(10.6, -4.6, 12.3, 4.6, 'F.CrtYd', 0.05)
    s += line(-10.5, -9.3, -10.5, -7.0, 'F.SilkS', 0.15) + line(-10.5, 9.3, -10.5, 7.0, 'F.SilkS', 0.15)
    s += line(10.75, -9.3, 10.75, -7.0, 'F.SilkS', 0.15) + line(10.75, 9.3, 10.75, 7.0, 'F.SilkS', 0.15)
    s += text('USB-C >', 8.0, 0, 'F.SilkS', 0.8) + text('1', 7.62, -10.3, 'F.SilkS', 0.8)
    s += text('BAT+', -5.03, -3.0, 'F.SilkS', 0.6) + text('BAT-', -5.03, 3.0, 'F.SilkS', 0.6)
    s += text('U.FL', -8.75, -3.44, 'F.Fab', 0.6)
    s += ')\n'
    return s

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

for name, fn in (('XIAO-ESP32-S3-Plus-SMD', xiao), ('FPC-AXE534124', fpc34)):
    with open(os.path.join(OUT, name + '.kicad_mod'), 'w') as f:
        f.write(fn())
print('Footprints geschrieben:', os.listdir(OUT))
