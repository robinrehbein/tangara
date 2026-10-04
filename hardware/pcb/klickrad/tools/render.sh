#!/bin/sh
# Vorschau-Bilder (SVG + PNG) von Vorder- und Rückseite
D=$(dirname "$0")/..; O=${1:-$D/vorschau}; mkdir -p "$O"
kicad-cli pcb export svg --mode-single --exclude-drawing-sheet --fit-page-to-board -l F.Cu,F.Mask,F.SilkS,Edge.Cuts "$D/klickrad.kicad_pcb" -o "$O/vorderseite.svg" >/dev/null
kicad-cli pcb export svg --mode-single --exclude-drawing-sheet --fit-page-to-board --mirror -l B.Cu,B.SilkS,Edge.Cuts "$D/klickrad.kicad_pcb" -o "$O/rueckseite.svg" >/dev/null
kicad-cli pcb export svg --mode-single --exclude-drawing-sheet --fit-page-to-board -l F.Cu,B.Cu,Edge.Cuts "$D/klickrad.kicad_pcb" -o "$O/kupfer.svg" >/dev/null
for n in vorderseite rueckseite kupfer; do rsvg-convert -w 1400 -b white "$O/$n.svg" -o "$O/$n.png"; done
