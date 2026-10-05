#!/usr/bin/env python3
"""Erzeugt README.md aus Vorlage + aktuellen Daten (Netzliste, Platzierung, GPIO-Zuordnung, ERC/DRC-Berichte, Stueckliste).
Aufruf: python3 tools/gen_readme.py   (nach tools/export.py)"""
import os, sys, json, re, csv, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import netlist, layout
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = {p['ref']: p for p in netlist.parts()}
pl = json.load(open(os.path.join(ROOT, 'tools', 'placement.json')))
gm = json.load(open(os.path.join(ROOT, 'tools', 'gpio_map.json')))
stat = json.load(open(os.path.join(ROOT, 'tools', 'stand.json'))) if os.path.exists(os.path.join(ROOT, 'tools', 'stand.json')) else {}
pad_of = {v: k for k, v in netlist.S31.items()}

def rpt_counts(path):
    c = collections.Counter(); txt = open(path).read() if os.path.exists(path) else ''
    for m in re.finditer(r'^\[(\w+)\]', txt, re.M): c[m.group(1)] += 1
    m = re.search(r'Found (\d+) violations', txt)
    return c, txt
erc, erc_txt = rpt_counts(os.path.join(ROOT, 'pruefung', 'erc.rpt'))
drc, drc_txt = rpt_counts(os.path.join(ROOT, 'pruefung', 'drc.rpt'))
def summarize(c):
    return ', '.join('%d x %s' % (v, k) for k, v in sorted(c.items())) or 'keine'

bom = list(csv.DictReader(open(os.path.join(ROOT, 'fertigung', 'hauptplatine_BOM_PCBWay.csv')))) if os.path.exists(os.path.join(ROOT, 'fertigung', 'hauptplatine_BOM_PCBWay.csv')) else []
n_lines = len(bom); n_parts = sum(int(r['Qty']) for r in bom)
n_top = sum(1 for r, s in pl.items() if s[3] == 'T' and P[r]['kind'] != 'H' and not P[r].get('nobom') and not P[r].get('dnp'))
n_bot = sum(1 for r, s in pl.items() if s[3] == 'B' and P[r]['kind'] != 'H' and not P[r].get('nobom') and not P[r].get('dnp'))
src_count = collections.Counter(p['src'] for p in netlist.parts() if not p.get('nobom'))

# GPIO-Tabelle
DESC = {'LCD_CS': 'Display QSPI CS', 'LCD_SCK': 'Display QSPI SCK', 'LCD_D0': 'Display QSPI D0', 'LCD_D1': 'Display QSPI D1', 'LCD_D2': 'Display QSPI D2', 'LCD_D3': 'Display QSPI D3',
        'LCD_RST': 'Display Reset', 'LCD_TE': 'Display Tearing-Effect', 'SDA': 'I2C SDA (Display-Touch, Klickrad, MAX17048, TUSB320, CS43131 ueber PCA9306)', 'SCL': 'I2C SCL',
        'TP_INT': 'Touch-Interrupt Display', 'WHEEL_INT': 'Klickrad CHANGE, Weckquelle (LP-GPIO)', 'I2S_BCLK': 'I2S Bitclock vom DAC (S31 = Slave) ueber Pegelwandler U31',
        'I2S_LRCK': 'I2S Wordclock vom DAC ueber Pegelwandler U32', 'I2S_DOUT': 'I2S Daten S31 -> DAC ueber Pegelwandler U33', 'DAC_RESET': 'CS43131 RESET (Gate von Q20 mit Pull-up an 3V3: Pin offen/high = Reset, low = RESET freigegeben; Q21/Q22 halten RESET ohne 3V3 low)',
        'DAC_INT': 'CS43131 INT (aktiv low, 10 k Pull-up)', 'SD_CD': 'microSD Karte erkannt', 'SD_VDD_EN': 'microSD Versorgung (TPS22948 ON)',
        'SYS_PWR_EN': 'Power-Latch: haelt die Versorgung (LP-GPIO)', 'KEY_LOCK_MCU': 'Ein/Aus-Taster lesen (LP-GPIO, Weckquelle)', 'CHG_STAT1': 'MCP73871 STAT1',
        'CHG_STAT2': 'MCP73871 STAT2', 'CHG_PG': 'MCP73871 PG', 'CHG_SEL': 'MCP73871 SEL (hoch = USB), Pull-up 10 k', 'CHG_PROG2': 'MCP73871 PROG2 (USB-Strom), Pull-up 100 k',
        'TUSB_ID': 'TUSB320 ID (low = wir sind Quelle)', 'TUSB_INT': 'TUSB320 INT_N', 'HOST_EN': 'Host-VBUS an/aus (Boost + Schalter)', 'FG_ALRT': 'MAX17048 ALRT'}
rows = ['| Signal | S31-GPIO | Modulpad | Funktion |', '|---|---|---|---|']
for s, io in sorted(gm.items(), key=lambda kv: int(kv[1][2:])):
    rows.append('| %s | %s | %s | %s |' % (s, io, pad_of[io], DESC.get(s, '')))
fixed_rows = ['| SD_D0 ... SD_D3, SD_CLK, SD_CMD | IO35 ... IO40 | 12, 21 ... 25 | SDMMC-Slot 2 (feste Pads laut Datenblatt: SD2_CDATA0 ... SD2_CCMD) |',
              '| USB_HS_DP / USB_HS_DM | DP / DM | 55 / 54 | USB-2.0-HS-OTG, ueber R102/R103 zur USB-C-Buchse |',
              '| BOOT | IO61 | 27 | Download-Modus: Taster SW2 (Rückseite) gedrückt halten, dabei EN antippen (SW3); alternativ TP15 gegen TP17 kurzschliessen |',
              '| ESP_EN | EN | 3 | Reset: RC 10 k / 1 uF, Taster SW3 (Rückseite); alternativ TP14 gegen TP16 kurzschliessen |',
              '| UART_TX0 / UART_RX0 | TX0 / RX0 | 37 / 36 | Testpunkte TP10 / TP11 |',
              '| USBJ_DP / USBJ_DM | IO34 / IO33 | 14 / 13 | USB-Serial/JTAG, Testpunkte TP12 / TP13 |']

def at(ref):
    s = pl.get(ref)
    return '(%+.1f, %+.1f)' % (s[0], s[1]) if s else '?'

TEMPLATE = open(os.path.join(ROOT, 'tools', 'README_vorlage.md')).read()
vals = dict(
    GPIO_TABLE='\n'.join(rows), GPIO_FIXED='\n'.join(['| Signal | S31-GPIO | Modulpad | Funktion |', '|---|---|---|---|'] + fixed_rows),
    N_FREE=len(gm), N_PARTS=n_parts, N_LINES=n_lines, N_TOP=n_top, N_BOT=n_bot,
    N_TG=src_count.get('Tangara', 0), N_ANG=src_count.get('angepasst', 0), N_ESP=src_count.get('Espressif', 0), N_CIR=src_count.get('Cirrus', 0), N_NEU=src_count.get('neu', 0),
    ERC=summarize(erc), DRC=summarize(drc), STAND_ROUTING=stat.get('routing', 'siehe unten'),
    X_J20=at('J20'), X_J21=at('J21'), X_U15=at('U15'), X_J4=at('J4'), X_J6=at('J6'), X_J1=at('J1'), X_SW1=at('SW1'), X_BT1=at('BT1'), X_U17=at('U17'), X_U10=at('U10'), X_U12=at('U12'),
    X_U22=at('U22'), X_X1=at('X1'),
)
out = TEMPLATE
for k, v in vals.items(): out = out.replace('@@%s@@' % k, str(v))
left = re.findall(r'@@(\w+)@@', out)
if left: print('WARNUNG: unbelegte Platzhalter', set(left))
open(os.path.join(ROOT, 'README.md'), 'w').write(out)
print('README.md geschrieben,', len(out.splitlines()), 'Zeilen')
