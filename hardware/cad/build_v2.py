"""Baut Endgeraet v2 (Duennbau A): STL, DXF, Vorschau, Pruefungen.

Aufruf:  .venv/bin/python build_v2.py        (Exitcode 1 bei Fehler)
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
import endgeraet_v2 as E
from build import export, load, render

HERE = os.path.dirname(os.path.abspath(__file__))
NAME = "endgeraet_v2"
STL = os.path.join(HERE, "stl", NAME)
DXF = os.path.join(HERE, "dxf", NAME)
VOR = os.path.join(HERE, "vorschau")
W, L, T = P.E2_W, P.E2_L, P.E2_T
LIPZ = E.LIP_Z0 - 0.05

EXPECT = {
    "rahmen": (W, L, T),
    "rueckwand": (E.PLATE_W, E.PLATE_L, P.E2_BACK_T + P.E2_BATT_RIB_H),
    "power_taste": (1.5, 6.4, 2.8),
    "frontplatte": (E.PLATE_W, E.PLATE_L, P.E2_FRONT_T),
    "klickrad_abdeckung": (P.E2_WHEEL_COVER_D, P.E2_WHEEL_COVER_D, P.E2_WHEEL_COVER_T),
}
OK = True


def say(msg, good=True):
    global OK
    OK &= good
    print(("[OK]  " if good else "[FEHLER] ") + msg)


# ------------------------------------------------------------------ DXF
def rrect(msp, cx, cy, w, h, r, layer):
    """Rechteck mit Eckenradius als LWPOLYLINE mit Bulge (Einheit mm)."""
    b = np.tan(np.radians(90) / 4)
    x0, x1, y0, y1 = cx - w / 2, cx + w / 2, cy - h / 2, cy + h / 2
    pts = [(x0 + r, y0, 0), (x1 - r, y0, b), (x1, y0 + r, 0), (x1, y1 - r, b),
           (x1 - r, y1, 0), (x0 + r, y1, b), (x0, y1 - r, 0), (x0, y0 + r, b)]
    msp.add_lwpolyline(pts, format="xyb", close=True, dxfattribs={"layer": layer})


def new_dxf():
    doc = ezdxf.new("R2010", setup=True)
    doc.units = ezdxf.units.MM
    for name, col in (("SCHNITT", 1), ("DRUCKMASKE_FENSTER", 5), ("BOHRUNG", 3), ("INFO", 8)):
        doc.layers.add(name, color=col)
    return doc, doc.modelspace()


def info(msp, x, y, text, h=1.4):
    msp.add_text(text, height=h, dxfattribs={"layer": "INFO"}).set_placement((x, y))


def write_dxf():
    os.makedirs(DXF, exist_ok=True)
    out = {}
    # Frontplatte
    doc, msp = new_dxf()
    rrect(msp, 0, 0, E.PLATE_W, E.PLATE_L, E.PLATE_R, "SCHNITT")
    msp.add_circle((0, E.WY), P.E2_WHEEL_OPEN_D / 2, dxfattribs={"layer": "SCHNITT"})
    aw, ah = P.E2_DISP_ACTIVE
    ww, wh = aw + 2 * P.E2_WIN_MARGIN, ah + 2 * P.E2_WIN_MARGIN
    rrect(msp, 0, P.E2_DISP_Y + P.E2_DISP_ACTIVE_DY, ww, wh, P.E2_WIN_R, "DRUCKMASKE_FENSTER")
    info(msp, -E.PLATE_W / 2, -E.PLATE_L / 2 - 4, f"Frontplatte Acryl/Glas {P.E2_FRONT_T} mm, Ansicht von vorn, Ursprung = Gehaeusemitte")
    info(msp, -E.PLATE_W / 2, -E.PLATE_L / 2 - 6.2, "SCHNITT: ausschneiden. DRUCKMASKE_FENSTER: Fensterkontur, AUSSERHALB rueckseitig schwarz bedrucken (nicht schneiden)")
    info(msp, -E.PLATE_W / 2, -E.PLATE_L / 2 - 8.4, "VORLAEUFIG: Fensterlage/-maß aus DUENNBAU.md, vor Bestellung mit Modul-Zeichnung abgleichen")
    p = os.path.join(DXF, "frontplatte.dxf"); doc.saveas(p); out["frontplatte"] = p
    # Rueckwand FR4 (Alternative)
    doc, msp = new_dxf()
    rrect(msp, 0, 0, E.PLATE_W, E.PLATE_L, E.PLATE_R, "SCHNITT")
    for x, y in P.E2_SCREWS:
        msp.add_circle((x, y), P.E2_SCREW_CLEAR_D / 2, dxfattribs={"layer": "BOHRUNG"})
    info(msp, -E.PLATE_W / 2, -E.PLATE_L / 2 - 4, f"Rueckwand FR4 {P.E2_BACK_FR4_T} mm (Alternative zur gedruckten 1,0), Ansicht von hinten NICHT gespiegelt")
    info(msp, -E.PLATE_W / 2, -E.PLATE_L / 2 - 6.2, "Bohrungen D1,8; Senkung D3,2 aussen (90 Grad) fuer M1,6-Senkkopf; VORLAEUFIG")
    p = os.path.join(DXF, "rueckwand_fr4.dxf"); doc.saveas(p); out["rueckwand_fr4"] = p
    # Klickrad-Abdeckung
    doc, msp = new_dxf()
    msp.add_circle((0, 0), P.E2_WHEEL_COVER_D / 2, dxfattribs={"layer": "SCHNITT"})
    info(msp, -15, -19, f"Klickrad-Abdeckung FR4 {P.E2_WHEEL_COVER_T} mm, D{P.E2_WHEEL_COVER_D} (Tangara-Vorbild)")
    p = os.path.join(DXF, "klickrad_abdeckung.dxf"); doc.saveas(p); out["klickrad_abdeckung"] = p
    return out


def check_dxf(paths):
    exp = {"frontplatte": (E.PLATE_W, E.PLATE_L), "rueckwand_fr4": (E.PLATE_W, E.PLATE_L),
           "klickrad_abdeckung": (P.E2_WHEEL_COVER_D, P.E2_WHEEL_COVER_D)}
    from ezdxf import bbox
    for k, p in paths.items():
        doc = ezdxf.readfile(p)
        msp = doc.modelspace()
        cut = [e for e in msp if e.dxf.layer == "SCHNITT"]
        bb = bbox.extents(cut)
        sz = bb.size
        good = abs(sz.x - exp[k][0]) < 0.02 and abs(sz.y - exp[k][1]) < 0.02
        n = {l: sum(1 for e in msp if e.dxf.layer == l) for l in ("SCHNITT", "DRUCKMASKE_FENSTER", "BOHRUNG")}
        say(f"DXF {k}: Aussenkontur {sz.x:.2f} x {sz.y:.2f} (Soll {exp[k][0]:.2f} x {exp[k][1]:.2f}), Elemente {n}", good)
    # Fenster muss innerhalb der Platte und ueber dem Rad-Ausschnitt liegen
    aw, ah = P.E2_DISP_ACTIVE
    top = P.E2_DISP_Y + ah / 2 + P.E2_WIN_MARGIN
    bot = P.E2_DISP_Y - ah / 2 - P.E2_WIN_MARGIN
    wheel_top = E.WY + P.E2_WHEEL_OPEN_D / 2
    say(f"Fenster y {bot:.2f} .. {top:.2f}, Rad-Ausschnitt oben {wheel_top:.2f}: Steg {bot - wheel_top:.2f} mm", bot - wheel_top > 2.0 and top < E.PLATE_L / 2 - 1.5)


# ------------------------------------------------------------------ Pruefungen
def wall_probe(m, n=6000, seed=1, zmax=None):
    """Grobe Wandstaerke: Strahl von Oberflaechenpunkten nach innen (Moeller-Trumbore, numpy).
    Liefert (min, 1%-Perzentil, Anteil <0,8 mm) oder None. Nur Strecken < 3 mm zaehlen als Wand."""
    pts, fi = trimesh.sample.sample_surface(m, n, seed=seed)
    if zmax is not None:
        keep = pts[:, 2] < zmax
        pts, fi = pts[keep], fi[keep]
    n = len(pts)
    nr = m.face_normals[fi]
    o = pts - nr * 1e-3
    dvec = -nr
    tri = m.triangles
    v0 = tri[:, 0]; e1 = tri[:, 1] - v0; e2 = tri[:, 2] - v0
    best = np.full(n, np.inf)
    for i0 in range(0, n, 200):
        oo = o[i0:i0 + 200, None, :]; dd = dvec[i0:i0 + 200, None, :]
        pv = np.cross(dd, e2[None])
        det = np.einsum("ijk,ijk->ij", np.broadcast_to(e1[None], pv.shape), pv)
        ok = np.abs(det) > 1e-9
        inv = np.where(ok, 1.0 / np.where(ok, det, 1), 0)
        tv = oo - v0[None]
        u = np.einsum("ijk,ijk->ij", tv, pv) * inv
        qv = np.cross(tv, e1[None])
        v = np.einsum("ijk,ijk->ij", np.broadcast_to(dd, qv.shape), qv) * inv
        t = np.einsum("ijk,ijk->ij", np.broadcast_to(e2[None], qv.shape), qv) * inv
        hit = ok & (u >= 0) & (v >= 0) & (u + v <= 1) & (t > 1e-4)
        best[i0:i0 + 200] = np.where(hit, t, np.inf).min(axis=1)
    d = best[best < 3.0] + 1e-3
    if len(d) == 0:
        return None
    return float(d.min()), float(np.percentile(d, 1)), float((d < 0.79).mean())


def main():
    os.makedirs(STL, exist_ok=True)
    os.makedirs(VOR, exist_ok=True)
    printed, cuts, dums = E.parts(), E.zuschnitt(), E.dummies()
    print("=== Endgeraet v2 (Duennbau A) ===")
    meshes = {}
    for k, shp in {**printed, **cuts}.items():
        p = os.path.join(STL, f"{k}.stl")
        export(shp, p)
        m = load(p); meshes[k] = m
        bb = m.bounds[1] - m.bounds[0]
        wt = m.is_watertight and m.is_winding_consistent and m.volume > 0
        ex = EXPECT[k]
        good = all(abs(a - b) <= 0.05 for a, b in zip(bb, ex))
        say(f"{k:20s} bbox {bb[0]:6.2f} x {bb[1]:6.2f} x {bb[2]:5.2f}  Soll {ex[0]:.2f} x {ex[1]:.2f} x {ex[2]:.2f}  Vol {m.volume:7.0f} mm3  wasserdicht={wt}", good and wt)
    dm = {}
    for k, shp in dums.items():
        p = os.path.join(HERE, ".tmp_" + k + ".stl")
        export(shp, p); dm[k] = load(p); os.remove(p)

    # Gesamtdicke aus dem Modell
    allm = list(meshes.values())
    lo = min(m.bounds[0][2] for m in allm); hi = max(m.bounds[1][2] for m in allm)
    say(f"Gesamtdicke laut Modell (alle Teile): {hi - lo:.2f} mm (Soll {T})", abs(hi - lo - T) < 0.01)
    wd = max(m.bounds[1][0] for m in allm) - min(m.bounds[0][0] for m in allm)
    ln = max(m.bounds[1][1] for m in allm) - min(m.bounds[0][1] for m in allm)
    say(f"Aussenmaß laut Modell: {wd:.2f} x {ln:.2f} x {hi - lo:.2f}", True)

    # Rueckseitenhoehe
    rear = {k: m for k, m in dm.items() if k in ("akku", "esp_modul", "usb_c", "klinke")}
    for k, m in rear.items():
        h_below = P.E2_PCB_Z0 - m.bounds[0][2]
        say(f"Rueckseite {k:10s}: Hoehe unter Platine {h_below:.2f} mm (Grenze {P.E2_REAR_ZONE}), unterste Kante z={m.bounds[0][2]:.2f}",
            h_below <= P.E2_REAR_ZONE + 1e-6 + (0.0 if k != 'klinke' else 0.0) and m.bounds[0][2] >= P.E2_BACK_T - 1e-6)
    jm = dm["klinke"]
    print(f"      Klinke ragt {jm.bounds[1][2] - P.E2_PCB_Z1:.2f} mm ueber die Platinenvorderseite (z {jm.bounds[1][2]:.2f}); Klickrad-Platine unten bei z {P.E2_WHEEL_PCB_Z0:.2f}")
    say(f"Luft Klinke -> Klickrad-Platine: {P.E2_WHEEL_PCB_Z0 - jm.bounds[1][2]:.2f} mm", P.E2_WHEEL_PCB_Z0 - jm.bounds[1][2] > 0.2)
    say(f"Luft Platine -> Display: {P.E2_DISP_Z0 - P.E2_PCB_Z1:.2f} mm (Bauteile vorn unter dem Display nur <= diesem Wert)", P.E2_DISP_Z0 - P.E2_PCB_Z1 > 0)
    say(f"Luft Platine -> Klickrad-Platine: {P.E2_WHEEL_PCB_Z0 - P.E2_PCB_Z1:.2f} mm = vorn + Radrueckseite zusammen (LRA {P.E2_LRA[2]:.1f})", True)

    # Kollisionen: gedruckte + Zuschnitt + Attrappen paarweise (Boolean)
    allp = {**printed, **cuts, **{"~" + k: v for k, v in dums.items()}}
    bad = []; npair = 0
    for (a, sa), (b, sb) in itertools.combinations(allp.items(), 2):
        if a.startswith("~") and b.startswith("~") and not (a, b) in ():
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
        say(f"Kollisionen: keine ({len(allp)} Koerper, {npair} ueberlappende Bounding-Box-Paare per Boolean geprueft, Attrappen mit ~)")

    # Wandstaerken
    print("Wandsondierung (Strahlen nach innen, Strecken < 3 mm; Zahlen sind eine Stichprobe, keine Garantie):")
    for k, zm in (("rahmen", None), ("rahmen", LIPZ), ("rueckwand", None)):
        r = wall_probe(meshes[k], zmax=zm)
        if r:
            tag = k + (" ohne Auflagesteg (z<%.2f)" % zm if zm else "")
            print(f"      {tag}: kleinste gefundene Wand {r[0]:.2f} mm (1%-Perzentil {r[1]:.2f}, Anteil < 0,8 mm: {100 * r[2]:.1f} %)")
    say(f"Parameter: Seitenwand {P.E2_WALL}, Randsteg {P.E2_RIM}, Rueckwand {P.E2_BACK_T}, Front-Falzsteg {T - P.E2_FRONT_Z0:.1f} hoch (alle >= 0,8)",
        min(P.E2_WALL, P.E2_RIM, P.E2_BACK_T) >= 0.8)
    kreste = P.E2_BACK_T - (P.E2_SCREW_CSK_D - P.E2_SCREW_CLEAR_D) / 2
    say(f"Senkschraube: Restwand unter Senkung {kreste:.2f} mm (duenn! Alternative FR4 {P.E2_BACK_FR4_T})", kreste >= 0.25)

    dx = write_dxf()
    check_dxf(dx)

    previews(meshes, dm)
    print("\nGESAMT:", "ALLES OK" if OK else "FEHLER")
    sys.exit(0 if OK else 1)


# ------------------------------------------------------------------ Vorschau
def previews(meshes, dm):
    for k, m in meshes.items():
        render([m], os.path.join(VOR, f"{NAME}_{k}.png"), f"{NAME}: {k}", views=((30, -55), (90, -90), (-60, -55)))
    order = ["rueckwand", "rahmen", "power_taste", "frontplatte", "klickrad_abdeckung"]
    zs = {"rueckwand": 0, "rahmen": 11, "power_taste": 11, "frontplatte": 22, "klickrad_abdeckung": 26}
    ex = []
    for k in order:
        m = meshes[k].copy(); m.apply_translation([0, 0, zs[k]]); ex.append(m)
    render(ex, os.path.join(VOR, f"{NAME}_explosion.png"), f"{NAME}: Explosion (Rueckwand, Rahmen, Taste, Frontplatte, Abdeckung)",
           views=((35, -60), (20, -20)), size=6)
    sec_fig(meshes, dm)
    dxf_fig()


def dxf_fig():
    """Vorschau der Zuschnitt-DXF (Frontplatte, Rueckwand FR4, Abdeckung)."""
    from ezdxf.addons.drawing import RenderContext, Frontend
    from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
    fig, axes = plt.subplots(1, 3, figsize=(12, 7), dpi=110, gridspec_kw={"width_ratios": [1, 1, 0.8]})
    for ax, (n, t) in zip(axes, (("frontplatte", "Frontplatte 0,8: rot = Schnitt, blau = Druckmaske Fenster"),
                                 ("rueckwand_fr4", "Rueckwand FR4 0,8 (Alternative)"), ("klickrad_abdeckung", "Abdeckung FR4 0,6"))):
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
    pc = {"rahmen": "#222222", "rueckwand": "#1f6fb2", "frontplatte": "#c0392b", "klickrad_abdeckung": "#d68910",
          "power_taste": "#7d3c98"}
    dc = {"hauptplatine": "#1e8449", "display": "#555555", "akku": "#7f8c8d", "klinke": "#e67e22", "usb_c": "#16a085",
          "esp_modul": "#8e44ad", "klickrad_pcb": "#27ae60", "lra": "#c0392b", "taster_pwr": "#2c3e50"}
    cases = [("Schnitt x = -12 (Klinke)", (1, 0, 0), (-12, 0, 0), 1, (-47.5, -24), 8.2),
             ("Schnitt y = -22 (Klickrad, Frontplatte, Abdeckung)", (0, 1, 0), (0, -22, 0), 0, (-21.5, 21.5), 8.2),
             ("Schnitt x = 0 (Display, Akku, ganze Laenge)", (1, 0, 0), (0, 0, 0), 1, (-46, 46), 3.0)]
    fig, axes = plt.subplots(3, 1, figsize=(12, 13), gridspec_kw={"height_ratios": [1, 1, 0.55]}, dpi=110)
    for ax, (title, nrm, org, axis, (lo, hi), _) in zip(axes, cases):
        items = [(k, m, pc[k], 2.2) for k, m in meshes.items()] + [("~" + k, m, dc[k], 1.2) for k, m in dm.items()]
        for k, m, col, lw in items:
            try:
                seg = trimesh.intersections.mesh_plane(m, nrm, org, return_faces=False)
            except Exception:
                continue
            if seg is None or len(seg) == 0:
                continue
            for s in seg:
                a = (s[0][axis], s[0][2]); b = (s[1][axis], s[1][2])
                ax.plot([a[0], b[0]], [a[1], b[1]], color=col, lw=lw, solid_capstyle="round")
        ax.set_xlim(lo - 1, hi + 4.5); ax.set_ylim(-1.2, T + 1.5)
        ax.set_aspect("equal"); ax.set_title(title, fontsize=10)
        ax.set_xlabel("y [mm]" if axis == 1 else "x [mm]"); ax.set_ylabel("z [mm]")
        ax.grid(alpha=0.25)
        xd = hi + 2.5
        ax.annotate("", xy=(xd, 0), xytext=(xd, T), arrowprops=dict(arrowstyle="<->", lw=1.4, color="#c0392b"))
        ax.text(xd + 0.5, T / 2, f"{T:.1f} mm\nGesamtdicke", va="center", fontsize=9, color="#c0392b")
    # Lagenbeschriftung im Radschnitt
    ax = axes[1]
    z = {"Rueckwand 1,0": (0, P.E2_BACK_T), "Rueckzone 3,5": (P.E2_BACK_T, P.E2_PCB_Z0), "Platine 0,8": (P.E2_PCB_Z0, P.E2_PCB_Z1),
         "Display 2,05": (P.E2_DISP_Z0, P.E2_DISP_Z1), "Front 0,8": (P.E2_FRONT_Z0, T)}
    for n, (a, b) in z.items():
        ax.text(-21.0, (a + b) / 2, n, fontsize=7, va="center", ha="left", color="#333333")
    handles = [plt.Line2D([0], [0], color=c, lw=2) for c in list(pc.values()) + list(dc.values())]
    labels = list(pc.keys()) + ["~" + k for k in dc.keys()]
    fig.legend(handles, labels, loc="lower center", ncol=7, fontsize=8)
    fig.suptitle("Endgeraet v2: Schnitte durch die dickste Stelle (ueberall 8,5 mm), Stack-up Variante A", fontsize=11)
    fig.tight_layout(rect=(0, 0.04, 1, 0.97))
    fig.savefig(os.path.join(VOR, f"{NAME}_schnitt.png"))
    plt.close(fig)
    # Zusammenbau 3D
    order = [meshes[k] for k in ("rueckwand", "rahmen", "frontplatte", "klickrad_abdeckung", "power_taste")]
    render(order + list(dm.values()), os.path.join(VOR, f"{NAME}_zusammenbau.png"),
           f"{NAME}: Zusammenbau inkl. Attrappen (Painter-Artefakte moeglich)", views=((35, -60), (-50, -55)), size=6)


if __name__ == "__main__":
    main()
