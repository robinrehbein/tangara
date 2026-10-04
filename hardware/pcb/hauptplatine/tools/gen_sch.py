#!/usr/bin/env python3
"""Erzeugt hauptplatine.kicad_sch (KiCad 9) aus netlist.py. Standardsymbole werden eingebettet, ICs/Stecker bekommen automatisch erzeugte
Symbole (Pins nach Gruppen, gleiche Netze/Namen werden gestapelt) -> lib/Hauptplatine.kicad_sym.
ERC-Hinweis: alle Pins der selbst erzeugten Symbole sind 'passive' (Pintypen-Pruefung entfaellt dort bewusst)."""
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
    if name.startswith('Q_'):    # Pinnummern G/S/D -> 1/2/3 (Footprint-Pads, bei allen Transistoren hier gleich)
        for a, b in (('G', '1'), ('S', '2'), ('D', '3')): txt = txt.replace('(number "%s"' % a, '(number "%s"' % b)
    return txt.replace('(symbol "%s"' % name, '(symbol "%s:%s"' % (lib, name), 1)

LIBS = [('Device', 'C'), ('Device', 'R'), ('Device', 'L'), ('Switch', 'SW_Push'), ('Connector', 'TestPoint'),
        ('Mechanical', 'MountingHole'), ('power', 'GND'), ('power', '+3V3'), ('power', 'PWR_FLAG')]
STD = {f'{l}:{n}': sx.pins(sx.sym(l, n)) for l, n in LIBS}
QSYM = {}      # Transistorsymbole mit Pinnummern 1/2/3 (= Footprint-Pads) als eigene Bibliothekssymbole
for n in ('Q_NMOS', 'Q_PMOS'):
    t = extract('Device', n)
    for a, b in (('G', '1'), ('S', '2'), ('D', '3')): t = t.replace('(number "%s"' % a, '(number "%s"' % b)
    QSYM[n] = t.replace('"Device:%s"' % n, '"Hauptplatine:%s_123"' % n).replace('"%s_' % n, '"%s_123_' % n)
    STD['Hauptplatine:%s_123' % n] = [({'G': '1', 'S': '2', 'D': '3'}[t_[0]],) + t_[1:] for t_ in sx.pins(sx.sym('Device', n))]

# ------------------------------------------------------------------ automatische Symbole
def pin_sort_key(p):
    return (0, int(p)) if p.isdigit() else (1, p)

def auto_symbol(p):
    """Pins gruppieren (gleiches Netz + gleicher Name -> gestapelt). Liefert (symboltext, geo) mit geo[Gruppe] = (x, y, winkel, [pins])."""
    pins = p['pins']; names = p.get('names', {})
    groups = {}
    for num in sorted(pins, key=pin_sort_key):
        net = pins[num]
        nm = names.get(num, num)
        key = (net, nm) if net not in (None,) else (None, nm)
        if net in ('GND', '3V3', 'SYS_POWER', 'VBAT', 'VBUS', 'VBUS_SW', 'V5A', 'VN5A') or net is None:
            key = (net, None if net is None else None)
            key = (net, 'NC' if net is None else net) if net is None or net in ('GND',) else (net, nm)
        groups.setdefault(key, []).append(num)
    glist = []
    for key, nums in groups.items():
        net, nm = key
        label = nm if nm not in (None,) else (net or 'NC')
        glist.append((label, nums, net))
    # GND-Gruppen nach unten, 3V3 nach oben: einfache Reihenfolge nach kleinster Pinnummer
    glist.sort(key=lambda g: pin_sort_key(min(g[1], key=pin_sort_key)))
    n = len(glist)
    nl = (n + 1) // 2
    left, right = glist[:nl], glist[nl:]
    H = max(len(left), len(right), 1) * 2.54 + 2.54
    W = 20.32 if p['kind'] != 'CONN' else 15.24
    longest = max([len(g[0]) for g in glist] + [4])
    W = max(W, 2 * (longest * 0.95 + 4))
    W = round(W / 2.54) * 2.54
    hx, hy = W / 2, H / 2
    L = 2.54
    geo = {}
    lines = []
    name = p['ref']
    for side, lst, px, ang in (('L', left, -hx - L, 0), ('R', right, hx + L, 180)):
        for i, (label, nums, net) in enumerate(lst):
            y = hy - 1.27 - 2.54 * i
            geo[(side, i)] = (px, y, ang, nums, net)
            for k, num in enumerate(nums):
                hide = '' if k == 0 else ' hide'
                lines.append(f'\t\t\t(pin passive line (at {px:.2f} {y:.2f} {ang}) (length {L}){hide} (name "{label}" (effects (font (size 1.27 1.27)))) '
                             f'(number "{num}" (effects (font (size 1.27 1.27)))))')
    txt = [f'\t(symbol "Hauptplatine:{name}"', '\t\t(pin_names (offset 1.016))', '\t\t(exclude_from_sim no) (in_bom yes) (on_board yes)',
           f'\t\t(property "Reference" "{p["ref"][0]}" (at 0 {hy + 2:.2f} 0) (effects (font (size 1.27 1.27))))',
           f'\t\t(property "Value" "{p["value"]}" (at 0 {-hy - 2:.2f} 0) (effects (font (size 1.27 1.27))))',
           '\t\t(property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))',
           '\t\t(property "Datasheet" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))',
           '\t\t(property "Description" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))',
           f'\t\t(symbol "{name}_0_1"',
           f'\t\t\t(rectangle (start {-hx:.2f} {hy:.2f}) (end {hx:.2f} {-hy:.2f}) (stroke (width 0.254) (type default)) (fill (type background)))',
           '\t\t)', f'\t\t(symbol "{name}_1_1"'] + lines + ['\t\t)', '\t\t(embedded_fonts no)', '\t)']
    return '\n'.join(txt), geo, (hx, hy)

parts = {p['ref']: p for p in netlist.parts()}
STD_KIND = {'R': 'Device:R', 'C': 'Device:C', 'L': 'Device:L', 'SW': 'Switch:SW_Push', 'TP': 'Connector:TestPoint', 'H': 'Mechanical:MountingHole'}
def std_sym(p):
    if p['kind'] in STD_KIND: return STD_KIND[p['kind']]
    if p['kind'] == 'Q': return 'Hauptplatine:Q_PMOS_123' if p.get('mpn', '').startswith('PMV') else 'Hauptplatine:Q_NMOS_123'
    return None
CUSTOM, CUSTOM_GEO, CUSTOM_HALF = {}, {}, {}
for ref, p in parts.items():
    if std_sym(p) is None:
        t, g, h = auto_symbol(p)
        CUSTOM[ref] = t; CUSTOM_GEO[ref] = g; CUSTOM_HALF[ref] = h

# ------------------------------------------------------------------ Blatt
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

def esc(s): return str(s).replace('"', "'")
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
        w(f'\t\t(property "{k}" "{esc(v)}" (at {fmt(x + dx)} {fmt(y + dy)} 0) (effects (font (size 1.27 1.27)) (justify left){hide}))')
    for n in pinnums: w(f'\t\t(pin "{n}" (uuid "{U("pin"+ref+n)}"))')
    w(f'\t\t(instances (project "{PRJ}" (path "/{ROOT_UUID}" (reference "{ref}") (unit 1))))')
    w('\t)')

pw = [0]
def power(kind, value, p, rot=0):
    pw[0] += 1
    symbol('power:' + kind, f'#PWR{pw[0]:03d}', value, p, bom=False, hide_ref=True, pinnums=('1',), hide_val=True, rot=rot)
POS_NETS = {'3V3', 'SYS_POWER', 'VBAT', 'VBUS', 'V5A', 'SD_VDD', 'V5_HOST', 'VBUS_SW'}
def stub(p, outward, net):
    p = (round(p[0], 4), round(p[1], 4))
    dx, dy = {0: (1, 0), 180: (-1, 0), 90: (0, -1), 270: (0, 1)}[outward]
    e = (p[0] + dx * 2.54, p[1] + dy * 2.54)
    wire(p, e)
    if net == 'GND' and outward in (90, 270): power('GND', 'GND', e, 0 if outward == 270 else 180)
    elif net in POS_NETS and outward in (90, 270): power('+3V3', net, e, 0 if outward == 90 else 180)
    else: label(net, e, outward)
    return e

def props_of(p):
    props = {}
    for k, nm in (('mpn', 'MPN'), ('mfr', 'Hersteller'), ('desc', 'Beschreibung'), ('lcsc', 'LCSC'), ('dk', 'DigiKey'), ('src', 'Herkunft'), ('tgref', 'Tangara-Ref')):
        if p.get(k): props[nm] = p[k]
    return props

# Gruppen / Blattaufteilung (A1)
GROUP = {}
def grp(name, refs):
    for r in refs: GROUP[r] = name
grp('mcu', ['U15', 'R100', 'C100', 'C101', 'C102', 'SW10', 'SW11', 'R101', 'C103', 'R102', 'R103', 'TP10', 'TP11', 'TP12', 'TP13', 'TP14', 'TP15', 'C30', 'C32', 'C34', 'C35', 'C38', 'C39'])
grp('display', ['J20', 'R130', 'R131', 'R132', 'R133', 'R134', 'R135', 'C130', 'C131', 'C132', 'C133'])
grp('audio', ['U17', 'U1', 'U7', 'U3', 'J1', 'L1', 'L2', 'C2', 'C3', 'C4', 'C6', 'C7', 'C9', 'C10', 'C12', 'C13', 'C14', 'C15', 'C16', 'C17', 'C18', 'C19', 'R3', 'R6', 'R8', 'R15',
              'R22', 'R5', 'R2', 'Q3', 'TP3', 'TP4', 'TP5', 'TP6', 'R210', 'R211', 'X1', 'C211', 'C1', 'C31'])
grp('power', ['J7', 'U10', 'U4', 'C24', 'C25', 'C27', 'C29', 'R34', 'R35', 'R36', 'R37', 'R38', 'R39', 'R41', 'R43', 'R1', 'TP7', 'SW1', 'R4', 'R200', 'R201', 'R202', 'D4', 'R7', 'U22', 'C104', 'R122', 'TP16'])
grp('usb', ['J6', 'U5', 'U12', 'Q1', 'Q10', 'Q11', 'D10', 'C37', 'R110', 'R111', 'R112', 'R113', 'R114', 'R115', 'C110', 'U20', 'L20', 'U21', 'R116', 'R117', 'R118', 'R119', 'C111', 'C112', 'C113', 'C114'])
grp('sd', ['J4', 'U16', 'R9', 'R11', 'R12', 'R57', 'R61', 'C42', 'C23'])
grp('wheel', ['J21', 'R136', 'R137', 'R120', 'R121', 'H1', 'H2', 'H3'])
ORIGIN = {'mcu': (20, 20), 'display': (230, 20), 'audio': (400, 20), 'power': (20, 330), 'usb': (400, 300), 'sd': (230, 330), 'wheel': (640, 20)}
TITLE = {'mcu': 'ESP32-S31-WROOM-3 (Espressif-Beschaltung)', 'display': 'AMOLED-Anschluss (FPC 34 Pol, wie Waveshare ESP32-S3-Touch-AMOLED-1.8)',
         'audio': 'Audio: WM8523 + INA1620 + TPS65133 + Klinke (1:1 von Tangara, + MCLK-Option)', 'power': 'Power: MCP73871 + TLV75733 + Akku + Power-Latch (von Tangara, angepasst), Fuel Gauge MAX17048',
         'usb': 'USB-C Dual-Role + Host-VBUS (TUSB320 + TPS61023 + TPS2553): EIGENE ENTWICKLUNG, UNGEPRUEFT; ESD wie Tangara', 'sd': 'microSD (SDMMC 4 Bit) + Lastschalter TPS22948',
         'wheel': 'Klickrad-Anschluss (JST-SH 6 Pol), Montagelocher'}

w('(kicad_sch')
w('\t(version 20250114)')
w('\t(generator "eeschema")')
w('\t(generator_version "9.0")')
w(f'\t(uuid "{ROOT_UUID}")')
w('\t(paper "A1")')
w('\t(title_block (title "Hauptplatine Nano-Player (Endgeraet), Rev. 1") (date "2026-10-04") (rev "1") (company "Nano-Player (Hobbyprojekt)")')
w('\t\t(comment 1 "Audio-, Power- und Peripherieteile abgeleitet von Tangara (cool tech zone / jacqueline, CERN-OHL-S-2.0, codeberg.org/cool-tech-zone/tangara-hw)")')
w('\t\t(comment 2 "ESP32-S31-WROOM-3-Beschaltung nach Espressif-Datenblatt v0.7; USB-C-Rollenumschaltung und Host-VBUS: eigene Entwicklung, ungeprueft")')
w('\t\t(comment 3 "Lizenz dieses Designs: CERN-OHL-S-2.0 (abgeleitetes Werk). Nicht an Hardware getestet - vor Bestellung menschlicher Review noetig"))')
w('\t(lib_symbols')
for l, n in LIBS: w(extract(l, n))
for r in CUSTOM: w(CUSTOM[r])
for n in QSYM: w(QSYM[n])
w('\t)')

def place_custom(ref, pos):
    p = parts[ref]; geo = CUSTOM_GEO[ref]
    pos = (snap(pos[0]), snap(pos[1]))
    hx, hy = CUSTOM_HALF[ref]
    allp = sorted({n for g in geo.values() for n in g[3]}, key=pin_sort_key)
    symbol(f'Hauptplatine:{ref}', ref, p['value'], pos, fp=p['fp'], props=props_of(p), dnp=bool(p.get('dnp')), bom=not p.get('nobom'), pinnums=allp,
           ref_off=(-hx, -hy - 3), val_off=(-hx, hy + 3))
    for (side, i), (px, py, ang, nums, net) in geo.items():
        sp = (pos[0] + px, pos[1] - py)
        outw = 180 if side == 'L' else 0
        if net is None: noconnect(sp)
        else: stub(sp, outw, net)
    return hx, hy

def place_std(ref, pos):
    p = parts[ref]; sym = std_sym(p); lp = STD[sym]
    spos = (snap(pos[0]), snap(pos[1]))
    pinnums = [pin[0] for pin in lp]
    symbol(sym, ref, p['value'], spos, fp=p['fp'], props=props_of(p), dnp=bool(p.get('dnp')), bom=not p.get('nobom'), pinnums=pinnums, val_off=(3, 2.54), ref_off=(3, -2.54),
           hide_ref=False)
    mapping = {}
    if p['kind'] == 'Q':    # Symbol-Pins G, S, D = Footprint-Pins gemaess p['pins'] (1=G, 2=S, 3=D)
        pass
    for num, nm, px, py, ang, typ in lp:
        net = p['pins'].get(num)
        sp = (spos[0] + px, spos[1] - py)
        outw = (int(ang) + 180) % 360
        if net is None: noconnect(sp)
        else: stub(sp, outw, net)

for gname, origin in ORIGIN.items():
    refs = [r for r in parts if GROUP.get(r) == gname]
    x0, y0 = origin
    text(TITLE[gname], x0, y0 - 4, 2.0, True)
    big = [r for r in refs if r in CUSTOM]
    small = [r for r in refs if r not in CUSTOM and parts[r]['kind'] != 'H']
    y = y0 + 10
    x = x0
    colw = 0
    for r in big:
        hx, hy = CUSTOM_HALF[r]
        if y + 2 * hy > y0 + (260 if gname in ('mcu',) else 150) and y > y0 + 10:
            x += colw + 50; y = y0 + 10; colw = 0
        place_custom(r, (x + hx + 45, y + hy + 4))
        y += 2 * hy + 14
        colw = max(colw, 2 * hx + 90)
    # Passive in Reihen
    sx_, sy_ = x0, y + 12
    if gname == 'mcu': sx_, sy_ = x0 + 140, y0 + 10
    elif big: sx_, sy_ = x0, max(y, y0 + 160) + 8
    cx = sx_
    n = 0
    for r in small:
        place_std(r, (cx, sy_ + 14))
        cx += 17.78
        n += 1
        if n % 7 == 0: cx = sx_; sy_ += 24
    for r in refs:
        if parts[r]['kind'] == 'H':
            place_std(r, (cx, sy_ + 14)); cx += 17.78
text('PWR_FLAGs fuer ERC (Speisenetze werden von Bauteilen mit passiven Pins gespeist)', 20, 560, 2.0, True)
for i, nname in enumerate(['GND', '3V3', 'SYS_POWER', 'VBAT', 'VBUS', 'VBUS_SW', 'V5A', 'VN5A', 'SD_VDD', 'V5_HOST']):
    px, py = 20 + 22 * i, 575
    symbol('power:PWR_FLAG', f'#FLG{i+1:03d}', 'PWR_FLAG', (px, py), bom=False, hide_ref=True, pinnums=('1',), hide_val=True)
    label(nname, (snap(px), snap(py)), 270)
w('\t(sheet_instances (path "/" (page "1")))')
w('\t(embedded_fonts no)')
w(')')
open(os.path.join(ROOT, PRJ + '.kicad_sch'), 'w').write('\n'.join(out) + '\n')

lib = ['(kicad_symbol_lib', '\t(version 20241209)', '\t(generator "kicad_symbol_editor")', '\t(generator_version "9.0")']
for r, txt in list(CUSTOM.items()) + list(QSYM.items()): lib.append(txt.replace('"Hauptplatine:', '"'))
lib.append(')')
open(os.path.join(ROOT, 'lib', 'Hauptplatine.kicad_sym'), 'w').write('\n'.join(lib) + '\n')
print('ok', len(out), 'Zeilen;', len(CUSTOM), 'eigene Symbole')
