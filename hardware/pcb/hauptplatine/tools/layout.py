"""Layout-Konstanten, feste Positionen, Sperrzonen.
Koordinaten: Mitte (0,0), x rechts, y oben, Blick von der Display-Seite (Oberseite). Unterseite 'B' = durch die Platine gesehen."""
import math
from shapely.geometry import box, Point
from shapely.ops import unary_union

BOARD_W, BOARD_H, BOARD_R = 38.0, 89.0, 5.0
WHEEL_Y = -27.0
CUT_R = 13.0
NOTCH_HALF, NOTCH_BOTTOM, NOTCH_CORNER = 6.0, -43.0, 0.5
WHEEL_R = 16.0                       # Klickrad-Platine
DISPLAY = (-16.5, 0.0, 16.5, 42.0)   # Display-Auflage laut CAD (33 x 42, Mitte y = 21)
DOMES = [(15.0, 40.0), (-15.0, 40.0), (15.0, -40.0), (-15.0, -40.0)]   # Schraubdome im Gehaeuse (CAD), stuetzen die Platine von unten
WHEEL_HOLES = [(14.6 * math.cos(math.radians(a)), WHEEL_Y + 14.6 * math.sin(math.radians(a))) for a in (90, 210, 330)]

# feste Bauteile: ref -> (x, y, Drehung, Seite)
# Modul: Antenne ueber der Oberkante hinaus (Espressif-Empfehlung: PCB-Antenne ausserhalb der Grundplatine); Pad-Bereich bleibt auf der Platine
FIXED = {
    'U15': (-4.2, 32.4, 0, 'B'),
    'J1':  (-9.9, -6.8, 180, 'B'),     # Klinke an der linken Wand, THT-Pins unter dem freien Streifen unterhalb des Displays
    'J6':  (16.9, -6.5, 90, 'B'),      # USB-C an der rechten Wand, THT-Laschen im freien Streifen
    'J4':  (-12.5, 7.2, 270, 'B'),     # microSD an der linken Wand
    'SW1': (12.0, 42.6, 0, 'T'),       # Ein/Aus-Taster an der Oberkante
    'J20': (1.8, -2.0, 0, 'T'),       # Display-FPC
}
OVERHANG = {'U15'}
# Teile, die nicht unter den Akku duerfen (Hoehe > ca. 1,4 mm) und nicht auf die Oberseite
TALL = {'U15', 'J1', 'J6', 'J7', 'J21', 'C29', 'J4', 'SW1'}
TOP_OK = {'U5', 'U12', 'U20', 'U21', 'U22', 'U16', 'Q1', 'Q3', 'Q10', 'Q11', 'D4', 'D10', 'U4', 'U10', 'U3'}
# Akku-Platzhalter (Unterseite, unter Klickrad-Aussparung): 24 x 28 x 3,85
BATT = (-12.0, -41.8, 12.0, -13.8)

# Zuordnung Passiv -> (Anker, Pin), wo sie sich nicht aus den Netzen ergibt
NEAR = {
    'C1': ('U17', '6'), 'C2': ('U17', '19'), 'C3': ('U17', '6'), 'C31': ('U17', '19'), 'C23': ('U16', '1'),
    'C30': ('U15', '3'), 'C32': ('U15', '4'), 'C38': ('U15', '3'), 'C101': ('U15', '3'), 'C102': ('U15', '4'),
    'C34': ('U12', '12'), 'C110': ('U12', '12'), 'C35': ('U4', '5'), 'C29': ('U4', '5'), 'C39': ('J21', '1'),
    'C130': ('J20', '16'), 'C131': ('J20', '16'), 'C132': ('J20', '24'), 'C133': ('J20', '26'),
    'C24': ('U10', '1'), 'C25': ('U10', '14'), 'C27': ('U10', '18'), 'C37': ('J6', 'A4_B9'), 'C104': ('U22', '3'),
    'C111': ('U20', '3'), 'C9': ('U7', '11'), 'C18': ('U7', '11'), 'R100': ('U15', '5'), 'C100': ('U15', '5'),
    'R101': ('U15', '71'), 'C103': ('U15', '71'), 'R120': ('J21', '3'), 'R121': ('J21', '4'), 'R136': ('J21', '5'), 'R137': ('J21', '6'),
    'C211': ('X1', '4'), 'R7': ('U4', '3'), 'R4': ('SW1', '1'), 'R200': ('SW1', '2'), 'R201': ('SW1', '2'), 'R202': ('D4', '1'),
    'R34': ('U10', '17'), 'R35': ('U10', '12'), 'R36': ('U10', '4'), 'R43': ('U10', '3'), 'R37': ('U10', '8'), 'R38': ('U10', '7'), 'R41': ('U10', '6'),
    'R39': ('U10', '13'), 'R1': ('J7', '1'), 'R22': ('U7', '7'), 'R5': ('U1', '16'), 'R2': ('Q3', '1'),
    'R9': ('J4', '7'), 'R11': ('J4', '3'), 'R12': ('J4', '2'), 'R57': ('J4', '8'), 'R61': ('J4', '1'), 'C42': ('J4', '4'),
    'R110': ('U12', '4'), 'R111': ('U12', '6'), 'R112': ('U12', '9'), 'R113': ('Q10', '1'), 'R114': ('Q10', '3'), 'R115': ('Q11', '3'),
    'R116': ('U20', '1'), 'R117': ('U20', '1'), 'R118': ('U21', '5'), 'R119': ('U21', '4'), 'C114': ('U21', '1'),
    'R130': ('J20', '17'), 'R131': ('J20', '19'), 'R132': ('J20', '14'), 'R133': ('J20', '12'), 'R134': ('J20', '22'), 'R135': ('J20', '1'),
    'R122': ('U22', '5'), 'R102': ('U15', '40'), 'R103': ('U15', '41'),
}

def board_poly():
    p = box(-BOARD_W / 2, -BOARD_H / 2, BOARD_W / 2, BOARD_H / 2)
    return p.buffer(-BOARD_R, 32).buffer(BOARD_R, 32)

def cutout_poly():
    c = Point(0, WHEEL_Y).buffer(CUT_R, 64)
    n = box(-NOTCH_HALF, NOTCH_BOTTOM, NOTCH_HALF, WHEEL_Y - 12)
    return unary_union([c, n])

def forbidden_b(margin=0.6, nut=2.4):
    """Unterseite: Aussparung, Schraubenkoepfe/Muttern der Klickrad-Montage."""
    return unary_union([cutout_poly().buffer(margin)] + [Point(x, y).buffer(nut) for x, y in WHEEL_HOLES] + [Point(x, y).buffer(3.0) for x, y in DOMES])

def forbidden_t(margin=0.6, flat=False):
    """Oberseite: Display-Auflage (nur flache Teile <= 0,6 mm erlaubt, wenn flat=True), Klickrad-Platine, Aussparung, Distanzhalter."""
    x0, y0, x1, y1 = DISPLAY
    return unary_union(([] if flat else [box(x0, y0 - 0.8, x1, y1 + 0.8)]) + [Point(0, WHEEL_Y).buffer(WHEEL_R + 0.3), cutout_poly().buffer(margin)] +
                       [Point(x, y).buffer(2.6) for x, y in WHEEL_HOLES])
