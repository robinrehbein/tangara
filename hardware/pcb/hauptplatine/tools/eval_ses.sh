#!/bin/sh
# eval_ses.sh <run-ordner> : SES in Basisplatine (pre_nr) importieren, Zonen fuellen, DRC, Zusammenfassung
W=$1; D=$(cd "$(dirname "$0")" && pwd); R=$D/..
export KICAD9_FOOTPRINT_DIR=/usr/share/kicad/footprints KICAD9_SYMBOL_DIR=/usr/share/kicad/symbols
BASE=${BASE:-/tmp/hp/pre_nr.kicad_pcb}
python3 -c "
import pcbnew; b=pcbnew.LoadBoard('$BASE'); pcbnew.ImportSpecctraSES(b,'$W/r.ses'); b.Save('$W/routed_nr.kicad_pcb')" 2>&1 | grep -v "swig\|assert"
cd $R; MODE=finish LOADFROM=$W/routed_nr.kicad_pcb TMPDIR_PCB=/tmp/hp python3 tools/build_pcb.py 2>&1 | grep -v "swig\|assert"
cp hauptplatine.kicad_pcb $W/final.kicad_pcb
kicad-cli pcb drc --severity-all --schematic-parity -o $W/drc.rpt hauptplatine.kicad_pcb >/dev/null 2>&1
grep -E "^\[" $W/drc.rpt | sed 's/\].*//;s/\[//' | sort | uniq -c
