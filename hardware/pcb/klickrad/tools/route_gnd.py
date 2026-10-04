#!/usr/bin/env python3
"""Zweiter Durchgang: Jedes GND-Kupferstück (Pads samt vorhandenen GND-Bahnen) bekommt eine Bahn zu einer freien Fläche,
in der später das GND-Gitter liegt. Eingabe: Platine mit allen Signalnetzen (route.py), Ausgabe: Platine mit GND-Anbindung.
Aufruf: route_gnd.py in.kicad_pcb out.kicad_pcb"""
import sys
src = open(__file__.replace('route_gnd.py', 'route.py')).read()
src = src[:src.index('queue = list(ORDER)')]
exec(src)
from scipy import ndimage
# freie Fläche = weiter als 0,9 mm von fremdem Kupfer, im Kreis r < 15 mm
other = [g for l in (0,) for n, g in objs[l] if n != 'GND' and n]
other += [h for h in holes]
for n, lst in fixedgeo.items():
    if n != 'GND': other += [g for la, g, w_ in lst if la == 0]
blkm = raster([g.buffer(0.9) for g in other] + [edge.buffer(0.8)])
free = ~blkm
lab, nl = ndimage.label(free)
sizes = ndimage.sum(free, lab, range(1, nl + 1))
main = lab == (1 + int(np.argmax(sizes)))
goals = {(0, c, r) for r, c in zip(*np.nonzero(main))}
# GND-Ring auf F.Cu (r = 4,2 ... 5,4 mm zwischen Taste und Rad): zusätzliche Ziele, erreichbar über Vias
fcu_other = [g for n, g in objs[1] if n != 'GND'] + [g for n, lst in fixedgeo.items() if n != 'GND' for la, g, w_ in lst if la == 1]
ringg = Point(0, 0).buffer(5.4).difference(Point(0, 0).buffer(3.3)).difference(unary_union(fcu_other + [Point(0, 0)]).buffer(0.35)) if fcu_other else Point(0, 0).buffer(5.4).difference(Point(0, 0).buffer(3.3))
ringm = raster([ringg])
# nur Via-taugliche Zellen (Via darf dort stehen, d.h. Via-Pad bleibt im Ring)
okv = ndimage.binary_erosion(ringm, iterations=int(0.33 / RES))
goals |= {(1, c, r) for r, c in zip(*np.nonzero(okv))}
print('freie Zellen:', len(goals))
# Cluster der GND-Terminals (Pads + vorhandene GND-Bahnen) nach Berührung
gnd_geo = [g for la, g, w_ in fixedgeo.get('GND', []) if la == 0] + [g for n, g in objs[0] if n == 'GND']
from shapely.ops import unary_union
cl = unary_union(gnd_geo)
parts_ = list(cl.geoms) if hasattr(cl, 'geoms') else [cl]
hard, vblk, soft = masks('GND', DEFW)
blk = [hard[0] | soft[0], hard[1] | soft[1]]
miss = 0
for pg in parts_:
    if pg.intersects(unary_union([Point(x, y).buffer(0.3) for (x, y) in [(c * RES - HALF, HALF - r * RES) for l_, c, r in list(goals)[::400]]])): pass
    st = cells_of(pg, 0, 0.0) or set()
    if not st: continue
    # liegt das Stück schon in der freien Fläche?
    if {(0, c, r) for l_, c, r in st} & {g for g in goals if g[0] == 0}: continue
    path = astar(st, goals, blk, vblk, allow_via=True)
    if not path: miss += 1; print('FEHLT Cluster bei', [round(v, 1) for v in pg.centroid.coords[0]], 'Startzellen', len(st), 'gesperrt', sum(blk[0][r_, c_] for l_, c_, r_ in st)); continue
    for kind, *data in simplify(path):
        if kind == 'trk': add_track('GND', data[0][0][0], [(p[1], p[2]) for p in data[0]], DEFW)
    for a_, b_ in zip(path[:-1], path[1:]):
        if a_[0] != b_[0]: add_via('GND', *xy(a_[1], a_[2]))
    geo.setdefault('GND', []).append((0, LineString([xy(c, r) for l_, c, r in path]).buffer(DEFW / 2), DEFW))
    blk = [blk[0] | raster([LineString([xy(c, r) for l_, c, r in path]).buffer(DEFW / 2)]), blk[1]]
board.Save(sys.argv[2])
print('GND-Cluster ohne Anbindung:', miss)
