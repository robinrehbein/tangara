# wird von build_pcb.py ausgeführt (exec)
PARTS = {p['ref']: p for p in netlist.parts()}
TMP = os.environ.get('TMPDIR_PCB', '/tmp/w')
VIAS = json.load(open(os.path.join(ROOT, 'tools', 'vias_touch.json')))
LRA = (-7.0, 3.0, 7.0, 9.0)      # Freifläche LRA 14 x 6 (Rückseite, nur Bauteile gesperrt); passt in den Ausschnitt 14 x 10 der Hauptplatine (Mitte y = -19 dort = +6 hier)
if MODE == 'place':
    # ---- Entwurfsregeln (JLCPCB/PCBWay 2 Lagen, 1,0 mm)
    ds = board.GetDesignSettings()
    ds.m_TrackMinWidth = FromMM(0.127); ds.m_MinClearance = FromMM(0.127)
    ds.m_ViasMinSize = FromMM(0.5); ds.m_MinThroughDrill = FromMM(0.3)
    ds.m_CopperEdgeClearance = FromMM(0.3); ds.m_HoleToHoleMin = FromMM(0.5)
    ds.m_ViasMinAnnulus = FromMM(0.13); ds.m_MinHoleClearance = FromMM(0.25)
    ds.SetBoardThickness(FromMM(0.8))
    nc = ds.m_NetSettings.GetDefaultNetclass()
    nc.SetClearance(FromMM(0.127)); nc.SetTrackWidth(FromMM(0.2)); nc.SetViaDiameter(FromMM(0.6)); nc.SetViaDrill(FromMM(0.3))
    pw = pcbnew.NETCLASS('Power')
    pw.SetClearance(FromMM(0.127)); pw.SetTrackWidth(FromMM(0.3)); pw.SetViaDiameter(FromMM(0.6)); pw.SetViaDrill(FromMM(0.3))
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
    for key, net_ in (('W0', 'E0'), ('W1', 'E1'), ('W2', 'E2'), ('B0', 'EB'), ('G0', 'EG')):
        via(net_, *VIAS[key])

    # ---- Bauteile (Rückseite, Koordinaten Frontansicht)
    exec(open(os.path.join(ROOT, 'tools', 'placement.py')).read())
    for ref, (x, y, r) in POS.items():
        place(PARTS[ref], x, y, 'B', r)
    # Paare, deren 3V3-Pads sich berühren (spart Leiterbahnen: gleiches Netz, Pads überlappen um 0,3 mm): (A, B) -> B wird um 180 Grad gedreht an A angesetzt
    for a_, b_, lb_ in (('C1', 'C2', 0.48), ('R8', 'R9', 0.48)):
        fa, fb = placed[a_], placed[b_]
        pa = [p for p in fa.Pads() if p.GetNetname() == '3V3'][0]
        ca, pp = fa.GetPosition(), pa.GetPosition()
        dx, dy = ToMM(pp.x - ca.x), ToMM(pp.y - ca.y); L = math.hypot(dx, dy); ux, uy = dx / L, dy / L
        fb.SetOrientationDegrees(fa.GetOrientationDegrees() + 180)
        s_ = L + lb_ + 0.3
        fb.SetPosition(VECTOR2I(ca.x + FromMM(ux * (0 + s_)) , ca.y + FromMM(uy * s_)))
    for fp in board.GetFootprints(): fp.Value().SetVisible(False); fp.Reference().SetVisible(False)
    for net_, lay, pts_, w_ in PRE_TRACKS: track(net_, B_CU if lay == 'B' else F_CU, pts_, w_)
    for net_, x_, y_ in PRE_VIAS: via(net_, x_, y_)

    # ---- Zonen: GND als Gitter (Tangara-Werte) auf B.Cu, LRA-Freifläche als Bauteil-Sperrzone, Randzone ohne Leiterbahnen
    zone(B_CU, [(LRA[0], LRA[1]), (LRA[2], LRA[1]), (LRA[2], LRA[3]), (LRA[0], LRA[3])], '', 0, keepout=True)
    # (Rand- und Vorderseiten-Sperrzonen entfallen: Specctra kennt keine Löcher in Sperrflächen; Prüfung per DRC und tools/pruefe_vorderseite.py)
    board.Save(os.path.join(TMP, 'pre.kicad_pcb'))
else:
    exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'finish.py')).read())
