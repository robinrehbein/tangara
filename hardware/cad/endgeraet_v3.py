"""Endgeraet v3: 44 x 100 x 10 mm fuer Hauptplatine Rev. 3 (41 x 97 x 1,0).

Gedruckt: rahmen (ASA/PETG), rueckwand (mit 3 Stegen, Akku-Haltestegen und Biegezunge fuer SW1).
Zuschnitt: frontplatte (0,8 Acryl/Glas, DXF), klickrad_abdeckung (0,6 FR4, DXF).
Alle Koordinaten in Board-Koordinaten (Mitte = 0, x rechts, y oben). Z: Rueckseite aussen = 0.
Parameter und Begruendungen: params.py (Block ENDGERAET v3), README.md (Abschnitt "Endgeraet v3").
"""
import math
import cadquery as cq
import params as P
from common import *

W, L, R, T = P.V3_W, P.V3_L, P.V3_R, P.V3_T
WALL, RIM, FIT = P.V3_WALL, P.V3_RIM, P.V3_FIT
WY = P.V3_WHEEL_Y
PCB_Z0, PCB_Z1 = P.V3_PCB_Z0, P.V3_PCB_Z1
BACK_T = P.V3_BACK_T
LIP_Z1 = P.V3_FRONT_Z0
LIP_Z0 = LIP_Z1 - P.V3_LIP_H
PLATE_W, PLATE_L = W - 2 * RIM - 2 * FIT, L - 2 * RIM - 2 * FIT
PLATE_R = R - RIM - FIT
SW_ACT_Z = PCB_Z0 - P.V3_SW1_BODY[2]          # Betaetigungsflaeche des Tasters (hinten)
JACK_Y0 = -P.V3_PCB_L / 2                     # Vorderkante Klinke = Platinenkante
USB_Y0 = -P.V3_PCB_L / 2
USB_OPEN_TOP = PCB_Z0 + 0.15
JACK_TOP = PCB_Z1 + P.V3_JACK_FRONT


def _tapered_cavity():
    ch = P.V3_LIP_INSET - WALL
    w, l, r = W - 2 * WALL, L - 2 * WALL, R - WALL
    sk = cq.Sketch().rect(w, l).vertices().fillet(r)
    cone = cq.Workplane("XY").workplane(offset=LIP_Z0).placeSketch(sk).extrude(ch, taper=45)
    h2 = P.V3_LIP_H - ch
    land = rbox(W - 2 * P.V3_LIP_INSET, L - 2 * P.V3_LIP_INSET, h2 + 0.01, R - P.V3_LIP_INSET, 0, 0, LIP_Z0 + ch - 0.005)
    return cone.union(land)


def _openings():
    cs = []
    z0 = BACK_T
    # Klinke (Boden, x = -12): bis Oberkante Klinke + 0,1; oben abgerundet, unten offen zur Rueckwand
    h = JACK_TOP + 0.1 - z0
    cs.append(cq.Workplane("XY").box(9.6, 3.0, h).edges("|Y and >Z").fillet(1.5)
              .translate((P.V3_JACK_X, -L / 2 + 0.6, z0 + h / 2)))
    # USB-C (Boden, x = +9)
    h = USB_OPEN_TOP - z0
    cs.append(cq.Workplane("XY").box(P.V3_USB_OPEN_W, 3.0, h).edges("|Y and >Z").fillet(1.0)
              .translate((P.V3_USB_X, -L / 2 + 0.6, z0 + h / 2)))
    # microSD (linke Wand, y = 37,5): Kartenmitte ca. 1 mm unter Platinenrueckseite
    sy, sz = P.V3_SD_OPEN
    zc = PCB_Z0 - P.V3_SD[2] / 2
    cs.append(cq.Workplane("XY").box(2.3, sy, sz).edges("|X").fillet(0.6)
              .translate((-W / 2 + 1.15 - 0.0, P.V3_SD_C[1], zc)))
    return cs


def rahmen():
    f = rbox(W, L, T, R, 0, 0, 0)
    f = f.cut(rbox(W - 2 * RIM, L - 2 * RIM, BACK_T + 1, R - RIM, 0, 0, -1))              # hinterer Falz
    f = f.cut(rbox(W - 2 * WALL, L - 2 * WALL, LIP_Z0 - BACK_T, R - WALL, 0, 0, BACK_T))   # Innenraum
    f = f.cut(_tapered_cavity())
    f = f.cut(rbox(W - 2 * RIM, L - 2 * RIM, T - LIP_Z1 + 1, R - RIM, 0, 0, LIP_Z1))       # vorderer Falz
    env = rbox(W - 0.6, L - 0.6, T, R - 0.3, 0, 0, 0)
    for x, y in P.V3_SCREWS:
        zt = LIP_Z1
        post = cyl(P.V3_POST_D, zt - PCB_Z1, x, y, PCB_Z1)
        sx = 1 if x > 0 else -1
        xe = sx * (W / 2 - 0.4)
        rib = bar(x, y, xe, y, P.V3_RIB_T, P.V3_RIB_H, PCB_Z1).intersect(env)
        f = f.union(post).union(rib)
        f = f.cut(cyl(P.V3_PILOT_D, 2.5, x, y, PCB_Z1 - 0.01))
    return cut_all(f, _openings())


def rueckwand():
    b = rbox(PLATE_W, PLATE_L, BACK_T, PLATE_R, 0, 0, 0)
    for x, y in P.V3_SCREWS:
        b = b.union(cyl(P.V3_STANDOFF_D, PCB_Z0 - BACK_T + 0.01, x, y, BACK_T - 0.01))
        b = b.cut(cyl(P.V3_HOLE_D, PCB_Z0 + 2, x, y, -1))
        b = b.cut(csk(x, y, P.V3_CSK_D, P.V3_HOLE_D, 0))
    # Biegezunge fuer SW1 (U-Schlitz, Gelenk am +y-Ende) und Stoessel
    sx, sy = P.V3_SW1
    tw, tl = P.V3_TAB
    s = P.V3_TAB_SLOT
    ty0, ty1 = sy - 5.0, sy - 5.0 + tl           # Zunge y: -35 ... -23 (Stoessel 5 mm vom freien Ende)
    for cx, cy, w_, l_ in ((sx - tw / 2 - s / 2, (ty0 - s + ty1) / 2, s, ty1 - ty0 + s),
                           (sx + tw / 2 + s / 2, (ty0 - s + ty1) / 2, s, ty1 - ty0 + s),
                           (sx, ty0 - s / 2, tw + 2 * s, s)):
        b = b.cut(box(w_, l_, BACK_T + 2, cx, cy, -1))
    pin_h = (SW_ACT_Z - P.V3_TAB_PIN_GAP) - BACK_T
    b = b.union(cyl(P.V3_TAB_PIN_D, pin_h + 0.01, sx, sy, BACK_T - 0.01))
    # Akku-Haltestege: ausserhalb des Fachs, nur 1,0 hoch (unter allen Rueckseitenbauteilen)
    fx0, fx1, fy0, fy1 = P.V3_BATT_FACH
    t, h, g = 0.8, 1.0, 0.2
    for sgn, xx in ((-1, fx0 - g - t / 2), (1, fx1 + g + t / 2)):
        for y in (-7.0, 3.0, 13.0, 22.0):
            b = b.union(box(t, 6.0, h, xx, y, BACK_T - 0.01))
    for xc in (-1.0, 7.0):
        b = b.union(box(6.0, t, h, xc, fy1 + g + t / 2, BACK_T - 0.01))                    # oben (Luecke fuer Litzen BT1 bei x -12,5)
    for xc in (-6.0, 6.0):
        b = b.union(box(6.0, t, h, xc, fy0 - g - t / 2, BACK_T - 0.01))                    # unten
    return b


def frontplatte():
    p = rbox(PLATE_W, PLATE_L, P.V3_FRONT_T, PLATE_R, 0, 0, P.V3_FRONT_Z0)
    return p.cut(cyl(P.V3_WHEEL_OPEN_D, 3, 0, WY, P.V3_FRONT_Z0 - 1))


def klickrad_abdeckung():
    # liegt ueber 0,1 Klebefilm auf der Klickrad-Platine, im Ausschnitt der Frontplatte (0,2 unter der Frontflaeche)
    return cyl(P.V3_WHEEL_COVER_D, P.V3_WHEEL_COVER_T, 0, WY, P.V3_FRONT_Z0)


def parts():
    return {"rahmen": rahmen(), "rueckwand": rueckwand()}


def zuschnitt():
    return {"frontplatte": frontplatte(), "klickrad_abdeckung": klickrad_abdeckung()}


def _screw(x, y):
    head = cq.Workplane("XY").add(cq.Solid.makeCone(1.5, 0.8, 0.7, cq.Vector(x, y, 0), cq.Vector(0, 0, 1)))
    return head.union(cyl(P.V3_SCREW_CORE_D, P.V3_SCREW_LEN - 0.69, x, y, 0.69))


def dummies():
    d = {}
    pw, pl, pt, pr = P.V3_PCB_W, P.V3_PCB_L, P.V3_PCB_T, P.V3_PCB_R
    pcb = rbox(pw, pl, pt, pr, 0, 0, PCB_Z0)
    js, jd = P.V3_JACK_SLOT
    y0 = -pl / 2 - 1
    pcb = pcb.cut(box(js, (-pl / 2 + jd) - y0, 3, P.V3_JACK_X, (y0 + (-pl / 2 + jd)) / 2, PCB_Z0 - 1))
    uw, ud = P.V3_USB_NOTCH
    pcb = pcb.cut(box(uw, (-pl / 2 + ud) - y0, 3, P.V3_USB_X, (y0 + (-pl / 2 + ud)) / 2, PCB_Z0 - 1))
    lw, lh, lr = P.V3_LRA_CUT
    pcb = pcb.cut(rbox(lw, lh, 3, lr, 0, P.V3_LRA_CUT_Y, PCB_Z0 - 1))
    for x, y in P.V3_SCREWS:
        pcb = pcb.cut(cyl(P.V3_HOLE_D, 3, x, y, PCB_Z0 - 1))
    d["hauptplatine"] = pcb
    mw, ml = P.V3_DISP_MOD
    d["display"] = rbox(mw, ml, P.V3_DISP_T, 3.0, 0, P.V3_DISP_Y, P.V3_DISP_Z0)
    fx0, fx1, fy0, fy1 = P.V3_BATT_FACH
    d["akku"] = box(fx1 - fx0, fy1 - fy0, P.V3_BATT_H, (fx0 + fx1) / 2, (fy0 + fy1) / 2, BACK_T)
    jb, jt = P.V3_JACK_BODY
    jr = box(jb, jt, P.V3_JACK_BACK, P.V3_JACK_X, JACK_Y0 + jt / 2, PCB_Z0 - P.V3_JACK_BACK)
    jf = box(js, jd, P.V3_PCB_T + P.V3_JACK_FRONT, P.V3_JACK_X, JACK_Y0 + jd / 2, PCB_Z0)
    d["klinke"] = jr.union(jf)
    ux, uy, uz = P.V3_USB
    d["usb_c"] = box(ux, uy, uz, P.V3_USB_X, USB_Y0 + uy / 2, PCB_Z0 - uz)
    ew, el, eh = P.V3_ESP
    d["esp_modul"] = box(ew, el, eh, P.V3_ESP_C[0], P.V3_ESP_C[1], PCB_Z0 - eh)
    sw, sl, sh = P.V3_SD
    d["microsd"] = box(sw, sl, sh, P.V3_SD_C[0], P.V3_SD_C[1], PCB_Z0 - sh)
    bx, by, bz = P.V3_SW1_BODY
    d["taster_sw1"] = box(bx, by, bz, P.V3_SW1[0], P.V3_SW1[1], PCB_Z0 - bz)
    cx, cy, cz = P.V3_C29_BODY
    d["c29"] = box(cx, cy, cz, P.V3_C29[0], P.V3_C29[1], PCB_Z0 - cz)
    d["klickrad_pcb"] = cyl(P.V3_WHEEL_D, P.V3_WHEEL_PCB_T, 0, WY, P.V3_WHEEL_PCB_Z0)
    lraw, lrah, lraz = P.V3_LRA
    free = box(16.0, 6.0, 5, 0, WY + P.V3_LRA_DY, P.V3_WHEEL_PCB_Z0 - 4)
    d["klickrad_teile"] = cyl(P.V3_WHEEL_COVER_D, P.V3_WHEEL_REAR_H, 0, WY, P.V3_WHEEL_PCB_Z0 - P.V3_WHEEL_REAR_H).cut(free)
    d["lra"] = box(lraw, lrah, lraz, 0, WY + P.V3_LRA_DY, P.V3_WHEEL_PCB_Z0 - lraz)
    for i, (x, y) in enumerate(P.V3_SCREWS):
        d[f"schraube{i + 1}"] = _screw(x, y)
    return d


def keepout():
    x0, x1, y0, y1 = P.V3_ANT_KEEP
    return box(x1 - x0, y1 - y0, P.V3_FRONT_Z0 - BACK_T, (x0 + x1) / 2, (y0 + y1) / 2, BACK_T)
