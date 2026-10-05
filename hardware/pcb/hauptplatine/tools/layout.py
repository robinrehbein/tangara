"""Layout-Konstanten, feste Positionen, Sperrzonen (Rev. 3: 41 x 97 x 1,0 mm, Geraet 44 x 100 x bis 11 mm).
Koordinaten: Mitte (0,0), x rechts, y oben, Blick von der Display-Seite (Oberseite 'T'). Unterseite 'B' = durch die Platine gesehen.
Konzept: Oberseite nur flache Teile (Hoehe <= 1,0 mm; Luft unter dem Display >= 1,1 mm), Rueckseite alle hohen Teile neben dem Akkufach, WROOM-1 gedreht (Antenne rechts) innerhalb der Kante."""
import math
from shapely.geometry import box, Point, Polygon
from shapely.ops import unary_union
from shapely import affinity

BOARD_W, BOARD_H, BOARD_R = 41.0, 97.0, 4.0
BOARD_T = 1.0
WHEEL_Y = -25.0                       # Mitte des Klickrads
WHEEL_R_TOP = 16.3                    # Oberseite: Klickrad-Platine (Rad-Rueckseite) liegt ueber diesem Kreis
DISPLAY = (-18.5, -6.5, 18.5, 40.5)   # Display-Modul 2,06" (Annahme 37 x 47), Lage ungeprueft; darunter nur flache Teile (<= 1,0 mm)
BATT = (-16.0, -12.0, 16.0, 26.5)     # Akkufach auf der Rueckseite 32 x 38,5, dort bauteilfrei
LRA_C, LRA_W, LRA_H = (0.0, WHEEL_Y + 6.0), 14.0, 10.0   # Standard-Ausschnitt fuer LRA bis 3,0 mm (Mitte, Breite, Hoehe)
DOMES = []

# Befestigungsloecher M1,6 (NPTH 1,8): Positionen zur Abstimmung mit dem CAD (auch in netlist.py H1..H3)
HOLES = [(-18.2, 46.2), (18.2, -46.2), (-18.2, -46.2)]
HOLE_R = 2.0

# feste Bauteile: ref -> (x, y, Drehung, Seite)
FIXED = {
    'SW1': (15.0, -30.0, 0, 'B'),      # Ein/Aus-Taster rechts unten (Rueckseite)
    'BT1': (-12.5, 28.8, 0, 'B'),      # Akku-Loetpads am oberen Akkuende
    'J4': (-13.7, 37.5, 270, 'B'),     # microSD links oben, Einschub von der linken Kante
    'U15': (6.5, 37.5, 270, 'B'),      # WROOM-1 gedreht: Antenne (6 mm) zeigt nach rechts, liegt innerhalb der Kante
    'U17': (-12.0, -27.5, 0, 'B'),     # DAC mittig im Analogbereich, rundum Platz fuer Entkopplung
    'J1': (-7.825, -45.75, 0, 'B'),    # Klinke, Mundloch an der Unterkante, Achse bei x = -12
    'J6': (9.0, -46.9, 0, 'B'),        # USB-C an der Unterkante, Achse bei x = +9
    'J20': (0.0, -0.65, 0, 'T'),       # Display-FPC, Molex 503480-3000 (Rev. 3b; vorher Hirose FH12 bei y = -0,5): Signalpads bleiben bei y = +1,35
    'J21': (0.0, -46.2, 0, 'T'),       # Klickrad-FFC, Vorderseite, Muendung (Pads) oben, genau unter dem Klickrad-Stecker (x = 0)
}
OVERHANG = {'U15'}
EDGE_PREF = {}
STRONG = {'U3', 'NT1', 'NT2'}          # Anker mit hoher Gewichtung (ESD und Referenz-Netties direkt an der Klinke)               # Teile, die moeglichst am Plattenrand sitzen sollen (Gewicht je mm Randabstand)

# ------------------------------------------------------------------ Randausschnitte (Klinke, USB) aus den Footprint-Daten
def _b_to_view(pos, pts):
    return [(pos[0] - x, pos[1] - y) for x, y in pts]

def jack_slot():
    """Randausschnitt der Klinke (Datenblatt Same Sky SJ-43504: 6,8 mm breit, Entlastungsbohrungen Ø1,3 fuer die Zapfen)."""
    pos = FIXED['J1']
    r = box(0.775, -10.0, 7.575, 3.5)
    c1 = Point(0.775, -4.8).buffer(0.65, 16); c2 = Point(7.575, -4.8).buffer(0.65, 16)
    g = unary_union([r, c1, c2])
    return Polygon(_b_to_view(pos, list(g.exterior.coords)))

def usb_pocket():
    """Randausschnitt fuer GCT USB4510 (Kontur aus dem Tangara-Footprint: 9,24 breit, Boden bei y_fp = -4,6, Ecken r 0,4)."""
    pos = FIXED['J6']
    r = box(-4.62, -4.4, 4.62, 3.5).buffer(-0.4, 8).buffer(0.4, 8)
    r = unary_union([r, box(-4.62, -3.8, 4.62, 3.5)])
    return Polygon(_b_to_view(pos, list(r.exterior.coords)))

def lra_cutout():
    """Innenausschnitt fuer den LRA (14 x 10, Ecken r = 1) unter dem Klickrad."""
    return box(LRA_C[0] - LRA_W / 2, LRA_C[1] - LRA_H / 2, LRA_C[0] + LRA_W / 2, LRA_C[1] + LRA_H / 2).buffer(-1.0, 8).buffer(1.0, 8)

def edge_cutout_poly():
    return unary_union([jack_slot(), usb_pocket()])

def cutout_poly():
    return unary_union([jack_slot(), usb_pocket(), lra_cutout()])

def board_poly():
    p = box(-BOARD_W / 2, -BOARD_H / 2, BOARD_W / 2, BOARD_H / 2)
    p = p.buffer(-BOARD_R, 32).buffer(BOARD_R, 32)
    return p.difference(cutout_poly())

def board_outer():
    p = box(-BOARD_W / 2, -BOARD_H / 2, BOARD_W / 2, BOARD_H / 2)
    return p.buffer(-BOARD_R, 32).buffer(BOARD_R, 32)

# ------------------------------------------------------------------ Hoehen (mm, ueber der Platinenebene) fuer die Seitenwahl
def height(p):
    """Bauteilhoehe aus Footprint/Gehaeuseform; Oberseite nur bis 1,0 mm (Display liegt 1,1 mm ueber der Platine)."""
    fp, kind, pkg, ref = p['fp'], p['kind'], p.get('pkg', ''), p['ref']
    if ref in ('U15',): return 3.1
    if ref == 'J1': return 5.0
    if ref == 'J6': return 3.2
    if ref == 'J4': return 1.9
    if ref == 'SW1': return 1.2
    if ref == 'L20': return 1.0
    if ref in ('J20', 'J21'): return 1.0
    if ref == 'J4': return 1.9
    if kind == 'H': return 0.0
    if kind == 'TP': return 0.0
    if 'BATT_PADS' in fp: return 0.2
    if kind == 'R': return 0.6
    if kind == 'C':
        if pkg == '0402': return 0.6
        if pkg == '0603': return 0.9
        if pkg == '0805': return 1.4
        if pkg == '1206': return 1.8
        return 2.7
    if 'Inductor_SMD:L_0402' in fp: return 0.5
    if 'SOT-23' in fp or 'TSOT' in fp or 'SOT65P210' in fp: return 1.45
    if 'SC-70' in fp or 'SOT-323' in fp: return 1.1
    if 'SOT-563' in fp: return 0.6
    if 'SOT-523' in fp: return 0.8
    if 'Crystal' in fp: return 0.6
    return 0.9    # QFN/DFN/SON/VSSOP/X2QFN

TOP_MAX_H = 1.0
TOPTALL = box(-20.5, 41.0, 20.5, 48.5)   # Vorderseite oberhalb des Displays: dort auch hoehere Teile (>1,0 mm) erlaubt

# ------------------------------------------------------------------ Sperrzonen
def forbidden_b(margin=0.6):
    """Unterseite: Akkufach, Randausschnitte, Befestigungsloecher."""
    return unary_union([box(*BATT), cutout_poly().buffer(0.8)] + [Point(x, y).buffer(HOLE_R) for x, y in HOLES])

def forbidden_t(margin=0.6):
    """Oberseite: Klickrad-Kreis, Randausschnitte (Klinke ragt 1,1 mm ueber die Platine), Befestigungsloecher."""
    return unary_union([Point(0, WHEEL_Y).buffer(WHEEL_R_TOP, 64), cutout_poly().buffer(1.0)] + [Point(x, y).buffer(HOLE_R) for x, y in HOLES])

# Zuordnung Passiv -> (Anker, Pin), wo sie sich nicht aus den Netzen ergibt
NEAR = {
    'C240': ('U17', '31'), 'C241': ('U17', '4'), 'C242': ('U17', '7'), 'C243': ('U17', '7'), 'C244': ('U17', '9'), 'C245': ('U17', '5'), 'C246': ('U17', '6'),
    'C247': ('U17', '10'), 'C248': ('U17', '25'), 'C249': ('U17', '21'), 'C250': ('U17', '18'), 'C251': ('U17', '24'), 'C252': ('U17', '20'),
    'C253': ('U17', '26'), 'C254': ('U17', '26'), 'FB1': ('U17', '31'), 'C255': ('U17', '37'), 'C256': ('U17', '36'), 'R240': ('U17', '37'), 'R241': ('U17', '36'),
    'R242': ('U17', '37'), 'R243': ('U17', '36'), 'X1': ('U17', '37'), 'X2': ('U17', '36'), 'Q20': ('U17', '28'), 'R244': ('U17', '28'), 'R245': ('U17', '28'),
    'R246': ('U17', '27'), 'U30': ('U17', '1'), 'R248': ('U30', '4'), 'R249': ('U30', '3'), 'R247': ('U30', '8'), 'C257': ('U30', '7'),
    'U31': ('U17', '34'), 'U32': ('U17', '38'), 'U33': ('U17', '2'), 'C258': ('U31', '6'), 'C259': ('U32', '6'), 'U34': ('U17', '31'), 'C260': ('U34', '1'),
    'C261': ('U34', '5'), 'C262': ('U34', '5'), 'U3': ('J1', '2'), 'NT1': ('J1', '1'), 'NT2': ('J1', '4'),
    'C30': ('U15', '2'), 'C32': ('U15', '2'), 'C101': ('U15', '2'), 'C102': ('U15', '2'), 'R100': ('U15', '3'), 'C100': ('U15', '3'),
    'R101': ('U15', '27'), 'C103': ('U15', '27'), 'R102': ('U15', '55'), 'R103': ('U15', '54'),
    'C34': ('U12', '12'), 'C110': ('U12', '12'), 'C35': ('U4', '5'), 'C29': ('U4', '5'), 'C23': ('U16', '1'),
    'C24': ('U10', '1'), 'C25': ('U10', '14'), 'C27': ('U10', '18'), 'C37': ('J6', 'A4_B9'), 'C104': ('U22', '3'),
    'C111': ('U20', '3'), 'R4': ('SW1', '1'), 'R200': ('SW1', '2'), 'R201': ('SW1', '2'), 'R202': ('D4', '1'),
    'R34': ('U10', '17'), 'R35': ('U10', '12'), 'R36': ('U10', '4'), 'R43': ('U10', '3'), 'R37': ('U10', '8'), 'R38': ('U10', '7'), 'R41': ('U10', '6'),
    'R39': ('U10', '13'), 'R1': ('BT1', '1'), 'R7': ('U4', '3'),
    'R9': ('J4', '7'), 'R11': ('J4', '3'), 'R12': ('J4', '2'), 'R57': ('J4', '8'), 'R61': ('J4', '1'), 'C42': ('J4', '4'),
    'R110': ('U12', '4'), 'R111': ('U12', '6'), 'R112': ('U12', '9'), 'R113': ('Q10', '1'), 'R114': ('Q10', '3'), 'R115': ('Q11', '3'),
    'R116': ('U20', '1'), 'R117': ('U20', '1'), 'R118': ('U21', '5'), 'R119': ('U21', '4'), 'C114': ('U21', '1'),
    'R130': ('J20', '15'), 'R131': ('J20', '17'), 'R132': ('J20', '9'), 'R134': ('J20', '21'), 'R135': ('J20', '19'),
    'C130': ('J20', '23'), 'C131': ('J20', '25'), 'C132': ('J20', '11'), 'C133': ('J20', '11'),
    'R122': ('U22', '5'), 'R120': ('J21', '3'), 'R121': ('J21', '4'), 'R136': ('J21', '5'),
}

# ------------------------------------------------------------------ Bereichsvorgaben (hart) fuer die Platzierung
# Gruppen -> erlaubte Flaechen je Seite (Ansicht von oben). Analog (DAC-Kette, Quarz, Klinke) links unten, Schaltregler/Lader/USB rechts unten,
# Digital/Funk/SD oben (Vorderseite, Vias zum Modul), Display-Anschluss in der Mitte.
def _u(*bs): return unary_union([box(*b) for b in bs])
_ANALOG = ['U17', 'X1', 'X2', 'FB1', 'U30', 'U31', 'U32', 'U33', 'U34', 'Q20', 'U3', 'NT1', 'NT2'] + \
    ['C%d' % n for n in list(range(240, 263))] + ['R%d' % n for n in range(240, 250)]
_POWER = ['U10', 'C24', 'C25', 'C27', 'R34', 'R35', 'R37', 'R38', 'R39', 'R41', 'C34', 'Q1', 'C37', 'R36', 'R43', 'U5', 'D4', 'C29', 'R7', 'R4', 'R200', 'R201', 'R202',
          'U12', 'R110', 'R111', 'R112', 'R113', 'R114', 'R115', 'C110', 'D10', 'Q10', 'Q11', 'U20', 'L20', 'R116', 'R117', 'C111', 'C112', 'C113', 'U21', 'R118', 'R119', 'C114']
_CORE = ['R1', 'U4', 'C35', 'U22', 'C104', 'R122', 'TP7']
_DISP = ['R130', 'R131', 'R132', 'R134', 'R135', 'C130', 'C131', 'C132', 'C133']
_MOD = ['R100', 'C100', 'C101', 'C102', 'C30', 'C32', 'R101', 'C103', 'R102', 'R103', 'TP10', 'TP11', 'TP12', 'TP13', 'TP14', 'TP15', 'TP16', 'TP17']
_SD = ['U16', 'R9', 'R11', 'R12', 'R57', 'R61', 'C42', 'C23']
_WHEEL = ['R136', 'R120', 'R121']
GROUPS = {
    'ANALOG': dict(refs=_ANALOG, back=_u((-20.5, -34.0, 6.0, -25.5), (-20.5, -25.5, -8.5, -13.5)), front=box(-20.5, -48.5, -3.5, -8.7)),
    'POWER': dict(refs=_POWER, back=_u((2.0, -40.5, 20.5, -25.5), (8.5, -25.5, 20.5, -13.5)), front=box(3.0, -48.5, 20.5, -8.7)),
    'CORE': dict(refs=_CORE, back=None, front=box(-20.5, -6.5, 20.5, 26.0)),
    'DISP': dict(refs=_DISP, back=None, front=box(-20.5, -6.5, 20.5, 10.0)),
    'MOD': dict(refs=_MOD, back=None, front=box(-20.5, 24.0, 20.5, 48.5)),
    'SD': dict(refs=_SD, back=None, front=box(-20.5, 24.0, -3.0, 48.5)),
    'WHEEL': dict(refs=_WHEEL, back=None, front=box(-20.5, -48.5, 20.5, -41.0)),
}
REGION_OF = {r: g for g, d in GROUPS.items() for r in d['refs']}
