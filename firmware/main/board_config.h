#pragma once
/**
 * Zentrale Hardware-Konfiguration: Waveshare ESP32-S3-Touch-AMOLED-1.8 + Klickrad-Modul.
 *
 * Status der Angaben:
 *   [geprüft]   aus Waveshare-Beispielcode (github.com/waveshareteam/ESP32-S3-Touch-AMOLED-1.8)
 *               bzw. Schaltplan-Recherche (docs/RECHERCHE.md)
 *   [Vorschlag] frei gewählt, am echten Board noch zu prüfen
 *   [prüfen]    unsicher, nicht verifiziert
 * Alles mit [Vorschlag]/[prüfen] ist nicht an Hardware getestet.
 */
#include "driver/gpio.h"
#include "driver/i2c_master.h"

/* ---- Display (QSPI) [geprüft: Waveshare ESP-IDF-Beispiel 13_display_colorbar] ---- */
#define BOARD_LCD_HOST       SPI2_HOST
#define BOARD_LCD_H_RES      368
#define BOARD_LCD_V_RES      448
#define BOARD_LCD_CS         GPIO_NUM_12
#define BOARD_LCD_SCLK       GPIO_NUM_11
#define BOARD_LCD_D0         GPIO_NUM_4
#define BOARD_LCD_D1         GPIO_NUM_5
#define BOARD_LCD_D2         GPIO_NUM_6
#define BOARD_LCD_D3         GPIO_NUM_7
/* Kein Reset-GPIO: LCD_RST hängt am IO-Expander (EXIO0) */
#define BOARD_LCD_RST_GPIO   GPIO_NUM_NC
/* V2 (CO5300) braucht einen X-Versatz von 0x10 [geprüft: Waveshare-Beispiel]; V1 (SH8601) 0 [prüfen] */
#define BOARD_LCD_GAP_X_V2   0x10
#define BOARD_LCD_GAP_X_V1   0

/* ---- Gemeinsamer I2C-Bus [geprüft]: Touch, PMU, IO-Expander, Codec, IMU, RTC, Klickrad ---- */
#define BOARD_I2C_PORT       I2C_NUM_0
#define BOARD_I2C_SDA        GPIO_NUM_15
#define BOARD_I2C_SCL        GPIO_NUM_14
#define BOARD_I2C_FREQ_HZ    400000
/* 2,2 kOhm Pull-ups liegen auf dem Board [geprüft laut Schaltplan, Zuordnung zu 3V3 nicht eigens geprüft];
 * auf dem Klickrad-Modul keine weiteren bestücken. Interne Pull-ups daher aus. */
#define BOARD_I2C_INTERNAL_PULLUP 0

/* Belegte Adressen [geprüft bzw. laut Recherche]: 0x15 CST820 (V2) / 0x38 FT3168 (V1), 0x18 ES8311,
 * 0x20 TCA9554, 0x34 AXP2101, 0x51 PCF85063, 0x6B QMI8658 -> kein Konflikt mit 0x5A / 0x5B */
#define BOARD_ADDR_TCA9554   0x20
#define BOARD_ADDR_TOUCH_V2  0x15
#define BOARD_ADDR_TOUCH_V1  0x38

/* ---- IO-Expander TCA9554 [geprüft: Waveshare board_variant.c] ----
 * Ausgangsregister 0x01, Konfigurationsregister 0x03 (0 = Ausgang) */
#define TCA_REG_OUTPUT       0x01
#define TCA_REG_CONFIG       0x03
#define TCA_BIT_LCD_RST      (1u << 0)
#define TCA_BIT_DSI_PWR_EN   (1u << 1)   /* Display-Versorgung */
#define TCA_BIT_TOUCH_RST    (1u << 2)
#define TCA_BIT_SD_CS        (1u << 7)
#define TCA_OUTPUT_MASK      (TCA_BIT_LCD_RST | TCA_BIT_DSI_PWR_EN | TCA_BIT_TOUCH_RST | TCA_BIT_SD_CS)

/* ---- Klickrad-Modul ---- */
#define WHEEL_ADDR_MPR121    0x5B   /* [Schnittstelle TEILE.md] ADDR an VDD */
#define WHEEL_ADDR_DRV2605L  0x5A   /* [Schnittstelle TEILE.md] fest */
/* Pads auf dem Waveshare-Board: GPIO17 und GPIO18 sind laut Schaltplan reine Testpunkte (TP11/TP12)
 * ohne weitere Last und auf 1,27-mm-Pads geführt. Zuordnung INT/BTN ist ein Vorschlag [Vorschlag]. */
#define WHEEL_INT_GPIO       GPIO_NUM_17   /* MPR121-IRQ, open drain, aktiv low (interner Pull-up an) */
#define WHEEL_BTN_GPIO       GPIO_NUM_18   /* Mitteltaste, aktiv low (interner Pull-up an) */

/* Optional: eigener I2C-Bus fürs Klickrad statt des gemeinsamen (Kconfig). Pins [prüfen]. */
#define WHEEL_I2C_PORT2      I2C_NUM_1
#define WHEEL_I2C2_SDA       GPIO_NUM_41   /* [prüfen] */
#define WHEEL_I2C2_SCL       GPIO_NUM_42   /* [prüfen] */

/* ---- Latenz-Messpunkte (Logic Analyzer), siehe Kconfig ---- */
#define PROBE_STEP_GPIO      GPIO_NUM_38   /* toggelt beim Erkennen eines Rasterschritts [Vorschlag; Pad laut Recherche frei] */
#define PROBE_HAPTIC_GPIO    GPIO_NUM_39   /* toggelt direkt nach dem I2C-Befehl an den DRV2605L [Vorschlag] */
