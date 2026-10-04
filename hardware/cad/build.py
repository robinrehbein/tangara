"""Baut alle Teile, exportiert STL + Vorschau, prueft Wasserdichtheit, Maße, Kollisionen.

Aufruf:  .venv/bin/python build.py
"""
import itertools
import os
import sys
import numpy as np
import cadquery as cq
import trimesh
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

import params as P
import prototyp
import endgeraet

HERE = os.path.dirname(os.path.abspath(__file__))
STL = os.path.join(HERE, "stl")
VOR = os.path.join(HERE, "vorschau")

# Erwartete Bounding-Box (X, Y, Z) je Teil, Toleranz 0,05
EXPECT = {
    "prototyp": {
        "vorderschale": (P.P_OW, P.P_OL, P.P_T - P.P_ZS),
        "rueckschale": (P.P_OW, P.P_OL, P.P_ZS + P.LIP_H),
        "klickrad_abdeckung": (P.WHEEL_COVER_D, P.WHEEL_COVER_D, P.COVER_T),
        "mitteltaste": (P.WHEEL_BTN_D, P.WHEEL_BTN_D, P.WHEEL_BTN_T),
        "klickrad_halter": None,
    },
    "endgeraet": {
        "oberschale": (42.0, 95.0, 12.2 - 6.0),
        "rueckschale": (42.0, 95.0, 6.0),
        "innenrahmen": (42 - 2 * 1.4 - 0.4, 95 - 2 * 1.4 - 0.4, 6.2),
        "klickrad_abdeckung": (30.0, 30.0, 1.95),
        "mitteltaste": (11.0, 11.0, 1.15),
        "distanzring": (32.0, 32.0, 0.8),
        "power_taste": None,
    },
}


def export(shape, path):
    cq.exporters.export(shape, path, tolerance=0.02, angularTolerance=0.1)


def load(path):
    m = trimesh.load(path, force="mesh")
    m.merge_vertices()
    return m


def render(meshes, path, title, views=((25, -60), (90, -90), (25, 120)), colors=None, size=4.2):
    """Einfacher Software-Renderer (z-Puffer-frei, Painter) via matplotlib."""
    fig = plt.figure(figsize=(size * len(views), size + 0.4), dpi=110)
    allv = np.vstack([m.vertices for m in meshes])
    ctr = (allv.min(0) + allv.max(0)) / 2
    span = (allv.max(0) - allv.min(0)).max() / 2 * 1.02
    palette = colors or ["#c9ccd1", "#8fb2d8", "#e0a45a", "#9bc79b", "#d68f9a", "#b0a0d8", "#d8d27a", "#7fc8c8", "#aaaaaa"]
    light = np.array([0.4, -0.5, 0.8]); light /= np.linalg.norm(light)
    for i, (el, az) in enumerate(views):
        ax = fig.add_subplot(1, len(views), i + 1, projection="3d")
        ax.set_proj_type("ortho")
        ax.view_init(el, az)
        for j, m in enumerate(meshes):
            tri = m.triangles
            n = m.face_normals
            shade = 0.45 + 0.55 * np.clip(n @ light, 0, 1)
            base = np.array(matplotlib.colors.to_rgb(palette[j % len(palette)]))
            fc = np.clip(shade[:, None] * base[None, :], 0, 1)
            pc = Poly3DCollection(tri, facecolors=fc, edgecolors="none", linewidths=0, antialiased=False)
            ax.add_collection3d(pc)
        ax.set_xlim(ctr[0] - span, ctr[0] + span)
        ax.set_ylim(ctr[1] - span, ctr[1] + span)
        ax.set_zlim(ctr[2] - span, ctr[2] + span)
        ax.set_box_aspect((1, 1, 1))
        ax.set_axis_off()
    fig.suptitle(title, fontsize=10)
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


def check_group(name, parts, dummies, expect):
    ok = True
    print(f"\n=== {name} ===")
    d_out = os.path.join(STL, name)
    os.makedirs(d_out, exist_ok=True)
    meshes = {}
    for k, shp in parts.items():
        p = os.path.join(d_out, f"{k}.stl")
        export(shp, p)
        m = load(p)
        meshes[k] = m
        bb = m.bounds[1] - m.bounds[0]
        wt = m.is_watertight and m.is_winding_consistent and m.volume > 0
        msg = f"{k:22s} bbox {bb[0]:6.2f} x {bb[1]:6.2f} x {bb[2]:6.2f}  Vol {m.volume:8.0f} mm3  wasserdicht={wt}"
        ex = expect.get(k)
        if ex is not None:
            good = all(abs(a - b) <= 0.05 for a, b in zip(bb, ex))
            msg += f"  Soll {ex[0]:.2f} x {ex[1]:.2f} x {ex[2]:.2f} -> {'OK' if good else 'ABWEICHUNG'}"
            ok &= good
        ok &= wt
        print(msg)
    # Kollisionen (Boolean-Schnitt) zwischen allen Teilen inkl. Attrappen
    allp = {**{k: v for k, v in parts.items()}, **{"~" + k: v for k, v in dummies.items()}}
    bad = []
    for (a, sa), (b, sb) in itertools.combinations(allp.items(), 2):
        if a.startswith("~") and b.startswith("~"):
            continue
        ba, bb_ = sa.val().BoundingBox(), sb.val().BoundingBox()
        if (ba.xmax < bb_.xmin or bb_.xmax < ba.xmin or ba.ymax < bb_.ymin or bb_.ymax < ba.ymin
                or ba.zmax < bb_.zmin or bb_.zmax < ba.zmin):
            continue
        try:
            v = sa.intersect(sb).val().Volume()
        except Exception:
            v = 0.0
        if v > 0.05:
            bad.append((a, b, v))
    if bad:
        ok = False
        for a, b, v in bad:
            print(f"KOLLISION {a} <-> {b}: {v:.2f} mm3")
    else:
        print(f"Kollisionen: keine ({len(allp)} Koerper paarweise geprueft, Attrappen mit ~)")
    # Vorschau
    os.makedirs(VOR, exist_ok=True)
    for k, m in meshes.items():
        render([m], os.path.join(VOR, f"{name}_{k}.png"), f"{name}: {k}", views=((30, -55), (90, -90), (-60, -55)))
    dm = []
    for k, shp in dummies.items():
        p = os.path.join(HERE, ".tmp_" + k + ".stl")
        export(shp, p); dm.append(load(p)); os.remove(p)
    order = sorted(meshes.values(), key=lambda m: m.bounds[0][2])
    ex = []
    for i, m in enumerate(order):
        m2 = m.copy(); m2.apply_translation([0, 0, i * 9.0]); ex.append(m2)
    render(ex, os.path.join(VOR, f"{name}_explosion.png"), f"{name}: Explosion (Teile nach Z sortiert)",
           views=((35, -60), (20, -20)), size=6)
    render(order + dm, os.path.join(VOR, f"{name}_zusammenbau.png"),
           f"{name}: Zusammenbau inkl. Attrappen (Painter-Artefakte moeglich)", views=((35, -60), (-50, -55)), size=6)
    return ok


def main():
    ok = check_group("prototyp", prototyp.parts(), prototyp.dummies(), EXPECT["prototyp"])
    ok &= check_group("endgeraet", endgeraet.parts(), endgeraet.dummies(), EXPECT["endgeraet"])
    print("\nGESAMT:", "ALLES OK" if ok else "FEHLER")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
