#!/bin/sh
# post.sh <run-ordner> : SES importieren, Zonen fuellen (finish), DRC, GND-Nachbesserung, neu fuellen, DRC
W=$1; D=$(cd "$(dirname "$0")" && pwd); R=$D/..
export KICAD9_FOOTPRINT_DIR=/usr/share/kicad/footprints KICAD9_SYMBOL_DIR=/usr/share/kicad/symbols
BASE=${BASE:?BASE=...nr.kicad_pcb}
f() { grep -E "^\[" $1 | sed 's/\].*//;s/\[//' | sort | uniq -c | tr '\n' ';'; echo; }
python3 -c "
import pcbnew; b=pcbnew.LoadBoard('$BASE'); pcbnew.ImportSpecctraSES(b,'$W/r.ses'); b.Save('$W/routed_nr.kicad_pcb')" 2>&1 | grep -v "swig\|assert"
cd $R; MODE=finish LOADFROM=$W/routed_nr.kicad_pcb TMPDIR_PCB=/tmp/hp python3 tools/build_pcb.py 2>&1 | grep -v "swig\|assert" | tail -1
kicad-cli pcb drc --severity-all -o $W/drc1.rpt hauptplatine.kicad_pcb >/dev/null 2>&1; echo vor Stitch: $(f $W/drc1.rpt)
for i in 1 2; do
  python3 tools/stitch.py hauptplatine.kicad_pcb $W/drc1.rpt $W/stitched.kicad_pcb 2>&1 | grep -v "swig\|assert"
  python3 tools/refill.py $W/stitched.kicad_pcb hauptplatine.kicad_pcb 2>&1 | grep -v "swig\|assert"
  kicad-cli pcb drc --severity-all -o $W/drc1.rpt hauptplatine.kicad_pcb >/dev/null 2>&1; echo nach Stitch $i: $(f $W/drc1.rpt)
done
cp hauptplatine.kicad_pcb $W/final.kicad_pcb
