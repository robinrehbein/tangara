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
 ('R', '75k'): ('UNI-ROYAL', '0402WGF7502TCE', '', '1 %, 0402; LCSC-Nummer nicht geprüft'),
 ('R', '4.7k'): ('UNI-ROYAL', '0402WGF4701TCE', 'C25900', '1 %, 0402, nur DNP-Option'),
 ('U', 'MPR121QR2'): ('NXP', 'MPR121QR2', 'C91322', 'QFN-20 3x3 mm, Raster 0,4 mm'),
 ('U', 'DRV2605LDGSR'): ('Texas Instruments', 'DRV2605LDGSR', 'C527464', 'VSSOP/MSOP-10'),
 ('SW', 'B3U-1000P'): ('Omron', 'B3U-1000P', 'C231329', '3,0 x 2,5 x 1,2 mm, SMD-Taster'),
 ('J', 'SM06B-SRSS-TB'): ('JST', 'SM06B-SRSS-TB(LF)(SN)', 'C160405', 'SH 1,0 mm, 6-pol., seitlich; höher als 1,5 mm (Datenblatt prüfen)'),
}
HEIGHT = {'C_0402': '0,5', 'C_0603': '0,8', 'R_0402': '0,4', 'QFN': 'ca. 0,8', 'MSOP': 'ca. 1,1', 'B3U': '1,2 (Vorderseite)', 'SM06B': '>1,5 (Datenblatt prüfen)'}
groups = {}
for p in netlist.parts():
    if p.get('nobom') or p['ref'].startswith(('SEG', 'TP')): continue
    key = (p['ref'].rstrip('0123456789'), p['value'], p['fp'], bool(p.get('dnp')))
    groups.setdefault(key, []).append(p['ref'])
rows = []
for (pre, val, fp, dnp), refs in sorted(groups.items(), key=lambda kv: (kv[0][0] not in 'UJ', kv[1][0])):
    mfr, mpn, lcsc, note = EXTRA[(pre, val)]
    h = next((v for k, v in HEIGHT.items() if k in fp), '')
    rows.append([', '.join(sorted(refs, key=lambda r: int(r.lstrip('ABCDEFGHIJKLMNOPQRSTUVWXYZ')))), len(refs), val, fp.split(':')[-1], mfr, mpn, lcsc, 'DNP (nicht bestücken)' if dnp else 'ja', h, note])
rows.append(['TP1, TP2', 2, 'LRA+/LRA-', 'SolderWirePad_1x01_SMD_1x2mm', '', '', '', 'Pads (kein Bauteil)', '0', 'Lötpads für die LRA-Litzen'])
rows.append(['SEG1-SEG12', 12, 'Touch', 'Klickrad:SEG1..12', '', '', '', 'Kupferfläche (kein Bauteil)', '0', 'Touch-Segmente vorn'])
rows.append(['(extern)', 1, 'LRA (X-Achse)', '', '', '', '', 'aufkleben, Litzen an TP1/TP2', '', 'nicht Teil der Platine; Typ und Maße siehe TEILE.md und Einkaufsliste'])
with open(os.path.join(ROOT, 'klickrad_bom.csv'), 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f)
    w.writerow(['Referenzen', 'Anzahl', 'Wert', 'Footprint', 'Hersteller', 'Herstellerteilenummer', 'LCSC', 'Bestückung', 'Höhe_mm', 'Hinweis'])
    w.writerows(rows)
print('klickrad_bom.csv:', len(rows), 'Zeilen')
