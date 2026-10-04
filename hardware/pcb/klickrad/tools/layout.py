# wird von build_pcb.py ausgeführt (exec)
import subprocess, shutil
PARTS = {p['ref']: p for p in netlist.parts()}
STAGE = os.environ.get('STAGE', 'all')       # place | all
TMP = os.environ.get('TMPDIR_PCB', '/tmp/w')

# ---- Entwurfsregeln
ds = board.GetDesignSettings()
ds.m_TrackMinWidth = FromMM(0.127); ds.m_MinClearance = FromMM(0.127)
ds.m_ViasMinSize = FromMM(0.5); ds.m_MinThroughDrill = FromMM(0.3)
ds.m_CopperEdgeClearance = FromMM(0.3); ds.m_HoleToHoleMin = FromMM(0.5)
ds.m_ViasMinAnnulus = FromMM(0.13); ds.m_MinHoleClearance = FromMM(0.25)
nc = ds.m_NetSettings.GetDefaultNetclass()
nc.SetClearance(FromMM(0.15)); nc.SetTrackWidth(FromMM(0.2)); nc.SetViaDiameter(FromMM(0.6)); nc.SetViaDrill(FromMM(0.3))

# ---- Umriss und Löcher
circle(pcbnew.Edge_Cuts, (0, 0), 16.0, 0.1)
for i, a in enumerate((90, 210, 330)):
    fp = loadfp('Klickrad:MountingHole_2.2mm_NPTH'); fp.SetReference(f'H{i+1}'); board.Add(fp)
    fp.SetPosition(V(14.6 * math.cos(math.radians(a)), 14.6 * math.sin(math.radians(a))))
    fp.SetAttributes(fp.GetAttributes() | pcbnew.FP_BOARD_ONLY)
    fp.Reference().SetVisible(False); fp.Value().SetVisible(False)

# ---- Segmente (Vorderseite) mit Via in der Fläche
for k in range(12):
    a = math.radians(make_lib.seg_angle(k)); vx, vy = make_lib.VIA_R * math.cos(a), make_lib.VIA_R * math.sin(a)
    place(PARTS[f'SEG{k+1}'], vx, vy, 'F', 0)
    via(PARTS[f'SEG{k+1}']['pins']['1'], vx, vy)

# ---- Bauteile (Rückseite, Koordinaten Frontansicht)
POS = {
 'U1': (0, 0, 270), 'U2': (-10.4, -1.0, 270), 'J1': (0, -11.4, 0), 'SW1': (0, 0, 0),
 'C1': (3.0, -2.2, 90), 'C2': (-1.0, -3.4, 0), 'C3': (1.4, -3.4, 0), 'R1': (-3.0, -1.6, 90),
 'C4': (-11.2, 4.6, 90), 'C6': (-11.2, 6.4, 90), 'C5': (-8.6, -5.0, 0),
 'R2': (6.6, -8.8, 0), 'R3': (6.6, -10.0, 0), 'R4': (6.6, -11.2, 0),
 'TP1': (-9.6, 8.6, 0), 'TP2': (-9.6, 6.4, 0),
}
for ref, (x, y, r) in POS.items():
    place(PARTS[ref], x, y, 'F' if ref == 'SW1' else 'B', r)

if os.environ.get('DUMP'):
    for r in ('U1', 'U2', 'J1'):
        print(r, [(p.GetNumber(), tuple(round(c, 2) for c in P(p.GetPosition()))) for p in placed[r].Pads()])

pre = os.path.join(TMP, 'pre.kicad_pcb')
board.Save(pre)
if STAGE == 'place':
    sys.exit(0)

# ---- Autorouting mit Freerouting (nur Signal-/Versorgungsleitungen; GND kommt als Fläche)
dsn, ses = os.path.join(TMP, 'k.dsn'), os.path.join(TMP, 'k.ses')
pcbnew.ExportSpecctraDSN(board, dsn)
for f in (ses,):
    if os.path.exists(f): os.remove(f)
subprocess.run(['java', '-jar', os.environ.get('FREEROUTING', '/tmp/w/fr.jar'), '-de', dsn, '-do', ses, '-mp', '30'], check=False,
               stdout=open(os.path.join(TMP, 'fr.log'), 'w'), stderr=subprocess.STDOUT)
assert os.path.exists(ses), 'Freerouting hat keine .ses geschrieben'
pcbnew.ImportSpecctraSES(board, ses)

exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'finish.py')).read())
