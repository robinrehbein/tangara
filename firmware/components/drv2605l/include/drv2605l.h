/*
 * Copyright 2023 jacqueline <me@jacqueline.id.au>, robin <robin@rhoward.id.au> (Tangara, cool tech zone)
 * Siehe drv2605l.c.
 *
 * SPDX-License-Identifier: GPL-3.0-only
 */
#pragma once
/**
 * Treiber für den TI DRV2605L (Haptik-Treiber) im LRA-Betrieb, I2C-Master-API von ESP-IDF 5.x.
 * Nicht thread-sicher: pro Instanz nur aus einem Task aufrufen (oder extern sperren).
 */
#include <stdint.h>
#include <stdbool.h>
#include "esp_err.h"
#include "driver/i2c_master.h"

#ifdef __cplusplus
extern "C" {
#endif

#define DRV2605L_ADDR 0x5A

#include "drv2605l_effects.h"

typedef struct drv2605l *drv2605l_handle_t;

typedef struct {
    uint32_t lra_freq_hz;       ///< Resonanzfrequenz des LRA (Datenblatt), für DRIVE_TIME
    uint32_t rated_mvrms;       ///< Nennspannung des LRA in mV RMS (Datenblatt)
    uint32_t overdrive_mvpeak;  ///< Maximale Spitzenspannung (Overdrive-Clamp) in mV
    bool     use_stored_cal;    ///< true: cal-Werte unten statt Auto-Kalibrierung setzen
    uint8_t  cal_comp;          ///< A_CAL_COMP (nur mit use_stored_cal)
    uint8_t  cal_bemf;          ///< A_CAL_BEMF (nur mit use_stored_cal)
    uint8_t  cal_bemf_gain;     ///< BEMF_GAIN (0..3, nur mit use_stored_cal)
    bool     motor_erm;         ///< true: ERM-Motor (offener Regelkreis, Bibliothek C) statt LRA, wie Tangara
    bool     disable_ack_check; ///< ACK-Prüfung abschalten (Tangara-Workaround: Chip NACKt manchmal)
    bool     interrupt_running; ///< vor jedem Effekt laufenden abbrechen (GO = 0), wie Tangara
} drv2605l_config_t;

typedef struct {
    bool    ok;        ///< DIAG_RESULT == 0 (Kalibrierung erfolgreich)
    uint8_t comp;      ///< A_CAL_COMP
    uint8_t bemf;      ///< A_CAL_BEMF
    uint8_t bemf_gain; ///< BEMF_GAIN (aus Register 0x1A)
} drv2605l_cal_result_t;

/** Gerät am Bus anlegen, Chip-ID prüfen, Reset, LRA-Modus + Bibliothek 6 (LRA) einstellen. */
esp_err_t drv2605l_init(i2c_master_bus_handle_t bus, const drv2605l_config_t *cfg,
                        drv2605l_handle_t *out);

/** Auto-Kalibrierung (ca. 1 s, LRA schwingt dabei hörbar). Ergebnis optional. */
esp_err_t drv2605l_autocalibrate(drv2605l_handle_t h, drv2605l_cal_result_t *result);

/** Wählt Bibliothek (1..5 ERM, 6 LRA). */
esp_err_t drv2605l_select_library(drv2605l_handle_t h, uint8_t lib);

/**
 * Spielt einen Effekt (1..123) aus der Bibliothek ab. Schnellster Pfad: Ist der Effekt schon als
 * einziger Eintrag der Wellenform-Sequenz geladen, wird nur das GO-Bit geschrieben (1 Transaktion,
 * 2 Bytes), sonst Sequenz + GO in einer Burst-Transaktion.
 */
esp_err_t drv2605l_play_effect(drv2605l_handle_t h, uint8_t effect);

/** Sequenz mit bis zu 8 Effekten (0 beendet die Sequenz; 0x80|n = Pause n*10 ms). */
esp_err_t drv2605l_play_sequence(drv2605l_handle_t h, const uint8_t *effects, size_t n);

/** Wiedergabe sofort stoppen. */
esp_err_t drv2605l_stop(drv2605l_handle_t h);

/** In den Standby (Strom sparen) bzw. aufwecken. */
esp_err_t drv2605l_standby(drv2605l_handle_t h, bool standby);

esp_err_t drv2605l_read_reg(drv2605l_handle_t h, uint8_t reg, uint8_t *val);
esp_err_t drv2605l_write_reg(drv2605l_handle_t h, uint8_t reg, uint8_t val);

#ifdef __cplusplus
}
#endif
