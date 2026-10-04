#!/bin/sh
# Komplettlauf: Platzierung -> Freerouting (mehrere Durchlaeufe) -> Zonen/Beschriftung -> hauptplatine.kicad_pcb
#   FREEROUTING=/pfad/freerouting.jar   TMPDIR_PCB=Arbeitsordner   SKIPROUTE=1 (vorhandenes tools/routed_freerouting.kicad_pcb verwenden)
set -e
D=$(cd "$(dirname "$0")" && pwd)
T=${TMPDIR_PCB:-/tmp/hp}; export TMPDIR_PCB=$T; mkdir -p $T
export KICAD9_SYMBOL_DIR=${KICAD9_SYMBOL_DIR:-/usr/share/kicad/symbols} KICAD9_FOOTPRINT_DIR=${KICAD9_FOOTPRINT_DIR:-/usr/share/kicad/footprints}
python3 $D/make_lib.py >/dev/null; python3 $D/make_pro.py
if [ -z "$SKIPROUTE" ]; then
  MODE=place python3 $D/build_pcb.py 2>&1 | grep -v swig | grep -E "KEIN|NICHT|platziert" || true
  cp $T/pre.kicad_pcb $T/r.kicad_pcb; cp $D/projekt_vorlage.kicad_pro $T/r.kicad_pro
  python3 - <<P 2>&1 | grep -v swig || true
import pcbnew; b=pcbnew.LoadBoard("$T/r.kicad_pcb"); pcbnew.ExportSpecctraDSN(b,"$T/r.dsn")
P
  rm -f $T/r.ses
  java -jar ${FREEROUTING:-$T/fr.jar} -de $T/r.dsn -do $T/r.ses -mp ${MAXPASSES:-40} > $T/fr.log 2>&1 || true
  python3 - <<P 2>&1 | grep -v swig || true
import pcbnew; b=pcbnew.LoadBoard("$T/r.kicad_pcb"); pcbnew.ImportSpecctraSES(b,"$T/r.ses"); b.Save("$T/routed.kicad_pcb")
P
  cp $T/routed.kicad_pcb $D/routed_freerouting.kicad_pcb
fi
MODE=finish LOADFROM=$D/routed_freerouting.kicad_pcb python3 $D/build_pcb.py 2>&1 | grep -v swig || true
cp $D/projekt_vorlage.kicad_pro $D/../hauptplatine.kicad_pro
