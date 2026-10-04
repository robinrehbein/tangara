# wird von build_pcb.py ausgeführt (exec)
PARTS = {p['ref']: p for p in netlist.parts()}
TMP = os.environ.get('TMPDIR_PCB', '/tmp/w')
VIAS = json.load(open(os.path.join(ROOT, 'tools', 'vias_touch.json')))
LRA = (-8.0, 3.0, 8.0, 9.0)           # Freifläche LRA (Rückseite, nur Bauteile gesperrt)
if MODE == 'place':
    # ---- Entwurfsregeln (JLCPCB/PCBWay 2 Lagen, 1,0 mm)
    ds = board.GetDesignSettings()
    ds.m_TrackMinWidth = FromMM(0.127); ds.m_MinClearance = FromMM(0.127)
    ds.m_ViasMinSize = FromMM(0.5); ds.m_MinThroughDrill = FromMM(0.3)
    ds.m_CopperEdgeClearance = FromMM(0.3); ds.m_HoleToHoleMin = FromMM(0.5)
    ds.m_ViasMinAnnulus = FromMM(0.13); ds.m_MinHoleClearance = FromMM(0.25)
    ds.SetBoardThickness(FromMM(1.0))
    nc = ds.m_NetSettings.GetDefaultNetclass()
    nc.SetClearance(FromMM(0.15)); nc.SetTrackWidth(FromMM(0.2)); nc.SetViaDiameter(FromMM(0.6)); nc.SetViaDrill(FromMM(0.3))
    pw = pcbnew.NETCLASS('Power')
    pw.SetClearance(FromMM(0.15)); pw.SetTrackWidth(FromMM(0.3)); pw.SetViaDiameter(FromMM(0.6)); pw.SetViaDrill(FromMM(0.3))
    ds.m_NetSettings.SetNetclass('Power', pw)
    for n in ('3V3', 'GND', 'LRA_P', 'LRA_N'): ds.m_NetSettings.SetNetclassPatternAssignment(n, 'Power')

    # ---- Umriss und Löcher
    circle(pcbnew.Edge_Cuts, (0, 0), 16.0, 0.1)
    for i, a in enumerate((90, 210, 330)):
        fp = loadfp('Klickrad:MountingHole_2.2mm_NPTH'); fp.SetReference(f'H{i+1}'); board.Add(fp)
        fp.SetPosition(V(14.6 * math.cos(math.radians(a)), 14.6 * math.sin(math.radians(a))))
        fp.SetAttributes(fp.GetAttributes() | pcbnew.FP_BOARD_ONLY)
        fp.Reference().SetVisible(False); fp.Value().SetVisible(False)

    # ---- Touch-Flächen vorn (Footprints liegen in Platinenkoordinaten) und ihre Durchkontaktierungen
    for ref in ('SW1', 'SW2', 'SW3'): place(PARTS[ref], 0, 0, 'F', 0)
    for key, net_ in (('W0', 'E0'), ('W1', 'E1'), ('W2', 'E2'), ('B0', 'EB'), ('G0', 'EG'), ('G1', 'EG'), ('G2', 'EG')):
        via(net_, *VIAS[key])

    # ---- Bauteile (Rückseite, Koordinaten Frontansicht)
    exec(open(os.path.join(ROOT, 'tools', 'placement.py')).read())
    for ref, (x, y, r) in POS.items():
        place(PARTS[ref], x, y, 'B', r)
    for fp in board.GetFootprints(): fp.Value().SetVisible(False); fp.Reference().SetVisible(False)

    # ---- Zonen: GND als Gitter (Tangara-Werte) auf B.Cu, LRA-Freifläche als Bauteil-Sperrzone, Randzone ohne Leiterbahnen
    z = zone(B_CU, disc(15.7), 'GND', 0, hatch=True)
    z.SetMinThickness(FromMM(0.127)); z.SetLocalClearance(FromMM(0.2))
    z.SetHatchThickness(FromMM(0.127)); z.SetHatchGap(FromMM(1.016)); z.SetHatchSmoothingLevel(2); z.SetHatchSmoothingValue(0.1)
    zone(B_CU, [(LRA[0], LRA[1]), (LRA[2], LRA[1]), (LRA[2], LRA[3]), (LRA[0], LRA[3])], '', 0, keepout=True)
    kz = zone(F_CU, disc(17.0), '', 0, keepout=True, hole=disc(15.5), layers=[F_CU, B_CU])
    kz.SetDoNotAllowFootprints(False); kz.SetDoNotAllowTracks(True); kz.SetDoNotAllowVias(True)
    # Vorderseite: keine Leiterbahnen oder Vias des Routers außerhalb des Innenkreises r < 6 (Rad und Guard bleiben frei von fremdem Kupfer)
    fz = zone(F_CU, disc(15.5), '', 0, keepout=True, hole=disc(6.0), layers=[F_CU])
    fz.SetDoNotAllowFootprints(False); fz.SetDoNotAllowTracks(True); fz.SetDoNotAllowVias(True)
    board.Save(os.path.join(TMP, 'pre.kicad_pcb'))
else:
    if not os.environ.get('NOSES'): pcbnew.ImportSpecctraSES(board, os.path.join(TMP, 'k.ses'))
    exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'finish.py')).read())
