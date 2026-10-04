#!/bin/sh
# Komplettlauf: Platzierung -> eigener Router (tools/route_loop.py) -> GND-Gitter/Beschriftung.
#   TMPDIR_PCB=Arbeitsordner  SKIPROUTE=1 (vorhandenes tools/routed.kicad_pcb verwenden, kein Router)  ITER=Anzahl Routerdurchläufe
set -e
T=${TMPDIR_PCB:-/tmp/w}; mkdir -p $T; export TMPDIR_PCB=$T; D=$(cd "$(dirname "$0")" && pwd)
export KICAD9_SYMBOL_DIR=${KICAD9_SYMBOL_DIR:-/usr/share/kicad/symbols} KICAD9_FOOTPRINT_DIR=${KICAD9_FOOTPRINT_DIR:-/usr/share/kicad/footprints}
if [ -z "$SKIPROUTE" ]; then
  python3 $D/make_lib.py > /dev/null
  MODE=place python3 $D/build_pcb.py 2>&1 | grep -v swig || true
  python3 $D/route_loop.py $T/pre.kicad_pcb $T/routed.kicad_pcb 2>&1 | grep -v swig
  cp $T/routed.kicad_pcb $D/routed.kicad_pcb
fi
# Beschriftung, GND-Gitter, Füllung
MODE=finish NOSES=1 LOADFROM=$D/routed.kicad_pcb python3 $D/build_pcb.py 2>&1 | grep -v swig || true
# pcbnew überschreibt beim Speichern die Projektdatei -> Vorlage wiederherstellen
cp $D/projekt_vorlage.kicad_pro $D/../klickrad.kicad_pro
