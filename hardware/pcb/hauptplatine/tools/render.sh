#!/bin/sh
# Schnellvorschau: render.sh <pcb> <out-prefix>  (Oberseite und Unterseite als PNG)
set -e
PCB=$1; OUT=$2
kicad-cli pcb export svg --layers F.Cu,F.SilkS,F.Fab,Edge.Cuts --page-size-mode 2 --exclude-drawing-sheet -o $OUT-top.svg $PCB >/dev/null
kicad-cli pcb export svg --layers B.Cu,B.SilkS,B.Fab,Edge.Cuts --mirror --page-size-mode 2 --exclude-drawing-sheet -o $OUT-bot.svg $PCB >/dev/null
rsvg-convert -h 1600 -b white $OUT-top.svg -o $OUT-top.png
rsvg-convert -h 1600 -b white $OUT-bot.svg -o $OUT-bot.png
