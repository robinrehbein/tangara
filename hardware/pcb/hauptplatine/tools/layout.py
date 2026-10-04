"""Layout-Konstanten, feste Positionen, Sperrzonen (Rev. 2: 37 x 84 x 0,8 mm, Duennbau-Konzept).
Koordinaten: Mitte (0,0), x rechts, y oben, Blick von der Display-Seite (Oberseite 'T'). Unterseite 'B' = durch die Platine gesehen.
Konzept: Oberseite nur flache Teile (Hoehe <= 1,0 mm; Display liegt 1,1 mm darueber), Rueckseite alle hohen Teile (<= 3,3 mm) neben dem Akkufach."""
import math
from shapely.geometry import box, Point, Polygon
from shapely.ops import unary_union
from shapely import affinity

BOARD_W, BOARD_H, BOARD_R = 37.0, 86.0, 4.0
BOARD_T = 0.8
WHEEL_Y = -25.0                       # Mitte des Klickrads (Gehaeuse-Abstimmung: Display unten bei y ca. -6, Rad Ø32 darunter)
WHEEL_R_TOP = 16.3                    # Oberseite: Klickrad-Platine liegt ueber diesem Kreis, Luft zwischen den Platinen nur 1,2 mm
DISPLAY = (-17.4, -6.0, 17.4, 37.1)   # Display-Modul 34,8 x 43,1 (LCM), Lage ungeprueft
BATT = (-17.0, -29.4, 17.0, 20.6)     # Akkufach auf der Rueckseite 34 x 50 (Pouch 303450), Rueckseite dort bauteilfrei
DOMES = []                            # keine Domes ueber der Platine: Verschraubung in den Rahmen-Seitenwaenden (DUENNBAU.md 5)

# Befestigungsloecher M1,6 (NPTH 1,8): Positionen zur Abstimmung mit dem CAD
HOLES = [(17.4, 41.0), (16.2, -41.0), (17.4, 22.0)]

# feste Bauteile: ref -> (x, y, Drehung, Seite)
FIXED = {
    'U5': (-3.2, -33.0, 0, 'B'),       # Rueckseiten-Teile >1,0 mm im Streifen zwischen Akkufach und USB-C/Klickrad-Stecker (handplatziert)
    'D10': (1.4, -33.0, 0, 'B'),
    'Q1': (6.2, -33.0, 0, 'B'),
    'SW1': (12.8, -32.8, 0, 'B'),      # Ein/Aus-Taster rechts neben dem Akkufach, unten
    'D4': (-12.5, 26.1, 0, 'B'),       # Streifen zwischen Akkufach, Akkuanschluss und microSD
    'C29': (-6.9, 26.2, 0, 'B'),
    'U16': (-9.0, 22.6, 0, 'B'),
    'J4': (-12.1, 35.2, 270, 'B'),     # microSD, Einschubrichtung nach links (Plattenkante)
    'U15': (6.0, 33.75, 0, 'B'),       # Modul: Antenne (obere 6 mm) ragt 5 mm ueber die Oberkante (y = 42) hinaus
    'J1': (-7.825, -40.25, 0, 'B'),    # Klinke, Mundloch an der Unterkante, Achse bei x = -12
    'J6': (9.0, -41.4, 0, 'B'),        # USB-C an der Unterkante, Achse bei x = +9
    'BT1': (-14.6, 22.5, 0, 'B'),      # Akku-Loetpads am oberen Akkuende (Akkuanschluss oben)
    'J20': (0.0, 3.0, 0, 'T'),         # Display-FPC (Mundloch nach unten, FPC kommt von der Displayunterkante zurueckgefaltet)
    'J21': (-2.1, -38.8, 0, 'B'),      # Klickrad-FFC auf der Rueckseite, Mundloch an der Unterkante (Kabel laeuft um die Plattenkante)
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

FFC_SLOT = (-1.5, -30.2, 5.4, 1.4)    # Schlitz fuer das Klickrad-Flachkabel (Mitte x, y, Breite, Hoehe)

def ffc_slot():
    cx, cy, w, h = FFC_SLOT
    from shapely.geometry import LineString
    return LineString([(cx - w / 2 + h / 2, cy), (cx + w / 2 - h / 2, cy)]).buffer(h / 2, 8)

def cutout_poly():
    return unary_union([jack_slot(), usb_pocket()])

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

# ------------------------------------------------------------------ Sperrzonen
def forbidden_b(margin=0.6):
    """Unterseite: Akkufach, Randausschnitte, Befestigungsloecher."""
    return unary_union([box(*BATT), cutout_poly().buffer(0.8)] + [Point(x, y).buffer(2.1) for x, y in HOLES])

def forbidden_t(margin=0.6):
    """Oberseite: Klickrad-Kreis, Randausschnitte (Klinke ragt 1,1 mm ueber die Platine), Befestigungsloecher."""
    return unary_union([Point(0, WHEEL_Y).buffer(WHEEL_R_TOP, 64), cutout_poly().buffer(1.0)] + [Point(x, y).buffer(2.1) for x, y in HOLES])

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
