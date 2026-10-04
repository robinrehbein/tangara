#!/usr/bin/env python3
"""Fertigungsdaten: Gerber+Bohrdaten (ZIP), Stueckliste (PCBWay-Format), Bestueckungsdatei (CPL), Vorschau, Schaltplan-PDF, ERC/DRC-Berichte.
Aufruf: python3 tools/export.py   (aus hauptplatine/, benoetigt kicad-cli)"""
import os, sys, csv, json, subprocess, zipfile, shutil, glob, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import netlist
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FERT = os.path.join(ROOT, 'fertigung'); PRUEF = os.path.join(ROOT, 'pruefung'); VOR = os.path.join(ROOT, 'vorschau')
for d in (FERT, PRUEF, VOR): os.makedirs(d, exist_ok=True)
PCB = os.path.join(ROOT, 'hauptplatine.kicad_pcb'); SCH = os.path.join(ROOT, 'hauptplatine.kicad_sch')
env = dict(os.environ, KICAD9_SYMBOL_DIR='/usr/share/kicad/symbols', KICAD9_FOOTPRINT_DIR='/usr/share/kicad/footprints')
def run(*a):
    r = subprocess.run(a, capture_output=True, text=True, env=env)
    if r.returncode not in (0,): print('WARN', a[:4], r.stdout[-300:], r.stderr[-300:])
    return r

# ------------------------------------------------------------------ Gerber + Bohrdaten
G = os.path.join(FERT, '_gerber'); shutil.rmtree(G, ignore_errors=True); os.makedirs(G)
layers = 'F.Cu,In1.Cu,In2.Cu,B.Cu,F.Paste,B.Paste,F.SilkS,B.SilkS,F.Mask,B.Mask,Edge.Cuts'
run('kicad-cli', 'pcb', 'export', 'gerbers', '--layers', layers, '--no-protel-ext', '--subtract-soldermask', '--use-drill-file-origin', '-o', G + '/', PCB)
run('kicad-cli', 'pcb', 'export', 'drill', '--format', 'excellon', '--drill-origin', 'plot', '--excellon-units', 'mm', '--excellon-separate-th',
    '--generate-map', '--map-format', 'gerberx2', '-o', G + '/', PCB)
zp = os.path.join(FERT, 'hauptplatine_gerber_bohrdaten.zip')
with zipfile.ZipFile(zp, 'w', zipfile.ZIP_DEFLATED) as z:
    for f in sorted(glob.glob(G + '/*')): z.write(f, os.path.basename(f))
print('ZIP:', zp, sorted(os.listdir(G)))
shutil.rmtree(G)

# ------------------------------------------------------------------ Stueckliste
PARTS = [p for p in netlist.parts() if not p.get('nobom')]
def thtype(p):
    return 'THT' if p['fp'] in ('Hauptplatine:GCT_USB4510-03-1-A_REVA',) else 'SMD'
groups = {}
for p in PARTS:
    key = (p['value'], p.get('mpn', ''), p['fp'], bool(p.get('dnp')), p['src'])
    groups.setdefault(key, []).append(p)
def refkey(r):
    m = re.match(r'([A-Z]+)(\d+)', r); return (m.group(1), int(m.group(2)))
rows = []
for i, (key, ps) in enumerate(sorted(groups.items(), key=lambda kv: refkey(sorted(kv[1], key=lambda q: refkey(q['ref']))[0]['ref'])), 1):
    ps = sorted(ps, key=lambda q: refkey(q['ref'])); p = ps[0]
    rows.append({'Item': i, 'Designator': ','.join(q['ref'] for q in ps), 'Qty': len(ps), 'Manufacturer': p.get('mfr', ''), 'Mfg Part #': p.get('mpn', ''),
                 'Description': (p['value'] + ' - ' + p.get('desc', ''))[:200], 'Package': p.get('pkg') or p['fp'].split(':')[-1], 'Type': thtype(p),
                 'LCSC #': p.get('lcsc', ''), 'DigiKey #': p.get('dk', ''), 'Herkunft': p['src'],
                 'Bestueckung': 'NICHT BESTUECKEN (DNP)' if p.get('dnp') else 'ja'})
cols = ['Item', 'Designator', 'Qty', 'Manufacturer', 'Mfg Part #', 'Description', 'Package', 'Type', 'LCSC #', 'DigiKey #', 'Herkunft', 'Bestueckung']
with open(os.path.join(FERT, 'hauptplatine_BOM_PCBWay.csv'), 'w', newline='', encoding='utf-8') as f:
    wr = csv.DictWriter(f, cols); wr.writeheader(); wr.writerows(rows)
print('BOM:', len(rows), 'Positionen,', sum(r['Qty'] for r in rows), 'Bauteile')

# ------------------------------------------------------------------ Bestueckungsdatei (CPL)
tmp = os.path.join(FERT, '_pos.csv')
run('kicad-cli', 'pcb', 'export', 'pos', '--format', 'csv', '--units', 'mm', '--side', 'both', '--exclude-dnp', '--use-drill-file-origin', '-o', tmp, PCB)
dnp = {p['ref'] for p in netlist.parts() if p.get('dnp')}
with open(tmp, newline='') as f: rd = list(csv.DictReader(f))
os.remove(tmp)
out = []
for r in rd:
    ref = r['Ref']
    if ref.startswith('FID') or ref in dnp: continue
    out.append({'Designator': ref, 'Mid X': r['PosX'] + 'mm', 'Mid Y': r['PosY'] + 'mm', 'Layer': 'Top' if r['Side'] == 'top' else 'Bottom', 'Rotation': r['Rot']})
with open(os.path.join(FERT, 'hauptplatine_CPL_PCBWay.csv'), 'w', newline='') as f:
    wr = csv.DictWriter(f, ['Designator', 'Mid X', 'Mid Y', 'Layer', 'Rotation']); wr.writeheader(); wr.writerows(sorted(out, key=lambda r: refkey(r['Designator'])))
print('CPL:', len(out), 'Bauteile (', sum(1 for o in out if o['Layer'] == 'Top'), 'oben,', sum(1 for o in out if o['Layer'] == 'Bottom'), 'unten )')

# ------------------------------------------------------------------ Schaltplan-PDF, Pruefberichte
run('kicad-cli', 'sch', 'export', 'pdf', '-o', os.path.join(FERT, 'hauptplatine_schaltplan.pdf'), SCH)
run('kicad-cli', 'sch', 'erc', '--severity-all', '-o', os.path.join(PRUEF, 'erc.rpt'), SCH)
run('kicad-cli', 'pcb', 'drc', '--severity-all', '--schematic-parity', '-o', os.path.join(PRUEF, 'drc.rpt'), PCB)
print('Berichte geschrieben')
