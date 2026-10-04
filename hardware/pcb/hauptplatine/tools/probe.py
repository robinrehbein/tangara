import os, sys, math
os.environ.setdefault('KICAD9_FOOTPRINT_DIR','/usr/share/kicad/footprints')
import pcbnew
from pcbnew import VECTOR2I, FromMM, ToMM
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import netlist
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def load(spec):
    lib,name=spec.split(':')
    path=os.path.join(ROOT,'lib','Tangara.pretty') if lib=='Tangara' else '/usr/share/kicad/footprints/%s.pretty'%lib
    return pcbnew.FootprintLoad(path,name)
OX,OY=100.0,100.0
def V(x,y): return VECTOR2I(FromMM(OX+x),FromMM(OY-y))
def P(p): return (round(ToMM(p.x)-OX,3), round(OY-ToMM(p.y),3))
b=pcbnew.BOARD()
for ref,spec,rot,side in [('U1','Tangara:XIAO-ESP32-S3-Plus-SMD',270,'B'),('U2','Package_DFN_QFN:Texas_RHB0032E_VQFN-32-1EP_5x5mm_P0.5mm_EP3.45x3.45mm',0,'B'),('J4','Connector_Audio:Jack_3.5mm_CUI_SJ-3524-SMT_Horizontal',180,'B'),('J5','Connector_Card:microSD_HC_Molex_104031-0811',90,'B')]:
    fp=load(spec); b.Add(fp); fp.SetPosition(V(0,0))
    if side=='B': fp.Flip(V(0,0), pcbnew.FLIP_DIRECTION_LEFT_RIGHT)
    fp.SetOrientationDegrees(rot)
    print(ref,'orient',fp.GetOrientationDegrees())
    for p in fp.Pads():
        if ref=='U1' or ref=='J4' or ref=='J5' or p.GetNumber() in ('1','8','9','16','17','25','32','33'):
            print('  ',p.GetNumber(),P(p.GetPosition()))
