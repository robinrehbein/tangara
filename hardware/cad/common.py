"""Hilfsfunktionen (CadQuery)."""
import math
import cadquery as cq


def box(w, l, h, x=0.0, y=0.0, z0=0.0):
    return cq.Workplane("XY").box(w, l, h, centered=(True, True, False)).translate((x, y, z0))


def rbox(w, l, h, r, x=0.0, y=0.0, z0=0.0):
    b = cq.Workplane("XY").box(w, l, h, centered=(True, True, False))
    if r > 0:
        b = b.edges("|Z").fillet(min(r, w / 2 - 0.01, l / 2 - 0.01))
    return b.translate((x, y, z0))


def cyl(d, h, x=0.0, y=0.0, z0=0.0):
    return cq.Workplane("XY").circle(d / 2).extrude(h).translate((x, y, z0))


def csk(x, y, d_top=4.4, d_bot=2.4, z0=0.0):
    """Senkung (90 Grad) von der Flaeche z0 nach innen (+Z)."""
    h = (d_top - d_bot) / 2
    return cq.Workplane("XY").add(
        cq.Solid.makeCone(d_top / 2 + 0.2, d_bot / 2, h + 0.2, cq.Vector(x, y, z0 - 0.2), cq.Vector(0, 0, 1)))


def bar(x0, y0, x1, y1, w, h, z0):
    """Rechteckstab von (x0,y0) nach (x1,y1), Breite w, Hoehe h (Z)."""
    ln = math.hypot(x1 - x0, y1 - y0)
    ang = math.degrees(math.atan2(y1 - y0, x1 - x0))
    b = box(ln, w, h, 0, 0, 0).rotate((0, 0, 0), (0, 0, 1), ang)
    return b.translate(((x0 + x1) / 2, (y0 + y1) / 2, z0))


def cut_all(base, cutters):
    for c in cutters:
        base = base.cut(c)
    return base


def union_all(base, parts):
    for p in parts:
        base = base.union(p)
    return base


def try_fillet(wp, selector, r):
    try:
        return wp.faces(selector).edges().fillet(r)
    except Exception:
        return wp


def polar(r, deg, cx=0.0, cy=0.0):
    a = math.radians(deg)
    return cx + r * math.cos(a), cy + r * math.sin(a)


def solid_of(wp):
    return wp.val()
