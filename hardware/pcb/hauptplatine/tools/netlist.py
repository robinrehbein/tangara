"""Bauteil- und Netzliste der Hauptplatine v2 (einzige Quelle fuer Schaltplan, Platine, Stueckliste).

Herkunft der Teile (Feld "src"):
  Tangara    - 1:1 aus der Tangara-Hardware (cooltech.zone, CERN-OHL-S-2.0; Stand der .kicad_sch-Dateien, quellen/tangara_netlist_rev5.json)
  angepasst  - von Tangara uebernommen, aber geaendert (Begruendung im Feld "desc" und im README)
  Espressif  - Referenzbeschaltung aus Datenblatt/Hardware-Design-Guidelines des ESP32-S31-WROOM-3
  neu        - eigene Entwicklung, ungeprueft
"""
import json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
TG = json.load(open(os.path.join(os.path.dirname(HERE), 'quellen', 'tangara_netlist_rev5.json')))

def nn(n):
    """Tangara-Netzname -> unser Netzname."""
    if n is None: return None
    m = {'+3V3': '3V3', '+5VA': 'V5A', '-5VA': 'VN5A', 'USB.DP': 'USB_DP', 'USB.DN': 'USB_DN', 'I2C.SDA': 'SDA', 'I2C.SCL': 'SCL',
         'DAC.MCK': 'DAC_MCK', 'DAC.BCK': 'DAC_BCK', 'DAC.LRCK': 'DAC_LRCK', 'DAC.DATA': 'DAC_DATA', '3.5mm_DETECT': 'JACK_DETECT',
         'VBUS_SWITCHED': 'VBUS_SW', 'Net-(J7-Pin_3)': 'VBAT', 'Net-(U4-EN)': 'LDO_EN', 'Net-(SW1-C)': 'LOCK_COM',
         'Net-(U10-CE)': 'CHG_CE', 'Net-(U10-PROG1)': 'CHG_PROG1', 'Net-(U10-PROG3)': 'CHG_PROG3', 'Net-(Q1-G)': 'Q1_G',
         'CHG_PROG': 'CHG_PROG2', '~{CHG_PWR_OK}': 'CHG_PG', 'Net-(J6-CC1)': 'CC1', 'Net-(J6-CC2)': 'CC2', 'SYS_PWR_EN_SAMD': 'SYS_PWR_EN',
         '~{SD_VDD_EN}': 'SD_VDD_EN', 'Net-(J4-VDD)': 'SD_VDD', 'Net-(J4-CMD)': 'SD_CMD', 'Net-(J4-CLK)': 'SD_CLK', 'Net-(J4-DAT0)': 'SD_D0',
         'Net-(J4-DAT1)': 'SD_D1', 'Net-(J4-DAT2)': 'SD_D2', 'Net-(J4-CD/DAT3)': 'SD_D3', 'SD_CD': 'SD_CD', 'Net-(Q3-G)': 'Q3_G'}
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

KIND = {'X': 'X', 'R': 'R', 'C': 'C', 'L': 'L', 'Q': 'Q', 'D': 'D', 'U': 'IC', 'J': 'CONN', 'SW': 'SW', 'TP': 'TP'}
FPMAP = {   # Tangara-Footprint -> unser Footprint
    'footprints:CUI_SJ-3506-SMT': 'Hauptplatine:CUI_SJ-3506-SMT',
    'footprints:GCT_USB4510-03-1-A_REVA': 'Hauptplatine:GCT_USB4510-03-1-A_REVA',
    'footprints:SON40P300X300X80-13N': 'Hauptplatine:SON40P300X300X80-13N',
    'footprints:SOT65P210X110-6N': 'Hauptplatine:SOT65P210X110-6N',
    'footprints:QFN-20-1EP_4x4mm_P0.5mm_EP2.5x2.5mm_ThermalVias2': 'Package_DFN_QFN:QFN-20-1EP_4x4mm_P0.5mm_EP2.5x2.5mm',
    'Package_DFN_QFN:QFN-24-1EP_4x4mm_P0.5mm_EP2.7x2.7mm_ThermalVias': 'Package_DFN_QFN:Texas_RTW_WQFN-24-1EP_4x4mm_P0.5mm_EP2.7x2.7mm',
    'Button_Switch_SMD:SW_SPDT_CK-JS102011SAQN': 'Button_Switch_SMD:SW_SPDT_CK_JS102011SAQN',
}
MFR = {'GRM': 'Murata', 'GCM': 'Murata', 'AC0603': 'Yageo', 'RC0603': 'Yageo', 'RR1220': 'Susumu', 'TPS': 'Texas Instruments', 'INA': 'Texas Instruments',
       'WM8523': 'Cirrus Logic', 'MCP': 'Microchip', 'TLV': 'Texas Instruments', 'PMV': 'Nexperia', 'PJC': 'PANJIT', 'BAT54': 'Nexperia',
       '1239AS': 'Murata (TOKO)', 'D5V0': 'Diodes Inc.', 'PE1605': 'ProTek Devices', 'S3B-PH': 'JST', 'SJ-3506': 'CUI Devices',
       'USB4510': 'GCT', 'JS102011': 'C&K', 'TUSB': 'Texas Instruments', 'CL': 'Samsung', 'B3U': 'Omron'}
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

# ======================================================================================================== MCU ESP32-S31-WROOM-3
S31 = {   # Pad -> Modulname (Datenblatt v0.7, Tabelle 3-1)
    **{str(i): 'GND' for i in (1, 2, 26, 47, 48, 72)}, '3': '3V3', '4': '3V3', '5': 'EN',
    '6': 'IO2', '7': 'IO3', '8': 'IO0', '9': 'IO1', '10': 'IO4', '11': 'IO5', '12': 'IO6', '13': 'IO7', '14': 'IO8', '15': 'IO9', '16': 'IO10',
    '17': 'IO11', '18': 'IO12', '19': 'IO13', '20': 'IO14', '21': 'IO15', '22': 'IO16', '23': 'IO17', '24': 'IO18', '25': 'IO19',
    '27': 'SD_D0', '28': 'SD_D1', '29': 'SD_D2', '30': 'SD_D3', '31': 'SD_CLK', '32': 'SD_CMD',
    **{str(i): 'NC' for i in range(33, 40)}, '40': 'USB_DP', '41': 'USB_DM', '42': 'IO33', '43': 'IO34', '44': 'IO35', '45': 'IO36', '46': 'IO37',
    '49': 'IO38', '50': 'IO39', '51': 'IO40', '52': 'IO42', '53': 'IO43', '54': 'IO44', '55': 'IO45', '56': 'IO46', '57': 'IO47', '58': 'IO48',
    '59': 'IO49', '60': 'IO50', '61': 'IO51', '62': 'IO52', '63': 'IO53', '64': 'IO54', '65': 'IO55', '66': 'IO56', '67': 'IO57',
    '68': 'TX0', '69': 'RX0', '70': 'IO60', '71': 'IO61',
    **{str(i): 'GND' for i in range(73, 91)}, '91': 'NC', **{str(i): 'GND' for i in range(92, 100)},
}
# Signale, die ein freies S31-GPIO bekommen (Zuordnung: tools/gpio_assign.py -> tools/gpio_map.json)
GPIO_SIGNALS = ['LCD_CS', 'LCD_SCK', 'LCD_D0', 'LCD_D1', 'LCD_D2', 'LCD_D3', 'LCD_RST', 'LCD_TE', 'SDA', 'SCL', 'TP_INT',
                'DAC_MCK_MCU', 'DAC_BCK', 'DAC_LRCK', 'DAC_DATA', 'AMP_EN', 'Q3_G', 'JACK_DETECT', 'WHEEL_INT', 'WHEEL_BTN',
                'SYS_PWR_EN', 'KEY_LOCK_MCU', 'CHG_STAT1', 'CHG_STAT2', 'CHG_PG', 'CHG_SEL', 'CHG_PROG2', 'TUSB_ID', 'TUSB_INT', 'HOST_EN', 'SD_CD', 'SD_VDD_EN', 'FG_ALRT']
GPIO_MAP = {}   # Signal -> Modulname (IOx)
_gm = os.path.join(HERE, 'gpio_map.json')
if os.path.exists(_gm): GPIO_MAP = json.load(open(_gm))
_rev = {v: k for k, v in GPIO_MAP.items()}
FIXED_S31 = {'EN': 'ESP_EN', 'USB_DP': 'USB_HS_DP', 'USB_DM': 'USB_HS_DM', 'IO33': 'USBJ_DM', 'IO34': 'USBJ_DP', 'IO61': 'BOOT', 'TX0': 'UART_TX0', 'RX0': 'UART_RX0',
             'SD_D0': 'SD_D0', 'SD_D1': 'SD_D1', 'SD_D2': 'SD_D2', 'SD_D3': 'SD_D3', 'SD_CLK': 'SD_CLK', 'SD_CMD': 'SD_CMD', '3V3': '3V3', 'GND': 'GND'}
s31pins = {}
for pad, name in S31.items():
    if name in FIXED_S31: s31pins[pad] = FIXED_S31[name]
    elif name == 'NC': s31pins[pad] = None
    else: s31pins[pad] = _rev.get(name)
add('U15', 'ESP32-S31-WROOM-3-N16R16V', 'IC', 'Hauptplatine:ESP32-S31-WROOM-3', s31pins, 'neu', names=dict(S31), mpn='ESP32-S31-WROOM-3-N16R16V',
    mfr='Espressif', lcsc='', dk='', pkg='Modul 22 x 30 x 3,5',
    desc='WLAN 6, Bluetooth 5.4 (Classic + LE Audio), USB 2.0 HS OTG, 16 MB Flash (Quad), 16 MB PSRAM (Octal) (Datenblatt v0.7 PRELIMINARY); Tangara: ESP32-WROVER-E mit 8 MB PSRAM',
    at=None)

# ======================================================================================================== Audio (Tangara, 1:1)
for ref in ['U17', 'U1', 'U7', 'U3']: tg(ref)
for ref in ['C2', 'C3', 'C4', 'C6', 'C7', 'C9', 'C10', 'C12', 'C13', 'C14', 'C15', 'C16', 'C17', 'C18', 'C19', 'L1', 'L2', 'R3', 'R6', 'R8', 'R15',
            'TP3', 'TP4', 'TP5', 'TP6', 'Q3', 'R2', 'R5', 'R22']:
    tg(ref)
tg('J1', names={'1': 'GND', '2': 'HP_L', '3': 'HP_R', '4': 'DETECT', '5': 'GND', '6': 'NC', 'SH1': 'SHIELD', 'SH2': 'SHIELD'})

# ======================================================================================================== Power (Tangara)
tg('J6', names={'A1_B12': 'GND', 'B1_A12': 'GND', 'A4_B9': 'VBUS', 'B4_A9': 'VBUS', 'A5': 'CC1', 'B5': 'CC2', 'A6': 'DP', 'B6': 'DP', 'A7': 'DN', 'B7': 'DN', 'A8': 'SBU1', 'B8': 'SBU2'})
tg('U10')
for ref in ['C24', 'C25', 'C27', 'C29', 'R34', 'R35', 'R37', 'R38', 'R39', 'R41', 'R1', 'TP7', 'Q1', 'C37', 'R7', 'D4']:
    tg(ref)
tg('U5')
# Tangara: TLV75533 (500 mA). S31 zieht bei WLAN-TX bis ca. 375 mA (Datenblatt Tab. 6-4), dazu Display, LRA, Audio, SD -> TLV75733P (1 A), gleiche Pinbelegung.
tg('J7', fp='Connector_JST:JST_SH_SM03B-SRSS-TB_1x03-1MP_P1.00mm_Horizontal', mpn='SM03B-SRSS-TB(LF)(SN)', mfr='JST', src='angepasst', lcsc='C160403', dk='455-SM03B-SRSS-TBCT-ND', pkg='JST-SH 3 Pol',
   desc='JST-SH 3-pol. SMD statt PH 3-pol. THT (Tangara S3B-PH-K): Oberseite bleibt unter dem Display eben, passt in den Platz; Pin 1 NTC, 2 GND, 3 BAT+'); get('J7')['pins']['MP']='GND'
tg('U4', value='TLV75733PDBV', mpn='TLV75733PDBVR', src='angepasst', lcsc='C485517', dk='296-50414-1-ND', desc='3V3-LDO 1 A statt 500 mA (TLV75533)')
# Tangara: Schiebeschalter SW1 (KEY_LOCK, Hold/Power) + SAMD21 haelt SYS_PWR_EN. Hier: Ein/Aus-Taster (seitlich betaetigt, wie im Gehaeuse-CAD),
# der S31 haelt die Versorgung ueber SYS_PWR_EN (BAT54C D4) und kann sich selbst abschalten (Power-Latch).
add('SW1', 'B3U-3000P', 'SW', 'Button_Switch_SMD:SW_SPST_B3U-3000P', {'1': 'LOCK_COM', '2': 'KEY_LOCK'}, 'angepasst', mpn='B3U-3000P', mfr='Omron', lcsc='C963349',
    pkg='3,0 x 2,5 x 1,2 seitlich', desc='Ein/Aus-Taster statt Schiebeschalter JS102011SAQN (Tangara): drueckt SYS_POWER auf KEY_LOCK -> LDO_EN')
tg('R4', value='10k', mpn='AC0603JR-0710KL', src='angepasst', desc='Taster-Vorwiderstand (Tangara: 100 k); bei Tastendruck KEY_LOCK ca. 0,9 x SYS_POWER')
add('R200', '100k', 'R', 'Resistor_SMD:R_0603_1608Metric', {'1': 'KEY_LOCK', '2': 'GND'}, 'neu', mpn='AC0603FR-07100KL', mfr='Yageo', pkg='0603', desc='KEY_LOCK Pull-down (Taster offen = low)')
add('R201', '10k', 'R', 'Resistor_SMD:R_0603_1608Metric', {'1': 'KEY_LOCK', '2': 'KEY_LOCK_MCU'}, 'neu', mpn='AC0603JR-0710KL', mfr='Yageo', pkg='0603', desc='Serienwiderstand zum S31-GPIO (SYS_POWER bis 5 V, GPIO 3,3 V)')
add('R202', '100k', 'R', 'Resistor_SMD:R_0603_1608Metric', {'1': 'SYS_PWR_EN', '2': 'GND'}, 'neu', mpn='AC0603FR-07100KL', mfr='Yageo', pkg='0603', desc='SYS_PWR_EN Pull-down (Latch faellt, wenn S31 aus)')
# Bei Tangara stellt der SAMD21 CHG_SEL/CHG_PROG ein; hier feste Pull-ups (aus Tangara Rev. 4), S31 liest nur den Status
add('R36', '100k', 'R', 'Resistor_SMD:R_0603_1608Metric', {'1': '3V3', '2': 'CHG_PROG2'}, 'angepasst', mpn='AC0603FR-07100KL', mfr='Yageo', pkg='0603',
    desc='PROG2 hoch = USB-Eingangslimit 500 mA (Tangara: Pin vom SAMD21 gesteuert); hier Pull-up an 3V3 (S31-GPIO darf nicht auf 5 V haengen), S31 kann ueberschreiben')
add('R43', '10k', 'R', 'Resistor_SMD:R_0603_1608Metric', {'1': '3V3', '2': 'CHG_SEL'}, 'angepasst', mpn='AC0603JR-0710KL', mfr='Yageo', pkg='0603',
    desc='SEL hoch = USB-Eingang (Tangara Rev. 4)')

# ======================================================================================================== Peripherie (Tangara)
add('J4', 'microSD', 'CONN', 'Connector_Card:microSD_HC_Molex_104031-0811',
    {'1': 'SD_D2', '2': 'SD_D3', '3': 'SD_CMD', '4': 'SD_VDD', '5': 'SD_CLK', '6': 'GND', '7': 'SD_D0', '8': 'SD_D1', '9': 'SD_CD', '10': 'GND', '11': 'GND'},
    'angepasst', names={'1': 'DAT2', '2': 'DAT3', '3': 'CMD', '4': 'VDD', '5': 'CLK', '6': 'VSS', '7': 'DAT0', '8': 'DAT1', '9': 'CD', '10': 'CD_COM', '11': 'SHIELD'},
    mpn='104031-0811', mfr='Molex', dk='WM6357DKR-ND', pkg='microSD Push-Push',
    desc='microSD statt Vollformat-SD (Tangara: Hirose DM1AA-SF-PEJ(82), 32 x 32 mm); SDMMC 4 Bit direkt am S31 statt SPI + Multiplexer')
tg('U16', names={'1': 'IN', '2': 'GND', '3': 'ON', '4': 'NC', '5': 'FLT', '6': 'OUT'})
for ref in ['R9', 'R11', 'R12', 'R57', 'R61', 'C42']: tg(ref)
for ref in ['C30', 'C32', 'C34', 'C35', 'C38', 'C39', 'C23', 'C31', 'C1']: tg(ref)

# ======================================================================================================== Espressif-Beschaltung
res('R100', '10k', '3V3', 'ESP_EN', 'EN-Pull-up (Espressif: RC-Verzoegerung 10 k / 1 uF)', src='Espressif')
cap('C100', '1uF', 'ESP_EN', 'GND', 'EN-Kondensator (Espressif: RC 10 k / 1 uF)', src='Espressif')
cap('C101', '22uF', '3V3', 'GND', 'Espressif: 22 uF am Modul-3V3', src='Espressif', fp=C805, mpn='CL21A226MAQNNNE', lcsc='C45783')
cap('C102', '100nF', '3V3', 'GND', 'Espressif: 100 nF am Modul-3V3', src='Espressif')
for ref, nm, net, d in [('SW10', 'EN', 'ESP_EN', 'Reset-Taster (EN nach GND)'),
                        ('SW11', 'BOOT', 'BOOT', 'Boot-Taster: GPIO61 nach GND = Joint-Download-Modus (GPIO60 offen = high)')]:
    add(ref, nm, 'SW', 'Button_Switch_SMD:SW_SPST_B3U-1000P', {'1': net, '2': 'GND'}, 'Espressif', mpn='B3U-1000P', mfr='Omron', lcsc='C231329', desc=d, pkg='3,0 x 2,5 x 1,2')
res('R101', '10k', '3V3', 'BOOT', 'GPIO61 Pull-up (definierter Strapping-Pegel)', src='Espressif')
cap('C103', '100nF', 'BOOT', 'GND', 'Entprellung Boot-Taster', src='Espressif')
res('R102', '0', 'USB_DP', 'USB_HS_DP', 'USB-HS D+: Platz fuer Serienwiderstand (Espressif: nahe am Chip; Anfangswert 0 Ohm)', src='Espressif')
res('R103', '0', 'USB_DN', 'USB_HS_DM', 'USB-HS D-: Platz fuer Serienwiderstand', src='Espressif')
for ref, net, nm in [('TP10', 'UART_TX0', 'TX0'), ('TP11', 'UART_RX0', 'RX0'), ('TP12', 'USBJ_DP', 'IO34 USB-JTAG D+'), ('TP13', 'USBJ_DM', 'IO33 USB-JTAG D-'),
                     ('TP14', 'ESP_EN', 'EN'), ('TP15', 'BOOT', 'BOOT')]:
    add(ref, nm, 'TP', 'TestPoint:TestPoint_Pad_D1.0mm', {'1': net}, 'Espressif', nobom=True, desc='Testpunkt Programmierung/Debug')
# WM8523 braucht MCLK (128..1152 x fs, kein PLL). S31 erzeugt MCLK aus dem Digitaltakt (Bruchteilsteiler, kein Audio-PLL erwaehnt -> Jitter).
# Option: Oszillator (22,5792 MHz fuer 44,1/88,2 kHz bzw. 24,576 MHz fuer 48/96 kHz), per 0-Ohm-Bruecke statt S31-MCLK.
res('R210', '0', 'DAC_MCK_MCU', 'DAC_MCK', 'MCLK-Quelle S31 (bestueckt)', src='angepasst')
res('R211', '0', 'MCK_OSC', 'DAC_MCK', 'MCLK-Quelle Oszillator (DNP); R210 dann entfernen', src='neu', dnp=True)
add('X1', 'Osc 22.5792MHz', 'X', 'Oscillator:Oscillator_SMD_Abracon_ASE-4Pin_3.2x2.5mm', {'1': '3V3', '2': 'GND', '3': 'MCK_OSC', '4': '3V3'}, 'neu', dnp=True, names={'1': 'EN', '2': 'GND', '3': 'OUT', '4': 'VDD'},
    mpn='(Typ nach Abtastraten-Familie waehlen, z. B. 22,5792 MHz)', pkg='3,2 x 2,5', desc='Optionaler MCLK-Oszillator, 3V3, nicht bestueckt (DNP)')
cap('C211', '100nF', '3V3', 'GND', 'Oszillator VDD (DNP)', dnp=True)
# Pull-ups fuer Signale, die Tangara auf dem SAMD21/PCA8575 hatte oder die das Klickrad nicht bestueckt
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
add('Q10', 'PJC138K', 'Q', 'Package_TO_SOT_SMD:SOT-323_SC-70', {'1': 'Q1_GN', '2': 'GND', '3': 'Q1_G'}, 'neu', names={'1': 'G', '2': 'S', '3': 'D'},
    mpn='PJC138K_R1_00001', mfr='PANJIT', pkg='SC-70', desc='zieht Q1-Gate nach GND (Sink-Betrieb); aus, wenn ID low (Host)', qtype='N')
res('R114', '100k', 'VBUS', 'Q1_G', 'Q1-Gate Pull-up an VBUS (Q1 aus im Host-Betrieb)')
add('Q11', 'PJC138K', 'Q', 'Package_TO_SOT_SMD:SOT-323_SC-70', {'1': 'TUSB_ID', '2': 'GND', '3': 'HOST_EN'}, 'neu', names={'1': 'G', '2': 'S', '3': 'D'},
    mpn='PJC138K_R1_00001', mfr='PANJIT', pkg='SC-70', desc='invertiert ID -> HOST_EN', qtype='N')
res('R115', '10k', '3V3', 'HOST_EN', 'HOST_EN Pull-up (S31 kann per GPIO nach GND ziehen = Host aus)')
add('U20', 'TPS61023DRL', 'IC', 'Package_TO_SOT_SMD:SOT-563', {'1': 'BOOST_FB', '2': 'HOST_EN', '3': 'SYS_POWER', '4': 'GND', '5': 'BOOST_SW', '6': 'V5_HOST'}, 'neu',
    names={'1': 'FB', '2': 'EN', '3': 'VIN', '4': 'GND', '5': 'SW', '6': 'VOUT'}, mpn='TPS61023DRLR', mfr='Texas Instruments', lcsc='C919459', dk='296-TPS61023DRLRCT-ND',
    pkg='SOT-563', desc='Boost 5,1 V aus SYS_POWER (Schalterstrom 3,7 A)')
add('L20', '1uH', 'L', 'Inductor_SMD:L_1008_2520Metric', {'1': 'SYS_POWER', '2': 'BOOST_SW'}, 'neu', mpn='DFE252012F-1R0M=P2', mfr='Murata', pkg='1008',
    desc='1 uH (TPS61023 Tab. 8-2), Saettigungsstrom >= 3 A; Typ vor Bestellung gegen Datenblatt pruefen')
res('R116', '390k', 'V5_HOST', 'BOOST_FB', 'FB-Teiler: 0,595 V x (1 + 390k/51k) = 5,15 V')
res('R117', '51k', 'BOOST_FB', 'GND', 'FB-Teiler')
cap('C111', '10uF', 'SYS_POWER', 'GND', 'Boost Eingang', fp=C805, mpn='GRM21BR61C106KE15K')
cap('C112', '22uF', 'V5_HOST', 'GND', 'Boost Ausgang (25 V X5R)', fp=C805, mpn='CL21A226MAQNNNE', lcsc='C45783')
cap('C113', '10uF', 'V5_HOST', 'GND', 'Boost Ausgang', fp=C805, mpn='GRM21BR61C106KE15K')
add('U21', 'TPS2553DBV', 'IC', 'Package_TO_SOT_SMD:SOT-23-6', {'1': 'V5_HOST', '2': 'GND', '3': 'HOST_EN', '4': 'HOST_FLT', '5': 'HOST_ILIM', '6': 'VBUS'}, 'neu',
    names={'1': 'IN', '2': 'GND', '3': 'EN', '4': 'FAULT', '5': 'ILIM', '6': 'OUT'}, mpn='TPS2553DBVR', mfr='Texas Instruments', lcsc='C55266', dk='296-32464-1-ND',
    pkg='SOT-23-6', desc='Lastschalter mit Strombegrenzung (49,9 k = ca. 520 mA)')
res('R118', '49.9k', 'HOST_ILIM', 'GND', 'Stromlimit ca. 520 mA (Datenblatt: IOS 490-550 mA bei 49,9 k)')
cap('C114', '100nF', 'V5_HOST', 'GND', 'TPS2553 IN')
res('R119', '10k', '3V3', 'HOST_FLT', 'FAULT Pull-up (open drain)')

# ======================================================================================================== Display (AMOLED, FPC)
FPC_PINS = {   # laut Waveshare ESP32-S3-Touch-AMOLED-1.8 Schaltplan, U4 (AXE534124)
    '1': 'LCD_RST', '2': 'LCD_TE', '3': 'GND', '4': 'GND', '5': 'LCD_D0', '6': None, '7': 'LCD_D1', '8': 'SCL', '9': 'LCD_SCK', '10': 'SDA',
    '11': 'LCD_CS', '12': 'TP_INT', '13': 'LCD_D2', '14': 'TP_RST', '15': 'LCD_D3', '16': '3V3', '17': 'LCD_IM1', '18': '3V3', '19': 'LCD_IM0', '20': '3V3',
    '21': 'GND', '22': 'LCD_PWR_EN', '23': 'GND', '24': '3V3', '25': 'GND', '26': '3V3', '27': 'GND', '28': 'GND', '29': 'GND', '30': None, '31': 'GND',
    '32': None, '33': 'GND', '34': None, '35': 'GND', '36': 'GND', '37': 'GND', '38': 'GND'}
FPC_NAMES = {'1': 'RESET', '2': 'TE', '5': 'SIO0', '7': 'SIO1', '8': 'TP_SCL', '9': 'QSPI_SCL', '10': 'TP_SDA', '11': 'CS', '12': 'TP_INT', '13': 'SIO2', '14': 'TP_RST',
             '15': 'SIO3', '16': 'TP_VDD', '17': 'IM1', '19': 'IM0', '22': 'PWR_EN', '24': 'VCI', '26': 'VDDIO', '34': 'VPP'}
add('J20', 'AXE534124', 'CONN', 'Hauptplatine:FPC-AXE534124', FPC_PINS, 'neu', names=FPC_NAMES, mpn='AXE534124', mfr='Panasonic', pkg='FPC 34 Pol 0,4 mm',
    desc='Display-FPC-Buchse wie Waveshare ESP32-S3-Touch-AMOLED-1.8 (CO5300, QSPI); Land-Muster abgeleitet, ungeprueft; Bauteil laut Hersteller auslaufend')
res('R130', '10k', '3V3', 'LCD_IM1', 'Display IM1 = 1 (Waveshare R27)')
res('R131', '10k', 'LCD_IM0', 'GND', 'Display IM0 = 0 (Waveshare R28)')
res('R132', '10k', '3V3', 'TP_RST', 'Touch-Reset hoch (immer aus dem Reset)')
res('R133', '10k', '3V3', 'TP_INT', 'Touch-INT Pull-up (Waveshare R26)')
res('R134', '4.7k', '3V3', 'LCD_PWR_EN', 'FPC-Pin 22 (Waveshare DSI_PWR_EN) fest high')
res('R135', '100k', '3V3', 'LCD_RST', 'Reset-Pull-up Display')
for i, (ref, v, fp) in enumerate([('C130', '10uF', C805), ('C131', '100nF', None), ('C132', '10uF', C805), ('C133', '100nF', None)]):
    cap(ref, v, '3V3', 'GND', 'Display-Versorgung (Waveshare C24/C25/C27/C28)', **({'fp': fp, 'mpn': 'GRM21BR61C106KE15K'} if fp else {}))

# ======================================================================================================== Klickrad-Anschluss
add('J21', 'SM06B-SRSS-TB', 'CONN', 'Connector_JST:JST_SH_SM06B-SRSS-TB_1x06-1MP_P1.00mm_Horizontal',
    {'1': '3V3', '2': 'GND', '3': 'SDA', '4': 'SCL', '5': 'WHEEL_INT', '6': 'WHEEL_BTN', 'MP': 'GND'}, 'neu',
    names={'1': '3V3', '2': 'GND', '3': 'SDA', '4': 'SCL', '5': 'INT/CHANGE', '6': 'BTN', 'MP': 'MP'},
    mpn='SM06B-SRSS-TB(LF)(SN)', mfr='JST', lcsc='C160405', dk='455-SM06B-SRSS-TBCT-ND', pkg='JST-SH 6 Pol',
    desc='Klickrad-Modul (Belegung laut TEILE.md; Pin 5 = INT/CHANGE, Pin 6 = BTN)')
res('R136', '10k', '3V3', 'WHEEL_INT', 'Pull-up Klickrad INT/CHANGE (open drain, aktiv low)')
res('R137', '10k', '3V3', 'WHEEL_BTN', 'Pull-up Klickrad BTN (aktiv low)')
for i, ang in enumerate((90, 210, 330)):
    add(f'H{i+1}', 'M2-Klickrad', 'H', 'MountingHole:MountingHole_2.2mm_M2', {}, 'neu', nobom=True, desc='Montageloch Abstandshalter Klickrad (NPTH 2,2 mm, r = 14,6 mm um (0,-27))',
        wheel_angle=ang)

def parts():
    return PARTS
