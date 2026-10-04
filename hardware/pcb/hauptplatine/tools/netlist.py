"""Bauteil- und Netzliste der Hauptplatine v3 (einzige Quelle fuer Schaltplan, Platine, Stueckliste).

Herkunft der Teile (Feld "src"):
  Tangara    - 1:1 aus der Tangara-Hardware (cooltech.zone, CERN-OHL-S-2.0; Stand der .kicad_sch-Dateien, quellen/tangara_netlist_rev5.json)
  angepasst  - von Tangara uebernommen, aber geaendert (Begruendung im Feld "desc" und im README)
  Espressif  - Referenzbeschaltung aus Datenblatt/Hardware-Design-Guidelines des ESP32-S31-WROOM-1
  Cirrus     - Beschaltung des CS43131 nach Datenblatt DS1155F2, Abb. 2-1
  neu        - eigene Entwicklung, ungeprueft
"""
import json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
TG = json.load(open(os.path.join(os.path.dirname(HERE), 'quellen', 'tangara_netlist_rev5.json')))

def nn(n):
    """Tangara-Netzname -> unser Netzname."""
    if n is None: return None
    m = {'+3V3': '3V3', '+5VA': 'V5A', '-5VA': 'VN5A', 'USB.DP': 'USB_DP', 'USB.DN': 'USB_DN', 'I2C.SDA': 'SDA', 'I2C.SCL': 'SCL',
         'VBUS_SWITCHED': 'VBUS_SW', 'Net-(J7-Pin_3)': 'VBAT', 'Net-(U4-EN)': 'LDO_EN', 'Net-(SW1-C)': 'LOCK_COM',
         'Net-(U10-CE)': 'CHG_CE', 'Net-(U10-PROG1)': 'CHG_PROG1', 'Net-(U10-PROG3)': 'CHG_PROG3', 'Net-(Q1-G)': 'Q1_G',
         'CHG_PROG': 'CHG_PROG2', '~{CHG_PWR_OK}': 'CHG_PG', 'Net-(J6-CC1)': 'CC1', 'Net-(J6-CC2)': 'CC2', 'SYS_PWR_EN_SAMD': 'SYS_PWR_EN',
         '~{SD_VDD_EN}': 'SD_VDD_EN', 'Net-(J4-VDD)': 'SD_VDD', 'Net-(J4-CMD)': 'SD_CMD', 'Net-(J4-CLK)': 'SD_CLK', 'Net-(J4-DAT0)': 'SD_D0',
         'Net-(J4-DAT1)': 'SD_D1', 'Net-(J4-DAT2)': 'SD_D2', 'Net-(J4-DAT3)': 'SD_D3', 'Net-(J4-CD/DAT3)': 'SD_D3', 'SD_CD': 'SD_CD'}
    if n in m: return m[n]
    if n.startswith('unconnected-'): return None
    mm = re.match(r'Net-\((.+)\)$', n)
    if mm: return re.sub(r'[^A-Za-z0-9]+', '_', mm.group(1)).strip('_')
    return re.sub(r'[~{}]', '', n)

PARTS = []
def add(ref, value, kind, fp, pins, src, **kw):
    d = dict(ref=ref, value=value, kind=kind, fp=fp, pins=pins, src=src, at=None, near=None)
    d.update(kw)
    PARTS.append(d)
    return d
def get(ref): return [p for p in PARTS if p['ref'] == ref][0]

KIND = {'X': 'X', 'R': 'R', 'C': 'C', 'L': 'L', 'Q': 'Q', 'D': 'D', 'U': 'IC', 'J': 'CONN', 'SW': 'SW', 'TP': 'TP', 'F': 'L'}
FPMAP = {   # Tangara-Footprint -> unser Footprint
    'footprints:CUI_SJ-3506-SMT': 'Hauptplatine:CUI_SJ-3506-SMT',
    'footprints:GCT_USB4510-03-1-A_REVA': 'Hauptplatine:GCT_USB4510-03-1-A_REVA',
    'footprints:SON40P300X300X80-13N': 'Hauptplatine:SON40P300X300X80-13N',
    'footprints:SOT65P210X110-6N': 'Hauptplatine:SOT65P210X110-6N',
    'footprints:QFN-20-1EP_4x4mm_P0.5mm_EP2.5x2.5mm_ThermalVias2': 'Package_DFN_QFN:QFN-20-1EP_4x4mm_P0.5mm_EP2.5x2.5mm',
    'Package_DFN_QFN:QFN-24-1EP_4x4mm_P0.5mm_EP2.7x2.7mm_ThermalVias': 'Package_DFN_QFN:Texas_RTW_WQFN-24-1EP_4x4mm_P0.5mm_EP2.7x2.7mm',
}
MFR = {'GRM': 'Murata', 'GCM': 'Murata', 'AC0603': 'Yageo', 'RC0603': 'Yageo', 'RR1220': 'Susumu', 'TPS': 'Texas Instruments', 'INA': 'Texas Instruments',
       'MCP': 'Microchip', 'TLV': 'Texas Instruments', 'PMV': 'Nexperia', 'PJC': 'PANJIT', 'BAT54': 'Nexperia', 'PCA': 'Texas Instruments', 'SN74': 'Texas Instruments',
       '1239AS': 'Murata (TOKO)', 'D5V0': 'Diodes Inc.', 'PE1605': 'ProTek Devices', 'S3B-PH': 'JST', 'SJ-': 'Same Sky (CUI Devices)',
       'USB4510': 'GCT', 'JS102011': 'C&K', 'TUSB': 'Texas Instruments', 'CL': 'Samsung', 'B3U': 'Omron', 'CS43': 'Cirrus Logic', 'NX2016': 'NDK',
       'FH12': 'Hirose', 'BLM': 'Murata', 'MAX17': 'Analog Devices (Maxim)'}
def mfr_of(mpn):
    mpn = mpn or ''
    for k, v in MFR.items():
        if mpn.startswith(k): return v
    return ''

def pkg_of(fp):
    m = re.search(r'_(0402|0603|0805|1008|1206|1210)_', fp)
    return m.group(1) if m else ''

def tg(ref, newref=None, value=None, mpn=None, fp=None, names=None, src='Tangara', netmap=None, **kw):
    """Teil aus der Tangara-Netzliste uebernehmen."""
    c = TG[ref]
    pins, nm = {}, {}
    for p, (n, fn) in c['pins'].items():
        n2 = nn(n)
        if netmap and n in netmap: n2 = netmap[n]
        pins[p] = n2
        if fn and fn != 'None': nm[p] = fn
    fpn = fp or FPMAP.get(c['fp'], c['fp'].replace('footprints:', 'Hauptplatine:'))
    mpn = mpn or c['mpn'] or ''
    val = value or c['value'].replace('Ω', '').replace('μ', 'u')
    if ref.startswith('TP'): kind = 'TP'
    elif ref.startswith('SW'): kind = 'SW'
    else: kind = KIND.get(ref[0], 'IC')
    base = dict(mpn=mpn, mfr=mfr_of(mpn), tgref=ref, names={**nm, **(names or {})}, pkg=pkg_of(fpn)); base.update(kw)
    return add(newref or ref, val, kind, fpn, pins, src, **base)

R_TAB = {'0': ('0402WGF0000TCE', 'C17168'), '1k': ('0402WGF1001TCE', 'C11702'), '2.2k': ('0402WGF2201TCE', 'C25879'), '4.7k': ('0402WGF4701TCE', 'C25900'),
         '10k': ('0402WGF1002TCE', 'C25744'), '100k': ('0402WGF1003TCE', 'C25741')}
C_TAB = {'100nF': ('CL05B104KO5NNNC', 'C1525'), '1uF': ('CL05A105KA5NQNC', 'C52923')}
def res(ref, val, n1, n2, desc='', src='neu', **kw):
    mpn, lcsc = R_TAB.get(val, ('', ''))
    return add(ref, val, 'R', 'Resistor_SMD:R_0402_1005Metric', {'1': n1, '2': n2}, src, mpn=mpn, mfr='UNI-ROYAL' if mpn else '', lcsc=lcsc, desc=desc, pkg='0402', **kw)
def cap(ref, val, n1, n2, desc='', src='neu', fp='Capacitor_SMD:C_0402_1005Metric', mpn='', lcsc='', **kw):
    if not mpn and val in C_TAB and fp.endswith('0402_1005Metric'): mpn, lcsc = C_TAB[val]
    return add(ref, val, 'C', fp, {'1': n1, '2': n2}, src, mpn=mpn, mfr=mfr_of(mpn), lcsc=lcsc, desc=desc, pkg=pkg_of(fp), **kw)
C805 = 'Capacitor_SMD:C_0805_2012Metric'
C603 = 'Capacitor_SMD:C_0603_1608Metric'
R603 = 'Resistor_SMD:R_0603_1608Metric'

# ======================================================================================================== MCU ESP32-S31-WROOM-1
S31 = {   # Pad -> Modulname (Datenblatt ESP32-S31-WROOM-1 v0.5, Tabelle 3-1)
    '1': 'GND', '2': '3V3', '3': 'EN', '4': 'IO2', '5': 'IO3', '6': 'IO4', '7': 'IO5', '8': 'IO0', '9': 'IO1', '10': 'IO6', '11': 'IO7', '12': 'IO35',
    '13': 'IO33', '14': 'IO34', '15': 'IO20', '16': 'IO21', '17': 'IO22', '18': 'IO23', '19': 'IO24', '20': 'IO25', '21': 'IO36', '22': 'IO37',
    '23': 'IO38', '24': 'IO39', '25': 'IO40', '26': 'IO60', '27': 'IO61', '28': 'IO42', '29': 'IO43', '30': 'IO44', '31': 'IO45', '32': 'IO46',
    '33': 'IO47', '34': 'IO54', '35': 'IO55', '36': 'RX0', '37': 'TX0', '38': 'IO56', '39': 'IO57', '40': 'GND', '41': 'GND',
    '42': 'IO8', '43': 'IO9', '44': 'IO10', '45': 'IO11', '46': 'IO12', '47': 'IO13', '48': 'IO14', '49': 'IO15', '50': 'IO16', '51': 'IO17',
    '52': 'IO18', '53': 'IO19', '54': 'DM', '55': 'DP', '56': 'IO48', '57': 'IO49', '58': 'IO50', '59': 'IO51', '60': 'IO52', '61': 'IO53',
}
# Signale, die ein freies S31-GPIO bekommen (Zuordnung: tools/gpio_assign.py -> tools/gpio_map.json)
GPIO_SIGNALS = ['LCD_CS', 'LCD_SCK', 'LCD_D0', 'LCD_D1', 'LCD_D2', 'LCD_D3', 'LCD_RST', 'LCD_TE', 'SDA', 'SCL', 'TP_INT', 'WHEEL_INT',
                'I2S_BCLK', 'I2S_LRCK', 'I2S_DOUT', 'DAC_RESET', 'DAC_INT', 'SD_CD', 'SD_VDD_EN',
                'SYS_PWR_EN', 'KEY_LOCK_MCU', 'CHG_STAT1', 'CHG_STAT2', 'CHG_PG', 'CHG_SEL', 'CHG_PROG2', 'TUSB_ID', 'TUSB_INT', 'HOST_EN', 'FG_ALRT']
GPIO_MAP = {}   # Signal -> Modulname (IOx)
_gm = os.path.join(HERE, 'gpio_map.json')
if os.path.exists(_gm): GPIO_MAP = json.load(open(_gm))
_rev = {v: k for k, v in GPIO_MAP.items()}
FIXED_S31 = {'EN': 'ESP_EN', 'DP': 'USB_HS_DP', 'DM': 'USB_HS_DM', 'IO33': 'USBJ_DM', 'IO34': 'USBJ_DP', 'IO61': 'BOOT', 'TX0': 'UART_TX0', 'RX0': 'UART_RX0',
             'IO35': 'SD_D0', 'IO36': 'SD_D1', 'IO37': 'SD_D2', 'IO38': 'SD_D3', 'IO39': 'SD_CLK', 'IO40': 'SD_CMD', '3V3': '3V3', 'GND': 'GND'}
NO_GPIO = {'IO60', 'IO33', 'IO34', 'IO35', 'IO36', 'IO37', 'IO38', 'IO39', 'IO40', 'IO61'}   # nicht fuer freie Signale verwenden
s31pins = {}
for pad, name in S31.items():
    if name in FIXED_S31: s31pins[pad] = FIXED_S31[name]
    else: s31pins[pad] = _rev.get(name)
add('U15', 'ESP32-S31-WROOM-1-N16R16V', 'IC', 'Hauptplatine:ESP32-S31-WROOM-1', s31pins, 'neu', names=dict(S31), mpn='ESP32-S31-WROOM-1-N16R16V',
    mfr='Espressif', lcsc='', dk='', pkg='Modul 18 x 25,5 x 3,1',
    desc='WLAN 6, Bluetooth 5.4 (Classic + LE Audio), USB 2.0 HS OTG, 16 MB Flash, 16 MB PSRAM (Datenblatt v0.5 PRELIMINARY); Tangara: ESP32-WROVER-E',
    at=None)

# ======================================================================================================== Audio: CS43131 (Cirrus, neu) + Klinke SJ-43504
# Pinbelegung CS43131 QFN-40 laut DS1155F2 Tabelle 1-1. Ungenutzte Eingaenge (HPINA/B, DSD, CLKOUT, TSO) offen (schwache Pull-downs im Chip).
CS_NAMES = {'1': 'SCL', '2': 'SDIN1', '3': 'TSO', '4': 'VD', '5': 'FILT+', '6': 'FILT-', '7': 'VA', '8': 'GNDA', '9': '-VA', '10': 'FLYP_VA', '11': 'FLYN_VA',
            '12': 'HPINA', '13': 'HPREFA', '14': 'HPOUTA', '15': 'HPINB', '16': 'HPOUTB', '17': 'HPREFB', '18': 'VCP_FILT-', '19': 'GNDCP', '20': 'FLYN_VCP',
            '21': 'VCP_FILT+', '22': 'HP_DETECT', '23': 'FLYC_VCP', '24': 'FLYP_VCP', '25': 'VCP', '26': 'VP', '27': 'INT', '28': 'RESET', '29': 'DSDB/LRCK2',
            '30': 'ADR', '31': 'VL', '32': 'DSDCLK/SCLK2', '33': 'CLKOUT', '34': 'SCLK1', '35': 'GNDD', '36': 'XTO', '37': 'XTI/MCLK', '38': 'LRCK1',
            '39': 'SDA', '40': 'DSDA/SDIN2', '41': 'EP'}
CS_PINS = {'1': 'DAC_SCL', '2': 'I2S_DIN_1V8', '3': None, '4': 'V1P8', '5': 'FILTP', '6': 'FILTN', '7': 'V1P8A', '8': 'GND', '9': 'NVA', '10': 'FLYPVA', '11': 'FLYNVA',
           '12': None, '13': 'HPREFA', '14': 'HPOUTA', '15': None, '16': 'HPOUTB', '17': 'HPREFB', '18': 'VCPFN', '19': 'GND', '20': 'FLYNVCP',
           '21': 'VCPFP', '22': 'HP_DETECT', '23': 'FLYCVCP', '24': 'FLYPVCP', '25': 'V1P8A', '26': 'SYS_POWER', '27': 'DAC_INT', '28': 'DAC_RESET_N', '29': None,
           '30': 'GND', '31': 'V1P8', '32': None, '33': None, '34': 'I2S_BCLK_1V8', '35': 'GND', '36': 'XTO', '37': 'XTI', '38': 'I2S_LRCK_1V8',
           '39': 'DAC_SDA', '40': None, '41': 'GND'}
add('U17', 'CS43131-CNZR', 'IC', 'Package_DFN_QFN:QFN-40-1EP_5x5mm_P0.4mm_EP3.6x3.6mm', CS_PINS, 'neu', names=CS_NAMES, mpn='CS43131-CNZR', mfr='Cirrus Logic',
    dk='598-CS43131-CNZRCT-ND', pkg='QFN-40 5 x 5', desc='DAC mit Class-H-Kopfhoererverstaerker (125 dB DNR an 32 Ohm), I2C, I2S-Master (statt Tangara WM8523 + INA1620 + TPS65133)')
# Entkopplung nach Abb. 2-1 (Zuordnung der Werte aus dem Bild gelesen, vor Bestellung im Layout-Review pruefen)
cap('C240', '100nF', 'V1P8', 'GND', 'VL', src='Cirrus')
cap('C241', '100nF', 'V1P8', 'GND', 'VD', src='Cirrus')
cap('C242', '100nF', 'V1P8A', 'GND', 'VA', src='Cirrus')
cap('C243', '2.2uF', 'V1P8A', 'GND', 'VA (X5R, 6,3 V)', src='Cirrus', mpn='GRM155R60J225ME15D', lcsc='')
cap('C244', '2.2uF', 'NVA', 'GND', '-VA (negative Ladungspumpe)', src='Cirrus', mpn='GRM155R60J225ME15D')
cap('C245', '15uF', 'FILTP', 'GND', 'FILT+ (X5R)', src='Cirrus', fp=C603, mpn='(15 uF X5R >= 6,3 V 0603, Typ nach Verfuegbarkeit)')
cap('C246', '15uF', 'FILTN', 'GND', 'FILT- (X5R)', src='Cirrus', fp=C603, mpn='(15 uF X5R >= 6,3 V 0603, Typ nach Verfuegbarkeit)')
cap('C247', '2.2uF', 'FLYPVA', 'FLYNVA', 'Fliegender Kondensator -VA', src='Cirrus', mpn='GRM155R60J225ME15D')
cap('C248', '2.2uF', 'V1P8A', 'GND', 'VCP', src='Cirrus', mpn='GRM155R60J225ME15D')
cap('C249', '2.2uF', 'VCPFP', 'GND', 'VCP_FILT+', src='Cirrus', mpn='GRM155R60J225ME15D')
cap('C250', '2.2uF', 'VCPFN', 'GND', 'VCP_FILT-', src='Cirrus', mpn='GRM155R60J225ME15D')
cap('C251', '2.2uF', 'FLYPVCP', 'FLYCVCP', 'Fliegender Kondensator -VCP (1)', src='Cirrus', mpn='GRM155R60J225ME15D')
cap('C252', '2.2uF', 'FLYCVCP', 'FLYNVCP', 'Fliegender Kondensator -VCP (2)', src='Cirrus', mpn='GRM155R60J225ME15D')
cap('C253', '100nF', 'SYS_POWER', 'GND', 'VP', src='Cirrus')
cap('C254', '4.7uF', 'SYS_POWER', 'GND', 'VP (X5R)', src='Cirrus', fp=C603, mpn='GRM188R60J475KE19D')
add('FB1', 'BLM15 120R', 'L', 'Inductor_SMD:L_0402_1005Metric', {'1': 'V1P8', '2': 'V1P8A'}, 'Cirrus', mpn='BLM15AG121SN1D', mfr='Murata', pkg='0402',
    desc='Ferritperle: VA/VCP vom digitalen 1,8-V-Zweig trennen (Datenblatt Abschnitt 8.1: VA, VCP aus sauberer Versorgung)')
# Takt: Quarz 22,5792 MHz direkt am DAC, DAC = I2S-Master. Zweiter Quarz 24,576 MHz als DNP-Option, Umschaltung per 0-Ohm-Bruecke (Bestueckungsoption)
add('X1', '22.5792MHz', 'X', 'Crystal:Crystal_SMD_2016-4Pin_2.0x1.6mm', {'1': 'XTAL1', '2': 'GND', '3': 'XTAL2', '4': 'GND'}, 'Cirrus', mpn='NX2016SA 22.5792M EXS00A-CS09116', mfr='NDK',
    pkg='2,0 x 1,6', desc='Quarz 22,5792 MHz, Last 8 pF, laut CS43131 Tab. 5-1 geeignet; Register 0x20052 = 0x02')
add('X2', '24.576MHz', 'X', 'Crystal:Crystal_SMD_2016-4Pin_2.0x1.6mm', {'1': 'XTAL3', '2': 'GND', '3': 'XTAL4', '4': 'GND'}, 'neu', mpn='NX2016SA 24.576M EXS00A-CS09117', mfr='NDK',
    pkg='2,0 x 1,6', dnp=True, desc='Optionaler Quarz 24,576 MHz fuer die 48-kHz-Familie (DNP); dann R241/R242 statt R240/R243 bestuecken (AUDIO.md 5.3)')
res('R240', '0', 'XTAL1', 'XTI', 'Quarz 22,5792 MHz an XTI', src='neu')
res('R241', '0', 'XTAL2', 'XTO', 'Quarz 22,5792 MHz an XTO', src='neu')
res('R242', '0', 'XTAL3', 'XTI', 'Quarz 24,576 MHz an XTI (DNP)', src='neu', dnp=True)
res('R243', '0', 'XTAL4', 'XTO', 'Quarz 24,576 MHz an XTO (DNP)', src='neu', dnp=True)
cap('C255', '10pF', 'XTI', 'GND', 'Quarz-Lastkondensator C0G (nach Abschnitt 5.3 abstimmen)', src='Cirrus', mpn='GRM1555C1H100JA01D')
cap('C256', '10pF', 'XTO', 'GND', 'Quarz-Lastkondensator C0G', src='Cirrus', mpn='GRM1555C1H100JA01D')
# Steuerung: RESET liegt in der VP-Domaene (Pegel relativ VP, bis 5 V) -> Transistor-Pegelwandler, RESET bleibt bei fehlender MCU-Ansteuerung aktiv
add('Q20', '2N7002T', 'Q', 'Package_TO_SOT_SMD:SOT-523', {'1': 'DAC_RESET', '2': 'GND', '3': 'DAC_RESET_N'}, 'neu', names={'1': 'G', '2': 'S', '3': 'D'},
    mpn='2N7002T-7-F', mfr='Diodes Inc.', pkg='SOT-523', qtype='N',
    desc='DAC-RESET: S31 setzt DAC_RESET = 0 -> Transistor aus -> RESET hoch (Betrieb); Pull-up am Gate haelt den DAC im Reset, solange der S31 den Pin nicht treibt')
res('R244', '100k', '3V3', 'DAC_RESET', 'Gate-Pull-up: DAC im Reset bis der S31 ihn loslaesst', src='neu')
res('R245', '100k', 'SYS_POWER', 'DAC_RESET_N', 'RESET-Pull-up an VP', src='neu')
res('R246', '10k', '3V3', 'DAC_INT', 'INT Pull-up (open drain, VP-Domaene, 3V3 erlaubt)', src='neu')
# I2C: DAC arbeitet mit VL = 1,8 V, der Bus der Platine mit 3,3 V -> PCA9306 als Pegelwandler
add('U30', 'PCA9306DCUR', 'IC', 'Package_SO:VSSOP-8_2.3x2mm_P0.5mm', {'1': 'GND', '2': 'V1P8', '3': 'DAC_SCL', '4': 'DAC_SDA', '5': 'SDA', '6': 'SCL', '7': '3V3', '8': 'PCA_EN'}, 'neu',
    names={'1': 'GND', '2': 'VREF1', '3': 'SCL1', '4': 'SDA1', '5': 'SDA2', '6': 'SCL2', '7': 'VREF2', '8': 'EN'}, mpn='PCA9306DCUR', mfr='Texas Instruments', pkg='VSSOP-8 2,3 x 2,0',
    desc='I2C-Pegelwandler 1,8 V (DAC) <-> 3,3 V (Bus); EN ueber 200 k an VREF2 (Datenblatt)')
res('R247', '200k', '3V3', 'PCA_EN', 'EN-Pull-up PCA9306 (200 k laut Datenblatt)', src='neu')
res('R248', '4.7k', 'V1P8', 'DAC_SDA', 'I2C-Pull-up 1,8-V-Seite', src='neu')
res('R249', '4.7k', 'V1P8', 'DAC_SCL', 'I2C-Pull-up 1,8-V-Seite', src='neu')
cap('C257', '100nF', '3V3', 'GND', 'PCA9306 VREF2', src='neu')
# I2S: die DAC-Pins arbeiten mit VL = 1,8 V -> SN74AXC1T45 je Signal (A = 1,8 V, B = 3,3 V)
for ref, a, b, dirn, d in (('U31', 'I2S_BCLK_1V8', 'I2S_BCLK', 'V1P8', 'BCLK: DAC (Master) -> S31'), ('U32', 'I2S_LRCK_1V8', 'I2S_LRCK', 'V1P8', 'LRCK: DAC -> S31'),
                           ('U33', 'I2S_DIN_1V8', 'I2S_DOUT', 'GND', 'Daten: S31 -> DAC')):
    add(ref, 'SN74AXC1T45DRL', 'IC', 'Package_TO_SOT_SMD:SOT-563', {'1': 'V1P8', '2': 'GND', '3': a, '4': b, '5': dirn, '6': '3V3'}, 'neu',
        names={'1': 'VCCA', '2': 'GND', '3': 'A', '4': 'B', '5': 'DIR', '6': 'VCCB'}, mpn='SN74AXC1T45DRLR', mfr='Texas Instruments', pkg='SOT-563', desc='Pegelwandler 1,8 V <-> 3,3 V, ' + d)
cap('C258', '100nF', '3V3', 'GND', 'VCCB der Pegelwandler U31/U32/U33', src='neu')
cap('C259', '100nF', '3V3', 'GND', 'VCCB der Pegelwandler U31/U32/U33', src='neu')
# 1,8-V-LDO (rauscharm, 500 mA) aus 3V3
add('U34', 'TLV75518PDRV', 'IC', 'Package_SON:WSON-6-1EP_2x2mm_P0.65mm_EP1x1.6mm', {'1': 'V1P8', '2': None, '3': 'GND', '4': '3V3', '5': None, '6': '3V3', '7': 'GND'}, 'neu',
    names={'1': 'OUT', '2': 'NC', '3': 'GND', '4': 'EN', '5': 'NC', '6': 'IN', '7': 'EP'}, mpn='TLV75518PDRVR', mfr='Texas Instruments', pkg='WSON-6 2 x 2',
    desc='1,8-V-LDO fuer VL/VD/VA/VCP des CS43131 (ca. 20 mA typ., 60 mA Reserve), rauscharm, gleiche Familie wie U4 (TLV757P)')
cap('C260', '1uF', '3V3', 'GND', 'LDO Eingang', src='neu')
cap('C261', '2.2uF', 'V1P8', 'GND', 'LDO Ausgang', src='neu', mpn='GRM155R60J225ME15D')
cap('C262', '100nF', 'V1P8', 'GND', 'Entkopplung 1,8 V', src='neu')
# Klinke SJ-43504-SMT-TR: 1 Huelse, 2 Spitze (links), 3 Ring 1 (rechts), 4 Ring 2, 5 Spitzenschalter, 6 Ringschalter. TRS-Stecker schliesst 1 und 4 kurz -> beide als Referenz (HPREFA/B einzeln gefuehrt)
add('J1', 'SJ-43504-SMT-TR', 'CONN', 'Hauptplatine:CUI_SJ-43504-SMT-TR', {'1': 'HPREFA', '2': 'HPOUTA', '3': 'HPOUTB', '4': 'HPREFB', '5': 'HP_DETECT', '6': None}, 'angepasst',
    names={'1': 'SLEEVE', '2': 'TIP', '3': 'RING1', '4': 'RING2', '5': 'TIP_SW', '6': 'RING1_SW'}, mpn='SJ-43504-SMT-TR', mfr='Same Sky (CUI Devices)', pkg='3,5 mm 4-polig, 5,0 mm hoch',
    dk='', desc='Klinke 5,0 mm hoch (Tangara: SJ-3506-SMT, 6,0 mm), Mid-Mount im Randausschnitt der Platine, Pads auf der Rueckseite; Spitzenschalter -> HP_DETECT (HPDETECT_INV im DAC setzen)')
# HPREFA/HPREFB werden einzeln bis zum Buchsenpin gefuehrt und dort ueber einen Net-Tie (Kupferbruecke) mit der Massefläche verbunden (Datenblatt 8.3)
for ref, net, pinn in (('NT1', 'HPREFA', 'HPREFA (DAC-Pin 13) -> Buchse Pin 1'), ('NT2', 'HPREFB', 'HPREFB (DAC-Pin 17) -> Buchse Pin 4')):
    add(ref, 'NetTie', 'X', 'NetTie:NetTie-2_SMD_Pad0.5mm', {'1': net, '2': 'GND'}, 'Cirrus', nobom=True, nettie=True, names={'1': 'REF', '2': 'GND'},
        desc='Net-Tie: verbindet ' + pinn + ' an der Buchse mit GND (eigene Leitung je Kanal, Massepunkt an der Buchse)')
# ESD wie Tangara
tg('U3', netmap={'Net-(C17-Pad2)': 'HPOUTA', 'Net-(C19-Pad2)': 'HPOUTB'}, desc='ESD-Schutz Kopfhoerer-Ausgaenge (Tangara 1:1, Netze angepasst)')

# ======================================================================================================== Power (Tangara)
tg('J6', names={'A1_B12': 'GND', 'B1_A12': 'GND', 'A4_B9': 'VBUS', 'B4_A9': 'VBUS', 'A5': 'CC1', 'B5': 'CC2', 'A6': 'DP', 'B6': 'DP', 'A7': 'DN', 'B7': 'DN', 'A8': 'SBU1', 'B8': 'SBU2'})
tg('U10')
for ref in ['C24', 'C25', 'C27', 'R34', 'R35', 'R37', 'R38', 'R39', 'R41', 'R1', 'TP7', 'Q1', 'C37', 'R7', 'D4']:
    tg(ref)
tg('C29', src='Tangara')
tg('U5')
# Akku: 3 Loetpads fuer die Litzen des Pouch-Akkus (Stecker waere zu hoch fuer 3,3 mm Rueckzone neben dem Akku)
add('BT1', 'Akku 3-pol.', 'CONN', 'Hauptplatine:BATT_PADS_3', {'1': 'NTC', '2': 'GND', '3': 'VBAT'}, 'angepasst', nobom=True, names={'1': 'NTC', '2': 'GND', '3': 'BAT+'},
    desc='Loetpads 1 NTC, 2 GND, 3 BAT+ fuer die Litzen des Pouch-Akkus (303450, mit Schutzschaltung); Tangara: JST-PH-Stecker J7')
add('U4', 'TLV75733PDRV', 'IC', 'Package_SON:WSON-6-1EP_2x2mm_P0.65mm_EP1x1.6mm', {'1': '3V3', '2': None, '3': 'GND', '4': 'LDO_EN', '5': None, '6': 'SYS_POWER', '7': 'GND'}, 'angepasst',
    names={'1': 'OUT', '2': 'NC', '3': 'GND', '4': 'EN', '5': 'NC', '6': 'IN', '7': 'EP'}, mpn='TLV75733PDRVR', mfr='Texas Instruments', pkg='WSON-6 2 x 2',
    desc='3V3-LDO 1 A (Tangara: TLV75533PDBV, 500 mA) im flachen WSON-6 (0,8 mm), Pinbelegung DRV nach Datenblatt SBVS322C; Spitzen bis ca. 375 mA S31-Senden + Display + DAC-LDO', tgref='U4')
# Tangara: Schiebeschalter SW1 (KEY_LOCK, Hold/Power) + SAMD21 haelt SYS_PWR_EN. Hier: Ein/Aus-Taster, der S31 haelt die Versorgung ueber SYS_PWR_EN (BAT54C D4)
add('SW1', 'B3U-3000P', 'SW', 'Button_Switch_SMD:SW_SPST_B3U-3000P', {'1': 'LOCK_COM', '2': 'KEY_LOCK'}, 'angepasst', mpn='B3U-3000P', mfr='Omron', lcsc='C963349',
    pkg='3,0 x 2,5 x 1,2', desc='Ein/Aus-Taster statt Schiebeschalter JS102011SAQN (Tangara): drueckt SYS_POWER auf KEY_LOCK -> LDO_EN')
tg('R4', value='10k', mpn='AC0603JR-0710KL', src='angepasst', desc='Taster-Vorwiderstand (Tangara: 100 k); bei Tastendruck KEY_LOCK ca. 0,9 x SYS_POWER')
add('R200', '100k', 'R', R603, {'1': 'KEY_LOCK', '2': 'GND'}, 'neu', mpn='AC0603FR-07100KL', mfr='Yageo', pkg='0603', desc='KEY_LOCK Pull-down (Taster offen = low)')
add('R201', '10k', 'R', R603, {'1': 'KEY_LOCK', '2': 'KEY_LOCK_MCU'}, 'neu', mpn='AC0603JR-0710KL', mfr='Yageo', pkg='0603', desc='Serienwiderstand zum S31-GPIO (SYS_POWER bis 5 V, GPIO 3,3 V)')
add('R202', '100k', 'R', R603, {'1': 'SYS_PWR_EN', '2': 'GND'}, 'neu', mpn='AC0603FR-07100KL', mfr='Yageo', pkg='0603', desc='SYS_PWR_EN Pull-down (Latch faellt, wenn S31 aus)')
add('R36', '100k', 'R', R603, {'1': '3V3', '2': 'CHG_PROG2'}, 'angepasst', mpn='AC0603FR-07100KL', mfr='Yageo', pkg='0603',
    desc='PROG2 hoch = USB-Eingangslimit 500 mA (Tangara: Pin vom SAMD21 gesteuert); hier Pull-up an 3V3, S31 kann ueberschreiben')
add('R43', '10k', 'R', R603, {'1': '3V3', '2': 'CHG_SEL'}, 'angepasst', mpn='AC0603JR-0710KL', mfr='Yageo', pkg='0603', desc='SEL hoch = USB-Eingang (Tangara Rev. 4)')

# ======================================================================================================== Peripherie (Tangara)
add('J4', 'microSD', 'CONN', 'Connector_Card:microSD_HC_Molex_104031-0811',
    {'1': 'SD_D2', '2': 'SD_D3', '3': 'SD_CMD', '4': 'SD_VDD', '5': 'SD_CLK', '6': 'GND', '7': 'SD_D0', '8': 'SD_D1', '9': 'SD_CD', '10': 'GND', '11': 'GND'},
    'angepasst', names={'1': 'DAT2', '2': 'DAT3', '3': 'CMD', '4': 'VDD', '5': 'CLK', '6': 'VSS', '7': 'DAT0', '8': 'DAT1', '9': 'CD', '10': 'CD_COM', '11': 'SHIELD'},
    mpn='104031-0811', mfr='Molex', dk='WM6357DKR-ND', pkg='microSD Push-Push',
    desc='microSD statt Vollformat-SD (Tangara: Hirose DM1AA-SF-PEJ(82)); SDMMC 4 Bit direkt am S31 (IO35...IO40) statt SPI + Multiplexer')
tg('U16', names={'1': 'IN', '2': 'GND', '3': 'ON', '4': 'NC', '5': 'FLT', '6': 'OUT'})
for ref in ['R9', 'R11', 'R12', 'R57', 'R61', 'C42']: tg(ref)
for ref in ['C30', 'C32', 'C34', 'C35', 'C23']: tg(ref)

# ======================================================================================================== Espressif-Beschaltung
res('R100', '10k', '3V3', 'ESP_EN', 'EN-Pull-up (Espressif: RC-Verzoegerung 10 k / 1 uF)', src='Espressif')
cap('C100', '1uF', 'ESP_EN', 'GND', 'EN-Kondensator (Espressif: RC 10 k / 1 uF)', src='Espressif')
cap('C101', '22uF', '3V3', 'GND', 'Espressif: 22 uF am Modul-3V3', src='Espressif', fp=C805, mpn='CL21A226MAQNNNE', lcsc='C45783')
cap('C102', '100nF', '3V3', 'GND', 'Espressif: 100 nF am Modul-3V3', src='Espressif')
res('R101', '10k', '3V3', 'BOOT', 'GPIO61 Pull-up (definierter Strapping-Pegel)', src='Espressif')
cap('C103', '100nF', 'BOOT', 'GND', 'Entprellung/Filter BOOT', src='Espressif')
res('R102', '0', 'USB_DP', 'USB_HS_DP', 'USB-HS D+: Platz fuer Serienwiderstand (Anfangswert 0 Ohm)', src='Espressif')
res('R103', '0', 'USB_DN', 'USB_HS_DM', 'USB-HS D-: Platz fuer Serienwiderstand', src='Espressif')
# Testpunkte: EN und BOOT (mit Pinzette gegen den benachbarten GND-Punkt kurzschliessen), UART, USB-Serial/JTAG
for ref, net, nm in [('TP10', 'UART_TX0', 'TX0'), ('TP11', 'UART_RX0', 'RX0'), ('TP12', 'USBJ_DP', 'IO34 USB-JTAG D+'), ('TP13', 'USBJ_DM', 'IO33 USB-JTAG D-'),
                     ('TP14', 'ESP_EN', 'EN (gegen TP16 kurzschliessen = Reset)'), ('TP15', 'BOOT', 'BOOT (gegen TP17 kurzschliessen = Download-Modus)'),
                     ('TP16', 'GND', 'GND neben EN'), ('TP17', 'GND', 'GND neben BOOT')]:
    add(ref, nm, 'TP', 'TestPoint:TestPoint_Pad_D1.0mm', {'1': net}, 'Espressif', nobom=True, desc='Testpunkt Programmierung/Debug')
res('R120', '2.2k', '3V3', 'SDA', 'I2C Pull-up (Klickrad-Modul bestueckt keine)')
res('R121', '2.2k', '3V3', 'SCL', 'I2C Pull-up')

# ======================================================================================================== Fuel Gauge
add('U22', 'MAX17048G+T10', 'IC', 'Package_DFN_QFN:TDFN-8-1EP_2x2mm_P0.5mm_EP0.8x1.2mm',
    {'1': 'GND', '2': 'VBAT', '3': 'VBAT', '4': 'GND', '5': 'FG_ALRT', '6': 'GND', '7': 'SCL', '8': 'SDA', '9': 'GND'}, 'neu',
    names={'1': 'CTG', '2': 'CELL', '3': 'VDD', '4': 'GND', '5': 'ALRT', '6': 'QSTRT', '7': 'SCL', '8': 'SDA', '9': 'EP'},
    mpn='MAX17048G+T10', mfr='Analog Devices (Maxim)', lcsc='C2682616', dk='MAX17048G+T10CT-ND', pkg='TDFN-8 2x2',
    desc='Fuel Gauge 1S LiPo, I2C 0x36 (Tangara: Spannungsteiler Q2/R50/R51 + ADC)')
cap('C104', '100nF', 'VBAT', 'GND', 'MAX17048 VDD')
res('R122', '10k', '3V3', 'FG_ALRT', 'ALRT Pull-up (open drain)')

# ======================================================================================================== USB-C Dual-Role + Host-VBUS: EIGENE ENTWICKLUNG, UNGEPRUEFT
add('U12', 'TUSB320LAI', 'IC', 'Hauptplatine:X2QFN-12-RWB',
    {'1': 'CC1', '2': 'CC2', '3': None, '4': 'TUSB_VBUSDET', '5': 'GND', '6': 'TUSB_INT', '7': 'SDA', '8': 'SCL', '9': 'TUSB_ID', '10': 'GND', '11': 'GND', '12': '3V3'},
    'neu', names={'1': 'CC1', '2': 'CC2', '3': 'PORT', '4': 'VBUS_DET', '5': 'ADDR', '6': 'INT_N/OUT3', '7': 'SDA/OUT1', '8': 'SCL/OUT2', '9': 'ID', '10': 'GND', '11': 'EN_N', '12': 'VDD'},
    mpn='TUSB320LAIRWBR', mfr='Texas Instruments', lcsc='C132554', dk='296-TUSB320LAIRWBRCT-ND', pkg='X2QFN-12 1,6 x 1,6',
    desc='USB-C DRP-Controller, I2C 0x47 (ADDR=GND), ersetzt Tangara BD91N01NUX (nur Sink)')
res('R110', '887k', 'VBUS', 'TUSB_VBUSDET', 'VBUS_DET: ca. 900 k in Reihe laut Datenblatt (887 k E96)')
get('R110').update(mpn='', desc='VBUS_DET: ca. 900 k in Reihe laut Datenblatt (887 k E96; 0402)')
cap('C110', '100nF', '3V3', 'GND', 'TUSB320 VDD')
res('R111', '10k', '3V3', 'TUSB_INT', 'INT_N Pull-up')
res('R112', '100k', '3V3', 'TUSB_ID', 'ID Pull-up (open drain, low = Geraet angeschlossen, wir sind Quelle)')
tg('D4', newref='D10', src='neu', desc='Entkopplung ID -> Gate-Knoten (Totbatterie: ID ohne 3V3 hochohmig)')
get('D10')['pins'] = {'1': 'Q1_GN', '2': None, '3': 'TUSB_ID'}
res('R113', '100k', 'VBUS', 'Q1_GN', 'Gate-Knoten Hilfs-Transistor Q10: Pull-up an VBUS (funktioniert ohne 3V3)')
add('Q10', '2N7002T', 'Q', 'Package_TO_SOT_SMD:SOT-523', {'1': 'Q1_GN', '2': 'GND', '3': 'Q1_G'}, 'neu', names={'1': 'G', '2': 'S', '3': 'D'},
    mpn='2N7002T-7-F', mfr='Diodes Inc.', pkg='SOT-523', desc='zieht Q1-Gate nach GND (Sink-Betrieb); aus, wenn ID low (Host)', qtype='N')
res('R114', '100k', 'VBUS', 'Q1_G', 'Q1-Gate Pull-up an VBUS (Q1 aus im Host-Betrieb)')
add('Q11', '2N7002T', 'Q', 'Package_TO_SOT_SMD:SOT-523', {'1': 'TUSB_ID', '2': 'GND', '3': 'HOST_EN'}, 'neu', names={'1': 'G', '2': 'S', '3': 'D'},
    mpn='2N7002T-7-F', mfr='Diodes Inc.', pkg='SOT-523', desc='invertiert ID -> HOST_EN', qtype='N')
res('R115', '10k', '3V3', 'HOST_EN', 'HOST_EN Pull-up (S31 kann per GPIO nach GND ziehen = Host aus)')
add('U20', 'TPS61023DRL', 'IC', 'Package_TO_SOT_SMD:SOT-563', {'1': 'BOOST_FB', '2': 'HOST_EN', '3': 'SYS_POWER', '4': 'GND', '5': 'BOOST_SW', '6': 'V5_HOST'}, 'neu',
    names={'1': 'FB', '2': 'EN', '3': 'VIN', '4': 'GND', '5': 'SW', '6': 'VOUT'}, mpn='TPS61023DRLR', mfr='Texas Instruments', lcsc='C919459', dk='296-TPS61023DRLRCT-ND',
    pkg='SOT-563', desc='Boost 5,1 V aus SYS_POWER (Schalterstrom 3,7 A)')
add('L20', '1uH', 'L', 'Inductor_SMD:L_0805_2012Metric', {'1': 'SYS_POWER', '2': 'BOOST_SW'}, 'neu', mpn='DFE201610E-1R0M=P2', mfr='Murata', pkg='2016',
    desc='1 uH 2,0 x 1,6 x 1,0 mm (TPS61023 Tab. 8-2: Saettigungsstrom >= 3 A!); Typ und Landmuster (hier L_0805 als Naeherung) vor Bestellung pruefen')
res('R116', '390k', 'V5_HOST', 'BOOST_FB', 'FB-Teiler: 0,595 V x (1 + 390k/51k) = 5,15 V')
res('R117', '51k', 'BOOST_FB', 'GND', 'FB-Teiler')
cap('C111', '10uF', 'SYS_POWER', 'GND', 'Boost Eingang', fp=C805, mpn='GRM21BR61C106KE15K')
cap('C112', '22uF', 'V5_HOST', 'GND', 'Boost Ausgang (25 V X5R)', fp=C805, mpn='CL21A226MAQNNNE', lcsc='C45783')
cap('C113', '10uF', 'V5_HOST', 'GND', 'Boost Ausgang', fp=C805, mpn='GRM21BR61C106KE15K')
add('U21', 'TPS2553DRV', 'IC', 'Package_SON:WSON-6-1EP_2x2mm_P0.65mm_EP1x1.6mm', {'1': 'VBUS', '2': 'HOST_ILIM', '3': 'HOST_FLT', '4': 'HOST_EN', '5': 'GND', '6': 'V5_HOST', '7': 'GND'}, 'neu',
    names={'1': 'OUT', '2': 'ILIM', '3': 'FAULT', '4': 'EN', '5': 'GND', '6': 'IN', '7': 'PAD'}, mpn='TPS2553DRVR', mfr='Texas Instruments', pkg='WSON-6 2 x 2',
    desc='Lastschalter mit Strombegrenzung (49,9 k = ca. 520 mA), WSON-Gehaeuse 0,8 mm hoch (Pinbelegung nach Datenblatt SLVS...)')
res('R118', '49.9k', 'HOST_ILIM', 'GND', 'Stromlimit ca. 520 mA (Datenblatt: IOS 490-550 mA bei 49,9 k)')
cap('C114', '100nF', 'V5_HOST', 'GND', 'TPS2553 IN')
res('R119', '10k', '3V3', 'HOST_FLT', 'FAULT Pull-up (open drain)')

# ======================================================================================================== Display (2,06" AMOLED 410 x 502, CO5300, QSPI, FPC 30 Pin 0,5 mm)
# Belegung aus dem Waveshare-Schaltplan ESP32-S3-Touch-AMOLED-2.06 V1.0, Stecker J3 (30 Pin + 4 Halter 31...34); MIPI-Pins (18, 20, 22, 24, 26, 28) liegen dort auf Masse
FPC_PINS = {'1': 'GND', '2': 'GND', '3': 'SCL', '4': 'LCD_SCK', '5': 'SDA', '6': 'LCD_CS', '7': 'TP_INT', '8': 'LCD_D3', '9': 'TP_RST', '10': 'LCD_D2',
            '11': '3V3', '12': 'LCD_D1', '13': None, '14': 'LCD_D0', '15': 'LCD_IM1', '16': 'GND', '17': 'LCD_IM0', '18': 'GND', '19': 'LCD_RST', '20': 'GND',
            '21': 'LCD_PWR_EN', '22': 'GND', '23': '3V3', '24': 'GND', '25': '3V3', '26': 'GND', '27': 'LCD_TE', '28': 'GND', '29': '3V3', '30': '3V3', 'MP': 'GND'}
FPC_NAMES = {'1': 'GND', '2': 'GND', '3': 'TP_SCL', '4': 'QSPI_SCL', '5': 'TP_SDA', '6': 'LCD_CS', '7': 'TP_INT', '8': 'QSPI_SIO3', '9': 'TP_RESET', '10': 'QSPI_SIO2',
             '11': 'TP_VDD', '12': 'QSPI_SIO1', '13': 'NC', '14': 'QSPI_SIO0', '15': 'IM1', '16': 'GND', '17': 'IM0', '18': 'MIPI_CLKP', '19': 'LCD_RESET', '20': 'MIPI_CLKN',
             '21': 'DSI_PWR_EN', '22': 'NC', '23': 'VCI', '24': 'MIPI_D0P', '25': 'VDDIO', '26': 'MIPI_D0N', '27': 'LCD_TE', '28': 'NC', '29': '3V3', '30': '3V3', 'MP': 'SHIELD'}
add('J20', 'FH12-30S-0.5SH(55)', 'CONN', 'Connector_FFC-FPC:Hirose_FH12-30S-0.5SH_1x30-1MP_P0.50mm_Horizontal', FPC_PINS, 'neu', names=FPC_NAMES,
    mpn='FH12-30S-0.5SH(55)', mfr='Hirose', pkg='FPC 30 Pin 0,5 mm, 1,0 mm hoch',
    desc='Display-FPC-Stecker, 30 Pin 0,5 mm (Waveshare 2,06"-Board J3); Typ (Kontaktseite oben/unten, FPC-Dicke) gegen das gekaufte Panel pruefen')
res('R130', '10k', '3V3', 'LCD_IM1', 'Display IM1 = 1 (Waveshare R27)')
res('R131', '10k', 'LCD_IM0', 'GND', 'Display IM0 = 0 (Waveshare R28)')
res('R132', '10k', '3V3', 'TP_RST', 'Touch-Reset hoch (immer aus dem Reset; Waveshare: GPIO9)')
res('R134', '4.7k', '3V3', 'LCD_PWR_EN', 'FPC-Pin 21 (Waveshare DSI_PWR_EN) fest high')
res('R135', '100k', '3V3', 'LCD_RST', 'Reset-Pull-up Display')
cap('C130', '10uF', '3V3', 'GND', 'Display-Versorgung VCI/VDDIO (Waveshare C27)', mpn='GRM155R60J106ME05D')
cap('C131', '100nF', '3V3', 'GND', 'Display-Versorgung VCI/VDDIO (Waveshare C28)')
cap('C132', '10uF', '3V3', 'GND', 'Touch-Versorgung (Waveshare C25)', mpn='GRM155R60J106ME05D')
cap('C133', '100nF', '3V3', 'GND', 'Touch-Versorgung (Waveshare C24)')

# ======================================================================================================== Klickrad-Anschluss (FFC 6 Pin 0,5 mm wie hardware/pcb/klickrad)
add('J21', 'FH12-6S-0.5SH(55)', 'CONN', 'Connector_FFC-FPC:Hirose_FH12-6S-0.5SH_1x06-1MP_P0.50mm_Horizontal',
    {'1': '3V3', '2': 'GND', '3': 'SDA', '4': 'SCL', '5': 'WHEEL_INT', '6': None, 'MP': 'GND'}, 'neu',
    names={'1': '3V3', '2': 'GND', '3': 'SDA', '4': 'SCL', '5': 'CHANGE', '6': 'Reserve', 'MP': 'MP'},
    mpn='FH12-6S-0.5SH(55)', mfr='Hirose', pkg='FFC 6 Pin 0,5 mm, 1,0 mm hoch',
    desc='Klickrad-Modul v2 (AT42QT2120 0x1C + DRV2605L 0x5A), gleicher Stecker wie auf hardware/pcb/klickrad (J1); Pin 5 = CHANGE, Pin 6 = Reserve')
res('R136', '10k', '3V3', 'WHEEL_INT', 'Pull-up CHANGE (open drain, aktiv low)')
for i, (hx, hy) in enumerate(((-16.0, 40.0), (16.0, 40.0), (16.2, -39.5), (-16.8, 24.5))):
    add(f'H{i+1}', 'M1.6', 'H', 'Hauptplatine:MountingHole_1.8mm', {}, 'neu', nobom=True, hole_at=(hx, hy),
        desc='Gehaeuse-Befestigung M1,6 (NPTH 1,8 mm), Position zur Abstimmung mit dem CAD')

# 0805-Kondensatoren -> 0603 (Oberseite darf nur Teile bis 1,0 mm Hoehe tragen; 0805 ist 1,25 mm)
_C603 = {'10uF': 'GRM188R61A106KE69', '22uF': 'GRM188R60J226MEA0', '4.7uF': 'GRM188R60J475KE19D', '1uF': 'GRM188R61A105KA61D'}
for _p in PARTS:
    if _p['kind'] == 'C' and _p['fp'] == C805:
        _p['fp'] = C603; _p['pkg'] = '0603'
        _p['mpn'] = _C603.get(_p['value'].replace(' ', ''), '(' + _p['value'] + ' X5R >= 10 V 0603, Typ nach Verfuegbarkeit)'); _p['mfr'] = mfr_of(_p['mpn']); _p['lcsc'] = ''
        if _p['src'] == 'Tangara': _p['src'] = 'angepasst'; _p['desc'] = (_p.get('desc') or '') + ' 0603 statt 0805 (Hoehe <= 1,0 mm fuer die Oberseite)'

def parts():
    return PARTS
