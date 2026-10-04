#!/usr/bin/env python3
"""Ruft route.py wiederholt auf und zieht Netze mit fehlenden Verbindungen in der Reihenfolge nach vorn (Rip-up-and-retry von Hand)."""
import subprocess, sys, os, re
here = os.path.dirname(os.path.abspath(__file__))
src, dst = sys.argv[1], sys.argv[2]
order = 'GND,3V3,SDA,K2,KB,KG,K1,K0,E0,E1,E2,EB,EG,SDA,SCL,CHANGE,EN,REG,RESET,LRA_P,LRA_N'.split(',')
if os.path.exists(os.path.join(here, 'route_order.txt')): order = open(os.path.join(here, 'route_order.txt')).read().strip().split(',')
best = None
for it in range(int(os.environ.get('ITER', '10'))):
    env = dict(os.environ, ORDER=','.join(order))
    r = subprocess.run([sys.executable, os.path.join(here, 'route.py'), src, dst + '.try'], capture_output=True, text=True, env=env)
    fails = [f for f in re.findall(r'FEHLT (\S+) ', r.stdout) if f in order]
    n = len(fails) + len(re.findall(r'STUMMEL fehlt', r.stdout))
    print('Durchlauf', it + 1, 'fehlende Verbindungen:', n, 'Reihenfolge', ','.join(order), flush=True)
    if best is None or n < best:
        best = n; os.replace(dst + '.try', dst); open(os.path.join(here, 'route_order.txt'), 'w').write(','.join(order))
    if n == 0: break
    bad = []
    for f in fails:
        if f not in bad: bad.append(f)
    order = bad + [o for o in order if o not in bad]
    if False:
        import random
        random.seed(it); rest = order[:]; random.shuffle(rest); order = rest
print('beste Lösung: fehlende Verbindungen', best)
