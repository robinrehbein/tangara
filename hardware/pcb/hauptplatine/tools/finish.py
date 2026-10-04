# Wird von build_pcb.py (MODE=finish) mit exec ausgefuehrt: Nachbearbeitung nach dem Routing.
# Zonen, DNP-Markierung, Beschriftung, Passermarken, Fuellung, Speichern nach ../hauptplatine.kicad_pcb
from shapely.geometry import box as sbox, Point as SPoint, LineString
from shapely.ops import unary_union

pl_parts = {p['ref']: p for p in netlist.parts()}
fps = {f.GetReference(): f for f in board.GetFootprints()}

# ---------------------------------------------------------------- Bauteilmarkierungen / Beschriftung
for ref, f in fps.items():
    p = pl_parts.get(ref)
    if p is None: continue
    if p.get('dnp'): f.SetDNP(True)
    f.SetExcludedFromBOM(bool(p.get('nobom')))
    if p.get('nobom') or ref.startswith('H'): f.SetExcludedFromPosFiles(True)
    f.Value().SetVisible(False)
    r = f.Reference()
    r.SetTextSize(VECTOR2I(FromMM(0.6), FromMM(0.6))); r.SetTextThickness(FromMM(0.1))
    if p['kind'] in ('R', 'C', 'TP', 'H') or p.get('pkg') in ('0402',):
        r.SetVisible(False)
        r.SetVisible(False)
    for fld in (f.Reference(), f.Value()):
        fld.SetTextSize(VECTOR2I(FromMM(0.8), FromMM(0.8))); fld.SetTextThickness(FromMM(0.15))
        fld.SetMirrored(f.GetLayer() == pcbnew.B_Cu)
    for g in f.GraphicalItems():
        if g.GetClass() in ('PCB_TEXT', 'FP_TEXT'):
            if g.GetLayer() in (pcbnew.F_SilkS, pcbnew.B_SilkS):
                g.SetTextSize(VECTOR2I(FromMM(0.8), FromMM(0.8))); g.SetTextThickness(FromMM(0.15))
                g.SetMirrored(g.GetLayer() == pcbnew.B_SilkS)
    for fld in f.GetFields(): fld.SetVisible(False)
    # Eigenschaften fuer Stueckliste/Nachvollziehbarkeit
    for k, nm in (('mpn', 'MPN'), ('mfr', 'Manufacturer'), ('src', 'Herkunft')):
        if p.get(k):
            try: f.SetField(nm, str(p[k])); f.GetFieldByName(nm).SetVisible(False)
            except Exception: pass

# ---------------------------------------------------------------- freie Flaechen ermitteln
def occupied(side):
    """Belegung (shapely) einer Kupferseite: Pads, Leiterbahnen, Vias, Kontur-Umgebung."""
    lay = F_CU if side == 'T' else B_CU
    geoms = []
    for f in board.GetFootprints():
        for pad in f.Pads():
            if not pad.IsOnLayer(lay): continue
            bb = pad.GetBoundingBox()
            geoms.append(sbox(ToMM(bb.GetLeft()) - OX, OY - ToMM(bb.GetBottom()), ToMM(bb.GetRight()) - OX, OY - ToMM(bb.GetTop())))
    for t in board.GetTracks():
        if t.Type() == pcbnew.PCB_VIA_T:
            c = P(t.GetPosition()); geoms.append(SPoint(*c).buffer(ToMM(t.GetWidth()) / 2))
        elif t.GetLayer() == lay:
            a, b = P(t.GetStart()), P(t.GetEnd()); geoms.append(LineString([a, b]).buffer(ToMM(t.GetWidth()) / 2))
    return unary_union(geoms)

def board_inner(margin):
    return layout.board_poly().difference(layout.cutout_poly()).buffer(-margin)

def silk_sides():
    return {'T': occupied('T'), 'B': occupied('B')}

occ = silk_sides()
_keep = []
for _f in board.GetFootprints():
    bb = _f.GetBoundingBox(False)
    _keep.append(sbox(ToMM(bb.GetLeft()) - OX, OY - ToMM(bb.GetBottom()), ToMM(bb.GetRight()) - OX, OY - ToMM(bb.GetTop())).buffer(0.6))
    for _z in _f.Zones():
        _o = _z.Outline(); _ch = _o.Outline(0)
        from shapely.geometry import Polygon as _Pg
        _keep.append(_Pg([P(_ch.CPoint(k)) for k in range(_ch.PointCount())]).buffer(0.5))
KEEP_ALL = unary_union(_keep)
occ = {s: unary_union([occ[s], KEEP_ALL]) for s in occ}
# Rahmen-/Holes-Bereiche, in denen Silkscreen/Fiducials nicht liegen duerfen
holes_poly = unary_union([SPoint(x, y).buffer(2.5) for x, y in HOLES])

def free_spot(side, w, h, cands, gap=0.6):
    inner = board_inner(1.2)
    for (cx, cy) in cands:
        r = sbox(cx - w / 2 - gap, cy - h / 2 - gap, cx + w / 2 + gap, cy + h / 2 + gap)
        if inner.contains(r) and not r.intersects(occ[side]) and not r.intersects(holes_poly):
            # nicht ueber THT/Bauteilen der Gegenseite, die durchkommen -> Pads der Gegenseite sind in occ der anderen Seite; hier nur Kupfer dieser Seite
            return (cx, cy)
    return None

# Passermarken (Fiducials): je 3 pro Seite wenn Platz (PCBWay-Bestueckung braucht min. 2 pro Seite, Raster ausserhalb Bauteilen)
fid_count = {'T': 0, 'B': 0}
cand = sorted([(x, y) for y in range(-40, 41, 3) for x in (-16, -12, -8, -4, 0, 4, 8, 12, 16)], key=lambda p: -(abs(p[0]) / 18.5 + abs(p[1]) / 42))
FID_FP = 'Fiducial:Fiducial_1mm_Mask2mm'
fid_n = 0
for side in ('T', 'B'):
    placed_f = []
    for (cx, cy) in cand:
        if len(placed_f) >= 3: break
        if any(math.dist((cx, cy), q) < 25 for q in placed_f): continue
        spot = free_spot(side, 2.0, 2.0, [(cx, cy)], gap=1.0)
        if not spot: continue
        fp = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Fiducial.pretty', 'Fiducial_1mm_Mask2mm')
        fp.SetFPID(pcbnew.LIB_ID('Fiducial', 'Fiducial_1mm_Mask2mm'))
        fid_n += 1
        fp.SetReference('FID%d' % fid_n); fp.SetValue('Fiducial')
        board.Add(fp)
        if side == 'B': fp.Flip(V(0, 0), pcbnew.FLIP_DIRECTION_LEFT_RIGHT)
        fp.SetPosition(V(*spot))
        fp.SetExcludedFromBOM(True); fp.SetExcludedFromPosFiles(True); fp.SetBoardOnly(True)
        fp.Reference().SetVisible(False); fp.Value().SetVisible(False)
        placed_f.append(spot)
    fid_count[side] = len(placed_f)
print('Fiducials', fid_count)

# Beschriftung auf Silkscreen (nur wenn Platz)
lines = ['Hauptplatine Rev.3', 'CERN-OHL-S-2.0', 'nach Tangara (cooltech.zone)']
for side in ('B', 'T'):
    spot = free_spot(side, 17.0, 3.2, [(x, y) for y in (-45.0, 43.0, -42.0, 38.0, 14.0, 30.0, 36.0) for x in (0.0, -6.0, 6.0)], gap=0.3)
    if not spot: print('Beschriftung', side, 'kein Platz'); continue
    layer = pcbnew.F_SilkS if side == 'T' else pcbnew.B_SilkS
    for i, s in enumerate(lines):
        text(layer, s, spot[0], spot[1] + 1.0 - i * 1.0, 0.8, mirror=(side == 'B'))
    break

# ---------------------------------------------------------------- Kupferflaechen
pts = board_pts(0.3)
# Aussenlagen ohne GND-Flaeche (Router verbindet GND per Via mit In1; Flaechen ergaeben unverbundene Inseln um die Pads)
# Innenlage 2 (Signal/3V3-Reserve): GND-Auffuellung ohne Prioritaet, hilft der Rueckleitung
zone(IN2, pts, 'GND', prio=0, clearance=0.2, thermal=False)
filler = pcbnew.ZONE_FILLER(board)
filler.Fill(board.Zones())

# Zeichnungsurspruenge / Plot
board.GetDesignSettings().SetAuxOrigin(V(0, 0))
board.GetDesignSettings().SetGridOrigin(V(0, 0))
out = os.path.join(ROOT, 'hauptplatine.kicad_pcb')
pcbnew.SaveBoard(out, board)
print('gespeichert', out)
