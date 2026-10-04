#!/usr/bin/env python3
"""Erzeugt hauptplatine.kicad_sch (KiCad 9) aus netlist.py. Standardsymbole werden eingebettet,
eigene Symbole (XIAO, DAC, MAX17048, FPC, SD, Klinke) werden hier erzeugt und zusaetzlich nach lib/Tangara.kicad_sym geschrieben."""
import math, os, sys, uuid
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import netlist, sx
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NS = uuid.UUID('7c2e5a52-1d3e-4d8b-8b1e-7a3d8b4b2222')
def U(name): return str(uuid.uuid5(NS, name))
ROOT_UUID = U('root')
SYMDIR = '/usr/share/kicad/symbols/'
PRJ = 'hauptplatine'

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

# ------------------------------------------------------------------ eigene Symbole
def custom_symbol(name, d):
    left, right = d['left'], d['right']
    bottom = d.get('extra_bottom', [])
    n = max(len(left), len(right), 1)
    W, H = d['w'], n * 2.54 + 2.54
    hx, hy = W / 2, H / 2
    L = 2.54
    pins = []
    def ptxt(typ, x, y, ang, nm, num):
        return (f'\t\t\t(pin {typ} line (at {x:.2f} {y:.2f} {ang}) (length {L}) (name "{nm}" (effects (font (size 1.27 1.27)))) '
                f'(number "{num}" (effects (font (size 1.27 1.27)))))')
    geo = {}
    for i, (num, nm, typ) in enumerate(left):
        y = hy - 1.27 - 2.54 * i
        pins.append(ptxt(typ, -hx - L, y, 0, nm, num)); geo[(num, 'L')] = (-hx - L, y, 0, typ)
    for i, (num, nm, typ) in enumerate(right):
        y = hy - 1.27 - 2.54 * i
        pins.append(ptxt(typ, hx + L, y, 180, nm, num)); geo[(num, 'R')] = (hx + L, y, 180, typ)
    for i, (num, nm, typ) in enumerate(bottom):
        x = -hx + 2.54 * (i + 1)
        pins.append(ptxt(typ, x, -hy - L, 90, nm, num)); geo[(num, 'B')] = (x, -hy - L, 90, typ)
    lines = [f'\t(symbol "Tangara:{name}"', '\t\t(pin_names (offset 1.016))', '\t\t(exclude_from_sim no) (in_bom yes) (on_board yes)',
             f'\t\t(property "Reference" "{d["ref"]}" (at 0 {hy + 2:.2f} 0) (effects (font (size 1.27 1.27))))',
             f'\t\t(property "Value" "{name}" (at 0 {-hy - 5:.2f} 0) (effects (font (size 1.27 1.27))))',
             '\t\t(property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))',
             '\t\t(property "Datasheet" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))',
             '\t\t(property "Description" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))',
             f'\t\t(symbol "{name}_0_1"',
             f'\t\t\t(rectangle (start {-hx:.2f} {hy:.2f}) (end {hx:.2f} {-hy:.2f}) (stroke (width 0.254) (type default)) (fill (type background)))',
             '\t\t)', f'\t\t(symbol "{name}_1_1"'] + pins + ['\t\t)', '\t\t(embedded_fonts no)', '\t)']
    return '\n'.join(lines), geo

# LDO-Symbol (SOT-23-5: 1 IN, 2 GND, 3 EN, 4 NC, 5 OUT)
SYMBOLS = dict(netlist.SYMBOLS)
SYMBOLS['LDO_SOT23_5'] = dict(left=[('1', 'IN', 'power_in'), ('3', 'EN', 'input'), ('2', 'GND', 'power_in')],
                              right=[('5', 'OUT', 'power_out'), ('4', 'NC', 'no_connect')], w=10.16, ref='U')
CUSTOM = {}
CUSTOM_GEO = {}
for nm, d in SYMBOLS.items():
    txt, geo = custom_symbol(nm, d)
    CUSTOM['Tangara:' + nm] = txt
    CUSTOM_GEO['Tangara:' + nm] = geo

LIBS = [('Device', 'C'), ('Device', 'R'), ('Switch', 'SW_Push'), ('Connector_Generic', 'Conn_01x06'), ('Connector_Generic', 'Conn_01x02'),
        ('Connector', 'TestPoint'), ('Mechanical', 'MountingHole'), ('power', 'GND'), ('power', 'GNDA'), ('power', '+3V3'), ('power', 'PWR_FLAG')]
STD = {f'{l}:{n}': sx.pins(sx.sym(l, n)) for l, n in LIBS}

out = []
def w(s): out.append(s)
nid = [0]
def uid(): nid[0] += 1; return U('e%d' % nid[0])
def fmt(v): return ('%.4f' % v).rstrip('0').rstrip('.')
def wire(a, b): w(f'\t(wire (pts (xy {fmt(a[0])} {fmt(a[1])}) (xy {fmt(b[0])} {fmt(b[1])})) (stroke (width 0) (type default)) (uuid "{uid()}"))')
def noconnect(p): w(f'\t(no_connect (at {fmt(p[0])} {fmt(p[1])}) (uuid "{uid()}"))')
def text(s, x, y, size=1.27, bold=False):
    w(f'\t(text "{s}" (exclude_from_sim no) (at {fmt(x)} {fmt(y)} 0) (effects (font (size {size} {size}){" bold" if bold else ""}) (justify left bottom)) (uuid "{uid()}"))')
def label(name, p, ang):
    just = {0: 'left', 180: 'right', 90: 'left', 270: 'right'}[ang]
    w(f'\t(global_label "{name}" (shape passive) (at {fmt(p[0])} {fmt(p[1])} {ang}) (fields_autoplaced yes) (effects (font (size 1.27 1.27)) (justify {just})) (uuid "{uid()}")')
    w(f'\t\t(property "Intersheetrefs" "${{INTERSHEET_REFS}}" (at {fmt(p[0])} {fmt(p[1])} 0) (effects (font (size 1.27 1.27)) (hide yes)))')
    w('\t)')
def snap(v): return round(v / 1.27) * 1.27

def symbol(lib, ref, value, pos, fp='', props=None, dnp=False, bom=True, hide_ref=False, pinnums=(), ref_off=None, val_off=None, hide_val=False, rot=0):
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
    w(f'\t\t(instances (project "{PRJ}" (path "/{ROOT_UUID}" (reference "{ref}") (unit 1))))')
    w('\t)')

pw = [0]
def power(kind, value, p, rot=0):
    pw[0] += 1
    symbol('power:' + kind, f'#PWR{pw[0]:02d}', value, p, bom=False, hide_ref=True, pinnums=('1',), hide_val=True, rot=rot)
def pwrflag(p):
    pw[0] += 1
    symbol('power:PWR_FLAG', f'#FLG{pw[0]:02d}', 'PWR_FLAG', p, bom=False, hide_ref=True, pinnums=('1',), hide_val=True)

POS_NETS = {'3V3', 'VBAT', 'AVDD', 'DVDD', 'VBUS'}
def stub(p, outward, net, flag=False):
    p = (round(p[0], 4), round(p[1], 4))
    dx, dy = {0: (1, 0), 180: (-1, 0), 90: (0, -1), 270: (0, 1)}[outward]
    e = (p[0] + dx * 2.54, p[1] + dy * 2.54)
    wire(p, e)
    if net in POS_NETS | {'GND', 'AGND'} and outward in (90, 270):
        if net == 'GND': power('GND', 'GND', e, 0 if outward == 270 else 180)
        elif net == 'AGND': power('GNDA', 'AGND', e, 0 if outward == 270 else 180)
        else: power('+3V3', net, e, 0 if outward == 90 else 180)
        if flag: pwrflag(e)
    else:
        label(net, e, outward)
        if flag:
            pwrflag(e)
    return e

parts = {p['ref']: p for p in netlist.parts()}

# ------------------------------------------------------------------ Platzierung im Schaltplan (A2)
SCH = {
    'U1': (90, 120), 'J1': (230, 100), 'U2': (370, 120), 'J4': (470, 70), 'U3': (370, 245), 'U4': (370, 285),
    'U5': (90, 262), 'J2': (230, 262), 'J3': (230, 300), 'J5': (160, 330), 'SW1': (300, 175),
}
GRID = {   # Gruppe -> (Startposition, Refs)
    'lcd':    ((200, 168), ['R6', 'R7', 'R8', 'R9', 'R10', 'R11', 'C2', 'C3', 'C4', 'C5', 'TP1']),
    'i2c':    ((60, 205), ['R1', 'R2', 'R3', 'R4', 'R5', 'C1', 'R12']),
    'sd':     ((260, 330), ['R13', 'R14', 'R15', 'R16', 'R17', 'C6', 'C7']),
    'pwr':    ((60, 335), ['C8', 'C30', 'TP2', 'TP3', 'TP4']),
    'dac':    ((330, 168), ['C10', 'C11', 'C12', 'C13', 'C14', 'C15', 'C16', 'C17', 'C18', 'C19', 'C20']),
    'dac2':   ((330, 205), ['R18', 'C21', 'R19', 'C22', 'C23', 'R20', 'R21', 'R22', 'R23', 'R24']),
    'ldo':    ((430, 250), ['C24', 'C25', 'C26', 'C27', 'C28', 'C29']),
}
TITLES = [
    ('XIAO ESP32S3 Plus (SMD-Montage): GPIO-Zuordnung siehe README / Pin-Tabelle', 35, 70),
    ('Display-Anschluss (34 Pin, Belegung wie Waveshare ESP32-S3-Touch-AMOLED-1.8, CO5300 QSPI 368x448)', 190, 38),
    ('Audio: TLV320DAC3100, I2S + I2C 0x18, PLL aus BCLK (MCLK auf GND), AVDD 3,0 V / DVDD 1,8 V eigene LDOs', 330, 62),
    ('Klinkenbuchse mit Steckererkennung (Schliesser TN an der Spitze)', 440, 35),
    ('Spannungsversorgung Audio: U3 AVDD 3,0 V (analog, auf AGND), U4 DVDD 1,8 V', 330, 232),
    ('Fuel Gauge MAX17048 (I2C 0x36), Akkuanschluss', 55, 238),
    ('Klickrad-Modul (SM06B-SRSS-TB, Belegung laut TEILE.md)', 205, 238),
    ('microSD (SDMMC 1-Bit), Pull-ups', 130, 305),
    ('I2C-Pull-ups (Bus: DAC 0x18, MAX17048 0x36, Klickrad 0x5A/0x5B, Touch 0x15/0x38), Klickrad-Pull-ups, Ein/Aus-Taster', 55, 192),
    ('Display-Entkopplung, Reset, IM-Pins, Touch', 195, 155),
    ('Ein/Aus-Taster: seitlich betaetigter Taster an der Oberkante (Oberseite)', 285, 160),
]

w('(kicad_sch')
w('\t(version 20250114)')
w('\t(generator "eeschema")')
w('\t(generator_version "9.0")')
w(f'\t(uuid "{ROOT_UUID}")')
w('\t(paper "A2")')
w('\t(title_block (title "Hauptplatine Nano-Player (Endgeraet)") (date "2026-10-04") (rev "1") (company "Nano-Player (Hobbyprojekt)")')
w('\t\t(comment 1 "XIAO ESP32S3 Plus + TLV320DAC3100 + AMOLED-FPC + microSD + Klickrad-Anschluss")')
w('\t\t(comment 2 "Nicht an Hardware getestet - vor Bestellung menschlicher Review noetig"))')
w('\t(lib_symbols')
for l, n in LIBS: w(extract(l, n))
for k in CUSTOM: w(CUSTOM[k])
w('\t)')

placed_geo = {}

def place_custom(ref):
    p = parts[ref]
    lib = p['sym']; geo = CUSTOM_GEO[lib]
    pos = (snap(SCH[ref][0]), snap(SCH[ref][1]))
    symbol(lib, ref, p['value'], pos, fp=p['fp'], props=props_of(p),
           pinnums=sorted({k[0] for k in geo}, key=lambda s: (0, int(s)) if s.isdigit() else (1, s)),
           ref_off=(-8, -geo_height(lib) / 2 - 3), val_off=(-8, geo_height(lib) / 2 + 3))
    outw = {'L': 180, 'R': 0, 'B': 270}
    for (num, side), (px, py, ang, typ) in geo.items():
        net = p['pins'].get(num, 'NOPIN')
        if num not in p['pins'] and typ != 'no_connect' and net == 'NOPIN':
            net = None
        sp = (pos[0] + px, pos[1] - py)
        if net is None:
            noconnect(sp)
        else:
            stub(sp, outw[side], net, flag=(ref == 'U1' and num in ('13', '32')))
def geo_height(lib):
    return max((abs(v[1]) for v in CUSTOM_GEO[lib].values()), default=5) * 2
def props_of(p):
    props = {}
    for k, nm in (('mpn', 'MPN'), ('mfr', 'Hersteller'), ('desc', 'Beschreibung'), ('lcsc', 'LCSC'), ('dk', 'DigiKey')):
        if p.get(k): props[nm] = p[k]
    return props

def place_std(ref, pos, flags=()):
    p = parts[ref]; lp = STD[p['sym']]
    spos = (snap(pos[0]), snap(pos[1]))
    pinnums = [pin[0] for pin in lp]
    symbol(p['sym'], ref, p['value'], spos, fp=p['fp'], props=props_of(p), bom=not p.get('nobom'), pinnums=pinnums, val_off=(3, 2.54), ref_off=(3, -2.54))
    for num, nm, px, py, ang, typ in lp:
        net = p['pins'].get(num)
        sp = (spos[0] + px, spos[1] - py)
        outw = (int(ang) + 180) % 360
        if net is None:
            noconnect(sp)
        else:
            stub(sp, outw, net, flag=(ref + ':' + num) in flags)

for ref in ('U1', 'U2', 'J1', 'J4', 'U3', 'U4', 'U5', 'J5'):
    if ref in ('U3', 'U4'): parts[ref]['sym'] = 'Tangara:LDO_SOT23_5'
    place_custom(ref)
# J2/J3/SW1: Standardsymbole
place_std('J2', SCH['J2']); place_std('J3', SCH['J3']); place_std('SW1', SCH['SW1'])
FLAGS = {'C14:2'}
for gname, (start, refs) in GRID.items():
    x, y = start
    for ref in refs:
        place_std(ref, (x, y), FLAGS)
        x += 12.7
for i, ref in enumerate(('H1', 'H2', 'H3')):
    place_std(ref, (60 + i * 12.7, 360))
for s, x, y in TITLES: text(s, x, y, 1.8, True)
text('Montagelocher Klickrad (NPTH 2,2 mm, r = 14,6 mm um (0,-27) bei 90/210/330 Grad)', 55, 355, 1.27)
w('\t(sheet_instances (path "/" (page "1")))')
w('\t(embedded_fonts no)')
w(')')
open(os.path.join(ROOT, PRJ + '.kicad_sch'), 'w').write('\n'.join(out) + '\n')

# Projektbibliothek fuer eigene Symbole (damit der Editor sie findet)
lib = ['(kicad_symbol_lib', '\t(version 20241209)', '\t(generator "kicad_symbol_editor")', '\t(generator_version "9.0")']
for k, txt in CUSTOM.items():
    lib.append(txt.replace('"Tangara:', '"'))
lib.append(')')
open(os.path.join(ROOT, 'lib', 'Tangara.kicad_sym'), 'w').write('\n'.join(lib) + '\n')
print('ok', len(out), 'Zeilen')
