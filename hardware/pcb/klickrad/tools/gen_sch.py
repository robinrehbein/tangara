#!/usr/bin/env python3
"""Erzeugt klickrad.kicad_sch (KiCad 9) aus netlist.py. Symbole werden aus den KiCad-Standardbibliotheken eingebettet."""
import math, os, sys, uuid
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import netlist, sx
ROOT = netlist.ROOT
NS = uuid.UUID('6b1f4b52-0c1e-4c8b-9a0e-6b2d7a3a1111')
def U(name): return str(uuid.uuid5(NS, name))
ROOT_UUID = U('root')
SYMDIR = '/usr/share/kicad/symbols/'

def extract(lib, name):
    t = open(SYMDIR + lib + '.kicad_sym').read()
    key = '\n\t(symbol "%s"' % name
    i = t.index(key) + 1
    d, k = 0, i
    while True:
        c = t[k]
        if c == '(': d += 1
        elif c == ')':
            d -= 1
            if d == 0: break
        elif c == '"': k = t.index('"', k + 1)
        k += 1
    txt = t[i:k + 1]
    assert 'extends' not in txt.split('\n')[1], name
    return txt.replace('(symbol "%s"' % name, '(symbol "%s:%s"' % (lib, name), 1)

out = []
def w(s): out.append(s)
nid = [0]
def uid(): nid[0] += 1; return U('e%d' % nid[0])

def fmt(v): return ('%.4f' % v).rstrip('0').rstrip('.')
def wire(a, b): w(f'\t(wire (pts (xy {fmt(a[0])} {fmt(a[1])}) (xy {fmt(b[0])} {fmt(b[1])})) (stroke (width 0) (type default)) (uuid "{uid()}"))')
def junction(p): w(f'\t(junction (at {fmt(p[0])} {fmt(p[1])}) (diameter 0) (color 0 0 0 0) (uuid "{uid()}"))')
def text(s, x, y, size=1.27, bold=False):
    w(f'\t(text "{s}" (exclude_from_sim no) (at {fmt(x)} {fmt(y)} 0) (effects (font (size {size} {size}){" bold" if bold else ""}) (justify left bottom)) (uuid "{uid()}"))')
def label(name, p, ang):
    just = {0: 'left', 180: 'right', 90: 'left', 270: 'right'}[ang]
    w(f'\t(global_label "{name}" (shape passive) (at {fmt(p[0])} {fmt(p[1])} {ang}) (fields_autoplaced yes) (effects (font (size 1.27 1.27)) (justify {just})) (uuid "{uid()}")')
    w(f'\t\t(property "Intersheetrefs" "${{INTERSHEET_REFS}}" (at {fmt(p[0])} {fmt(p[1])} 0) (effects (font (size 1.27 1.27)) (hide yes)))')
    w('\t)')

refs = {}
def snap(v): return round(v / 1.27) * 1.27
def symbol(lib, ref, value, pos, rot=0, fp='', props=None, dnp=False, bom=True, hide_ref=False, pinnums=(), ref_off=None, val_off=None, hide_val=False):
    x, y = snap(pos[0]), snap(pos[1])
    pr = [('Reference', ref, True), ('Value', value, True), ('Footprint', fp, False), ('Datasheet', '', False)]
    for k, v in (props or {}).items(): pr.append((k, v, False))
    w(f'\t(symbol (lib_id "{lib}") (at {fmt(x)} {fmt(y)} {rot}) (unit 1) (exclude_from_sim no) (in_bom {"yes" if bom else "no"}) (on_board yes) (dnp {"yes" if dnp else "no"}) (uuid "{U("sym"+ref+str(x)+str(y))}")')
    for k, v, vis in pr:
        hide = '' if vis and not (hide_ref and k == 'Reference') and not (hide_val and k == 'Value') else ' (hide yes)'
        dx, dy = (3.0, -2.54) if k == 'Reference' else ((3.0, 2.54) if k == 'Value' else (3.0, 0))
        if k == 'Reference' and ref_off: dx, dy = ref_off
        if k == 'Value' and val_off: dx, dy = val_off
        w(f'\t\t(property "{k}" "{v}" (at {fmt(x + dx)} {fmt(y + dy)} 0) (effects (font (size 1.27 1.27)) (justify left){hide}))')
    for n in pinnums: w(f'\t\t(pin "{n}" (uuid "{U("pin"+ref+n)}"))')
    w(f'\t\t(instances (project "klickrad" (path "/{ROOT_UUID}" (reference "{ref}") (unit 1))))')
    w('\t)')

pw = [0]
def power(kind, value, p, rot=0):
    """kind: GND oder +3V3 (Netzname = value)."""
    pw[0] += 1
    symbol('power:' + kind, f'#PWR{pw[0]:02d}', value, p, rot, bom=False, hide_ref=True, pinnums=('1',), hide_val=rot not in (0, 180))
def pwrflag(p):
    pw[0] += 1
    symbol('power:PWR_FLAG', f'#FLG{pw[0]:02d}', 'PWR_FLAG', p, 0, bom=False, hide_ref=True, pinnums=('1',), hide_val=True)

def stub(p, outward, net, flag=False):
    p = (round(p[0], 4), round(p[1], 4))
    """2,54 mm Leitung vom Pin nach außen, dann Netzlabel bzw. Leistungssymbol."""
    dx, dy = {0: (1, 0), 180: (-1, 0), 90: (0, -1), 270: (0, 1)}[outward]   # Blatt: y nach unten, 90 = oben
    e = (p[0] + dx * 2.54, p[1] + dy * 2.54)
    wire(p, e)
    if net in ('GND', '3V3') and outward in (0, 180):
        label(net, e, outward)
    elif net in ('GND', '3V3'):
        # Leistungssymbole: aufrecht (Pin oben/unten) bzw. seitlich gedreht
        if net == '3V3':
            rot = {90: 0, 270: 180, 180: 90, 0: 270}[outward]
            power('+3V3', '3V3', e, rot)
        else:
            rot = {270: 0, 90: 180, 180: 270, 0: 90}[outward]
            power('GND', 'GND', e, rot)
        if flag: pwrflag(e)
    else:
        label(net, e, outward)
    return e
def pwrflag_at(e):
    pass

def pin_sheet(lib_pins, num, pos):
    pos = (snap(pos[0]), snap(pos[1]))
    for (n, nm, px, py, ang, typ) in lib_pins:
        if n == num: return (pos[0] + px, pos[1] - py), (int(ang) + 180) % 360
    raise KeyError(num)
def outward_sheet(a):  # Bibliothekswinkel (y nach oben) -> Blattwinkel für stub()
    return {0: 0, 180: 180, 90: 90, 270: 270}[a]

parts = {p['ref']: p for p in netlist.parts()}
OFFS = {'U1': dict(ref_off=(-12, -26), val_off=(-12, 28)), 'U2': dict(ref_off=(-12, -18), val_off=(-12, 20)), 'J1': dict(ref_off=(0, -12), val_off=(0, 12)),
        'SW1': dict(ref_off=(-3, -5), val_off=(-3, 4))}
for k in range(12): OFFS[f'SEG{k+1}'] = dict(ref_off=(2, -1), hide_val=True)
LIBS = [('Sensor_Touch', 'MPR121QR2'), ('Driver_Haptic', 'DRV2605LDGS'), ('Device', 'C'), ('Device', 'R'), ('Switch', 'SW_Push'),
        ('Connector_Generic', 'Conn_01x06'), ('Connector', 'TestPoint'), ('power', 'GND'), ('power', '+3V3'), ('power', 'PWR_FLAG')]
PINS = {f'{l}:{n}': sx.pins(sx.sym(l, n)) for l, n in LIBS}

w('(kicad_sch')
w('\t(version 20250114)')
w('\t(generator "eeschema")')
w('\t(generator_version "9.0")')
w(f'\t(uuid "{ROOT_UUID}")')
w('\t(paper "A3")')
w('\t(title_block (title "Klickrad-Modul v1") (date "2026-10-04") (rev "1") (company "Nano-Player (Hobbyprojekt)")')
w('\t\t(comment 1 "MPR121 (0x5B) + DRV2605L (0x5A, LRA) + Taster, JST-SH 6-pol.")')
w('\t\t(comment 2 "Schnittstelle laut TEILE.md, Abschnitt Klickrad-Modul"))')
w('\t(lib_symbols')
for l, n in LIBS: w(extract(l, n))
w('\t)')

def place(ref, pos, rot=0, **kw):
    kw = dict(OFFS.get(ref, {}), **kw)
    p = parts[ref]
    props = {}
    if p.get('mpn'): props['MPN'] = p['mpn']
    if p.get('mfr'): props['Hersteller'] = p['mfr']
    if p.get('desc'): props['Beschreibung'] = p['desc']
    symbol(p['sym'], ref, p['value'], pos, rot, fp=p['fp'], props=props, dnp=p.get('dnp', False), bom=not p.get('nobom'),
           pinnums=sorted(p['pins'].keys(), key=lambda s: int(s) if s.isdigit() else 999), **kw)
    return p

def conn_pins(ref, pos, sidefn=None):
    """Alle Pins des Bauteils mit Stummel+Label/Leistungssymbol versehen."""
    p = parts[ref]; lp = PINS[p['sym']]
    for num, netname in p['pins'].items():
        spos, outw = pin_sheet(lp, num, pos)
        if sidefn: outw = sidefn(num, outw)
        stub(spos, outw, netname)

# ---- MPR121
place('U1', (110.0, 100.0)); conn_pins('U1', (110.0, 100.0))
text('MPR121 (QFN-20): ADDR an VDD = I2C 0x5B, REXT 75k, VREG 0,1uF', 80, 64, 1.5, True)
# Entkopplung MPR121 (Reihe darunter)
x0 = 70.0
for i, ref in enumerate(('C1', 'C3', 'C2', 'R1')):
    pos = (x0 + i * 15.24, 148.0); place(ref, pos)
    p = parts[ref]; lp_ = PINS[p['sym']]
    for num, netname in p['pins'].items():
        spos, outw = pin_sheet(lp_, num, pos)
        stub(spos, outw, netname, flag=(ref == 'C1' and netname in ('3V3', 'GND')))
text('MPR121 Entkopplung / REXT / VREG', 68, 138, 1.27, True)
# ---- Taster
place('SW1', (60.0, 60.0)); conn_pins('SW1', (60.0, 60.0))
text('Mitteltaste (aktiv low, Pull-up auf MCU-Seite)', 48, 52, 1.27, True)
# ---- Stecker
jpos = (40.0, 110.0); place('J1', jpos)
lp = PINS[parts['J1']['sym']]
for num, netname in parts['J1']['pins'].items():
    spos, outw = pin_sheet(lp, num, jpos)
    e = stub(spos, outw, netname)
text('J1 JST-SH 6-pol. (SM06B-SRSS-TB)', 18, 94, 1.27, True)
# ---- DRV2605L
place('U2', (215.0, 100.0)); conn_pins('U2', (215.0, 100.0))
text('DRV2605L (MSOP-10): I2C 0x5A, LRA-Modus, EN fest an 3V3, IN/TRIG an GND', 188, 64, 1.5, True)
for i, ref in enumerate(('C4', 'C6', 'C5')):
    pos = (190.0 + i * 15.24, 148.0); place(ref, pos); conn_pins(ref, pos)
text('DRV2605L Entkopplung (VDD 1uF + 10uF, REG 1uF)', 188, 138, 1.27, True)
# LRA-Pads
for i, ref in enumerate(('TP1', 'TP2')):
    pos = (255.0 + i * 15.24, 100.0)
    place(ref, pos)
    stub((snap(pos[0]), snap(pos[1])), 270, parts[ref]['pins']['1'])
text('Loetpads LRA-Litzen (Rueckseite)', 250, 92, 1.27, True)
# ---- Pull-ups (DNP)
for i, ref in enumerate(('R2', 'R3')):
    pos = (110.0 + i * 15.24, 185.0); place(ref, pos); conn_pins(ref, pos)
text('I2C-Pull-ups 4,7k: DNP (Hauptboard hat 2,2k). Nur bestuecken, wenn Modul allein getestet wird.', 100, 174, 1.27, True)
# ---- Segmente
sm = netlist.seg_map()
for k in range(12):
    col, row = k % 6, k // 6
    pos = (230.0 + col * 15.24, 40.0 + row * 28)
    place(f'SEG{k+1}', pos)
    stub((snap(pos[0]), snap(pos[1])), 270, f'ELE{sm[k]}')
    text(f'S{k+1} {15+30*k}deg', pos[0] - 4, pos[1] - 4, 1.0)
text('Touch-Segmente (Kupfer vorn, Mitte Winkel 0 = rechts, gegen den Uhrzeigersinn)', 228, 30, 1.27, True)
w('\t(sheet_instances (path "/" (page "1")))')
w('\t(embedded_fonts no)')
w(')')
open(os.path.join(ROOT, 'klickrad.kicad_sch'), 'w').write('\n'.join(out) + '\n')
print('ok')
