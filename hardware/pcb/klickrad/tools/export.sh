#!/bin/sh
# Prüfberichte, Fertigungsdaten (JLCPCB und PCBWay), Vorschau, Stückliste und Abdeckung neu erzeugen.
# Voraussetzung: kicad-cli (KiCad 9), rsvg-convert
set -e
cd "$(dirname "$0")/.."
export KICAD9_SYMBOL_DIR=${KICAD9_SYMBOL_DIR:-/usr/share/kicad/symbols} KICAD9_FOOTPRINT_DIR=${KICAD9_FOOTPRINT_DIR:-/usr/share/kicad/footprints}
mkdir -p pruefung fertigung/gerber vorschau
python3 tools/gen_sch.py
kicad-cli sch erc --severity-all --format report --units mm -o pruefung/erc.rpt klickrad.kicad_sch
kicad-cli pcb drc --severity-all --schematic-parity --all-track-errors --format report --units mm -o pruefung/drc.rpt klickrad.kicad_pcb
find fertigung/gerber -type f -delete; rm -f fertigung/*.zip
# Ursprung = Platinenmitte (Hilfsursprung) für Gerber, Bohrdaten und Bestückungsdatei, damit alles zusammenpasst
kicad-cli pcb export gerbers --use-drill-file-origin --layers F.Cu,B.Cu,F.Paste,B.Paste,F.SilkS,B.SilkS,F.Mask,B.Mask,Edge.Cuts --output fertigung/gerber/ klickrad.kicad_pcb
kicad-cli pcb export drill --format excellon --drill-origin plot --excellon-units mm --excellon-separate-th --output fertigung/gerber/ klickrad.kicad_pcb
(cd fertigung/gerber && zip -q ../klickrad_v2_gerber_jlcpcb.zip ./*)
cp fertigung/klickrad_v2_gerber_jlcpcb.zip fertigung/klickrad_v2_gerber_pcbway.zip
kicad-cli pcb export pos --format csv --units mm --side both --use-drill-file-origin -o fertigung/bauteilpositionen.csv klickrad.kicad_pcb
python3 tools/gen_bom.py
tools/render.sh
timeout 100 kicad-cli pcb render --side top --width 1200 --height 1200 --quality basic -o vorschau/3d_vorne.png klickrad.kicad_pcb || true
timeout 100 kicad-cli pcb render --side bottom --width 1200 --height 1200 --quality basic -o vorschau/3d_hinten.png klickrad.kicad_pcb || true
kicad-cli sch export svg -o vorschau/sch_tmp klickrad.kicad_sch
cp vorschau/sch_tmp/klickrad.svg vorschau/schaltplan.svg; rsvg-convert -w 2400 -b white vorschau/schaltplan.svg -o vorschau/schaltplan.png
find vorschau/sch_tmp -type f -delete; rmdir vorschau/sch_tmp
kicad-cli sch export pdf -o vorschau/klickrad_schaltplan.pdf klickrad.kicad_sch
# FR4-Abdeckung
python3 tools/make_cover.py
mkdir -p abdeckung/fertigung/gerber abdeckung/vorschau; find abdeckung/fertigung -type f -delete
kicad-cli pcb export gerbers --layers F.Cu,B.Cu,F.SilkS,F.Mask,B.Mask,Edge.Cuts --output abdeckung/fertigung/gerber/ abdeckung/klickrad-abdeckung.kicad_pcb
kicad-cli pcb export drill --output abdeckung/fertigung/gerber/ abdeckung/klickrad-abdeckung.kicad_pcb || true
(cd abdeckung/fertigung/gerber && zip -q ../klickrad_abdeckung_gerber.zip ./*)
kicad-cli pcb export svg --mode-single --exclude-drawing-sheet --fit-page-to-board -l F.SilkS,Edge.Cuts abdeckung/klickrad-abdeckung.kicad_pcb -o abdeckung/vorschau/abdeckung.svg
rsvg-convert -w 1000 -b white abdeckung/vorschau/abdeckung.svg -o abdeckung/vorschau/abdeckung.png
