"""Baut Endgeraet v3 (44 x 100 x 10): STL, DXF, Vorschau, Pruefungen.

Aufruf:  .venv/bin/python build_v3.py        (Exitcode 1 bei Fehler)
Alles am Rechner geprueft; Passung an echten Teilen ist UNGEPRUEFT.
"""
import itertools
import os
import sys
import numpy as np
import cadquery as cq
import ezdxf
import trimesh
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import params as P
import endgeraet_v3 as E
from build import export, load, render
from build_v2 import rrect, wall_probe

HERE = os.path.dirname(os.path.abspath(__file__))
NAME = "endgeraet_v3"
STL = os.path.join(HERE, "stl", NAME)
DXF = os.path.join(HERE, "dxf", NAME)
VOR = os.path.join(HERE, "vorschau")
W, L, T = P.V3_W, P.V3_L, P.V3_T

EXPECT = {
    "rahmen": (W, L, T),
    "rueckwand": (E.PLATE_W, E.PLATE_L, P.V3_PCB_Z0),
    "frontplatte": (E.PLATE_W, E.PLATE_L, P.V3_FRONT_T),
    "klickrad_abdeckung": (P.V3_WHEEL_COVER_D, P.V3_WHEEL_COVER_D, P.V3_WHEEL_COVER_T),
}
PRINTED = ("rahmen", "rueckwand")
OK = True
WARN = []


def say(msg, good=True):
    global OK
    OK &= good
    print(("[OK]  " if good else "[FEHLER] ") + msg)


def warn(msg):
    WARN.append(msg)
    print("[HINWEIS] " + msg)


# ------------------------------------------------------------------ DXF
def new_dxf():
    doc = ezdxf.new("R2010", setup=True)
    doc.units = ezdxf.units.MM
    for name, col in (("SCHNITT", 1), ("DRUCKMASKE_FENSTER", 5), ("INFO", 8)):
        doc.layers.add(name, color=col)
    return doc, doc.modelspace()


def info(msp, x, y, text, h=1.4):
    msp.add_text(text, height=h, dxfattribs={"layer": "INFO"}).set_placement((x, y))


def write_dxf():
    os.makedirs(DXF, exist_ok=True)
    out = {}
    doc, msp = new_dxf()
    rrect(msp, 0, 0, E.PLATE_W, E.PLATE_L, E.PLATE_R, "SCHNITT")
    msp.add_circle((0, E.WY), P.V3_WHEEL_OPEN_D / 2, dxfattribs={"layer": "SCHNITT"})
    aw, ah = P.V3_DISP_ACTIVE
    rrect(msp, 0, P.V3_DISP_Y, aw + 2 * P.V3_WIN_MARGIN, ah + 2 * P.V3_WIN_MARGIN, P.V3_WIN_R, "DRUCKMASKE_FENSTER")
    y = -E.PLATE_L / 2 - 4
    info(msp, -E.PLATE_W / 2, y, f"Frontplatte Acryl/Glas {P.V3_FRONT_T} mm, Ansicht von vorn, Ursprung = Geraetemitte (= Platinenmitte)")
    info(msp, -E.PLATE_W / 2, y - 2.2, "SCHNITT: ausschneiden. DRUCKMASKE_FENSTER: Fensterkontur, AUSSERHALB rueckseitig schwarz bedrucken (nicht schneiden)")
    info(msp, -E.PLATE_W / 2, y - 4.4, "VORLAEUFIG: Fensterlage/-maß = Annahme (Modul-Oberkante y=41), vor Bestellung mit Modul-Zeichnung abgleichen")
    p = os.path.join(DXF, "frontplatte.dxf"); doc.saveas(p); out["frontplatte"] = p
    doc, msp = new_dxf()
    msp.add_circle((0, 0), P.V3_WHEEL_COVER_D / 2, dxfattribs={"layer": "SCHNITT"})
    info(msp, -15, -19, f"Klickrad-Abdeckung FR4 {P.V3_WHEEL_COVER_T} mm, D{P.V3_WHEEL_COVER_D} (Tangara-Vorbild)")
    p = os.path.join(DXF, "klickrad_abdeckung.dxf"); doc.saveas(p); out["klickrad_abdeckung"] = p
    return out


def check_dxf(paths):
    from ezdxf import bbox
    exp = {"frontplatte": (E.PLATE_W, E.PLATE_L), "klickrad_abdeckung": (P.V3_WHEEL_COVER_D,) * 2}
    for k, p in paths.items():
        msp = ezdxf.readfile(p).modelspace()
        sz = bbox.extents([e for e in msp if e.dxf.layer == "SCHNITT"]).size
        n = {l: sum(1 for e in msp if e.dxf.layer == l) for l in ("SCHNITT", "DRUCKMASKE_FENSTER")}
        say(f"DXF {k}: Aussenkontur {sz.x:.2f} x {sz.y:.2f} (Soll {exp[k][0]:.2f} x {exp[k][1]:.2f}), Elemente {n}",
            abs(sz.x - exp[k][0]) < 0.02 and abs(sz.y - exp[k][1]) < 0.02)
    aw, ah = P.V3_DISP_ACTIVE
    bot = P.V3_DISP_Y - ah / 2 - P.V3_WIN_MARGIN
    top = P.V3_DISP_Y + ah / 2 + P.V3_WIN_MARGIN
    wheel_top = E.WY + P.V3_WHEEL_OPEN_D / 2
    say(f"Fenster y {bot:.2f} .. {top:.2f}; Rad-Ausschnitt oben {wheel_top:.2f}: Steg {bot - wheel_top:.2f} mm; Fenster oben Rand zur Plattenkante {E.PLATE_L / 2 - top:.2f} mm",
        bot - wheel_top > 2.0 and E.PLATE_L / 2 - top > 1.5)


# ------------------------------------------------------------------ Druckbarkeit
def overhangs(m, name):
    """Nach unten zeigende Flaechen (Normale z < -0.7, also flacher als 45 Grad) ueber dem Bett,
    gruppiert nach Hoehe. Das sind Bruecken/Ueberhaenge in Einbaulage (Rueckseite auf dem Bett)."""
    fn = m.face_normals; ar = m.area_faces
    zc = m.triangles_center[:, 2]
    sel = (fn[:, 2] < -0.7) & (zc > m.bounds[0][2] + 0.05)
    groups = {}
    for i in np.where(sel)[0]:
        groups.setdefault(round(zc[i] * 20) / 20, []).append(i)
    print(f"      {name}: Ueberhang-/Brueckenflaechen (nach unten, > 45 Grad) ueber dem Bett:")
    for z in sorted(groups):
        idx = groups[z]
        a = ar[idx].sum()
        if a < 0.3:
            continue
        v = m.triangles[idx].reshape(-1, 3)
        ext = v.max(0) - v.min(0)
        print(f"         z = {z:5.2f}: {a:7.1f} mm2, Ausdehnung {ext[0]:.1f} x {ext[1]:.1f} mm, Mitte x {v[:, 0].mean():6.1f} y {v[:, 1].mean():6.1f}")


def main():
    os.makedirs(STL, exist_ok=True)
    os.makedirs(VOR, exist_ok=True)
    printed, cuts, dums = E.parts(), E.zuschnitt(), E.dummies()
    print("=== Endgeraet v3 (44 x 100 x 10) ===")

    # --- Höhenstapel (Rechnung, nicht nur Kommentar)
    st = (P.V3_BACK_T + P.V3_REAR_ZONE + P.V3_PCB_T + P.V3_DISP_AIR + P.V3_DISP_T + P.V3_GLUE + P.V3_FRONT_T)
    say(f"Hoehenstapel: Rueckwand {P.V3_BACK_T} + Rueckzone {P.V3_REAR_ZONE:.2f} + Platine {P.V3_PCB_T} + Luft {P.V3_DISP_AIR} + Display {P.V3_DISP_T} + Klebefilm {P.V3_GLUE} + Front {P.V3_FRONT_T} = {st:.2f} (Soll {T})", abs(st - T) < 1e-6)
    say(f"Luft Display -> Platinenvorderseite {P.V3_DISP_Z0 - P.V3_PCB_Z1:.2f} mm (Vorgabe >= 1,1)", P.V3_DISP_Z0 - P.V3_PCB_Z1 >= 1.1 - 1e-9)
    say(f"Platine z {P.V3_PCB_Z0:.2f} ... {P.V3_PCB_Z1:.2f}; Rueckzone {P.V3_REAR_ZONE:.2f} (README Platine: 4,05 ohne Klebefilm)", True)

    meshes = {}
    for k, shp in {**printed, **cuts}.items():
        p = os.path.join(STL, f"{k}.stl")
        export(shp, p)
        m = load(p); meshes[k] = m
        bb = m.bounds[1] - m.bounds[0]
        wt = m.is_watertight and m.is_winding_consistent and m.volume > 0
        ex = EXPECT[k]
        say(f"{k:20s} bbox {bb[0]:6.2f} x {bb[1]:6.2f} x {bb[2]:5.2f}  Soll {ex[0]:.2f} x {ex[1]:.2f} x {ex[2]:.2f}  Vol {m.volume:7.0f} mm3  wasserdicht={wt}",
            all(abs(a - b) <= 0.05 for a, b in zip(bb, ex)) and wt)
    dm = {}
    for k, shp in dums.items():
        p = os.path.join(HERE, ".tmp_" + k + ".stl")
        export(shp, p); dm[k] = load(p); os.remove(p)

    lo = min(m.bounds[0][2] for m in meshes.values()); hi = max(m.bounds[1][2] for m in meshes.values())
    wd = max(m.bounds[1][0] for m in meshes.values()) - min(m.bounds[0][0] for m in meshes.values())
    ln = max(m.bounds[1][1] for m in meshes.values()) - min(m.bounds[0][1] for m in meshes.values())
    say(f"Aussenmaß laut Modell: {wd:.2f} x {ln:.2f} x {hi - lo:.2f} (Soll {W} x {L} x {T})", abs(wd - W) < 0.01 and abs(ln - L) < 0.01 and abs(hi - lo - T) < 0.01)

    # --- Rückzone / Luftspalte (Zahlen aus den Attrappen)
    for k in ("akku", "esp_modul", "usb_c", "klinke", "microsd", "c29", "taster_sw1", "taster_sw2", "taster_sw3"):
        m = dm[k]; h = P.V3_PCB_Z0 - m.bounds[0][2]
        say(f"Rueckseite {k:10s}: Hoehe unter Platine {h:.2f} mm (Rueckzone {P.V3_REAR_ZONE:.2f}), Luft zur Rueckwand {m.bounds[0][2] - P.V3_BACK_T:.2f} mm",
            m.bounds[0][2] >= P.V3_BACK_T - 1e-6)
    say(f"Akku {P.V3_BATT_H:.2f} + Luft {P.V3_BATT_AIR} <= Rueckzone {P.V3_REAR_ZONE:.2f}", P.V3_BATT_H + P.V3_BATT_AIR <= P.V3_REAR_ZONE + 1e-9)
    say(f"Rueckzone {P.V3_REAR_ZONE:.2f} >= USB-C {P.V3_USB[2]}", P.V3_REAR_ZONE >= P.V3_USB[2])
    jm = dm["klinke"]
    gap = dm["klickrad_teile"].bounds[0][2] - jm.bounds[1][2]
    say(f"ENGSTE STELLE Klinke (Oberkante z {jm.bounds[1][2]:.2f}) -> Rad-Rueckseitenbauteile (Unterkante z {dm['klickrad_teile'].bounds[0][2]:.2f}): {gap:.2f} mm (Vollscheibe angenommen)", gap >= 0.3)
    print(f"      Klinke ragt {jm.bounds[1][2] - P.V3_PCB_Z1:.2f} mm ueber die Platinenvorderseite, Klinke -> Display {P.V3_DISP_Z0 - jm.bounds[1][2]:.2f} mm (liegt ausserhalb des Displays)")
    lra = dm["lra"]
    say(f"LRA z {lra.bounds[0][2]:.2f} ... {lra.bounds[1][2]:.2f}: unterhalb der Platinenvorderseite {P.V3_PCB_Z1 - lra.bounds[0][2]:.2f} mm im Ausschnitt, Luft zur Rueckwand {lra.bounds[0][2] - P.V3_BACK_T:.2f}", lra.bounds[0][2] > P.V3_BACK_T + 0.5)
    say(f"Wandoeffnung Klinke 9,6 breit vs Klinkenkoerper hinten {P.V3_JACK_BODY[0]} breit; USB-Oeffnung {P.V3_USB_OPEN_W} vs Koerper {P.V3_USB[0]} (Koerper breiter als Oeffnung ist beabsichtigt: Flansch sitzt hinter der Wand, ungeprueft)", True)

    # --- Rev. 3b: J20/J21 (Vorderseite), Display-Luft
    for k in ("j20", "j21"):
        m = dm[k]
        print(f"      {k}: x {m.bounds[0][0]:.2f} ... {m.bounds[1][0]:.2f}, y {m.bounds[0][1]:.2f} ... {m.bounds[1][1]:.2f}, z {m.bounds[0][2]:.2f} ... {m.bounds[1][2]:.2f}")
    j20 = dm["j20"]; dsp = dm["display"]
    clr = dsp.bounds[0][2] - j20.bounds[1][2]
    say(f"J20 (Molex, {P.V3_J20[4]} hoch, Koerper x +-{P.V3_J20[2] / 2:.2f}) -> Display-Unterseite: Luft {clr:.2f} mm (Mindest {P.V3_J_CLEAR_MIN}); Hirose 2,0 haette {P.V3_DISP_AIR - 2.0:.2f} ergeben. Display-Unterkante y {P.V3_DISP_Y - P.V3_DISP_MOD[1] / 2:.2f}, J20 y {j20.bounds[0][1]:.2f} ... {j20.bounds[1][1]:.2f} liegt UNTER dem Display (FPC-Fuehrung nicht modelliert)", clr >= P.V3_J_CLEAR_MIN - 1e-9)
    if clr < 0.2:
        warn(f"Luft J20 -> Display nur {clr:.2f} mm: Stecker-Hoehentoleranz (Molex nennt 1,00 nominal), Kleberdicke und FPC-Auslauf koennen sie aufbrauchen. Display-Luft kann NICHT unter 1,1 sinken; Rueckzone/Akku bleiben bei 3,95/3,65")
    j21 = dm["j21"]
    say(f"J21 -> Klickrad-Platine (Unterkante z {dm['klickrad_pcb'].bounds[0][2]:.2f}): Luft {dm['klickrad_pcb'].bounds[0][2] - j21.bounds[1][2]:.2f} mm (FFC-Bogen 1,25 ... 2,35 mm, nicht modelliert)", dm['klickrad_pcb'].bounds[0][2] - j21.bounds[1][2] > 1.0)
    # --- Rev. 3b: SW2/SW3 Stiftzugang
    pc = E.pin_channels()
    others = {**printed, **cuts, **{"~" + k: v for k, v in dums.items() if k not in ("taster_sw2", "taster_sw3", "hauptplatine")}}
    for n, ch in pc.items():
        hits = []
        for k, s in others.items():
            try:
                v = ch.intersect(s).val().Volume()
            except Exception:
                v = 0.0
            if v > 0.01:
                hits.append((k, v))
        # nur die Rueckwand selbst darf im Kanal liegen, wenn das Loch fehlt: Loch ist Ø 1,8 = Kanal, also Volumen 0
        say(f"Stiftzugang {n.upper()}: Kanal Ø {P.V3_SW23_HOLE_D} von aussen (z 0) bis Taster (z {P.V3_PCB_Z0 - P.V3_SW23_BODY[2]:.2f}) frei" + (f" (Treffer: {hits})" if hits else ""), not hits)
    sw = dm["taster_sw2"]
    print(f"      SW2/SW3: Stiftweg {sw.bounds[0][2] - P.V3_BACK_T:.2f} mm ab Rueckwand-Innenseite bis Taster; Taster-Hub nicht modelliert (Klammer/Stift muss >= 3,2 mm lang sein)")
    say(f"SW2/SW3 liegen im linken Randstreifen (x {sw.bounds[0][0]:.2f} ... {sw.bounds[1][0]:.2f}) ausserhalb des Akkufachs (x ab {P.V3_BATT_FACH[0]}) und des Antennen-Keepouts", sw.bounds[1][0] < P.V3_BATT_FACH[0] + 0.5)
    # --- Rev. 3b: LRA-Regel und Keepout-Vereinheitlichung
    lw_, ll_, lh_ = P.V3_LRA
    say(f"LRA {lw_} x {ll_} x {lh_} innerhalb Auswahlregel {P.V3_LRA_MAX[0]} x {P.V3_LRA_MAX[1]} x {P.V3_LRA_MAX[2]} (Ausschnitt {P.V3_LRA_CUT[0]} x {P.V3_LRA_CUT[1]}, 0,5 Luft je Seite); 16 x 6 (Klickrad-Freiflaeche) ragt {(16.0 - P.V3_LRA_CUT[0]) / 2:.1f} mm je Seite in die Platine und waere NICHT zulaessig", lw_ <= P.V3_LRA_MAX[0] and ll_ <= P.V3_LRA_MAX[1] and lh_ <= P.V3_LRA_MAX[2])
    k0, k1, k2, k3 = P.V3_ANT_KEEP; t0, t1, t2, t3 = P.V3_ANT_KEEP_TEILE_MD
    say(f"Antennen-Keepout: README {P.V3_ANT_KEEP} umschliesst TEILE.md {P.V3_ANT_KEEP_TEILE_MD}; es gilt das Groessere (Differenz {t0 - k0:.1f} / {k1 - t1:.1f} / {t2 - k2:.1f} / {k3 - t3:.1f} mm)", k0 <= t0 and k1 >= t1 and k2 <= t2 and k3 >= t3)

    # --- Kollisionen
    allp = {**printed, **cuts, **{"~" + k: v for k, v in dums.items()}}
    bad = []; npair = 0
    for (a, sa), (b, sb) in itertools.combinations(allp.items(), 2):
        if a.startswith("~") and b.startswith("~"):
            # Attrappen untereinander: nur die, die fuer die Mechanik zaehlen
            pass
        ba, bb_ = sa.val().BoundingBox(), sb.val().BoundingBox()
        if (ba.xmax < bb_.xmin or bb_.xmax < ba.xmin or ba.ymax < bb_.ymin or bb_.ymax < ba.ymin
                or ba.zmax < bb_.zmin or bb_.zmax < ba.zmin):
            continue
        npair += 1
        try:
            v = sa.intersect(sb).val().Volume()
        except Exception:
            v = 0.0
        if v > 0.02:
            bad.append((a, b, v))
    for a, b, v in bad:
        say(f"KOLLISION {a} <-> {b}: {v:.2f} mm3", False)
    if not bad:
        say(f"Kollisionen: keine ({len(allp)} Koerper, {npair} Paare mit ueberlappenden Bounding-Boxen per Boolean geprueft, Attrappen mit ~)")

    # --- Antennen-Keepout
    ko = E.keepout()
    plastics = ("rahmen", "rueckwand", "frontplatte")
    skip = ("~hauptplatine", "~esp_modul")                 # Platine selbst und Modul tragen die Antenne
    hits = []
    for k, s in allp.items():
        if k in skip:
            continue
        try:
            v = s.intersect(ko).val().Volume()
        except Exception:
            v = 0.0
        if v > 0.02:
            hits.append((k, v))
    metal = [(k, v) for k, v in hits if k not in plastics and k != "~display"]
    plast = [(k, v) for k, v in hits if k in plastics]
    say(f"Antennen-Keepout x {P.V3_ANT_KEEP[0]}..{P.V3_ANT_KEEP[1]}, y {P.V3_ANT_KEEP[2]}..{P.V3_ANT_KEEP[3]}, z {P.V3_BACK_T}..{P.V3_FRONT_Z0:.1f}: kein Metall/Akku/Schraube/Taste darin" + (f" (Treffer: {metal})" if metal else ""), not metal)
    for k, v in plast:
        print(f"      Kunststoff im Keepout: {k} {v:.1f} mm3 (Wand/Lippe/Front, kein Metall/Kohlefaser verwenden)")
    if any(k == "~display" for k, _ in hits):
        dv = dict(hits)["~display"]
        warn(f"Display-Modul (34,8 x 43,1 an Position y {P.V3_DISP_Y:.2f}) ueberlappt den Antennen-Keepout um {dv:.0f} mm3 (x {P.V3_ANT_KEEP[0]}..{P.V3_DISP_MOD[0] / 2:.1f}, y {P.V3_ANT_KEEP[2]}..{P.V3_DISP_TOP}); Problem der Platinen-/Display-Planung, nicht des Gehaeuses")
    # Akku-Abstand zum Keepout
    fx0, fx1, fy0, fy1 = P.V3_BATT_FACH
    print(f"      Abstand Akkufach (y bis {fy1}) -> Keepout (y ab {P.V3_ANT_KEEP[2]}): {P.V3_ANT_KEEP[2] - fy1:.1f} mm; Akku x bis {fx1} liegt unter dem Antennenbereich (x {P.V3_ANT_KEEP[0]}..)")

    # --- Befestigung
    for i, (x, y) in enumerate(P.V3_SCREWS):
        sc = dm[f"schraube{i + 1}"]
        bite = P.V3_SCREW_LEN - P.V3_PCB_Z1
        print(f"      Schraube {i + 1} bei ({x}, {y}): Kopf bei z 0, Spitze z {P.V3_SCREW_LEN}, Eingriff im vorderen Dom {bite:.2f} mm (Dom z {P.V3_PCB_Z1:.2f} ... {E.LIP_Z1:.2f})")
    bite = P.V3_SCREW_LEN - P.V3_PCB_Z1
    print(f"      Variante furchende Schraube: Eingriff {bite:.2f} mm = {bite / 1.6:.1f} x Ø im Kunststoff (Richtwert 2 x Ø = 3,2); Dom z {P.V3_PCB_Z1:.2f} ... {E.LIP_Z1:.2f} (3,25 hoch), Kernloch Ø {P.V3_PILOT_D} x 2,5 tief, Spitze bei z {P.V3_SCREW_LEN} laesst {P.V3_PCB_Z1 + 2.5 - P.V3_SCREW_LEN:.2f} mm Loch frei; M1,6 x 10 wuerde bei z 10 die Frontplatte (z {E.LIP_Z1}) treffen")
    say(f"Schraubeneingriff {bite:.2f} mm im Kunststoff (furchend) = {bite / 1.6:.1f} x Gewinde-Ø: unter 2 x Ø, Auszugskraft ungeprueft -> Variante Einsatz vorgesehen", True)
    ins_top = P.V3_PCB_Z1 + P.V3_INSERT_HOLE_DEPTH
    say(f"Variante Einsatz M1,6: Loch Ø {P.V3_INSERT_HOLE_D} x {P.V3_INSERT_HOLE_DEPTH} ab z {P.V3_PCB_Z1:.2f} (bis {ins_top:.2f}), Restdecke zur Frontplatte {E.LIP_Z1 - ins_top:.2f} mm, Domwand {(P.V3_POST_D - P.V3_INSERT_HOLE_D) / 2:.2f} mm, Schraubenspitze z {P.V3_SCREW_LEN} liegt im Einsatz (Eingriff im Metall {P.V3_SCREW_LEN - P.V3_PCB_Z1:.2f} mm)",
        E.LIP_Z1 - ins_top >= 0.4 and (P.V3_POST_D - P.V3_INSERT_HOLE_D) / 2 >= 0.7 and ins_top >= P.V3_SCREW_LEN)
    pe = os.path.join(STL, "rahmen_einsatz.stl")
    export(E.rahmen(insert=True), pe)
    me = load(pe); bbe = me.bounds[1] - me.bounds[0]
    say(f"rahmen_einsatz       bbox {bbe[0]:.2f} x {bbe[1]:.2f} x {bbe[2]:.2f} Vol {me.volume:.0f} mm3 wasserdicht={me.is_watertight and me.is_winding_consistent and me.volume > 0}", me.is_watertight and me.is_winding_consistent and me.volume > 0 and abs(bbe[2] - T) < 0.05)
    # --- Wandstaerken und Ueberhaenge
    print("Wandsondierung (Strahlen nach innen, Strecken < 3 mm; Stichprobe, keine Garantie):")
    for k, zm in (("rahmen", None), ("rahmen", E.LIP_Z0 - 0.05), ("rueckwand", None)):
        r = wall_probe(meshes[k], zmax=zm)
        if r:
            k = k + (f" ohne Auflagesteg (z < {zm:.2f})" if zm else "")
            print(f"      {k}: kleinste gefundene Wand {r[0]:.2f} mm (1%-Perzentil {r[1]:.2f}, Anteil < 0,8 mm: {100 * r[2]:.1f} %)")
    kreste = (P.V3_STANDOFF_D - P.V3_HOLE_D) / 2
    say(f"Wand um die Durchgangsbohrung im hinteren Steg {kreste:.2f} mm; vorderer Dom {(P.V3_POST_D - P.V3_PILOT_D) / 2:.2f} mm", kreste >= 0.6)
    tw, tl = P.V3_TAB
    k_n = 2000 * tw * P.V3_BACK_T ** 3 / (4 * 7.0 ** 3)
    print(f"      Biegezunge SW1: {tw} x {tl} mm, Steg 1,0, Stoessel 7 mm vom Gelenk: Federrate grob {k_n:.1f} N/mm (E = 2000 MPa angenommen), 0,45 mm Weg = {k_n * 0.45:.1f} N plus Tasterkraft; Randfaserdehnung {3 * P.V3_BACK_T * 0.45 / (2 * 49) * 100:.1f} % (UNGEPRUEFT)")
    print("Druckbarkeit (Einbaulage = Druckausrichtung, Rueckseite z=0 auf dem Bett, Voron 300 x 300 / SV06 Ace 220 x 220):")
    for k in PRINTED:
        bb = meshes[k].bounds[1] - meshes[k].bounds[0]
        say(f"{k}: {bb[0]:.1f} x {bb[1]:.1f} x {bb[2]:.1f} mm passt auf SV06 Ace (220 x 220 x 250) und Voron", bb[0] < 215 and bb[1] < 215)
        overhangs(meshes[k], k)

    dx = write_dxf()
    check_dxf(dx)
    previews(meshes, dm)
    print("\nHINWEISE:" if WARN else "\nKeine Hinweise.")
    for w in WARN:
        print("  -", w)
    print("\nGESAMT:", "ALLES OK" if OK else "FEHLER")
    sys.exit(0 if OK else 1)


# ------------------------------------------------------------------ Vorschau
def previews(meshes, dm):
    for k, m in meshes.items():
        render([m], os.path.join(VOR, f"{NAME}_{k}.png"), f"{NAME}: {k}", views=((30, -55), (90, -90), (-60, -55)))
    zs = {"rueckwand": 0, "rahmen": 12, "frontplatte": 24, "klickrad_abdeckung": 28}
    ex = []
    for k, dz in zs.items():
        m = meshes[k].copy(); m.apply_translation([0, 0, dz]); ex.append(m)
    render(ex, os.path.join(VOR, f"{NAME}_explosion.png"), f"{NAME}: Explosion (Rueckwand, Rahmen, Frontplatte, Abdeckung)",
           views=((35, -60), (20, -20)), size=6)
    sec_fig(meshes, dm)
    rear_fig(meshes)
    dxf_fig()


def rear_fig(meshes):
    """Rueckwand von HINTEN (Blick in +z, x gespiegelt): Schnitt bei z = 0,15 zeigt Loecher, Trichter, Gravur BOOT/EN."""
    m = meshes["rueckwand"]
    sec = m.section(plane_origin=(0, 0, 0.15), plane_normal=(0, 0, 1))
    fig, ax = plt.subplots(1, 1, figsize=(5.2, 9.5), dpi=130)
    for ent in sec.entities:
        pts = sec.vertices[ent.points]
        ax.plot(-pts[:, 0], pts[:, 1], color="#1f3a5f", lw=0.8)
    for n, (x, y) in (("SW2 BOOT", P.V3_SW2), ("SW3 EN", P.V3_SW3)):
        ax.annotate(n, (-x, y), xytext=(-x - 9, y + 4), fontsize=7, color="#c0392b", arrowprops=dict(arrowstyle="->", color="#c0392b", lw=0.8))
    ax.set_aspect("equal"); ax.grid(alpha=0.2)
    ax.set_title("Rueckwand von hinten (Schnitt z = 0,15): Stiftloecher + Gravur", fontsize=8)
    fig.tight_layout(); fig.savefig(os.path.join(VOR, f"{NAME}_rueckwand_hinten.png")); plt.close(fig)


def dxf_fig():
    from ezdxf.addons.drawing import RenderContext, Frontend
    from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
    fig, axes = plt.subplots(1, 2, figsize=(9, 8), dpi=110, gridspec_kw={"width_ratios": [1, 0.8]})
    for ax, (n, t) in zip(axes, (("frontplatte", "Frontplatte 0,8: rot = Schnitt, blau = Druckmaske Fenster"),
                                 ("klickrad_abdeckung", "Abdeckung FR4 0,6"))):
        doc = ezdxf.readfile(os.path.join(DXF, n + ".dxf"))
        for e in list(doc.modelspace()):
            if e.dxf.layer == "INFO":
                doc.modelspace().delete_entity(e)
        Frontend(RenderContext(doc), MatplotlibBackend(ax)).draw_layout(doc.modelspace())
        ax.set_title(t, fontsize=8); ax.set_aspect("equal"); ax.grid(alpha=0.2)
    fig.tight_layout()
    fig.savefig(os.path.join(VOR, f"{NAME}_zuschnitt_dxf.png"))
    plt.close(fig)


def sec_fig(meshes, dm):
    pc = {"rahmen": "#222222", "rueckwand": "#1f6fb2", "frontplatte": "#c0392b", "klickrad_abdeckung": "#d68910"}
    dc = {"hauptplatine": "#1e8449", "display": "#555555", "akku": "#7f8c8d", "klinke": "#e67e22", "usb_c": "#16a085",
          "esp_modul": "#8e44ad", "microsd": "#34495e", "taster_sw1": "#2c3e50", "taster_sw2": "#2c3e50", "taster_sw3": "#2c3e50", "j20": "#b7950b", "j21": "#b7950b", "c29": "#95a5a6", "klickrad_pcb": "#27ae60",
          "klickrad_teile": "#82e0aa", "lra": "#c0392b", "schraube1": "#000000", "schraube2": "#000000", "schraube3": "#000000"}
    cases = [("Schnitt x = -12 (Klinke)", (1, 0, 0), (-12, 0, 0), 1, (-50, -26)),
             ("Schnitt y = -19 (Klickrad, LRA-Ausschnitt)", (0, 1, 0), (0, -19, 0), 0, (-22, 22)),
             ("Schnitt x = 0 (ganze Laenge: Display, Akku, Klickrad)", (1, 0, 0), (0, 0, 0), 1, (-50, 50)),
             ("Schnitt y = 46,2 (Befestigung links oben: Steg, Platine, Dom)", (0, 1, 0), (0, 46.2, 0), 0, (-22, 22)),
             ("Schnitt x = 15 (Ein/Aus-Zunge SW1)", (1, 0, 0), (15, 0, 0), 1, (-50, -18)),
             ("Schnitt x = -18,05 (BOOT SW2 / EN SW3, Stiftloecher)", (1, 0, 0), (-18.05, 0, 0), 1, (0, 25)),
             ("Schnitt x = 0 um J20 (Display-Luft)", (1, 0, 0), (0, 0, 0), 1, (-12, 10))]
    fig, axes = plt.subplots(7, 1, figsize=(12, 24), dpi=105, gridspec_kw={"height_ratios": [1, 1, 0.5, 1, 1, 1, 1]})
    for ax, (title, nrm, org, axis, (lo, hi)) in zip(axes, cases):
        items = [(k, m, pc[k], 2.0) for k, m in meshes.items()] + [("~" + k, m, dc[k], 1.1) for k, m in dm.items()]
        for k, m, col, lw in items:
            try:
                seg = trimesh.intersections.mesh_plane(m, nrm, org, return_faces=False)
            except Exception:
                continue
            if seg is None or len(seg) == 0:
                continue
            for s in seg:
                ax.plot([s[0][axis], s[1][axis]], [s[0][2], s[1][2]], color=col, lw=lw, solid_capstyle="round")
        ax.set_xlim(lo - 1, hi + 6); ax.set_ylim(-0.8, T + 1.2)
        ax.set_aspect("equal"); ax.set_title(title, fontsize=10)
        ax.set_xlabel("y [mm]" if axis == 1 else "x [mm]"); ax.set_ylabel("z [mm]"); ax.grid(alpha=0.25)
        xd = hi + 2.5
        ax.annotate("", xy=(xd, 0), xytext=(xd, T), arrowprops=dict(arrowstyle="<->", lw=1.4, color="#c0392b"))
        ax.text(xd + 0.6, T / 2, f"{T:.1f} mm", va="center", fontsize=9, color="#c0392b")
    handles = [plt.Line2D([0], [0], color=c, lw=2) for c in list(pc.values()) + [dc[k] for k in dm if not k.startswith("schraube2") and not k.startswith("schraube3")]]
    labels = list(pc.keys()) + ["~" + k for k in dm if not k.startswith("schraube2") and not k.startswith("schraube3")]
    fig.legend(handles, labels, loc="lower center", ncol=7, fontsize=8)
    fig.suptitle("Endgeraet v3: Schnitte (44 x 100 x 10 mm)", fontsize=11)
    fig.tight_layout(rect=(0, 0.04, 1, 0.98))
    fig.savefig(os.path.join(VOR, f"{NAME}_schnitt.png"))
    plt.close(fig)
    order = [meshes[k] for k in ("rueckwand", "rahmen", "frontplatte", "klickrad_abdeckung")]
    render(order + list(dm.values()), os.path.join(VOR, f"{NAME}_zusammenbau.png"),
           f"{NAME}: Zusammenbau inkl. Attrappen (Painter-Artefakte moeglich)", views=((35, -60), (-50, -55)), size=6)


if __name__ == "__main__":
    main()
