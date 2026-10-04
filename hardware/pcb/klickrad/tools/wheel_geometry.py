#!/usr/bin/env python3
"""Elektroden-Geometrie des Klickrad-Moduls v2 (Tangara-Touchwheel, skaliert).

Algorithmus: Port des "Interpolated Electrode SVG Tool" von cool tech zone
(https://cooltech.zone/tangara/labs/touchwheel-electrode-tool/, Quelltext in der Seite;
Hintergrund: Blogartikel "A Deep Dive Into the Design of Tangara's Touchwheel", 2024-02-07,
nach Microchip AN "Capacitive Touch Sensor Design Guide" DS00002934).
3 Elektroden, 3 Ringe (verschachtelte Spiralen). Die Parameter von Tangara (innen 8 mm, Breite 12 mm,
Abstand 0,3 mm, Deadzone 2 mm) wurden aus dem Footprint qtouch-wheel zurückgerechnet (Flächen
3 x 295 mm2, kleinster Abstand 0,29 mm, r = 7,9 ... 19,86 mm).

Koordinaten hier: Platinenmitte = (0, 0), x nach rechts, y nach oben (Vorderansicht), Winkel gegen den Uhrzeigersinn.
"""
import math, functools
from shapely.geometry import Polygon, LineString, Point
from shapely.ops import unary_union
from shapely import affinity
import numpy as np

# ---- Parameter (Tangara -> Klickrad)
R_IN, R_OUT = 6.3, 12.3          # Tangara 7,9 ... 19,9 (Breite 12 mm -> hier 6 mm = Faktor 0,5)
RINGS = 3                        # wie Tangara
SEP = 0.25                       # Tangara 0,3 mm; hier 0,25 (Fertigung >= 0,127 mm)
DEAD = 1.5                       # Tangara 2,0 mm, nach Umfang skaliert
BTN_R = 2.5                      # wie Tangara (r = 2,5 mm, Ø 5)
GUARD_R_IN, GUARD_R_OUT = 13.5, 15.4   # Tangara: Ring r = 22,2 (Linie 1 mm), 2,35 mm vom Rad entfernt
HOLE_R, HOLE_ANG, HOLE_D = 14.6, (90, 210, 330), 2.2
GUARD_LINK_R, GUARD_LINK_W, GUARD_LINK_SPAN = 12.82, 0.2, 10.5   # Stege zwischen den Guard-Bögen
GUARD_HOLE_EXCL = 2.2            # kein Guard-Kupfer näher als 2,2 mm an der Lochmitte (Schraubenkopf Ø 3,5 / Tasche Ø 4)
OPEN_R = 0.10                    # Öffnen: entfernt Spitzen schmaler als 0,2 mm
TANGARA_PEAKS_BOARD = {2: 86.3, 0: 206.3, 1: 326.3}   # Elektrodenmaxima bei Tangara (Footprint gedreht um -148 Grad)

def _p2c(t, r): return (r * math.cos(t), r * math.sin(t))
def _c2p(x, y): return (math.atan2(y, x), math.hypot(x, y))
def _off(theta, r, ang, d):
    x, y = _p2c(theta, r); return _c2p(x + d * math.cos(ang), y + d * math.sin(ang))

def _segment_line(inner, outer, segments, rings, sep, dead, samples=50):
    r = inner; max_a = 2 * math.pi / segments
    pitch = (((outer - inner - sep) / rings) - sep * 2) / 2
    a, b = math.pi / 2, max_a - math.pi / 2
    pts = [_off(0, r, a, dead / 2)]; r += sep / 2; pts.append(_off(0, r, a, dead / 2))
    for _ in range(rings):
        pts.append(_off(0, r, a, dead / 2)); r += sep / 2; pts.append(_off(0, r, a, dead / 2)); r += pitch
        pts.append(_off(max_a, r, b, dead / 2)); r += sep; pts.append(_off(max_a, r, b, dead / 2)); r += pitch
        pts.append(_off(0, r, a, dead / 2)); r += sep / 2; pts.append(_off(0, r, a, dead / 2))
    r += sep / 2; pts.append(_off(0, r, a, dead / 2))
    cart = [_p2c(*p) for p in pts]; out = [cart[0]]
    for q in cart:
        pf, pt = _c2p(*out[-1]), _c2p(*q)
        dt, dr = (pt[0] - pf[0]) / samples, (pt[1] - pf[1]) / samples
        th, rr = pf
        for _ in range(samples):
            th += dt; rr += dr; out.append(_p2c(th, rr))
    return out

def raw_wheel(inner=R_IN, outer=R_OUT, rings=RINGS, sep=SEP, dead=DEAD):
    """3 Elektrodenflächen im Koordinatensystem des Werkzeugs (Tangara-Footprint-Koordinaten, y nach unten)."""
    ann = Point(0, 0).buffer(outer, 128).difference(Point(0, 0).buffer(inner, 128))
    cut = unary_union([affinity.rotate(LineString(_segment_line(inner, outer, 3, rings, sep, dead)), k * 120, origin=(0, 0)).buffer(sep / 2, cap_style=3)
                       for k in range(3)])
    g = ann.difference(cut)
    geoms = [x for x in (g.geoms if hasattr(g, 'geoms') else [g]) if x.area > 1.0]
    assert len(geoms) == 3, len(geoms)
    return geoms

def _peak_angle(poly, rmid, rf=5.0):
    angs = np.arange(0, 360, 2.0); w = []
    for a in angs:
        f = Point(rmid * math.cos(math.radians(a)), rmid * math.sin(math.radians(a))).buffer(rf, 16)
        w.append(poly.intersection(f).area)
    w = np.array(w) ** 4
    return float(np.degrees(np.angle(np.sum(w * np.exp(1j * np.radians(angs))))) % 360)

@functools.lru_cache(maxsize=1)
def build():
    """Liefert dict: wheel (Liste von 3 Polygonen in Schlüsselreihenfolge KEY0, KEY1, KEY2), button, guard (Liste), Durchkontaktierungen."""
    raw = raw_wheel()
    # Tool-Koordinaten (y nach unten) -> Platine (y nach oben), danach Drehung wie bei Tangara (-148 Grad) plus Feinabgleich
    flipped = [affinity.scale(p, 1, -1, origin=(0, 0)) for p in raw]
    base = [affinity.rotate(p, -148, origin=(0, 0)) for p in flipped]
    rmid = (R_IN + R_OUT) / 2
    pk = [_peak_angle(p, rmid) for p in base]
    # Schlüsselzuordnung: KEY2 am nächsten bei 86,3 Grad, KEY0 bei 206,3, KEY1 bei 326,3 (Tangara: Position 0 = oben, aufsteigend gegen den Uhrzeigersinn)
    def cd(a, b): return abs((a - b + 180) % 360 - 180)
    key_of = {}
    for i in range(3):
        key_of[i] = min(TANGARA_PEAKS_BOARD, key=lambda k: cd(pk[i], TANGARA_PEAKS_BOARD[k]))
    assert sorted(key_of.values()) == [0, 1, 2], (pk, key_of)
    # Feindrehung: mittlere Abweichung der Maxima
    dev = np.mean([((TANGARA_PEAKS_BOARD[key_of[i]] - pk[i] + 180) % 360) - 180 for i in range(3)])
    rot = [affinity.rotate(p, dev, origin=(0, 0)) for p in base]
    wheel = [None] * 3; peaks = [None] * 3
    for i in range(3):
        q = rot[i].buffer(-OPEN_R, 32).buffer(OPEN_R, 32)
        if q.geom_type != 'Polygon': q = max(q.geoms, key=lambda g: g.area)
        wheel[key_of[i]] = q.simplify(0.004)
        peaks[key_of[i]] = (pk[i] + dev) % 360
    btn = Point(0, 0).buffer(BTN_R, 64)
    ring = Point(0, 0).buffer(GUARD_R_OUT, 128).difference(Point(0, 0).buffer(GUARD_R_IN, 128))
    holes = unary_union([Point(HOLE_R * math.cos(math.radians(a)), HOLE_R * math.sin(math.radians(a))).buffer(GUARD_HOLE_EXCL, 64) for a in HOLE_ANG])
    arcs = ring.difference(holes)
    # Die drei Bögen werden innen (r = 12,82 mm) durch schmale Stege verbunden, die an den Befestigungslöchern vorbeilaufen
    # (Abstand zur Lochmitte 1,78 mm; zum Rad 0,42 mm). So bleibt der Guard ein Netz mit einer einzigen Durchkontaktierung.
    links = []
    for a in HOLE_ANG[:2]:      # nur zwei Stege: Bogenkette ohne geschlossenen Ring (sonst entstünde ein Loch im Polygon)
        band = Point(0, 0).buffer(GUARD_LINK_R + GUARD_LINK_W / 2, 128).difference(Point(0, 0).buffer(GUARD_LINK_R - GUARD_LINK_W / 2, 128))
        sector = Polygon([(0, 0)] + [(20 * math.cos(math.radians(a + d)), 20 * math.sin(math.radians(a + d))) for d in np.linspace(-GUARD_LINK_SPAN, GUARD_LINK_SPAN, 40)])
        links.append(band.intersection(sector))
        for s in (-1, 1):   # radiale Anschlüsse an die Bogenenden
            ang = math.radians(a + s * GUARD_LINK_SPAN)
            p0 = ((GUARD_LINK_R - 0.1) * math.cos(ang), (GUARD_LINK_R - 0.1) * math.sin(ang)); p1 = ((GUARD_R_IN + 0.3) * math.cos(ang), (GUARD_R_IN + 0.3) * math.sin(ang))
            links.append(LineString([p0, p1]).buffer(0.2, cap_style=2))
    g = unary_union([arcs] + links)
    g = g.buffer(-0.05).buffer(0.05)
    if g.geom_type != 'Polygon': g = max(g.geoms, key=lambda q: q.area)
    guard = g.simplify(0.004)
    return dict(wheel=wheel, button=btn, guard=guard, peaks=peaks, dev=float(dev), key_of=key_of)

def inner_point(poly, r0, r1, want_angle, margin=0.45, span=360, taken=()):
    """Punkt in `poly` mit Abstand >= margin zum Rand, r in [r0, r1], möglichst nahe bei Winkel want_angle (Grad)."""
    best = None
    for r in np.arange(r0, r1 + 1e-9, 0.05):
        for a in np.arange(0, 360, 0.5):
            x, y = r * math.cos(math.radians(a)), r * math.sin(math.radians(a))
            p = Point(x, y)
            dev = abs((a - want_angle + 180) % 360 - 180)
            if dev <= span / 2 and poly.contains(p) and poly.exterior.distance(p) >= margin and all(math.hypot(x - tx, y - ty) >= 1.3 for tx, ty in taken):
                d = dev + 0.02 * r
                if best is None or d < best[0]: best = (d, x, y)
    return None if best is None else (round(best[1], 2), round(best[2], 2))

if __name__ == '__main__':
    b = build()
    print('dev', round(b['dev'], 2), 'peaks (KEY0..2)', [round(p, 1) for p in b['peaks']])
    for k, p in enumerate(b['wheel']): print('KEY%d' % k, round(p.area, 1), 'mm2', len(p.exterior.coords), 'Punkte')
    print('Taste', round(b['button'].area, 1), 'Guard', [round(a.area, 1) for a in b['guard']])
    print('Abstand Rad-Guard', round(unary_union(b['wheel']).distance(unary_union(b['guard'])), 2), 'Rad-Taste', round(unary_union(b['wheel']).distance(b['button']), 2))
    print('Rad-Rad min', min(b['wheel'][i].distance(b['wheel'][j]) for i in range(3) for j in range(i + 1, 3)))
