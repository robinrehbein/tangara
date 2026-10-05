#!/usr/bin/env python3
"""Erzeugt klickrad.kicad_sch (KiCad 9) aus netlist.py. Symbole werden aus den KiCad-Standardbibliotheken und lib/Klickrad.kicad_sym eingebettet."""
import math, os, sys, uuid
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import netlist, sx
ROOT = netlist.ROOT
NS = uuid.UUID('6b1f4b52-0c1e-4c8b-9a0e-6b2d7a3a1111')
def U(name): return str(uuid.uuid5(NS, name))
ROOT_UUID = U('root')
SYMDIR = '/usr/share/kicad/symbols/'

def extract(lib, name):
    t = open(sx.SYMFILE(lib)).read()
    import re
    i = re.search(r'\n[ \t]*\(symbol "%s"' % re.escape(name), t).start() + 1
    while t[i] in ' \t': i += 1
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
def noconnect(p): w(f'\t(no_connect (at {fmt(p[0])} {fmt(p[1])}) (uuid "{uid()}"))')
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
OFFS = {'U1': dict(ref_off=(-12, -30), val_off=(-12, 32)), 'U2': dict(ref_off=(-12, -18), val_off=(-12, 20)), 'J1': dict(ref_off=(0, -12), val_off=(0, 12)),
        'SW1': dict(ref_off=(3, -2), val_off=(3, 2)), 'SW2': dict(ref_off=(3, -4), val_off=(3, 4)), 'SW3': dict(ref_off=(3, -2), val_off=(3, 2))}
LIBS = [('Klickrad', 'AT42QT2120'), ('Driver_Haptic', 'DRV2605LDGS'), ('Device', 'C'), ('Device', 'R'), ('Connector_Generic', 'Conn_01x01'),
        ('Connector_Generic', 'Conn_01x03'), ('Connector_Generic', 'Conn_01x06'), ('Connector', 'TestPoint'), ('power', 'GND'), ('power', '+3V3'), ('power', 'PWR_FLAG')]
PINS = {f'{l}:{n}': sx.pins(sx.sym(l, n)) for l, n in LIBS}

w('(kicad_sch')
w('\t(version 20250114)')
w('\t(generator "eeschema")')
w('\t(generator_version "9.0")')
w(f'\t(uuid "{ROOT_UUID}")')
w('\t(paper "A3")')
w('\t(title_block (title "Klickrad-Modul v2") (date "2026-10-04") (rev "2") (company "Nano-Player (Hobbyprojekt)")')
w('\t\t(comment 1 "AT42QT2120 (0x1C, Wheel) + DRV2605L (0x5A, LRA), Beschaltung nach Tangara-Faceplate (CERN-OHL-S-2.0, cool tech zone)")')
w('\t\t(comment 2 "Schnittstelle laut TEILE.md, Abschnitt Klickrad-Modul; FFC 6-pol., Pin 5 = CHANGE, Pin 6 = Reserve"))')
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

def conn_pins(ref, pos, flag_ref=None):
    """Alle Pins des Bauteils mit Stummel+Label/Leistungssymbol bzw. No-Connect-Flag versehen."""
    p = parts[ref]; lp = PINS[p['sym']]
    for num, netname in p['pins'].items():
        spos, outw = pin_sheet(lp, num, pos)
        typ = [t[5] for t in lp if t[0] == num][0]
        if netname is None:
            if typ != 'no_connect': noconnect(spos)
            continue
        stub(spos, outw, netname, flag=(ref == flag_ref and netname in ('3V3', 'GND')))

# ---- AT42QT2120
place('U1', (115.0, 105.0)); conn_pins('U1', (115.0, 105.0), flag_ref='U1')
text('U1 AT42QT2120 (VQFN-20, Comms-Modus): MODE an GND, I2C 0x1C, KEY0-2 = Wheel, KEY3 = Mitteltaste, KEY4 = Guard', 40, 62, 1.5, True)
text('Wie Tangara: kein Cs noetig (QT2120-Datenblatt: no external Cs required), RESET ueber 10k an 3V3, Exposed Pad ohne Anschluss', 40, 68, 1.27)
text('Pins 1, 2, 16-20 (KEY5-KEY11) unbenutzt. CHANGE ist open drain: Pull-up auf der MCU-Seite (wie bei Tangara: interner Pull-up der MCU).', 40, 73, 1.27)
# Entkopplung/Reset
for i, ref in enumerate(('C1', 'C2', 'R6')):
    pos = (60.0 + i * 15.24, 160.0); place(ref, pos); conn_pins(ref, pos)
text('U1 Entkopplung (0,1 uF direkt am Pin) / RESET-Pull-up', 58, 150, 1.27, True)
# Serienwiderstaende der Elektroden
for i, ref in enumerate(('R1', 'R2', 'R3', 'R4', 'R5')):
    pos = (60.0 + i * 15.24, 215.0); place(ref, pos); conn_pins(ref, pos)
text('Serienwiderstaende 10k je Elektrode (Datenblatt 3.1: 4,7k ... 20k), nah am Chip', 58, 205, 1.27, True)
# ---- Elektroden
place('SW2', (200.0, 215.0)); conn_pins('SW2', (200.0, 215.0))
place('SW1', (235.0, 215.0)); conn_pins('SW1', (235.0, 215.0))
place('SW3', (260.0, 215.0)); conn_pins('SW3', (260.0, 215.0))
text('Kupferflaechen vorn (Lackschicht geschlossen): Wheel (3 Elektroden), Mitteltaste, Guard (3 Boegen, ein Netz)', 195, 205, 1.27, True)
# ---- Stecker
jpos = (40.0, 105.0); place('J1', jpos); conn_pins('J1', jpos)
text('J1 FFC 6-pol. (Molex 503480-0600): Pin 6 = Reserve (nicht beschaltet)', 18, 86, 1.27, True)
# ---- DRV2605L
place('U2', (215.0, 105.0)); conn_pins('U2', (215.0, 105.0))
text('U2 DRV2605L (VSSOP-10): I2C 0x5A, LRA-Modus, IN/TRIG an GND, EN ueber 10k an 3V3 (wie Tangara)', 188, 62, 1.5, True)
for i, ref in enumerate(('C3', 'C4', 'R7')):
    pos = (190.0 + i * 15.24, 160.0); place(ref, pos); conn_pins(ref, pos)
text('DRV2605L: VDD 1 uF, REG 1 uF, EN-Pull-up (wie Tangara)', 188, 150, 1.27, True)
for i, ref in enumerate(('TP1', 'TP2')):
    pos = (265.0 + i * 15.24, 105.0)
    place(ref, pos); stub((snap(pos[0]), snap(pos[1])), 270, parts[ref]['pins']['1'])
text('Loetpads LRA-Litzen (Rueckseite)', 260, 96, 1.27, True)
# ---- Pull-ups I2C (DNP)
for i, ref in enumerate(('R8', 'R9')):
    pos = (115.0 + i * 15.24, 245.0); place(ref, pos); conn_pins(ref, pos)
text('I2C-Pull-ups 4,7k: DNP (das Waveshare-Board hat 2,2k). Nur bestuecken, wenn das Modul allein getestet wird.', 105, 235, 1.27, True)
w('\t(sheet_instances (path "/" (page "1")))')
w('\t(embedded_fonts no)')
w(')')
open(os.path.join(ROOT, 'klickrad.kicad_sch'), 'w').write('\n'.join(out) + '\n')
print('ok')
