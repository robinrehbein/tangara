# ---- Masseflächen (Rückseite): innen massiv, unter dem Touch-Ring gerastert (hatched)
def disc(r, n=96):
    return [(r * math.cos(2 * math.pi * i / n), r * math.sin(2 * math.pi * i / n)) for i in range(n)]
def zone(layer, pts, netname, prio=0, hatch=False, keepout=False):
    z = pcbnew.ZONE(board); z.SetLayer(layer)
    if not keepout: z.SetNet(net(netname))
    o = z.Outline(); o.NewOutline()
    for x, y in pts: o.Append(FromMM(OX + x), FromMM(OY - y))
    z.SetAssignedPriority(prio); z.SetMinThickness(FromMM(0.2)); z.SetLocalClearance(FromMM(0.2))
    z.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL)
    if hatch:
        z.SetFillMode(pcbnew.ZONE_FILL_MODE_HATCH_PATTERN)
        z.SetHatchThickness(FromMM(0.3)); z.SetHatchGap(FromMM(0.7)); z.SetHatchOrientation(pcbnew.EDA_ANGLE(45, pcbnew.DEGREES_T))
        z.SetHatchSmoothingLevel(0); z.SetHatchHoleMinArea(0.3)
    if keepout:
        z.SetIsRuleArea(True); z.SetDoNotAllowFootprints(True); z.SetDoNotAllowTracks(False); z.SetDoNotAllowVias(False)
        z.SetDoNotAllowPads(False); z.SetDoNotAllowZoneFills(False)
    board.Add(z); return z
zone(B_CU, disc(15.7), 'GND', 0, hatch=True)
zone(B_CU, disc(6.3), 'GND', 1, hatch=False)
# LRA-Freifläche 6 x 16 mm (nur Bauteile verboten), Markierung auf Rückseite
LRA = (-8.0, 3.0, 8.0, 9.0)
zone(B_CU, [(LRA[0], LRA[1]), (LRA[2], LRA[1]), (LRA[2], LRA[3]), (LRA[0], LRA[3])], '', 0, keepout=True)
rect(pcbnew.B_SilkS, *LRA, w=0.15)
for a, b in (((-8, 3), (8, 9)), ((-8, 9), (8, 3))): line(pcbnew.B_Fab, a, b, 0.1)
text(pcbnew.B_SilkS, 'LRA 6x16 aufkleben', 0, 6.0, 0.9, mirror=True)
text(pcbnew.B_SilkS, 'KLICKRAD v1', 0, -5.2, 1.0, mirror=True)
for i, s in enumerate(('3V3', 'GND', 'SDA', 'SCL', 'INT', 'BTN')):
    text(pcbnew.B_SilkS, s, 2.5 - i, -7.9, 0.6, mirror=True, rot=90)
text(pcbnew.B_SilkS, 'LRA+', -9.6, 10.2, 0.6, mirror=True)
text(pcbnew.B_SilkS, 'LRA-', -9.6, 4.9, 0.6, mirror=True)
# Positionsmarke 0 Grad vorne (Kupferfrei, nur Fab)
text(pcbnew.F_Fab, '0 Grad', 11.5, 0, 0.6)
# ---- Füllen und speichern
pcbnew.ZONE_FILLER(board).Fill(board.Zones())
board.Save(os.path.join(ROOT, 'klickrad.kicad_pcb'))
print('saved')
