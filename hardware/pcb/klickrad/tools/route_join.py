#!/usr/bin/env python3
"""Verbindet zwei Kupferstücke eines Netzes von Hand gewählten Punkten aus. Aufruf: route_join.py in.kicad_pcb out.kicad_pcb NETZ x1 y1 x2 y2"""
import sys
_A = sys.argv[:]
src = open(__file__.replace('route_join.py', 'route.py')).read()
src = src[:src.index('queue = list(ORDER)')]
sys.argv = [_A[0], _A[1], _A[2]]
exec(src)
net = _A[3]; p1 = (float(_A[4]), float(_A[5])); p2 = (float(_A[6]), float(_A[7]))
w = WIDTH.get(net, DEFW)
hard, vblk, soft = masks(net, w)
blk = [hard[0] | soft[0], hard[1] | soft[1]]
st = cells_of(Point(*p1).buffer(0.12), 0, 0.0) or {(0,) + cell(*p1)}
gl = cells_of(Point(*p2).buffer(0.12), 0, 0.0) or {(0,) + cell(*p2)}
path = astar(st, gl, blk, vblk, allow_via=True)
if not path: print('KEIN WEG'); sys.exit(1)
for kind, *data in simplify(path):
    if kind == 'trk': add_track(net, data[0][0][0], [(p[1], p[2]) for p in data[0]], w)
for x_, y_ in zip(path[:-1], path[1:]):
    if x_[0] != y_[0]: add_via(net, *xy(x_[1], x_[2]))
board.Save(_A[2]); print('verbunden, Zellen:', len(path))
