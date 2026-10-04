#pragma once
/** Treiber für den NXP MPR121 (12-Kanal kapazitiver Touch-Controller), I2C-Master-API von ESP-IDF 5.x. */
#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include "esp_err.h"
#include "driver/i2c_master.h"

#ifdef __cplusplus
extern "C" {
#endif

#define MPR121_ADDR_DEFAULT 0x5B  /* ADDR an VDD */
#define MPR121_MAX_ELECTRODES 12

typedef struct mpr121 *mpr121_handle_t;

typedef struct {
    uint8_t  address;         ///< 0x5A..0x5D
    uint8_t  num_electrodes;  ///< 1..12, ELE0..ELE(n-1) aktiv
    bool     auto_config;     ///< Auto-Konfiguration der Ladeströme/-zeiten (3,3 V)
    uint8_t  cdc;             ///< Ladestrom 1..63 uA (ohne auto_config), 0 = Default 16
    uint8_t  cdt;             ///< Ladezeit 1..7 (0,5 us * 2^(n-1)), 0 = Default 1
    uint8_t  touch_threshold;
    uint8_t  release_threshold;
} mpr121_config_t;

#define MPR121_CONFIG_DEFAULT() { \
    .address = MPR121_ADDR_DEFAULT, .num_electrodes = 12, .auto_config = true, \
    .cdc = 0, .cdt = 0, .touch_threshold = 12, .release_threshold = 6 }

/** Soft-Reset, Konfiguration (schnelle Filter, 4 ms Aktualisierung), Elektroden aktivieren. */
esp_err_t mpr121_init(i2c_master_bus_handle_t bus, const mpr121_config_t *cfg, mpr121_handle_t *out);

/** Touch-Status-Bits (Bit n = Elektrode n). */
esp_err_t mpr121_read_touch(mpr121_handle_t h, uint16_t *mask);

/**
 * Gefilterte Messwerte (10 Bit) der ersten n Elektroden. Das ist das, was der Chip an Daten liefert
 * (ein ungefiltertes Rohsignal gibt es beim MPR121 nicht). Touch = Wert fällt unter die Baseline.
 */
esp_err_t mpr121_read_filtered(mpr121_handle_t h, uint16_t *out, size_t n);

/** Baseline-Werte (10 Bit, im Chip 8 Bit << 2). */
esp_err_t mpr121_read_baseline(mpr121_handle_t h, uint16_t *out, size_t n);

/** Touch-Status und gefilterte Werte in einer I2C-Transaktion (schneller Pfad für das Rad). */
esp_err_t mpr121_read_status_filtered(mpr121_handle_t h, uint16_t *mask, uint16_t *filtered, size_t n);

esp_err_t mpr121_read_reg(mpr121_handle_t h, uint8_t reg, uint8_t *val);
esp_err_t mpr121_write_reg(mpr121_handle_t h, uint8_t reg, uint8_t val);

#ifdef __cplusplus
}
#endif
