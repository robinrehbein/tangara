#!/usr/bin/env python3
"""Stückliste klickrad_bom.csv. LCSC-Nummern nur, wo sie über lcsc.com geprüft wurden (Stand 2026-10-04)."""
import csv, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import netlist
ROOT = netlist.ROOT
EXTRA = {   # Wert/Footprint -> (Hersteller, MPN, LCSC, Hinweis)
 ('C', '0.1uF'): ('Samsung', 'CL05B104KO5NNNC', 'C1525', 'X7R 16 V, 0402'),
 ('C', '1uF'): ('Samsung', 'CL05A105KA5NQNC', 'C52923', 'X5R 6,3 V, 0402'),
 ('C', '10uF'): ('Samsung', 'CL10A106KP8NNNC', 'C19702', 'X5R 10 V, 0603, Höhe ca. 0,8 mm'),
 ('R', '10k'): ('UNI-ROYAL', '0402WGF1002TCE', 'C25744', '1 %, 0402; am 2026-10-04 auf lcsc.com bestätigt (Tangara: 0603)'),
 ('R', '4.7k'): ('UNI-ROYAL', '0402WGF4701TCE', 'C25900', '1 %, 0402, nur DNP-Option'),
 ('U', 'AT42QT2120'): ('Microchip', 'AT42QT2120-MMH', 'C617900', 'VQFN-20 3x3 mm, 0,45 mm; Nummer bestätigt, bei LCSC am 2026-10-04 NICHT auf Lager -> Mouser/DigiKey (ca. 5 USD)'),
 ('U', 'DRV2605LDGSR'): ('Texas Instruments', 'DRV2605LDGSR', 'C527464', 'VSSOP-10'),
 ('J', 'SM06B-SRSS-TB'): ('JST', 'SM06B-SRSS-TB(LF)(SN)', 'C160405', 'SH 1,0 mm, 6-pol., seitlich; höher als 1,5 mm (Datenblatt prüfen)'),
}
HEIGHT = {'C_0402': '0,5', 'C_0603': '0,8', 'R_0402': '0,4', 'VQFN': '0,85', 'VSSOP': 'ca. 1,1', 'SM06B': '>1,5 (Datenblatt prüfen)'}
groups = {}
for p in netlist.parts():
    if p.get('nobom') or p['ref'].startswith(('SW', 'TP')): continue
    key = (p['ref'].rstrip('0123456789'), p['value'], p['fp'], bool(p.get('dnp')))
    groups.setdefault(key, []).append(p['ref'])
rows = []
for (pre, val, fp, dnp), refs in sorted(groups.items(), key=lambda kv: (kv[0][0] not in 'UJ', kv[1][0])):
    mfr, mpn, lcsc, note = EXTRA[(pre, val)]
    h = next((v for k, v in HEIGHT.items() if k in fp), '')
    rows.append([', '.join(sorted(refs, key=lambda r: int(r.lstrip('ABCDEFGHIJKLMNOPQRSTUVWXYZ')))), len(refs), val, fp.split(':')[-1], mfr, mpn, lcsc, 'DNP (nicht bestücken)' if dnp else 'ja', h, note])
rows.append(['TP1, TP2', 2, 'LRA+/LRA-', 'SolderWirePad_1x01_SMD_1x2mm', '', '', '', 'Pads (kein Bauteil)', '0', 'Lötpads für die LRA-Litzen'])
rows.append(['SW1-SW3', 3, 'Touch', 'Klickrad:qtouch-button/-wheel/-guard', '', '', '', 'Kupferfläche (kein Bauteil)', '0', 'Mitteltaste, Wheel (3 Elektroden), Guard'])
rows.append(['(extern)', 1, 'FR4-Abdeckung 0,6 mm', 'abdeckung/klickrad-abdeckung', '', '', '', 'optional, separat bestellen', '0,6', 'Gerber: abdeckung/fertigung'])
rows.append(['(extern)', 1, 'LRA (X-Achse)', '', '', '', '', 'aufkleben, Litzen an TP1/TP2', '', 'nicht Teil der Platine; Typ und Maße siehe TEILE.md und Einkaufsliste'])
with open(os.path.join(ROOT, 'klickrad_bom.csv'), 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f)
    w.writerow(['Referenzen', 'Anzahl', 'Wert', 'Footprint', 'Hersteller', 'Herstellerteilenummer', 'LCSC', 'Bestückung', 'Höhe_mm', 'Hinweis'])
    w.writerows(rows)
# JLCPCB-Formate (BOM: Comment,Designator,Footprint,LCSC Part #; CPL: Designator,Mid X,Mid Y,Layer,Rotation)
with open(os.path.join(ROOT, 'fertigung', 'klickrad_v2_bom_jlcpcb.csv'), 'w', newline='', encoding='utf-8') as f:
    w2 = csv.writer(f); w2.writerow(['Comment', 'Designator', 'Footprint', 'LCSC Part #'])
    for r in rows:
        if r[7] == 'ja' and r[6]: w2.writerow([r[2], r[0], r[3], r[6]])
pos = os.path.join(ROOT, 'fertigung', 'bauteilpositionen.csv')
if os.path.exists(pos):
    with open(pos, encoding='utf-8') as f, open(os.path.join(ROOT, 'fertigung', 'klickrad_v2_cpl_jlcpcb.csv'), 'w', newline='', encoding='utf-8') as g:
        rd = csv.DictReader(f); w3 = csv.writer(g); w3.writerow(['Designator', 'Mid X', 'Mid Y', 'Layer', 'Rotation'])
        dnp = {p['ref'] for p in netlist.parts() if p.get('dnp')}
        for r in rd:
            if r['Ref'] in dnp or r['Ref'].startswith(('SW', 'TP', 'H')): continue
            w3.writerow([r['Ref'], r['PosX'] + 'mm', r['PosY'] + 'mm', 'Top' if r['Side'] == 'top' else 'Bottom', r['Rot']])
print('klickrad_bom.csv:', len(rows), 'Zeilen')
