#!/usr/bin/env python3
"""Automatische Platzierung (Simulated Annealing) -> tools/placement.json
Koordinaten: Mitte (0,0), x rechts, y oben, Blick von der Display-Seite. Unterseite = 'B' (durch die Platine gesehen, gespiegelt).
Feste Teile stehen in FIXED (Rand-/Wandanschluesse, Modul), alles andere wird optimiert.
Kostenfunktion: Netzlaenge (HPWL, gewichtet), Ueberlappung, Sperrzonen, Hoehenregeln, THT nur unter freiem Bereich (nicht unter dem Display)."""
import os, sys, math, json, random, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('KICAD9_FOOTPRINT_DIR', '/usr/share/kicad/footprints')
import pcbnew
from shapely.geometry import box, Point, Polygon
from shapely.ops import unary_union
from shapely.prepared import prep
import netlist, layout
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
random.seed(int(os.environ.get('SEED', '1')))

def rot(a, b, deg):
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    return a * c - b * s, a * s + b * c

# ---------------------------------------------------------------- Footprint-Geometrie
_cache = {}
def fpgeom(spec):
    if spec in _cache: return _cache[spec]
    lib, name = spec.split(':')
    path = os.path.join(ROOT, 'lib', 'Hauptplatine.pretty') if lib == 'Hauptplatine' else '/usr/share/kicad/footprints/%s.pretty' % lib
    f = pcbnew.FootprintLoad(path, name)
    if f is None: raise SystemExit('Footprint fehlt: ' + spec)
    pads = []
    for p in f.Pads():
        q = p.GetPosition()
        pads.append((p.GetNumber(), pcbnew.ToMM(q.x), pcbnew.ToMM(q.y), p.GetAttribute() in (pcbnew.PAD_ATTRIB_PTH,), pcbnew.ToMM(p.GetSizeX()), pcbnew.ToMM(p.GetSizeY())))
    cy = f.GetCourtyard(pcbnew.F_CrtYd).BBox()
    if cy.GetWidth() > 0:
        bb = (pcbnew.ToMM(cy.GetLeft()), pcbnew.ToMM(cy.GetRight()), pcbnew.ToMM(cy.GetTop()), pcbnew.ToMM(cy.GetBottom()))
    else:
        xs = [p[1] - p[4] / 2 for p in pads] + [p[1] + p[4] / 2 for p in pads]; ys = [p[2] - p[5] / 2 for p in pads] + [p[2] + p[5] / 2 for p in pads]
        bb = (min(xs) - 0.25, max(xs) + 0.25, min(ys) - 0.25, max(ys) + 0.25)
    _cache[spec] = dict(pads=pads, bb=bb)
    return _cache[spec]

def to_view(state, x_fp, y_fp):
    x, y, th, side = state
    u, v = x_fp, -y_fp
    if side == 'B': u = -u
    a, b = rot(u, v, th)
    return (x + a, y + b)

def rect_of(spec, state):
    g = fpgeom(spec)
    x0, x1, y0, y1 = g['bb']
    pts = [to_view(state, a, b) for a, b in ((x0, y0), (x1, y0), (x1, y1), (x0, y1))]
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    return (min(xs), min(ys), max(xs), max(ys))

# ---------------------------------------------------------------- Regeln
PARTS = {p['ref']: p for p in netlist.parts()}
BIG = {'GND', 'AGND'}
RAILS = {'3V3', 'SYS_POWER', 'VBAT', 'VBUS', 'VBUS_SW', 'SD_VDD', 'V1P8', 'V1P8A', 'V5_HOST'}
NETW = lambda n: 0.0 if n in BIG else (0.08 if n in RAILS else 1.0)

# feste Positionen (aus Wandanschluessen); Rest wird optimiert
FIXED = layout.FIXED
# Decoupling-/Zuordnungshinweise: Passiv -> (Anker, Pin)
NEAR = layout.NEAR

def anchor_of(ref):
    p = PARTS[ref]
    if ref in NEAR: return NEAR[ref]
    for n in p['pins'].values():
        if n is None or n in BIG or n in RAILS: continue
        for q in netlist.parts():
            if q['ref'] == ref or q['kind'] in ('R', 'C', 'L', 'TP', 'H'): continue
            for pin, nn_ in q['pins'].items():
                if nn_ == n: return (q['ref'], pin)
    return None

movable = [r for r in PARTS if r not in FIXED and PARTS[r]['kind'] != 'H']
allmov = list(movable)
if os.environ.get('MOVE'):
    movable = [r for r in movable if r in os.environ['MOVE'].split(',')]
state = {}
for r, st in FIXED.items(): state[r] = tuple(st)

HEIGHT = {r: layout.height(PARTS[r]) for r in PARTS}
def top_allowed(ref):
    return HEIGHT[ref] <= layout.TOP_MAX_H
TOPABLE = {r for r in allmov if top_allowed(r)}

BOARD = layout.board_poly()
BOARD_IN = BOARD.buffer(-0.7)
FORB = layout.forbidden_b()            # Bauteile unten verboten (Akkufach, Randausschnitte, Loecher)
FORB_T = layout.forbidden_t()          # oben verboten (Klickrad-Kreis, Randausschnitte, Loecher)
def antenna_keepout():
    f = pcbnew.FootprintLoad(os.path.join(ROOT, 'lib', 'Hauptplatine.pretty'), 'ESP32-S31-WROOM-1')
    polys = []
    for z in f.Zones():
        o = z.Outline(); pts = []
        for i in range(o.OutlineCount()):
            ch = o.Outline(i)
            pts = [to_view(FIXED['U15'], pcbnew.ToMM(ch.CPoint(k).x), pcbnew.ToMM(ch.CPoint(k).y)) for k in range(ch.PointCount())]
            if len(pts) >= 3: polys.append(Polygon(pts).buffer(0.2))
    return unary_union(polys)
ANT = antenna_keepout()
print('Antennen-Keepout-Flaeche', round(ANT.area, 1), [round(v, 1) for v in ANT.bounds])
FORB, FORB_T = unary_union([FORB, ANT]), unary_union([FORB_T, ANT])
PFORB, PFORB_T = prep(FORB), prep(FORB_T)
SPEC = {r: PARTS[r]['fp'] for r in PARTS}
_fx = []
for _r, _st in FIXED.items():
    _g = fpgeom(PARTS[_r]['fp']); _x0, _x1, _y0, _y1 = _g['bb']
    _pts = [to_view(_st, a, b) for a, b in ((_x0, _y0), (_x1, _y0), (_x1, _y1), (_x0, _y1))]
    _fx.append((_st[3], box(min(p[0] for p in _pts), min(p[1] for p in _pts), max(p[0] for p in _pts), max(p[1] for p in _pts))))
RAW_B = BOARD_IN.difference(unary_union([FORB] + [g for sd, g in _fx if sd == 'B']))
RAW_T = BOARD_IN.difference(unary_union([FORB_T] + [g for sd, g in _fx if sd == 'T']))
ALLOW_B = RAW_B.buffer(-0.6)
ALLOW_T = RAW_T.buffer(-0.6)
from shapely.geometry import Point as _Pt
def allowed(ref, side, raw=False):
    g = layout.REGION_OF.get(ref)
    base = (RAW_B if side == 'B' else RAW_T) if raw else (ALLOW_B if side == 'B' else ALLOW_T)
    if ref not in TOPABLE and side == 'T': base = base.intersection(layout.TOPTALL)
    if g is None: return base
    reg = layout.GROUPS[g]['back' if side == 'B' else 'front']
    if reg is None: return Polygon()
    return base.intersection(reg)
_AL = {}
def allowed_c(ref, side, raw=False):
    k = (ref, side, raw)
    if k not in _AL: _AL[k] = allowed(ref, side, raw)
    return _AL[k]
def sides_ok(ref):
    return [sd for sd in ('T', 'B') if not allowed_c(ref, sd).is_empty]
def pull_cost(st, ref=None):
    """Gradient zur erlaubten Flaeche (hilft dem Annealing, aus gesperrten Zonen herauszufinden)."""
    pt = _Pt(st[0], st[1]); area = allowed_c(ref, st[3]) if ref else (ALLOW_B if st[3] == 'B' else ALLOW_T)
    if area.is_empty: return 200.0
    return 0.0 if area.contains(pt) else 4.0 * pt.distance(area)

def tht_ok(ref, st):
    g = fpgeom(SPEC[ref])
    for num, x, y, tht, w, h in g['pads']:
        if tht:
            vx, vy = to_view(st, x, y)
            if not (vy < layout.DISPLAY[1] or vy > layout.DISPLAY[3] or abs(vx) > layout.DISPLAY[2]): return False
    return True

def part_cost_static(ref, st):
    """Strafen, die nur vom Teil selbst abhaengen."""
    pen = 0.0
    x0, y0, x1, y1 = rect_of(SPEC[ref], st)
    r = box(x0, y0, x1, y1)
    if not BOARD_IN.contains(r) and not (ref in layout.OVERHANG):
        pen += 50 + 20 * r.difference(BOARD_IN).area
    side = st[3]
    if side == 'B':
        if ref != 'U15' and PFORB.intersects(r): pen += 50 + 20 * r.intersection(FORB).area
    else:
        if PFORB_T.intersects(r) and ref != 'U15': pen += 50 + 20 * r.intersection(FORB_T).area
    if PARTS[ref].get('tht') and not tht_ok(ref, st): pen += 80
    if ref not in FIXED:
        ar = allowed_c(ref, side, True)
        if ar.is_empty: pen += 500
        elif not ar.buffer(0.05).contains(r): pen += 50 + 20 * r.difference(ar.buffer(0.05)).area
    if ref not in FIXED and pen > 0: pen += pull_cost(st, ref)
    if side == 'B' and ref in TOPABLE and ref not in FIXED: pen += 3   # Rueckseite ist knapp: flache Teile moeglichst nach oben
    return pen

def ncost():
    # HPWL ueber alle Netze
    nets = {}
    for ref, p in PARTS.items():
        if ref not in state: continue
        st = state[ref]
        g = fpgeom(SPEC[ref])
        pos = {}
        for num, x, y, tht, w, h in g['pads']:
            nm = p['pins'].get(num)
            if nm is None or nm in BIG: continue
            vx, vy = to_view(st, x, y)
            nets.setdefault(nm, []).append((vx, vy))
    tot = 0.0
    mc = state['U15'][:2]
    for nm in netlist.GPIO_SIGNALS:
        if nm in nets: nets[nm].append(mc)
    for nm, pts in nets.items():
        if len(pts) < 2: continue
        xs = [a for a, b in pts]; ys = [b for a, b in pts]
        tot += NETW(nm) * ((max(xs) - min(xs)) + (max(ys) - min(ys)))
    return tot

def anchor_cost(ref):
    a = ANCH.get(ref)
    if not a or a[0] not in state: return 0.0
    g = fpgeom(SPEC[a[0]])
    for num, x, y, tht, w, h in g['pads']:
        if num == a[1]:
            ax, ay = to_view(state[a[0]], x, y)
            st = state[ref]
            return (6.0 if ref in layout.STRONG else 1.5) * (abs(st[0] - ax) + abs(st[1] - ay))
    return 0.0

ANCH = {r: anchor_of(r) for r in movable if anchor_of(r)}
GAP = float(os.environ.get('GAP', '0.25'))
def _tht_rects(ref, st):
    out = []
    for num, x, y, tht, w, h in fpgeom(SPEC[ref])['pads']:
        if tht:
            vx, vy = to_view(st, x, y); m = max(w, h) / 2 + 0.3
            out.append((vx - m, vy - m, vx + m, vy + m))
    return out
_THT = {r: any(p[3] for p in fpgeom(SPEC[r])['pads']) for r in PARTS}
def cross_tht(a, sa, b, sb):
    """THT-Pads von a (kommen auf der Gegenseite heraus) duerfen nicht in Bauteil b liegen."""
    if not _THT[a]: return 0.0
    rb = rect_of(SPEC[b], sb)
    pen = 0.0
    for (x0, y0, x1, y1) in _tht_rects(a, sa):
        if min(x1, rb[2]) - max(x0, rb[0]) > 0 and min(y1, rb[3]) - max(y0, rb[1]) > 0: pen += 40
    return pen
def overlap_pen(ref, st):
    r0 = rect_of(SPEC[ref], st)
    pen = 0.0
    for o, so in state.items():
        if o == ref: continue
        if so[3] != st[3]:
            pen += cross_tht(ref, st, o, so) + cross_tht(o, so, ref, st)
            continue
        r1 = rect_of(SPEC[o], so)
        dx = min(r0[2], r1[2] + 0) - max(r0[0], r1[0]) + GAP
        dy = min(r0[3], r1[3]) - max(r0[1], r1[1]) + GAP
        if dx > 0 and dy > 0: pen += 30 + 25 * dx * dy
    return pen

def total_cost():
    c = ncost()
    for r in state:
        c += part_cost_static(r, state[r])
        c += overlap_pen(r, state[r]) * 0.5
        c += anchor_cost(r)
    return c

if os.environ.get('DBG'):
    for r in FIXED:
        st = state[r]; x0, y0, x1, y1 = rect_of(SPEC[r], st); rr = box(x0, y0, x1, y1)
        print(r, st, 'rect', [round(v, 1) for v in (x0, y0, x1, y1)], 'ausserhalb', round(rr.difference(BOARD_IN).area, 1),
              'forb', round(rr.intersection(FORB).area, 1) if st[3] == 'B' else round(rr.intersection(FORB_T).area, 1), 'tht_ok', tht_ok(r, st))
    sys.exit()
# Startzustand: zufaellig in der Platine
def rand_state(ref):
    side = random.choice(sides_ok(ref) or ['B'])
    area = allowed_c(ref, side)
    if area.is_empty: area = ALLOW_B
    bx0, by0, bx1, by1 = area.bounds
    for _ in range(200):
        x, y = random.uniform(bx0, bx1), random.uniform(by0, by1)
        if area.contains(_Pt(x, y)): break
    return (x, y, random.choice((0, 90, 180, 270)), side)
for r in allmov: state[r] = rand_state(r)
# Teile mit Ankern starten in der Naehe
for r in allmov:
    a = ANCH.get(r)
    if a and a[0] in state:
        g = fpgeom(SPEC[a[0]])
        for num, x, y, tht, w, h in g['pads']:
            if num == a[1]:
                ax, ay = to_view(state[a[0]], x, y)
                state[r] = (ax + random.uniform(-2, 2), ay + random.uniform(-2, 2), random.choice((0, 90, 180, 270)), state[a[0]][3] if not allowed_c(r, state[a[0]][3]).is_empty and (state[a[0]][3] == 'B' or r in TOPABLE) else state[r][3])
                break

def edge_cost(ref, st):
    w = layout.EDGE_PREF.get(ref)
    if not w: return 0.0
    return w * max(0.0, min(layout.BOARD_W / 2 - abs(st[0]), layout.BOARD_H / 2 - abs(st[1])) - 1.5)

def local_cost(ref, st):
    old = state[ref]; state[ref] = st
    # Netzlaenge nur der betroffenen Netze
    c = part_cost_static(ref, st) + overlap_pen(ref, st) + anchor_cost(ref) + edge_cost(ref, st)
    # Netze
    nets = {PARTS[ref]['pins'].get(n) for n, *_ in fpgeom(SPEC[ref])['pads']}
    nets = {n for n in nets if n and n not in BIG}
    for nm in nets:
        pts = []
        for o, so in state.items():
            po = PARTS[o]
            for num, x, y, tht, w, h in fpgeom(SPEC[o])['pads']:
                if po['pins'].get(num) == nm: pts.append(to_view(so, x, y))
        if nm in netlist.GPIO_SIGNALS: pts.append(tuple(state['U15'][:2]))
        if len(pts) > 1:
            xs = [a for a, b in pts]; ys = [b for a, b in pts]
            c += NETW(nm) * ((max(xs) - min(xs)) + (max(ys) - min(ys)))
    # Anker anderer Teile, die an diesem Teil haengen
    for o, a in ANCH.items():
        if a[0] == ref and o in state: c += anchor_cost(o)
    state[ref] = old
    return c

# NETZ-INDEX fuer Geschwindigkeit
t0 = time.time()
N = int(os.environ.get('ITER', '60000'))
T0, T1 = float(os.environ.get('T0', '12.0')), 0.05
if os.environ.get('INIT'):
    for r_, v_ in json.load(open(os.environ['INIT'])).items():
        if r_ in state and r_ not in FIXED: state[r_] = (v_[0], v_[1], v_[2], 'T' if (r_ in TOPABLE and not os.environ.get('KEEPSIDE')) else v_[3])
cur = None
for it in range(N):
    T = T0 * (T1 / T0) ** (it / N)
    ref = random.choice(movable)
    old = state[ref]
    sig = 6.0 * (1 - it / N) + 0.3
    if random.random() < 0.05:        # Sprung in die erlaubte Flaeche (Teile ueberqueren sonst gesperrte Zonen nicht)
        side = random.choice(sides_ok(ref)) if random.random() < 0.3 else old[3]
        area = allowed_c(ref, side)
        if area.is_empty: continue
        bx0, by0, bx1, by1 = area.bounds
        for _ in range(40):
            px, py = random.uniform(bx0, bx1), random.uniform(by0, by1)
            if area.contains(_Pt(px, py)): break
        new = (px, py, random.choice((0, 90, 180, 270)), side)
    elif random.random() < 0.15:
        a = ANCH.get(ref)
        if a and a[0] in state:
            g = fpgeom(SPEC[a[0]])
            for num, x, y, tht, w, h in g['pads']:
                if num == a[1]:
                    ax, ay = to_view(state[a[0]], x, y)
                    new = (ax + random.gauss(0, 3), ay + random.gauss(0, 3), random.choice((0, 90, 180, 270)), old[3])
                    break
        else:
            new = (old[0] + random.gauss(0, sig), old[1] + random.gauss(0, sig), old[2], old[3])
    else:
        mv = random.random()
        if mv < 0.7: new = (old[0] + random.gauss(0, sig), old[1] + random.gauss(0, sig), old[2], old[3])
        elif mv < 0.9: new = (old[0], old[1], (old[2] + random.choice((90, 180, 270))) % 360, old[3])
        else:
            new = old
    if new == old: continue
    c0 = local_cost(ref, old)
    c1 = local_cost(ref, new)
    if c1 <= c0 or random.random() < math.exp(-(c1 - c0) / T):
        state[ref] = new
    if it % 10000 == 0:
        json.dump({r: [round(v[0], 2), round(v[1], 2), v[2], v[3]] for r, v in state.items()}, open((os.environ.get('OUT') or 'placement.json') + '.ckpt', 'w'))
        print(f'it {it} T {T:.2f} total {total_cost():.0f}  ({time.time()-t0:.0f}s)', flush=True)

# Bericht
bad = 0
for r in state:
    ps = part_cost_static(r, state[r]); op = overlap_pen(r, state[r])
    if ps > 0 or op > 0:
        bad += 1; print('PROBLEM', r, round(ps), round(op), [round(v, 1) if isinstance(v, float) else v for v in state[r]])
print('Teile mit Problem:', bad, 'Gesamt', round(total_cost()))
json.dump({r: [round(s[0], 2), round(s[1], 2), s[2], s[3]] for r, s in state.items()}, open(os.environ.get('OUT') or os.path.join(os.path.dirname(os.path.abspath(__file__)), 'placement.json'), 'w'), indent=0)
