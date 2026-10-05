#!/bin/sh
# Rev. 3b: Review-Korrekturen auf den Stand Rev. 3 (tools/routing/stand_vor_review_fixes.kicad_pcb) anwenden. Dauer insgesamt ca. 30-40 min.
#   Voraussetzungen: KiCad 9 (pcbnew, kicad-cli), Python: shapely, numpy, scipy, Pillow. Kein Freerouting noetig.
#   Reihenfolge ist wichtig: USB-Paar (Stufe 4) vor den Tastern (Stufe 2) und der Verbreiterung (Stufe 3b/3c), weil das Paar den Platz auf F.Cu zuerst braucht.
set -e
D=$(cd "$(dirname "$0")" && pwd); W=${W:-/tmp/rev3b}; mkdir -p $W
export KICAD9_FOOTPRINT_DIR=/usr/share/kicad/footprints KICAD9_SYMBOL_DIR=/usr/share/kicad/symbols
cd $D
python3 make_lib.py >/dev/null                       # Footprints (Molex_503480-3000 fuer J20 neu)
python3 gen_sch.py                                    # Schaltplan aus netlist.py (B1, B2, B3, H1, H7, H8, H4)
python3 rev3b_stage1.py $W/s1.kicad_pcb               # Netze/Bauteile: PCA9306, Lader, Reset-Sicherung Q21/Q22/R250, J20 -> Molex, DNP R1/R57
python3 rev3b_stage4.py $W/s1.kicad_pcb $W/s4.kicad_pcb    # USB-HS-Paar gekoppelt (W=0,2 / S=0,15 mm)
python3 rev3b_stage2.py $W/s4.kicad_pcb $W/s2.kicad_pcb    # BOOT-/EN-Taster SW2/SW3
python3 rev3b_stage3b.py $W/s2.kicad_pcb $W/s3b.kicad_pcb  # Leistungsnetze verbreitern
NETS=VBUS_SW,VBUS,VBAT MAXEXP=250000 python3 rev3b_stage3c.py $W/s3b.kicad_pcb $W/s3c.kicad_pcb   # schmale Abschnitte neu verlegen (ca. 15 min; erste Fassung mit Restore-Fehler verworfen)
NETS=SYS_POWER,V5_HOST MAXEXP=250000 python3 rev3b_stage3c.py $W/s3c.kicad_pcb $W/s3e.kicad_pcb       # dito (ca. 20 min)
python3 rev3b_finish.py $W/s3e.kicad_pcb              # Zonen fuellen, nach ../hauptplatine.kicad_pcb speichern, Lagenaufbau, placement.json
python3 export.py                                      # DRC, Gerber, BOM, CPL, PDF, Vorschau
python3 gen_readme.py                                  # README aus tools/README_vorlage.md
