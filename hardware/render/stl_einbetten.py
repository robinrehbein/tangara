"""Bettet die v3-STL (hardware/cad/stl/endgeraet_v3/) als Base64 in explosionsmodell.html ein.

Aufruf (mit dem CAD-venv, braucht trimesh):  hardware/cad/.venv/bin/python hardware/render/stl_einbetten.py
Ersetzt den Block zwischen "// STL-DATEN-BEGIN" und "// STL-DATEN-ENDE". Vertices auf 0,01 mm gerundet
(int16, x/y/z in 1/100 mm), Dreiecke als uint16-Indizes.
"""
import base64, pathlib, re
import numpy as np
import trimesh

ROOT = pathlib.Path(__file__).resolve().parent
STL = ROOT.parent / "cad" / "stl" / "endgeraet_v3"
NAMES = ["rahmen", "rueckwand", "frontplatte", "klickrad_abdeckung"]

out = ["// STL-DATEN-BEGIN (erzeugt von stl_einbetten.py, nicht von Hand ändern)", "const STL_DATA = {"]
for n in NAMES:
    m = trimesh.load(STL / f"{n}.stl")
    v = np.round(m.vertices * 100).astype("<i2")
    # nach dem Runden doppelte Eckpunkte zusammenfassen
    uniq, inv = np.unique(v, axis=0, return_inverse=True)
    f = inv.reshape(-1)[m.faces].astype("<u2")
    ok = (f[:, 0] != f[:, 1]) & (f[:, 1] != f[:, 2]) & (f[:, 0] != f[:, 2])
    f = f[ok]
    b = lambda a: base64.b64encode(a.tobytes()).decode()
    out.append(f'  {n}: {{ v: "{b(uniq.astype("<i2"))}", f: "{b(f)}" }},')
    print(n, len(uniq), "Vertices", len(f), "Dreiecke", m.bounds.round(2).tolist())
out += ["};", "// STL-DATEN-ENDE"]
block = "\n".join(out)

p = ROOT / "explosionsmodell.html"
t = p.read_text(encoding="utf-8")
t2 = re.sub(r"// STL-DATEN-BEGIN.*?// STL-DATEN-ENDE", lambda _: block, t, flags=re.S)
assert t2 != t or block in t, "Marker nicht gefunden"
p.write_text(t2, encoding="utf-8")
