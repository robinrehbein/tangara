# wird von build_pcb.py ausgeführt (exec)
PARTS = {p['ref']: p for p in netlist.parts()}
TMP = os.environ.get('TMPDIR_PCB', '/tmp/w')
if MODE == 'place':
    # ---- Entwurfsregeln (JLCPCB 4 Lagen, 1,0 mm)
    ds = board.GetDesignSettings()
    ds.m_TrackMinWidth = FromMM(0.127); ds.m_MinClearance = FromMM(0.127)
    ds.m_ViasMinSize = FromMM(0.5); ds.m_MinThroughDrill = FromMM(0.3)
    ds.m_CopperEdgeClearance = FromMM(0.3); ds.m_HoleToHoleMin = FromMM(0.5)
    ds.m_ViasMinAnnulus = FromMM(0.13); ds.m_MinHoleClearance = FromMM(0.25)
    ds.SetBoardThickness(FromMM(1.0))
    nc = ds.m_NetSettings.GetDefaultNetclass()
    nc.SetClearance(FromMM(0.15)); nc.SetTrackWidth(FromMM(0.2)); nc.SetViaDiameter(FromMM(0.6)); nc.SetViaDrill(FromMM(0.3))

    # ---- Umriss und Löcher
    circle(pcbnew.Edge_Cuts, (0, 0), 16.0, 0.1)
    for i, a in enumerate((90, 210, 330)):
        fp = loadfp('Klickrad:MountingHole_2.2mm_NPTH'); fp.SetReference(f'H{i+1}'); board.Add(fp)
        fp.SetPosition(V(14.6 * math.cos(math.radians(a)), 14.6 * math.sin(math.radians(a))))
        fp.SetAttributes(fp.GetAttributes() | pcbnew.FP_BOARD_ONLY)
        fp.Reference().SetVisible(False); fp.Value().SetVisible(False)

    # ---- Segmente (Vorderseite), Anschluss über F.Cu von innen
    for k in range(12):
        a = math.radians(make_lib.seg_angle(k))
        place(PARTS[f'SEG{k+1}'], make_lib.VIA_R * math.cos(a), make_lib.VIA_R * math.sin(a), 'F', 0)

    # ---- Bauteile (Rückseite, Koordinaten Frontansicht)
    POS = {
     'U1': (0, 0, 270), 'U2': (-8.1, -8.5, 0), 'J1': (0, -11.4, 0), 'SW1': (0, 0, 0),
     'C1': (3.0, -1.8, 0), 'C2': (-2.0, -3.2, 90), 'C3': (3.0, -3.2, 0), 'R1': (-3.25, -0.75, 0),
     'C4': (-10.2, -6.3, 90), 'C6': (-10.0, -3.9, 90), 'C5': (-7.2, -6.6, 0),
     'R2': (1.5, -7.0, 0), 'R3': (1.2, -4.6, 0),
     'TP1': (-12.3, -3.0, 90), 'TP2': (-12.3, -0.4, 90),
    }
    for ref, (x, y, r) in POS.items():
        place(PARTS[ref], x, y, 'F' if ref == 'SW1' else 'B', r)
    def orient(ref, netname, key, want_high):
        """Zweipoler so drehen, dass das Pad mit `netname` bei key() den größeren (want_high) bzw. kleineren Wert hat."""
        fp = placed[ref]; part = PARTS[ref]
        a = [p for p in fp.Pads() if part['pins'][p.GetNumber()] == netname][0]
        b = [p for p in fp.Pads() if part['pins'][p.GetNumber()] != netname][0]
        if (key(P(a.GetPosition())) > key(P(b.GetPosition()))) != want_high: fp.SetOrientationDegrees(fp.GetOrientationDegrees() + 180)
    X, Y = (lambda p: p[0]), (lambda p: p[1])
    orient('C2', 'VREG', Y, True); orient('R1', 'REXT', X, True)
    orient('R2', 'SDA', X, False); orient('R3', 'SCL', X, False)

    # ---- Fanout der Elektrodenpins: Stummel senkrecht aus dem Pad, dann radial zum Via (R = 3,7 / 4,5 mm)
    for n in range(12):
        px, py = pad('U1', 8 + n); d = math.hypot(px, py); ux, uy = px / d, py / d
        Rv = 4.5 if n <= 2 else 3.7
        vx, vy = Rv * ux, Rv * uy
        if abs(px) > abs(py): kx, ky = (1 if px > 0 else -1), 0
        else: kx, ky = 0, (1 if py > 0 else -1)
        track(f'ELE{n}', B_CU, [(px, py), (px + kx * 0.75, py + ky * 0.75), (vx, vy)], 0.15); via(f'ELE{n}', vx, vy)

    # ---- Bus von Hand: Reihenfolge am Chip (INT, SCL, SDA) ist am Stecker (SDA, SCL, INT) umgekehrt
    # -> INT und SDA wechseln kurz auf F.Cu (innerhalb r < 6 mm, dort liegt nur Leiterbahn)
    jI, jC, jD, jB = pad('J1', 5), pad('J1', 4), pad('J1', 3), pad('J1', 6)
    pI, pC, pD, pA, p5 = pad('U1', 1), pad('U1', 2), pad('U1', 3), pad('U1', 4), pad('U1', 5)
    xt = pC[0] + (jC[0] - pC[0]) * (-3.0 - (-4.6)) / (-3.0 - (-8.0))
    track('SCL', B_CU, [pC, (pC[0], -3.0), (xt, -4.6), (jC[0], -8.0), jC])
    track('SDA', B_CU, [pD, (pD[0], -3.0), (-0.7, -3.7), (-0.7, -5.0)]); via('SDA', -0.7, -5.0)
    track('SDA', F_CU, [(-0.7, -5.0), (0.9, -5.7)]); via('SDA', 0.9, -5.7)
    xs = 0.9 + (jD[0] - 0.9) * (-7.0 - (-6.5)) / (-8.0 - (-6.5))
    track('SDA', B_CU, [(0.9, -5.7), (0.9, -6.5), (xs, -7.0), (jD[0], -8.0), jD])
    track('INT', B_CU, [pI, (pI[0], -2.0), (1.1, -3.3)]); via('INT', 1.1, -3.3)
    track('INT', F_CU, [(1.1, -3.3), (-1.3, -4.4)]); via('INT', -1.3, -4.4)
    track('INT', B_CU, [(-1.3, -4.4), (-1.3, -8.0), jI])
    # ADDR -> 3V3 (Ebene In2): Stummel + Via
    track('3V3', B_CU, [pA, (pA[0], -1.9), (-1.0, -2.5)]); via('3V3', -1.0, -2.5)
    # VREG -> C2, REXT -> R1
    c2n = [p for p in placed['C2'].Pads() if p.GetNetname() == 'VREG'][0]
    r1r = [p for p in placed['R1'].Pads() if p.GetNetname() == 'REXT'][0]
    track('VREG', B_CU, [p5, (p5[0], -1.7), (P(c2n.GetPosition())[0], -1.7), P(c2n.GetPosition())])
    track('REXT', B_CU, [pad('U1', 7), (P(r1r.GetPosition())[0], pad('U1', 7)[1]), P(r1r.GetPosition())])
    # Stichleitungen unter dem Stecker zum DRV2605L und zu den Pull-ups (DNP)
    s2, s3 = pad('U2', 2), pad('U2', 3)
    r3s = [p for p in placed['R3'].Pads() if p.GetNetname() == 'SCL'][0]; r2s = [p for p in placed['R2'].Pads() if p.GetNetname() == 'SDA'][0]
    track('SCL', B_CU, [jC, (jC[0], -10.9), (-3.5, -10.9), (-3.5, s2[1]), s2])
    r3p, r2p = P(r3s.GetPosition()), P(r2s.GetPosition())
    track('SCL', B_CU, [(xt, -4.6), r3p])   # Anzapfung der SCL-Leitung
    track('SDA', B_CU, [jD, (jD[0], -11.4), (-3.9, -11.4), (-3.9, s3[1]), s3])
    track('SDA', B_CU, [(xs, -7.0), r2p])  # Anzapfung der SDA-Leitung
    # Taster: BTN von der linken Padseite nach hinten, GND-Via rechts oben
    bp = pad('SW1', 1); gp = pad('SW1', 2)
    track('BTN', F_CU, [bp, (bp[0], -1.6), (-3.0, -4.6)]); via('BTN', -3.0, -4.6)
    track('BTN', B_CU, [(-3.0, -4.6), (-3.0, -8.0), jB])
    track('GND', F_CU, [gp, (gp[0], 1.4)], 0.25); via('GND', gp[0], 1.4)

    # ---- Ebenen: In1 = GND (gerastert), In2 = 3V3 (massiv); LRA-Freifläche als Bauteil-Sperrzone
    zone(IN1, disc(15.7), 'GND', 0, hatch=True)
    zone(IN2, disc(15.5), '3V3', 0)
    LRA = (-8.0, 3.0, 8.0, 9.0)
    zone(B_CU, [(LRA[0], LRA[1]), (LRA[2], LRA[1]), (LRA[2], LRA[3]), (LRA[0], LRA[3])], '', 0, keepout=True)
    # Randzone: keine Leiterbahnen/Vias näher als 0,75 mm an der Kante (JLCPCB-Randabstand 0,3 mm + Reserve)
    kz = zone(F_CU, disc(17.0), '', 0, keepout=True, hole=disc(15.25), layers=[F_CU, IN1, IN2, B_CU])
    kz.SetDoNotAllowFootprints(False); kz.SetDoNotAllowTracks(True); kz.SetDoNotAllowVias(True)
    board.Save(os.path.join(TMP, 'pre.kicad_pcb'))
else:
    if not os.environ.get('NOSES'): pcbnew.ImportSpecctraSES(board, os.path.join(TMP, 'k.ses'))
    exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'finish.py')).read())
