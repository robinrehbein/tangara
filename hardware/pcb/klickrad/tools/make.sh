#!/bin/sh
# Komplettlauf: Platzierung -> Freerouting (bis zu 3 Durchläufe) -> Zonen/Beschriftung.
#   FREEROUTING=/pfad/freerouting.jar  TMPDIR_PCB=Arbeitsordner  SKIPROUTE=1 (vorhandenes tools/routed_freerouting.kicad_pcb verwenden, kein Router)
set -e
T=${TMPDIR_PCB:-/tmp/w}; mkdir -p $T; export TMPDIR_PCB=$T; D=$(cd "$(dirname "$0")" && pwd)
export KICAD9_SYMBOL_DIR=${KICAD9_SYMBOL_DIR:-/usr/share/kicad/symbols} KICAD9_FOOTPRINT_DIR=${KICAD9_FOOTPRINT_DIR:-/usr/share/kicad/footprints}
if [ -z "$SKIPROUTE" ]; then
MODE=place python3 $D/build_pcb.py 2>&1 | grep -v swig || true
  cp $T/pre.kicad_pcb $T/r.kicad_pcb; cp $D/projekt_vorlage.kicad_pro $T/r.kicad_pro
  i=0
  while [ $i -lt ${PASSES:-3} ]; do
    i=$((i+1))
    python3 - <<P 2>&1 | grep -v swig || true
import pcbnew; b=pcbnew.LoadBoard("$T/r.kicad_pcb"); pcbnew.ExportSpecctraDSN(b,"$T/k.dsn")
P
    rm -f $T/k.ses
    java -jar ${FREEROUTING:-$T/fr.jar} -de $T/k.dsn -do $T/k.ses > $T/fr.log 2>&1 || true
    python3 - <<P 2>&1 | grep -v swig || true
import pcbnew; b=pcbnew.LoadBoard("$T/r.kicad_pcb"); pcbnew.ImportSpecctraSES(b,"$T/k.ses"); b.Save("$T/r.kicad_pcb")
P
    python3 - <<P 2>&1 | grep -v swig || true
import pcbnew; b=pcbnew.LoadBoard("$T/r.kicad_pcb"); pcbnew.ZONE_FILLER(b).Fill(b.Zones()); b.Save("$T/rf.kicad_pcb")
P
    cp $T/r.kicad_pro $T/rf.kicad_pro
    N=$(kicad-cli pcb drc --format json --severity-all -o $T/r_drc.json $T/rf.kicad_pcb >/dev/null 2>&1; python3 -c "import json;d=json.load(open('$T/r_drc.json'));print(len(d.get('unconnected_items',[])))")
    echo "Routing-Durchlauf $i: $N offene Verbindungen"
    [ "$N" = "0" ] && break
  done
  cp $T/r.kicad_pcb $T/routed.kicad_pcb
  cp $T/routed.kicad_pcb $D/routed_freerouting.kicad_pcb
  MODE=finish NOSES=1 LOADFROM=$T/routed.kicad_pcb python3 $D/build_pcb.py 2>&1 | grep -v swig || true
else
  # reproduziert exakt die abgegebene Platine: tools/routed_freerouting.kicad_pcb (Platzierung + Freerouting-Ergebnis, ohne Beschriftung/Füllung)
  MODE=finish NOSES=1 LOADFROM=$D/routed_freerouting.kicad_pcb python3 $D/build_pcb.py 2>&1 | grep -v swig || true
fi
# pcbnew überschreibt beim Speichern die Projektdatei -> Vorlage wiederherstellen
cp $D/projekt_vorlage.kicad_pro $D/../klickrad.kicad_pro
