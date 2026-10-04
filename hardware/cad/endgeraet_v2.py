"""Endgeraet v2 nach Duennbau-Variante A: 40 x 90 x 8,5 mm.

Teile (gedruckt): rahmen, rueckwand, power_taste.  Zuschnitt (DXF + 3D-Vorschau):
frontplatte (0,8 Acryl/Glas), klickrad_abdeckung (0,6 FR4), optional rueckwand_fr4.
Alle Maße VORLAEUFIG, siehe params.py (Block ENDGERAET v2) und docs/DUENNBAU.md.

Z: Rueckseite aussen = 0, Front aussen = E2_T. Alles in Einbaulage.
"""
import cadquery as cq
import params as P
from common import *

W, L, R, T = P.E2_W, P.E2_L, P.E2_R, P.E2_T
WALL, RIM, FIT = P.E2_WALL, P.E2_RIM, P.E2_FIT
WY = P.E2_WHEEL_Y
LIP_Z1 = P.E2_FRONT_Z0                     # 7,7
LIP_Z0 = LIP_Z1 - P.E2_LIP_H               # 6,9
PLATE_W, PLATE_L = W - 2 * RIM - 2 * FIT, L - 2 * RIM - 2 * FIT
PLATE_R = R - RIM - FIT
JACK_ZC = (P.E2_JACK_Z0 + P.E2_JACK_Z1) / 2
USB_ZC = P.E2_PCB_Z0 - P.E2_USB[2] / 2
JACK_Y0 = -L / 2 + WALL + 0.8              # Vorderkante Klinke: 0,8 hinter der Innenwand (Ecken-/Oeffnungsradien)
USB_Y0 = JACK_Y0 + 0.2                    # USB-C-Schale (11,5 breit) liegt 1,0 hinter der Wand


def _tapered_cavity():
    """Hohlraum Auflagesteg: 45-Grad-Schraege (Wand 1,2 -> E2_LIP_INSET), darueber senkrechte Kante."""
    ch = P.E2_LIP_INSET - WALL
    w, l, r = W - 2 * WALL, L - 2 * WALL, R - WALL
    sk = (cq.Sketch().rect(w, l).vertices().fillet(r))
    cone = cq.Workplane("XY").workplane(offset=LIP_Z0).placeSketch(sk).extrude(ch, taper=45)
    h2 = P.E2_LIP_H - ch
    land = rbox(W - 2 * P.E2_LIP_INSET, L - 2 * P.E2_LIP_INSET, h2 + 0.01, R - P.E2_LIP_INSET, 0, 0, LIP_Z0 + ch - 0.005)
    return cone.union(land)


def _openings():
    cs = []
    # Oeffnungen beginnen auf der Rueckwand-Oberkante (z = E2_BACK_T): kein duenner Steg ueber dem Falz
    z0 = P.E2_BACK_T
    jz1 = P.E2_JACK_Z1 + 0.1
    cs.append(cq.Workplane("XY").box(P.E2_JACK_OPEN_W, 3.0, jz1 - z0).edges("|Y").fillet(1.5)
              .translate((P.E2_JACK_X, -L / 2 + 0.6, (z0 + jz1) / 2)))
    uz1 = P.E2_PCB_Z0 + 0.15
    cs.append(cq.Workplane("XY").box(P.E2_USB_OPEN_W, 3.0, uz1 - z0).edges("|Y").fillet(1.0)
              .translate((P.E2_USB_X, -L / 2 + 0.6, (z0 + uz1) / 2)))
    pw, ph = P.E2_PWR_OPEN
    cs.append(cq.Workplane("XY").box(4.0, pw, ph).edges("|X").fillet(0.4)
              .translate((W / 2 - 0.6, P.E2_PWR_Y, P.E2_PWR_Z)))
    return cs


def rahmen():
    f = rbox(W, L, T, R, 0, 0, 0)
    # hinterer Falz fuer die Rueckwand (Randsteg RIM)
    f = f.cut(rbox(W - 2 * RIM, L - 2 * RIM, P.E2_BACK_T + 1, R - RIM, 0, 0, -1))
    # Innenraum
    f = f.cut(rbox(W - 2 * WALL, L - 2 * WALL, LIP_Z0 - P.E2_BACK_T, R - WALL, 0, 0, P.E2_BACK_T))
    f = f.cut(_tapered_cavity())
    # vorderer Falz fuer die Frontplatte
    f = f.cut(rbox(W - 2 * RIM, L - 2 * RIM, T - LIP_Z1 + 1, R - RIM, 0, 0, LIP_Z1))
    # Schraubdome (nur im Aussenumriss), Kernloch von hinten
    inner = rbox(W, L, T, R, 0, 0, 0)
    for x, y in P.E2_SCREWS:
        boss = cyl(P.E2_BOSS_D, P.E2_PCB_Z0 - P.E2_BACK_T, x, y, P.E2_BACK_T).intersect(inner)
        f = f.union(boss)
    for x, y in P.E2_SCREWS:
        f = f.cut(cyl(P.E2_SCREW_PILOT_D, 2.7, x, y, P.E2_BACK_T - 0.01))
    # Auflager der Platine
    px, pl, ph = P.E2_PAD
    for s, y in P.E2_PAD_POS:
        xin = s * (W / 2 - WALL - px)
        f = f.union(box(px + 0.5, pl, ph, xin + s * (px + 0.5) / 2, y, P.E2_PCB_Z0 - ph))
    f = cut_all(f, _openings())
    return f


def rueckwand():
    b = rbox(PLATE_W, PLATE_L, P.E2_BACK_T, PLATE_R, 0, 0, 0)
    for x, y in P.E2_SCREWS:
        b = b.cut(cyl(P.E2_SCREW_CLEAR_D, 3, x, y, -1))
        b = b.cut(csk(x, y, P.E2_SCREW_CSK_D, P.E2_SCREW_CLEAR_D, 0))
    # Haltestege fuer den Akku (Fach 34 x 50 + Spiel)
    bw = P.E2_BATT[0] + 2 * P.E2_FIT_PCB
    bl = P.E2_BATT[1] + 2 * P.E2_FIT_PCB
    by, t, h, z0 = P.E2_BATT_Y, P.E2_BATT_RIB_T, P.E2_BATT_RIB_H, P.E2_BACK_T
    for sx in (-1, 1):
        for y in (-15.0, 8.0):
            b = b.union(box(t, 8.0, h, sx * (bw / 2 + t / 2), y, z0))
    b = b.union(box(10.0, t, h, 3.0, by - bl / 2 - t / 2, z0))          # unten (zwischen Klinke und USB)
    for x in (-8.0, 8.0):
        b = b.union(box(6.0, t, h, x, by + bl / 2 + t / 2, z0))         # oben
    return b


def frontplatte():
    p = rbox(PLATE_W, PLATE_L, P.E2_FRONT_T, PLATE_R, 0, 0, P.E2_FRONT_Z0)
    return p.cut(cyl(P.E2_WHEEL_OPEN_D, 3, 0, WY, P.E2_FRONT_Z0 - 1))


def klickrad_abdeckung():
    z0 = P.E2_FRONT_Z0
    c = cyl(P.E2_WHEEL_COVER_D, P.E2_WHEEL_COVER_T, 0, WY, z0)
    return c


def power_taste():
    x_wall = W / 2 - WALL
    flange = box(0.5, 6.4, 2.8, x_wall - 0.25, P.E2_PWR_Y, P.E2_PWR_Z - 1.4)
    stem = box(1.0, P.E2_PWR_OPEN[0] - 0.2, P.E2_PWR_OPEN[1] - 0.2, x_wall + 0.5, P.E2_PWR_Y, P.E2_PWR_Z - (P.E2_PWR_OPEN[1] - 0.2) / 2)
    return flange.union(stem)


def parts():
    """Gedruckte Teile."""
    return {"rahmen": rahmen(), "rueckwand": rueckwand(), "power_taste": power_taste()}


def zuschnitt():
    """Teile aus Plattenmaterial (3D nur zur Pruefung, Fertigung per DXF)."""
    return {"frontplatte": frontplatte(), "klickrad_abdeckung": klickrad_abdeckung()}


def dummies():
    d = {}
    pw, pl, pr = P.E2_PCB
    pcb = rbox(pw, pl, P.E2_PCB_T, pr, 0, 0, P.E2_PCB_Z0)
    jw, jd, jh = P.E2_JACK
    n = P.E2_JACK_NOTCH_PAD
    ny1 = JACK_Y0 + jd + n
    pcb = pcb.cut(box(jw + 2 * n, ny1 - (-L / 2 - 1), 3, P.E2_JACK_X, (ny1 - L / 2 - 1) / 2, P.E2_PCB_Z0 - 1))
    sw, sh, sx, sy = P.E2_PCB_SLOT
    pcb = pcb.cut(box(sw, sh, 3, sx, sy, P.E2_PCB_Z0 - 1))
    d["hauptplatine"] = pcb
    mw, ml = P.E2_DISP_MOD
    d["display"] = rbox(mw, ml, P.E2_DISP_T, 3.0, 0, P.E2_DISP_Y, P.E2_DISP_Z0)
    bw, bl, bh = P.E2_BATT
    d["akku"] = box(bw, bl, bh, 0, P.E2_BATT_Y, P.E2_BACK_T + P.E2_AIR_BACK)
    d["klinke"] = box(jw, jd, jh, P.E2_JACK_X, JACK_Y0 + jd / 2, P.E2_JACK_Z0)
    uw, ud, uh = P.E2_USB
    d["usb_c"] = box(uw, ud, uh, P.E2_USB_X, USB_Y0 + ud / 2, P.E2_PCB_Z0 - uh)
    ew, el, eh = P.E2_ESP
    d["esp_modul"] = box(ew, el, eh, P.E2_ESP_X, pl / 2 - el / 2, P.E2_PCB_Z0 - eh)
    swx, swy, swz = P.E2_PWR_SWITCH
    d["taster_pwr"] = box(swx, swy, swz, W / 2 - WALL - 0.8 - swx / 2, P.E2_PWR_Y, P.E2_PWR_Z - swz / 2)
    d["klickrad_pcb"] = cyl(32.0, P.E2_WHEEL_PCB_T, 0, WY, P.E2_WHEEL_PCB_Z0)
    lw, ll, lh = P.E2_LRA
    d["lra"] = box(lw, ll, lh, 0, WY + P.E2_LRA_DY, P.E2_WHEEL_PCB_Z0 - lh)
    return d
