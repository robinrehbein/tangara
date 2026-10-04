"""Layout-Konstanten, Sperrzonen und automatische Platzierung der Passiven.
Koordinaten wie in netlist.py: Mitte (0,0), x rechts, y oben, Blick von der Display-Seite (Oberseite)."""
import math
from shapely.geometry import box, Point, Polygon
from shapely.ops import unary_union

BOARD_W, BOARD_H, BOARD_R = 38.0, 89.0, 5.0
WHEEL_Y = -27.0
CUT_R = 13.0
NOTCH_HALF, NOTCH_BOTTOM, NOTCH_CORNER = 6.0, -43.0, 0.5

# Befestigungsdome des Gehaeuses (Innenrahmen). Die Soll-Positionen (+-15, +-40) kollidieren auf der Unterseite mit XIAO und Klinke;
# Vorschlag: untere Dome wie im CAD, obere Dome in die freien Streifen neben der Aussparung (siehe README, Abschnitt "Aenderungen am Gehaeuse")
DOMES = [(-15.0, -40.0), (15.0, -40.0), (-16.0, -22.0), (16.0, -22.0)]
DOME_R = 3.3                 # Dom-Durchmesser 6,4 + Luft
NUT_R = 2.4                  # Schraubenkopf/Mutter der Klickrad-Montage (Unterseite)
WHEEL_HOLES = [(14.6 * math.cos(math.radians(a)), WHEEL_Y + 14.6 * math.sin(math.radians(a))) for a in (90, 210, 330)]

# Akku-Platzhalter 24 x 28 x 3,85 (Unterseite): unter dem Akku nur Bauteile <= 1,2 mm Hoehe
BATT = (-5.0, -6.0, 19.0, 22.0)      # x0, y0, x1, y1

def board_poly():
    p = box(-BOARD_W / 2, -BOARD_H / 2, BOARD_W / 2, BOARD_H / 2)
    p = p.buffer(-BOARD_R).buffer(BOARD_R)
    return p

def cutout_poly():
    c = Point(0, WHEEL_Y).buffer(CUT_R, 64)
    n = box(-NOTCH_HALF, NOTCH_BOTTOM, NOTCH_HALF, WHEEL_Y - 12)
    return unary_union([c, n])

def forbidden(margin=0.5):
    """Bereiche, in denen keine Bauteile liegen duerfen (Unterseite)."""
    outside = box(-30, -60, 30, 60).difference(board_poly().buffer(-0.7))
    parts = [outside, cutout_poly().buffer(margin)]
    for (x, y) in DOMES: parts.append(Point(x, y).buffer(DOME_R))
    for (x, y) in WHEEL_HOLES: parts.append(Point(x, y).buffer(NUT_R))
    return unary_union(parts)

HALF = {'0402': (1.0, 0.55), '0603': (1.45, 0.8), '0805': (1.8, 1.0), '1206': (2.4, 1.15), 'tp': (0.9, 0.9)}
PADOFF = {'0402': 0.51, '0603': 0.825, '0805': 0.95, '1206': 1.475, 'tp': 0.0}

def _rot(a, b, deg):
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    return a * c - b * s, a * s + b * c

def auto_place(netlist_parts, placed, padpos, pad_boxes_fn, anchor_net_fn, log=print, margin=0.3):
    """Platziert alle Teile mit near=(anker, pin, ...) ohne feste Position (Ausgabe: ref -> (x, y, theta, side)).
    Kosten = Abstand des Anschlusspads (gleiches Netz wie das Ankerpad) zum Ankerpad."""
    from shapely.prepared import prep
    result = {}
    forb = forbidden()
    obst = {'B': [], 'T': []}
    for ref, rects in pad_boxes_fn().items():
        for (poly, side) in rects: obst[side].append(poly)
    batt = box(*BATT)
    todo = [p for p in netlist_parts if p.get('near') and not p.get('at')]
    for part in todo:
        aref, apin = part['near'][0], part['near'][1]
        side = part.get('side') or placed_side.get(aref, 'B')
        pins = padpos(aref, apin)
        if not pins: raise SystemExit(f'Ankerpad fehlt: {aref}.{apin}')
        pa = pins[0]
        anet = anchor_net_fn(aref, apin)
        pkg = part.get('pkg') if part.get('pkg') in HALF else ('tp' if part['ref'].startswith('TP') else '0402')
        hx, hy = HALF[pkg]; off = PADOFF[pkg]
        tall = part.get('pkg') in ('0805', '1206')
        pn = part['pins']
        occ = prep(unary_union(obst[side])) if obst[side] else None
        best = None
        ctr = anchor_center[aref]
        dx, dy = pa[0] - ctr[0], pa[1] - ctr[1]
        if abs(dx) >= abs(dy): u = (math.copysign(1, dx), 0.0)
        else: u = (0.0, math.copysign(1, dy))
        w = (-u[1], u[0])
        dirs = [u, (w[0], w[1]), (-w[0], -w[1]), (-u[0], -u[1])]
        steps = [(di, d, p) for di in range(4) for d in (1.3, 1.8, 2.4, 3.0, 3.7, 4.5, 5.4, 6.5, 8.0, 10.0, 12.0) for p in (0, 0.8, -0.8, 1.6, -1.6, 2.4, -2.4, 3.2, -3.2, 4.0, -4.0, 5.0, -5.0, 6.5, -6.5)]
        for di, dist, perp in steps:
            uu = dirs[di]; ww = (-uu[1], uu[0])
            for theta in ((0, 90, 180, 270) if pkg != 'tp' else (0,)):
                cx, cy = pa[0] + uu[0] * dist + ww[0] * perp, pa[1] + uu[1] * dist + ww[1] * perp
                ex, ey = (hx, hy) if theta in (0, 180) else (hy, hx)
                r = box(cx - ex, cy - ey, cx + ex, cy + ey)
                if r.intersects(forb): continue
                if tall and r.intersects(batt): continue
                if occ is not None and occ.intersects(r.buffer(margin)): continue
                if pkg == 'tp': cost = math.hypot(cx - pa[0], cy - pa[1])
                else:
                    sgn = 1 if side == 'B' else -1
                    p1 = _rot(sgn * off, 0, theta); p2 = _rot(-sgn * off, 0, theta)
                    n1, n2 = pn.get('1'), pn.get('2')
                    cands = []
                    if n1 == anet: cands.append(p1)
                    if n2 == anet: cands.append(p2)
                    if not cands: cands = [p1, p2]
                    cost = min(math.hypot(cx + q[0] - pa[0], cy + q[1] - pa[1]) for q in cands)
                    far = max([p1, p2], key=lambda q: math.hypot(cx + q[0] - pa[0], cy + q[1] - pa[1]))
                    if ((n1 == anet and far is p1) or (n2 == anet and far is p2)) and n1 != n2: cost += 1.5
                if best is None or cost < best[0] - 1e-6:
                    best = (cost, cx, cy, theta, r)
            if best and best[0] < 2.8: break
        if not best:
            log('KEIN PLATZ fuer', part['ref'], pkg, pa, u, anet, tall); continue
        cost, cx, cy, theta, r = best
        result[part['ref']] = (round(cx, 2), round(cy, 2), theta, side)
        obst[side].append(r)
    return result

placed_side = {}
anchor_center = {}
