"""Prototyp-Gehaeuse v1 (Waveshare ESP32-S3-Touch-AMOLED-1.8 + Klickrad-Modul)."""
import cadquery as cq
import params as P
from common import *

IL = P.P_IL
OW, OL = P.P_OW, P.P_OL
PI, T, ZS = P.P_PI, P.P_T, P.P_ZS
# Y-Koordinaten: Gehaeusemitte = 0. yi(v) wandelt "Abstand ab Innenkante unten" um.
yi = lambda v: v - IL / 2
WX, WY = 0.0, yi(P.P_WHEEL_Y)               # Radmitte
BOARD_Y0 = yi(P.P_WHEEL_ZONE)               # Unterkante Board
BOARD_CY = BOARD_Y0 + P.BOARD_L / 2
BOARD_TOP = BOARD_Y0 + P.BOARD_L
BOARD_Z0 = PI - P.BOARD_T                   # Rueckseite des Boards
WHEEL_PCB_Z0 = PI - P.WHEEL_GAP - P.WHEEL_PCB_T
WHEEL_PCB_Z1 = PI - P.WHEEL_GAP
HOLDER_Z1 = ZS
HOLDER_Z0 = ZS - P.HOLDER_T
DOME_Z1 = WHEEL_PCB_Z0

# Gehaeuseschrauben: (x, y, am_Halter)
_bx = P.P_IW / 2 - 3.7
BOSSES = [(-_bx, yi(3.9), True), (_bx, yi(3.9), True),
          (-13.5, yi(IL - 3.6), False), (13.5, yi(IL - 3.6), False)]


def outer(z0, z1):
    return rbox(OW, OL, z1 - z0, P.R_OUT, 0, 0, z0)


def inset(d, z0, z1):
    return rbox(OW - 2 * d, OL - 2 * d, z1 - z0, max(P.R_OUT - d, 0.8), 0, 0, z0)


def _port_cutters():
    """Oeffnungen (USB-C oben, BOOT/PWR seitlich) - werden von beiden Schalen abgezogen."""
    cs = []
    zc = PI - P.USB_Z_FROM_FRONT
    ux = P.USB_X
    c = (cq.Workplane("XY").box(P.USB_OPEN_W, 10, P.USB_OPEN_H).edges("|Y").fillet(1.5)
         .translate((ux, OL / 2 - P.WALL, zc)))
    cs.append(c)
    zs_ = PI - P.SIDEBTN_Z_FROM_FRONT
    ys = BOARD_TOP - P.SIDEBTN_Y_FROM_TOP
    for sx in (-1, 1):
        c = (cq.Workplane("XY").box(10, P.SIDEBTN_OPEN, P.SIDEBTN_OPEN).edges("|X").fillet(1.0)
             .translate((sx * (OW / 2 - P.WALL), ys, zs_)))
        cs.append(c)
    return cs


def front_shell():
    f = outer(ZS, T)
    f = try_fillet(f, ">Z", P.EDGE_FILLET)
    f = f.cut(inset(P.WALL, ZS - 1, PI))
    f = f.cut(inset(P.SKIN, ZS - 1, ZS + P.LIP_H + 0.3))      # Falz fuer die Lippe
    # Fenster + Radoeffnung
    dcy = BOARD_TOP - P.DISP_CY_FROM_BOARD_TOP
    f = f.cut(rbox(P.DISP_WIN_W, P.DISP_WIN_H, FRONT_T_CUT(), P.DISP_WIN_R, P.DISP_CX_OFFSET, dcy, PI - 0.5))
    f = f.cut(cyl(P.WHEEL_OPEN_D, FRONT_T_CUT(), WX, WY, PI - 0.5))
    # Schraubdome (Einsatz von unten)
    for x, y, _ in BOSSES:
        f = f.union(cyl(P.BOSS_D, PI - ZS + 0.3, x, y, ZS))
    for x, y, _ in BOSSES:
        f = f.cut(cyl(P.INSERT_HOLE_D, P.INSERT_HOLE_DEPTH, x, y, ZS - 0.01))
    return cut_all(f, _port_cutters())


def FRONT_T_CUT():
    return P.FRONT_T + 1.0


def rear_shell():
    r = outer(0, ZS)
    r = try_fillet(r, "<Z", P.EDGE_FILLET)
    r = r.cut(inset(P.WALL, P.REAR_T, ZS + 1))
    lip = inset(P.SKIN + P.SEAM_GAP, ZS, ZS + P.LIP_H).cut(inset(P.WALL, ZS - 1, ZS + P.LIP_H + 1))
    r = r.union(lip)
    # Rohre fuer Schrauben
    for x, y, holder in BOSSES:
        top = HOLDER_Z0 if holder else ZS
        r = r.union(cyl(P.BOSS_D, top - P.REAR_T + 0.3, x, y, P.REAR_T - 0.3))
    for x, y, holder in BOSSES:
        r = r.cut(cyl(P.M2_CLEAR_D, ZS + 2, x, y, -1))
        r = r.cut(csk(x, y, P.M2_CSK_D, P.M2_CLEAR_D, 0))
    # Akku-Fuehrungsrippen (Akku liegt hinter dem Klickrad-Halter)
    for sx in (-1, 1):
        for sy in (-1, 1):
            r = r.union(box(1.2, 6, P.LIPO_T + 0.6, sx * (P.LIPO_W / 2 + 0.3 + 0.6), WY + sy * 6.0, P.REAR_T - 0.1))
    # Andruckrippen hinter dem Board (Spiel BOARD_REAR_GAP)
    rib_h = P.BOARD_REAR_GAP - 0.2
    for sx in (-1, 1):
        for sy in (-1, 1):
            r = r.union(box(4, 4, rib_h + 0.1, sx * (P.BOARD_W / 2 - 4), BOARD_CY + sy * (P.BOARD_L / 2 - 4), P.REAR_T - 0.1))
    return cut_all(r, _port_cutters())


def wheel_cover():
    z0 = WHEEL_PCB_Z1
    c = cyl(P.WHEEL_COVER_D, P.COVER_T, WX, WY, z0)
    try:
        c = c.faces(">Z").edges(cq.selectors.RadiusNthSelector(1)).chamfer(0.4)
    except Exception:
        pass
    c = c.cut(cyl(P.WHEEL_COVER_HOLE_D, P.COVER_T + 2, WX, WY, z0 - 1))
    for a in P.WHEEL_HOLE_ANGLES:
        px, py = polar(P.WHEEL_HOLE_R, a, WX, WY)
        c = c.cut(cyl(P.HEAD_POCKET_D, P.HEAD_POCKET_H + 1, px, py, z0 - 1))
    return c


def center_button():
    z_top = WHEEL_PCB_Z1 + P.COVER_T - 0.1
    z0 = z_top - P.WHEEL_BTN_T
    b = cyl(P.WHEEL_BTN_D, P.WHEEL_BTN_T, WX, WY, z0)
    pocket = max(0.0, WHEEL_PCB_Z1 + P.SWITCH_H + 0.15 - z0)
    b = b.cut(box(P.SWITCH_SIZE, P.SWITCH_SIZE, pocket + 0.01, WX, WY, z0 - 0.01))
    try:
        b = b.faces(">Z").edges().chamfer(0.3)
    except Exception:
        pass
    return b


def holder():
    h = cyl(2 * P.HOLDER_R, P.HOLDER_T, WX, WY, HOLDER_Z0)
    for x, y, is_h in BOSSES:
        if is_h:
            h = h.union(bar(WX, WY, x, y, P.EAR_W, P.HOLDER_T, HOLDER_Z0))
            h = h.union(cyl(P.EAR_W, P.HOLDER_T, x, y, HOLDER_Z0))
    for a in P.WHEEL_HOLE_ANGLES:
        px, py = polar(P.WHEEL_HOLE_R, a, WX, WY)
        h = h.union(cyl(P.DOME_D, DOME_Z1 - HOLDER_Z1 + 0.01, px, py, HOLDER_Z1 - 0.01))
    for a in P.WHEEL_HOLE_ANGLES:
        px, py = polar(P.WHEEL_HOLE_R, a, WX, WY)
        h = h.cut(cyl(P.INSERT_HOLE_D, P.INSERT_HOLE_DEPTH, px, py, DOME_Z1 - P.INSERT_HOLE_DEPTH))
    for x, y, is_h in BOSSES:
        if is_h:
            h = h.cut(cyl(P.M2_CLEAR_D, P.HOLDER_T + 2, x, y, HOLDER_Z0 - 1))
    sx, sy = P.CABLE_SLOT_POS
    h = h.cut(box(P.CABLE_SLOT[0], P.CABLE_SLOT[1], P.HOLDER_T + 2, WX + sx, WY + sy, HOLDER_Z0 - 1))
    return h


# --------------------------------------------------- Attrappen (nur fuer Kollisionstest)
def dummies():
    d = {}
    d["board"] = rbox(P.BOARD_W, P.BOARD_L, P.BOARD_T, P.BOARD_R, 0, BOARD_CY, BOARD_Z0)
    d["akku"] = box(P.LIPO_W, P.LIPO_L, P.LIPO_T, 0, WY, P.REAR_T + P.LIPO_GAP)
    pcb = cyl(P.WHEEL_PCB_D, P.WHEEL_PCB_T, WX, WY, WHEEL_PCB_Z0)
    for a in P.WHEEL_HOLE_ANGLES:
        px, py = polar(P.WHEEL_HOLE_R, a, WX, WY)
        pcb = pcb.cut(cyl(P.WHEEL_HOLE_D, 5, px, py, WHEEL_PCB_Z0 - 1))
    d["klickrad_pcb"] = pcb
    d["lra"] = box(P.LRA_L, P.LRA_W, P.LRA_H, WX, WY, WHEEL_PCB_Z0 - P.LRA_H)
    heads = None
    for a in P.WHEEL_HOLE_ANGLES:
        px, py = polar(P.WHEEL_HOLE_R, a, WX, WY)
        hd = cyl(P.SCREW_HEAD_D, P.SCREW_HEAD_H, px, py, WHEEL_PCB_Z1)
        heads = hd if heads is None else heads.union(hd)
    d["rad_schrauben"] = heads
    return d


def parts():
    return {"vorderschale": front_shell(), "rueckschale": rear_shell(),
            "klickrad_abdeckung": wheel_cover(), "mitteltaste": center_button(),
            "klickrad_halter": holder()}
