/*
 * Copyright 2023 jacqueline <me@jacqueline.id.au>
 * (Portierung nach C für den Nano-Player: Register, Init-Sequenz und Statuslogik aus Tangara,
 *  src/drivers/touchwheel.cpp, cool tech zone)
 *
 * SPDX-License-Identifier: GPL-3.0-only
 */
#pragma once
/**
 * Treiber für den Microchip AT42QT2120 (12 Tasten, Wheel-/Slider-Modus), I2C-Master-API von ESP-IDF.
 *
 * Belegung wie bei Tangara: Tasten 0..2 bilden das Wheel (Position 0..255), Taste 3 ist die Mitteltaste,
 * Taste 4 ist ein Guard (Touch-Guard gegen Fehlauslösung), Tasten 5..11 sind abgeschaltet.
 * CHANGE (aktiv low, open drain) liegt am Stecker-Pin 5 des Klickrad-Moduls.
 */
#include <stdint.h>
#include <stdbool.h>
#include "esp_err.h"
#include "driver/i2c_master.h"

#ifdef __cplusplus
extern "C" {
#endif

#define AT42QT2120_ADDR 0x1C

typedef struct at42qt2120 *at42qt2120_handle_t;

typedef struct {
    bool    wheel_touched;
    bool    button_touched;
    uint8_t wheel_position;  ///< 0..255, nur gültig bei wheel_touched
    bool    calibrating;     ///< Chip kalibriert gerade; Werte ignorieren
} at42qt2120_data_t;

/** Gerät anlegen, Reset (300 ms Wartezeit), Wheel-Konfiguration wie Tangara schreiben. */
esp_err_t at42qt2120_init(i2c_master_bus_handle_t bus, at42qt2120_handle_t *out);

/**
 * Status, Tastenzustand und Wheel-Position in einer I2C-Transaktion lesen (Register 2..5).
 * Das Lesen des Status-Registers löscht auch die CHANGE-Leitung.
 * Gegenüber Tangara: Es wird immer gelesen, nicht nur bei CHANGE = low, weil sich die Position
 * beim Drehen nicht in jedem Fall als CHANGE meldet (am echten Rad prüfen).
 */
esp_err_t at42qt2120_read(at42qt2120_handle_t h, at42qt2120_data_t *data);

/** Kalibrierung auslösen (Register CALIBRATE). */
esp_err_t at42qt2120_recalibrate(at42qt2120_handle_t h);

/** Low-Power-Modus-Register wie Tangara (en = true schreibt 0, sonst 1); Bedeutung gegen das Datenblatt prüfen. */
esp_err_t at42qt2120_low_power(at42qt2120_handle_t h, bool en);

/** Winkelvergleich auf dem Kreis 0..255 (wie TouchWheel::isAngleWithin in Tangara). */
bool at42qt2120_angle_within(int16_t wheel_angle, int16_t target_angle, int threshold);

esp_err_t at42qt2120_read_reg(at42qt2120_handle_t h, uint8_t reg, uint8_t *val);
esp_err_t at42qt2120_write_reg(at42qt2120_handle_t h, uint8_t reg, uint8_t val);

#ifdef __cplusplus
}
#endif
