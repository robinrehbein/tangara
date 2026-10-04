#!/usr/bin/env python3
"""Sucht eine Netzreihenfolge, bei der route.py alle Netze verlegt (Zufallsstart, danach Bergsteigen: fehlendes Netz weiter nach vorn).
Aufruf: route_random.py pre.kicad_pcb out.kicad_pcb SEED"""
import subprocess, sys, os, random, re
here = os.path.dirname(os.path.abspath(__file__))
src, dst, seed = sys.argv[1], sys.argv[2], int(sys.argv[3])
nets = 'LRA_P,LRA_N,GND,3V3,SDA,SCL,CHANGE,K2,KB,KG,K1,K0,E0,E1,E2,EB,EG,EN,REG,RESET'.split(',')
random.seed(seed); best = 99
def run(o):
    try:
        r = subprocess.run([sys.executable, os.path.join(here, 'route.py'), src, dst.replace('.kicad_pcb', '_try.kicad_pcb')], capture_output=True, text=True, timeout=450, env=dict(os.environ, ORDER=','.join(o)))
    except subprocess.TimeoutExpired:
        return 99, []
    m = re.search(r'fehlende Verbindungen: (\d+)', r.stdout)
    failed = [f for f in re.findall(r'^FEHLT (\S+) ', r.stdout, re.M) if f in o]
    n = int(m.group(1)) if m else 99
    if n == 0:   # alle Signalnetze verlegt -> GND-Anbindung (Stummel/Ring/Gitter)
        try:
            g = subprocess.run([sys.executable, os.path.join(here, 'route_gnd.py'), dst.replace('.kicad_pcb', '_try.kicad_pcb'), dst.replace('.kicad_pcb', '_try2.kicad_pcb')], capture_output=True, text=True, timeout=300)
            k = re.search(r'GND-Cluster ohne Anbindung: (\d+)', g.stdout)
            n = int(k.group(1)) if k else 99
            if os.path.exists(dst.replace('.kicad_pcb', '_try2.kicad_pcb')): os.replace(dst.replace('.kicad_pcb', '_try2.kicad_pcb'), dst.replace('.kicad_pcb', '_try.kicad_pcb'))
            failed = ['GND-Cluster'] if n else []
        except subprocess.TimeoutExpired:
            return 99, []
    return n, failed
cur = nets[:]; random.shuffle(cur); cur_n, cur_f = run(cur)
if os.path.exists(dst.replace('.kicad_pcb', '_try.kicad_pcb')): os.replace(dst.replace('.kicad_pcb', '_try.kicad_pcb'), dst.replace('.kicad_pcb', '_cur.kicad_pcb'))
for it in range(400):
    if cur_n < best:
        best = cur_n; import shutil; shutil.copy(dst.replace('.kicad_pcb', '_cur.kicad_pcb'), dst); open(dst + '.order', 'w').write(','.join(cur))
    print(seed, it, cur_n, cur_f, ','.join(cur), flush=True)
    if cur_n == 0: print('FERTIG'); break
    o = cur[:]
    f = random.choice(cur_f) if cur_f else random.choice(o)
    if f not in o: f = random.choice(o)
    o.remove(f); o.insert(random.randrange(0, max(1, cur.index(f))), f)
    if random.random() < 0.3:
        i, j = random.sample(range(len(o)), 2); o[i], o[j] = o[j], o[i]
    n, fl = run(o)
    if n <= cur_n and os.path.exists(dst.replace('.kicad_pcb', '_try.kicad_pcb')): cur, cur_n, cur_f = o, n, fl; os.replace(dst.replace('.kicad_pcb', '_try.kicad_pcb'), dst.replace('.kicad_pcb', '_cur.kicad_pcb'))
