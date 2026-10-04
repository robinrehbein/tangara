#!/bin/sh
# Routing-Lauf: route.sh <arbeitsordner> <eingabe.kicad_pcb> [max_passes]
#   DSN-Export -> Freerouting 1.9.0 (xvfb, headless) -> SES-Import -> <arbeitsordner>/routed.kicad_pcb
set -e
D=$(cd "$(dirname "$0")" && pwd); W=$1; IN=$2; MP=${3:-30}
FR=${FREEROUTING:-/tmp/fr/fr190.jar}
export KICAD9_FOOTPRINT_DIR=/usr/share/kicad/footprints KICAD9_SYMBOL_DIR=/usr/share/kicad/symbols
mkdir -p $W; cp $IN $W/r.kicad_pcb; cp $D/projekt_vorlage.kicad_pro $W/r.kicad_pro; cp $D/projekt_vorlage.kicad_dru $W/r.kicad_dru
python3 - <<P 2>&1 | grep -v swig || true
import pcbnew; b=pcbnew.LoadBoard("$W/r.kicad_pcb"); pcbnew.ExportSpecctraDSN(b,"$W/r.dsn")
P
rm -f $W/r.ses
xvfb-run -a timeout ${FR_TIMEOUT:-2400} java -jar $FR -de $W/r.dsn -do $W/r.ses -mp $MP ${FR_EXTRA} > $W/fr.log 2>&1 || true
python3 - <<P 2>&1 | grep -v swig || true
import pcbnew; b=pcbnew.LoadBoard("${NR:-$W/r.kicad_pcb}"); pcbnew.ImportSpecctraSES(b,"$W/r.ses"); b.Save("$W/routed.kicad_pcb")
P
echo fertig $W
