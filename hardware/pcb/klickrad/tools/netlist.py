"""Gemeinsame Bauteil- und Netzliste für Schaltplan- und Layout-Generator (einzige Quelle)."""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Tangara-Referenzen (tangara-faceplate.kicad_sch) -> hier:
#  U1 AT42QT2120 = U1, U2 DRV2605L = U2, R1-R3 = R1-R3 (Wheel), R5 = R4 (Taste), R6 = R5 (Guard), R7 = R6 (RESET), R4 = R7 (EN),
#  C1 = C1, C5 = C2, C3 = C3, C4 = C4, C2 (22 uF, Display) entfällt -> C5 (10 uF, LRA-Spitzen)

def parts():
    P = []
    def add(ref, value, sym, fp, pins, **kw):
        d = dict(ref=ref, value=value, sym=sym, fp=fp, pins=pins); d.update(kw); P.append(d)
    # AT42QT2120, VQFN-20, Comms-Modus: 1 KEY6 2 KEY5 3 KEY4 4 KEY3 5 KEY2 6 KEY1 7 KEY0 8 VSS 9 VDD 10 MODE(=VSS) 11 SDA 12 RESET 13 NC 14 SCL 15 CHANGE 16..20 KEY11..KEY7
    pins = {'3': 'KG', '4': 'KB', '5': 'K2', '6': 'K1', '7': 'K0', '8': 'GND', '9': '3V3', '10': 'GND', '11': 'SDA', '12': 'RESET', '14': 'SCL', '15': 'CHANGE'}
    for n in ('1', '2', '13', '16', '17', '18', '19', '20'): pins[n] = None      # unbenutzt (No-Connect), wie Tangara
    add('U1', 'AT42QT2120', 'Klickrad:AT42QT2120', 'Package_DFN_QFN:VQFN-20-1EP_3x3mm_P0.45mm_EP1.55x1.55mm', pins,
        mpn='AT42QT2120-MMH', mfr='Microchip', desc='12-Kanal QTouch, I2C 0x1C, Wheel-Modus (KEY0..2), Taste KEY3, Guard KEY4')
    add('U2', 'DRV2605LDGSR', 'Driver_Haptic:DRV2605LDGS', 'Package_SO:VSSOP-10_3x3mm_P0.5mm',
        {'1': 'REG', '2': 'SCL', '3': 'SDA', '4': 'GND', '5': 'EN', '6': '3V3', '7': 'LRA_P', '8': 'GND', '9': 'LRA_N', '10': '3V3'},
        mpn='DRV2605LDGSR', mfr='Texas Instruments', desc='Haptik-Treiber LRA/ERM, I2C 0x5A; IN/TRIG an GND, EN ueber 10k an 3V3 (wie Tangara)')
    cap = lambda ref, v, nets, fp='Capacitor_SMD:C_0402_1005Metric', d='': add(ref, v, 'Device:C', fp, {'1': nets[0], '2': nets[1]}, desc=d)
    cap('C1', '0.1uF', ('3V3', 'GND'), d='AT42QT2120 VDD, direkt am Pin (Datenblatt 3.4)')
    cap('C2', '1uF', ('3V3', 'GND'), d='AT42QT2120 VDD Puffer (Tangara C5)')
    cap('C3', '1uF', ('3V3', 'GND'), d='DRV2605L VDD (Tangara C3)')
    cap('C4', '1uF', ('REG', 'GND'), d='DRV2605L REG (Tangara C4)')
    cap('C5', '10uF', ('3V3', 'GND'), fp='Capacitor_SMD:C_0603_1608Metric', d='LRA-Stromspitzen (neu gegenueber Tangara)')
    res = lambda ref, v, nets, d='', dnp=False: add(ref, v, 'Device:R', 'Resistor_SMD:R_0402_1005Metric', {'1': nets[0], '2': nets[1]}, dnp=dnp, desc=d)
    res('R1', '10k', ('K0', 'E0'), 'Serienwiderstand Wheel-Elektrode 0 (Tangara R1)')
    res('R2', '10k', ('K1', 'E1'), 'Serienwiderstand Wheel-Elektrode 1 (Tangara R2)')
    res('R3', '10k', ('K2', 'E2'), 'Serienwiderstand Wheel-Elektrode 2 (Tangara R3)')
    res('R4', '10k', ('KB', 'EB'), 'Serienwiderstand Mitteltaste (Tangara R5)')
    res('R5', '10k', ('KG', 'EG'), 'Serienwiderstand Guard (Tangara R6)')
    res('R6', '10k', ('3V3', 'RESET'), 'RESET-Pull-up (Tangara R7)')
    res('R7', '10k', ('3V3', 'EN'), 'DRV2605L EN-Pull-up (Tangara R4)')
    res('R8', '4.7k', ('3V3', 'SDA'), 'I2C Pull-up SDA, DNP (liegt auf der Hauptplatine / dem Waveshare-Board)', True)
    res('R9', '4.7k', ('3V3', 'SCL'), 'I2C Pull-up SCL, DNP', True)
    add('SW1', 'BUTTON', 'Connector_Generic:Conn_01x01', 'Klickrad:qtouch-button', {'1': 'EB'}, nobom=True, desc='Kapazitive Mitteltaste (Tangara SW1)')
    add('SW2', 'WHEEL', 'Connector_Generic:Conn_01x03', 'Klickrad:qtouch-wheel', {'1': 'E0', '2': 'E1', '3': 'E2'}, nobom=True, desc='Touch-Wheel, 3 Elektroden (Tangara SW2)')
    add('SW3', 'GUARD', 'Connector_Generic:Conn_01x01', 'Klickrad:qtouch-guard', {'1': 'EG'}, nobom=True, desc='Guard-Kanal (Tangara SW3)')
    add('J1', 'FH12-6S-0.5SH', 'Connector_Generic:Conn_01x06', 'Connector_FFC-FPC:Hirose_FH12-6S-0.5SH_1x06-1MP_P0.50mm_Horizontal',
        {'1': '3V3', '2': 'GND', '3': 'SDA', '4': 'SCL', '5': 'CHANGE', '6': None}, mpn='FH12-6S-0.5SH(55)', mfr='Hirose', desc='FFC/FPC 6-pol., 0,5 mm, Flip-Lock, Bauhöhe 1,0 mm; Pin 6 = Reserve (BTN)')
    add('TP1', 'LRA+', 'Connector:TestPoint', 'Connector_Wire:SolderWirePad_1x01_SMD_1x2mm', {'1': 'LRA_P'}, desc='Loetpad LRA Litze +', nobom=True)
    add('TP2', 'LRA-', 'Connector:TestPoint', 'Connector_Wire:SolderWirePad_1x01_SMD_1x2mm', {'1': 'LRA_N'}, desc='Loetpad LRA Litze -', nobom=True)
    return P
