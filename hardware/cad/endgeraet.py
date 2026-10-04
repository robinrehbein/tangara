"""Endgeraet-Gehaeuse (erster Entwurf) nach Render/TEILE.md: 42 x 95 x 12,2."""
import cadquery as cq
import params as P
from common import *

W, L, R, WALL = P.E_W, P.E_L, P.E_R, P.E_WALL
TOP, SEAM = P.E_TOP, P.E_SEAM
PLATE_IN = TOP - P.E_PLATE            # 11.0
WY = P.E_WHEEL_Y
FZ0, FZ1 = P.E_FRAME_Z0, P.E_FRAME_Z1
PCB_Z0 = P.E_WHEEL_PCB_Z0


def outer(z0, z1):
    return rbox(W, L, z1 - z0, R, 0, 0, z0)


def inset(d, z0, z1):
    return rbox(W - 2 * d, L - 2 * d, z1 - z0, R - d, 0, 0, z0)


def _ports():
    cs = []
    uw, uh = P.E_USB
    cs.append(cq.Workplane("XY").box(uw, 6, uh).edges("|Y").fillet(1.2).translate((0, -L / 2 + WALL / 2, P.E_USB_Z)))
    cs.append(cq.Workplane("XY").cylinder(6, P.E_JACK_D / 2, direct=(0, 1, 0)).translate((P.E_JACK_X, -L / 2 + WALL / 2, P.E_USB_Z)))
    sw, sh = P.E_SD
    cs.append(cq.Workplane("XY").box(6, sw, sh).edges("|X").fillet(0.6).translate((W / 2 - WALL / 2, P.E_SD_Y, P.E_SD_Z)))
    return cs


def _pwr_cutter():
    return cq.Workplane("XY").box(P.E_PWR[0] + 0.4, 6, P.E_PWR[1] + 0.4).edges("|Y").fillet(0.5).translate(
        (P.E_PWR_X, L / 2 - WALL / 2, P.E_PWR_Z))


def top_shell():
    t = outer(SEAM, TOP)
    t = try_fillet(t, ">Z", 1.0)
    t = t.cut(inset(WALL, SEAM - 1, PLATE_IN))
    dw, dh, dr = P.E_DISP_WIN
    t = t.cut(rbox(dw, dh, 4, dr, 0, P.E_DISP_Y, PLATE_IN - 1))
    t = t.cut(cyl(P.WHEEL_OPEN_D, 4, 0, WY, PLATE_IN - 1))
    # Rastnasen innen (Halbkugeln) gegen die Rastmulden im Innenrahmen
    for sx in (-1, 1):
        for y in (-25.0, 25.0):
            t = t.union(cq.Workplane("XY").cylinder(5.0, 0.6, direct=(0, 1, 0)).translate((sx * (W / 2 - WALL + 0.2), y, SEAM + 0.65)))
    t = cut_all(t, _ports())
    t = t.cut(_pwr_cutter())
    return t


def back_shell():
    b = outer(0, SEAM)
    b = try_fillet(b, "<Z", 1.0)
    b = b.cut(inset(WALL, 1.2, SEAM + 1))
    for x, y in P.E_SCREWS:
        b = b.cut(cyl(P.M2_CLEAR_D, 4, x, y, -1))
        b = b.cut(csk(x, y, P.M2_CSK_D, P.M2_CLEAR_D, 0))
    return cut_all(b, _ports())


def frame():
    ow = W - 2 * WALL - 2 * P.E_FRAME_CLEAR
    ol = L - 2 * WALL - 2 * P.E_FRAME_CLEAR
    h = FZ1 - FZ0
    f = rbox(ow, ol, h, R - WALL - P.E_FRAME_CLEAR, 0, 0, FZ0)
    f = f.cut(rbox(ow - 2 * P.E_FRAME_WALL, ol - 2 * P.E_FRAME_WALL, h + 2, R - WALL - P.E_FRAME_CLEAR - P.E_FRAME_WALL, 0, 0, FZ0 - 1))
    f = f.union(box(ow - 1, 2, h, 0, 1.5, FZ0))                       # Quersteg
    # Sockel unter dem LRA (Tape-Kontakt, 0,2 mm Luft)
    lra_bottom = PCB_Z0 - 3.6
    f = f.union(box(12, 4, lra_bottom - 0.2 - FZ0, 0, P.E_LRA_Y, FZ0))
    for x, y in P.E_SCREWS:
        f = f.union(cyl(P.BOSS_D, h, x, y, FZ0))
    for x, y in P.E_SCREWS:
        f = f.cut(cyl(P.INSERT_HOLE_D, P.INSERT_HOLE_DEPTH, x, y, FZ1 - P.INSERT_HOLE_DEPTH))   # Einsatz von oben
        f = f.cut(cyl(P.M2_CLEAR_D, FZ1 - FZ0, x, y, FZ0 - 1))
    # Rastmulden
    for sx in (-1, 1):
        for y in (-25.0, 25.0):
            f = f.cut(cq.Workplane("XY").cylinder(7.0, 0.8, direct=(0, 1, 0)).translate((sx * (W / 2 - WALL + 0.2), y, SEAM + 0.65)))
    return f


def wheel_cover():
    c = cyl(P.WHEEL_COVER_D, P.E_COVER_T, 0, WY, P.E_COVER_Z0)
    try:
        c = c.faces(">Z").edges(cq.selectors.RadiusNthSelector(1)).chamfer(0.4)
    except Exception:
        pass
    return c.cut(cyl(P.WHEEL_COVER_HOLE_D, 5, 0, WY, P.E_COVER_Z0 - 1))


def center_button():
    z_top = P.E_COVER_Z0 + P.E_COVER_T - 0.05
    z0 = z_top - P.WHEEL_BTN_T
    b = cyl(P.WHEEL_BTN_D, P.WHEEL_BTN_T, 0, WY, z0)
    pz = PCB_Z0 + P.WHEEL_PCB_T + P.E_SWITCH_H + 0.15 - z0
    if pz > 0:
        b = b.cut(box(P.SWITCH_SIZE, P.SWITCH_SIZE, pz, 0, WY, z0 - 0.01))
    return b


def spacer_ring():
    od, idm, h = P.E_SPACER
    return cyl(od, h, 0, WY, PCB_Z0 - h).cut(cyl(idm, h + 2, 0, WY, PCB_Z0 - h - 1))


def power_button():
    ymin = L / 2 - WALL
    flange = box(9.6, 1.0, 3.2, P.E_PWR_X, ymin - 0.9, P.E_PWR_Z - 1.6)
    y0, y1 = ymin - 0.4, L / 2 + 0.4
    stem = box(P.E_PWR[0], y1 - y0, P.E_PWR[1], P.E_PWR_X, (y0 + y1) / 2, P.E_PWR_Z - P.E_PWR[1] / 2)
    return flange.union(stem)


def dummies():
    d = {}
    pcb = rbox(38, 89, 1.0, 5, 0, 0, 7.4).cut(cyl(26, 4, 0, WY, 6))
    for x, y in P.E_SCREWS:      # Domfreiraeume
        pass
    d["hauptplatine"] = pcb
    d["display"] = box(33, 42, 2.4, 0, P.E_DISP_Y, 8.5)
    pc = cyl(32, 1.0, 0, WY, PCB_Z0)
    d["klickrad_pcb"] = pc
    d["lra"] = box(16, 6, 3.6, 0, P.E_LRA_Y, PCB_Z0 - 3.6)
    d["akku"] = box(P.E_BATT[0], P.E_BATT[1], P.E_BATT[2], 0, P.E_BATT_Y, 1.4)
    d["schalter_pwr"] = box(4, 2.6, 1.6, 8, L / 2 - 4.5, 8.4)
    return d


def parts():
    return {"oberschale": top_shell(), "rueckschale": back_shell(), "innenrahmen": frame(),
            "klickrad_abdeckung": wheel_cover(), "mitteltaste": center_button(),
            "distanzring": spacer_ring(), "power_taste": power_button()}
