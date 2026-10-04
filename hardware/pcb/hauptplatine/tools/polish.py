"""Letzte Politur: Referenz-/Wertfelder und Fab-Texte ausblenden (Siebdruck bleibt lesbar), Silk-Texte 0,8/0,15 und spiegeln auf der Rueckseite."""
import sys, os
os.environ.setdefault('KICAD9_FOOTPRINT_DIR', '/usr/share/kicad/footprints')
import pcbnew
from pcbnew import VECTOR2I, FromMM
b = pcbnew.LoadBoard(sys.argv[1])
for f in b.GetFootprints():
    for fld in f.GetFields():
        fld.SetVisible(False)
    for fld in (f.Reference(), f.Value()):
        fld.SetVisible(False)
        fld.SetTextSize(VECTOR2I(FromMM(0.8), FromMM(0.8))); fld.SetTextThickness(FromMM(0.15)); fld.SetMirrored(f.GetLayer() == pcbnew.B_Cu)
    for g in f.GraphicalItems():
        if g.GetClass() in ('PCB_TEXT', 'FP_TEXT'):
            if g.GetLayer() in (pcbnew.F_Fab, pcbnew.B_Fab): g.SetVisible(False)
            elif g.GetLayer() in (pcbnew.F_SilkS, pcbnew.B_SilkS):
                g.SetTextSize(VECTOR2I(FromMM(0.8), FromMM(0.8))); g.SetTextThickness(FromMM(0.15)); g.SetMirrored(g.GetLayer() == pcbnew.B_SilkS)
# Antennen-Keepout auch auf Platinenebene (Footprint-Zonen sperren Flaechenfuellung nicht zuverlaessig)
if not any(z.GetZoneName() == 'antenna_keepout_board' for z in b.Zones()):
    u15 = b.FindFootprintByReference('U15')
    for z0 in u15.Zones():
        ch = z0.Outline().Outline(0)
        z = pcbnew.ZONE(b); z.SetLayer(pcbnew.F_Cu)
        ls = pcbnew.LSET()
        for l in (pcbnew.F_Cu, pcbnew.In1_Cu, pcbnew.In2_Cu, pcbnew.B_Cu): ls.AddLayer(l)
        z.SetLayerSet(ls); z.SetIsRuleArea(True); z.SetZoneName('antenna_keepout_board')
        z.SetDoNotAllowTracks(True); z.SetDoNotAllowVias(True); z.SetDoNotAllowCopperPour(True); z.SetDoNotAllowPads(False); z.SetDoNotAllowFootprints(False)
        o = z.Outline(); o.NewOutline()
        for k in range(ch.PointCount()): o.Append(ch.CPoint(k).x, ch.CPoint(k).y)
        b.Add(z)
# Offene Pads erhalten die vom Schaltplan erwarteten Einzelnetze (tools/nc_nets.json), je Pad ein Netz -> keine Luftlinie
import json
NC = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'nc_nets.json')))
for f in b.GetFootprints():
    for pad in f.Pads():
        if pad.GetNetname() == '' and (f.GetReference() + '/' + pad.GetNumber()) in NC:
            nm = NC[f.GetReference() + '/' + pad.GetNumber()]
            ni = b.FindNet(nm)
            if ni is None:
                ni = pcbnew.NETINFO_ITEM(b, nm); b.Add(ni)
            pad.SetNet(ni)
pcbnew.ZONE_FILLER(b).Fill(b.Zones())
pcbnew.SaveBoard(sys.argv[2], b)
