# ---- Router-Reste entfernen: doppelte Leiterbahnen und Stichleitungen mit losem Ende
_all = list(board.GetTracks())
_tr = [t for t in _all if t.Type() == pcbnew.PCB_TRACE_T]
_vias = [t.GetPosition() for t in _all if t.Type() == pcbnew.PCB_VIA_T]
_pads = [p for fp in board.GetFootprints() for p in fp.Pads()]
_rm = []
_seen = set()
for t in list(_tr):
    k = (t.GetLayer(), frozenset(((t.GetStart().x, t.GetStart().y), (t.GetEnd().x, t.GetEnd().y))))
    if k in _seen: _tr.remove(t); _rm.append(t)
    else: _seen.add(k)
def _touched(t, pt):
    for o in _tr:
        if o is not t and o.GetLayer() == t.GetLayer() and (o.GetStart() == pt or o.GetEnd() == pt): return True
    if any(v == pt for v in _vias): return True
    return any(p.HitTest(pt) and p.IsOnLayer(t.GetLayer()) for p in _pads)
_ch = True
while _ch:
    _ch = False
    for t in list(_tr):
        if not (_touched(t, t.GetStart()) and _touched(t, t.GetEnd())):
            _tr.remove(t); _rm.append(t); _ch = True; break
for t in _rm: board.Remove(t)
print('Router-Reste entfernt:', len(_rm))
# ---- Beschriftung (Rückseite gespiegelt), LRA-Markierung
LRA = (-8.0, 3.0, 8.0, 9.0)
rect(pcbnew.B_SilkS, *LRA, w=0.15)
for a, b in (((-8, 3), (8, 9)), ((-8, 9), (8, 3))): line(pcbnew.B_Fab, a, b, 0.1)
text(pcbnew.B_SilkS, 'LRA 6x16 aufkleben', 0, 6.0, 1.0, mirror=True)
text(pcbnew.B_SilkS, 'KLICKRAD v1', 0, -5.6, 1.0, mirror=True)
for i, s in enumerate(('3V3', 'GND', 'SDA', 'SCL', 'INT', 'BTN')):
    text(pcbnew.B_SilkS, s, 2.5 - i, -7.6, 0.9, mirror=True, rot=90)
text(pcbnew.B_SilkS, 'LRA+', -12.3, -4.4, 0.8, mirror=True)
text(pcbnew.B_SilkS, 'LRA-', -12.3, 1.1, 0.8, mirror=True)
text(pcbnew.F_Fab, '0 Grad', 11.5, 0, 0.8)
# Referenzen auf Fab-Lagen (keine Silk-Überlappung), Werte ausblenden
for fp in board.GetFootprints():
    back = fp.GetLayer() == B_CU
    fp.Reference().SetLayer(pcbnew.B_Fab if back else pcbnew.F_Fab); fp.Reference().SetTextSize(pcbnew.VECTOR2I(FromMM(0.8), FromMM(0.8)))
    fp.Value().SetVisible(False)
board.GetDesignSettings().SetAuxOrigin(V(0, 0))   # Platinenmitte als Bezug für Positionsdatei
pcbnew.ZONE_FILLER(board).Fill(board.Zones())
board.Save(os.path.join(ROOT, 'klickrad.kicad_pcb'))
print('saved')
