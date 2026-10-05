/* Copyright 2026 Nano-Player-Projekt
 * SPDX-License-Identifier: GPL-3.0-only */
#pragma once
/**
 * Board-Profil "Endgeraet": Hauptplatine Rev. 3b mit ESP32-S31-WROOM-1-N16R16V
 * (Quelle: hardware/pcb/hauptplatine/README.md "GPIO-Pruefung ... und Belegung", TEILE.md Rev. 3b).
 *
 * STATUS: nur vorbereitet. Nicht fuer den S31 gebaut (IDF 5.4.2 kennt das Ziel nicht), nicht auf Hardware
 * getestet. Die Pin-Zuordnung der Platine ist selbst "ungeprueft gegen das endgueltige Datenblatt (v0.5,
 * vorlaeufig)". Mit [offen] markierte Werte sind nicht eindeutig und stehen auch in
 * docs/FIRMWARE-PORTIERUNG.md Abschnitt "Board-Profil Endgeraet".
 *
 * Gegenueber dem Prototyp entfallen: IO-Expander TCA9554, Touch-Reset per Expander, AXP2101, ES8311, QMI8658,
 * PCF85063, Mitteltasten-Pin BTN (Stecker-Pin 6 ist Reserve), Latenz-Messpunkte (keine freien Pads vergeben),
 * eigener Wheel-Bus. Die Lader-Steuerung (SEL/PROG2) ist fest verdrahtet, keine GPIOs (IO14/IO15 frei).
 */
#include "driver/gpio.h"
#include "driver/i2c_master.h"

/* ---- Display: 2,06" AMOLED 410 x 502, CO5300, QSPI (nicht der Prototyp-Wert 368 x 448) ---- */
#define BOARD_LCD_HOST       SPI2_HOST          /* [offen] S31-Hostname/Pad-Eignung gegen IDF 6 pruefen */
#define BOARD_LCD_H_RES      410
#define BOARD_LCD_V_RES      502
#define BOARD_LCD_CS         GPIO_NUM_49
#define BOARD_LCD_SCLK       GPIO_NUM_48
#define BOARD_LCD_D0         GPIO_NUM_11
#define BOARD_LCD_D1         GPIO_NUM_10
#define BOARD_LCD_D2         GPIO_NUM_9
#define BOARD_LCD_D3         GPIO_NUM_51
#define BOARD_LCD_RST_GPIO   GPIO_NUM_19        /* LCD_RST direkt am S31 (100 k Pull-up), kein Expander */
#define BOARD_LCD_TE_GPIO    GPIO_NUM_12        /* Tearing-Effect, in Phase 1 nicht benutzt */
#define BOARD_TP_INT_GPIO    GPIO_NUM_50        /* Display-Touch-Interrupt, Phase 1 nicht benutzt */
/* [offen] X-/Y-Versatz des 2,06"-Panels (Waveshare-2.06-Beispiel nicht ausgewertet); 0 bis zur Pruefung.
 * Das 1,8"-Prototyp-Panel braucht 0x10, das hier ist ein anderes Modul. */
#define BOARD_LCD_GAP_X_V2   0
#define BOARD_LCD_GAP_X_V1   0
/* DSI_PWR_EN (FPC-Pin 21) liegt per 4,7 k fest auf 3V3, TP_RESET (Pin 9) per 10 k: nichts zu schalten. */

/* ---- I2C [Platine: IO6 = SDA, IO7 = SCL; Pull-ups R120/R121 (2,2 k) auf der Hauptplatine] ---- */
#define BOARD_I2C_PORT       I2C_NUM_0
#define BOARD_I2C_SDA        GPIO_NUM_6
#define BOARD_I2C_SCL        GPIO_NUM_7
#define BOARD_I2C_FREQ_HZ    400000
#define BOARD_I2C_INTERNAL_PULLUP 0
/* Adressen am Bus: 0x1C AT42QT2120, 0x5A DRV2605L (Klickrad), 0x36 MAX17048, 0x47 TUSB320LAI (ADDR = GND),
 * Display-Touch [offen: Controller/Adresse des 2,06"-Moduls nicht geklaert], CS43131 0x30..0x33 [offen, aus
 * docs/AUDIO.md, mit [?] markiert] liegt hinter dem Pegelwandler PCA9306 (U30; Segment DAC_SDA/DAC_SCL, EN-Knoten
 * PCA_EN = 200 k nach 3V3 + 100 pF, kein GPIO). Kein TCA9554 (0x20), kein 0x15/0x38 von Waveshare. */
#define BOARD_ADDR_MAX17048  0x36
#define BOARD_ADDR_TUSB320   0x47
#define BOARD_ADDR_CS43131   0x30   /* [offen] 0x30..0x33 */
#define BOARD_ADDR_TOUCH_V2  0x15   /* [offen] nur fuer board_touch_is_v2(); Controller des 2,06"-Moduls ungeklaert */
#define BOARD_ADDR_TOUCH_V1  0x38
#define BOARD_HAS_TCA9554    0

/* ---- Klickrad-Modul v2 (Stecker J21: 1 3V3, 2 GND, 3 SDA, 4 SCL, 5 CHANGE, 6 Reserve) ---- */
#define WHEEL_ADDR_MPR121    0x5B   /* v1, am Endgeraet nicht vorgesehen */
#define WHEEL_ADDR_QT2120    0x1C
#define WHEEL_ADDR_DRV2605L  0x5A
#define WHEEL_INT_GPIO       GPIO_NUM_0    /* WHEEL_INT = CHANGE, LP-GPIO IO0 (Weckquelle), R136 10 k Pull-up auf der Platine */
#define WHEEL_BTN_GPIO       GPIO_NUM_NC   /* Pin 6 ist Reserve; Mitteltaste nur kapazitiv (QT2120 Taste 3) */
#define WHEEL_BTN_USED       0
/* Eigener Wheel-Bus gibt es nicht (Kconfig-Option nur beim Prototyp). */
#define WHEEL_I2C_PORT2      I2C_NUM_1
#define WHEEL_I2C2_SDA       GPIO_NUM_NC
#define WHEEL_I2C2_SCL       GPIO_NUM_NC

/* ---- Versorgung / weitere Signale der Platine (Phase 1: nur der Power-Latch wird benutzt) ---- */
/* Power-Latch: SW1 schaltet nur kurz ein, der S31 muss SYS_PWR_EN frueh im Start halten, sonst faellt die
 * Versorgung nach dem Loslassen wieder ab. [offen] Aktivpegel nicht aus der README ablesbar, high angenommen;
 * Schaltplan (Netz SYS_PWR_EN, Q/LDO_EN) vor dem ersten Einschalten pruefen. */
#define BOARD_PWR_HOLD_GPIO   GPIO_NUM_4
#define BOARD_PWR_HOLD_LEVEL  1
#define BOARD_KEY_LOCK_GPIO   GPIO_NUM_5    /* Ein/Aus-Taster lesen (LP-GPIO, Weckquelle), Phase 1 nicht benutzt */
#define BOARD_FG_ALRT_GPIO    GPIO_NUM_1    /* MAX17048 ALRT, nicht benutzt */
#define BOARD_HOST_EN_GPIO    GPIO_NUM_2    /* Host-VBUS an/aus, nicht benutzt (Reset-Zustand: aus) */
#define BOARD_TUSB_ID_GPIO    GPIO_NUM_3
#define BOARD_TUSB_INT_GPIO   GPIO_NUM_18
#define BOARD_CHG_STAT1_GPIO  GPIO_NUM_13   /* MCP73871; SEL/PROG2 fest verdrahtet, keine GPIO */
#define BOARD_CHG_STAT2_GPIO  GPIO_NUM_16
#define BOARD_CHG_PG_GPIO     GPIO_NUM_17
/* DAC-Reset mit Sicherung (Rev. 3b): Gate von Q20 liegt per Pull-up an 3V3 => Pin offen/high = DAC in RESET,
 * low = RESET freigegeben; Q21/Q22 halten RESET ohne 3V3 ebenfalls low. Phase 1 laesst den Pin unberuehrt
 * (DAC bleibt im Reset, kein Audio). Beim spaeteren Audio-Code: erst 3V3/1,8 V stabil, dann IO20 auf low. */
#define BOARD_DAC_RESET_GPIO  GPIO_NUM_20
#define BOARD_DAC_INT_GPIO    GPIO_NUM_21   /* aktiv low, 10 k Pull-up */
#define BOARD_I2S_BCLK_GPIO   GPIO_NUM_22   /* S31 = I2S-Slave, DAC liefert Takt (kein MCLK) */
#define BOARD_I2S_LRCK_GPIO   GPIO_NUM_23
#define BOARD_I2S_DOUT_GPIO   GPIO_NUM_24
#define BOARD_SD_CD_GPIO      GPIO_NUM_25
#define BOARD_SD_VDD_EN_GPIO  GPIO_NUM_42
/* SDMMC Slot 2: feste Pads IO35..IO40 (D0..D3, CLK, CMD; Zuordnung in der README, nicht hier).
 * Nicht benutzen (Strapping/Boot/Debug): IO36, IO37, IO60, IO61 (BOOT, Taster SW2), IO33/IO34 (USB-Serial/JTAG),
 * TX0/RX0, EN (Taster SW3). BOOT/EN-Taster brauchen keine Firmware. */
/* Keine Latenz-Messpunkte vergeben (Kconfig-Option nur beim Prototyp). */
#define PROBE_STEP_GPIO      GPIO_NUM_NC
#define PROBE_HAPTIC_GPIO    GPIO_NUM_NC
