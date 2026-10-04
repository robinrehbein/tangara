# ---- GND-Ring auf F.Cu zwischen Taste und Rad (Zone; Router-Vias und F.Cu-Brücken anderer Netze werden ausgespart)
_zr = zone(F_CU, disc(5.5), 'GND', 0, hole=disc(2.8))
_zr.SetMinThickness(FromMM(0.2)); _zr.SetLocalClearance(FromMM(0.25))
# ---- GND-Gitter auf B.Cu (Tangara: Linie 0,127 mm, Lücke 1,016 mm, 45 Grad, Glättung 2) wird erst nach dem Routing angelegt.
# Jedes GND-Pad hat einen kurzen Leiterbahn-Stummel (route.py), der das Gitter kreuzt und es so anbindet.
_z = zone(B_CU, disc(15.7), 'GND', 0, hatch=True)
_z.SetMinThickness(FromMM(0.127)); _z.SetLocalClearance(FromMM(0.2))
_z.SetHatchThickness(FromMM(0.127)); _z.SetHatchGap(FromMM(1.016)); _z.SetHatchSmoothingLevel(2); _z.SetHatchSmoothingValue(0.1)
# ---- Beschriftung (Rückseite gespiegelt), LRA-Markierung
rect(pcbnew.B_SilkS, *LRA, w=0.15)

text(pcbnew.B_SilkS, 'LRA bis 3 mm hoch: 12x6 / 16x6', 0, 6.0, 0.8, mirror=True)
text(pcbnew.B_SilkS, 'KLICKRAD v2', 0, 12.6, 1.0, mirror=True)
text(pcbnew.B_SilkS, 'OBEN', 0, 14.0, 0.8, mirror=True)
text(pcbnew.B_SilkS, 'QT2120 0x1C  DRV 0x5A', 0, -13.0, 0.8, mirror=True)
for i, s in enumerate(('3V3', 'GND', 'SDA', 'SCL', 'CHG', '(6)')):
    text(pcbnew.B_SilkS, s, 1.25 - 0.5 * i, -5.6 if i % 2 == 0 else -7.0, 0.8, mirror=True, rot=90)
text(pcbnew.B_SilkS, 'LRA+', 13.1, -0.4, 0.8, mirror=True)
text(pcbnew.B_SilkS, 'LRA-', 12.0, -7.8, 0.8, mirror=True)
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
