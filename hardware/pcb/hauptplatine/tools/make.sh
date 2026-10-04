#!/bin/sh
# Komplettlauf: Bibliotheken -> (optional Platzierung + GPIO-Zuordnung) -> Platine -> Freerouting -> Nachbearbeitung -> Schaltplan -> Exporte
#   FREEROUTING=/pfad/freerouting-2.1.0.jar   TMPDIR_PCB=Arbeitsordner (Standard /tmp/hp)
#   PLACE=1      Platzierung (Simulated Annealing, ca. 10 min, SEED/ITER setzbar) und GPIO-Zuordnung neu berechnen (sonst tools/placement.json, tools/gpio_map.json)
#   SKIPROUTE=1  vorhandenes tools/routed_freerouting.kicad_pcb verwenden (kein Router)
set -e
D=$(cd "$(dirname "$0")" && pwd)
T=${TMPDIR_PCB:-/tmp/hp}; export TMPDIR_PCB=$T; mkdir -p $T
export KICAD9_SYMBOL_DIR=${KICAD9_SYMBOL_DIR:-/usr/share/kicad/symbols} KICAD9_FOOTPRINT_DIR=${KICAD9_FOOTPRINT_DIR:-/usr/share/kicad/footprints}
python3 $D/make_lib.py >/dev/null; python3 $D/make_pro.py
if [ -n "$PLACE" ]; then
  python3 $D/place_sa.py | grep -v swig
  python3 $D/gpio_assign.py | grep -v swig
fi
if [ -z "$SKIPROUTE" ]; then
  MODE=place python3 $D/build_pcb.py 2>&1 | grep -v swig || true
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
python3 $D/gen_sch.py | grep -v swig
python3 $D/export.py | grep -v swig
