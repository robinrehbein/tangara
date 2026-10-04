#!/bin/sh
# Ein Segment der Platzierung (Simulated Annealing in Abschnitten, damit jeder Aufruf kurz bleibt):
#   sa_seg.sh <seed> <T0> <iter> [init]   -> schreibt $SA/pl<seed>.json (Eingabe: $SA/pl<seed>.json des vorigen Segments)
D=$(cd "$(dirname "$0")" && pwd); SA=${SA:-/tmp/sa}; mkdir -p $SA
SEED=$1 T0=$2 ITER=$3 OUT=$SA/pl$1.next.json ${4:+INIT=$SA/pl$1.json} python3 $D/place_sa.py > $SA/log$1.txt 2>&1 && mv $SA/pl$1.next.json $SA/pl$1.json
