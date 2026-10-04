#!/usr/bin/env python3
"""Probiert zufällige Netzreihenfolgen mit route.py, bis keine Verbindung fehlt. Aufruf: route_random.py pre.kicad_pcb out.kicad_pcb SEED"""
import subprocess, sys, os, random, re
here = os.path.dirname(os.path.abspath(__file__))
src, dst, seed = sys.argv[1], sys.argv[2], int(sys.argv[3])
nets = 'LRA_P,LRA_N,GND,3V3,SDA,SCL,CHANGE,K2,KB,KG,K1,K0,E0,E1,E2,EB,EG,EN,REG,RESET'.split(',')
random.seed(seed); best = 99
for it in range(200):
    o = nets[:]; random.shuffle(o)
    try:
        r = subprocess.run([sys.executable, os.path.join(here, 'route.py'), src, dst + '.try'], capture_output=True, text=True, timeout=450, env=dict(os.environ, ORDER=','.join(o)))
    except subprocess.TimeoutExpired:
        print(seed, it, 'timeout', flush=True); continue
    m = re.search(r'fehlende Verbindungen: (\d+)', r.stdout); n = int(m.group(1)) if m else 99
    print(seed, it, n, ','.join(o), flush=True)
    if n < best: best = n; os.replace(dst + '.try', dst); open(dst + '.order', 'w').write(','.join(o))
    if n == 0: print('FERTIG'); break
