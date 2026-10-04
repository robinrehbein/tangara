import sys, os
os.environ.setdefault('KICAD9_FOOTPRINT_DIR', '/usr/share/kicad/footprints')
import pcbnew
b = pcbnew.LoadBoard(sys.argv[1]); pcbnew.ZONE_FILLER(b).Fill(b.Zones()); pcbnew.SaveBoard(sys.argv[2], b)
