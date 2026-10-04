/*
 * Copyright 2023 jacqueline <me@jacqueline.id.au>, robin <robin@rhoward.id.au> (Tangara, cool tech zone)
 * Init-Sequenz, LRA-/ERM-Einstellungen und Abspiellogik aus Tangara: src/drivers/haptics.cpp.
 * Anpassungen für den Nano-Player (C, Auto-Kalibrierung als eigene Funktion, Burst-Pfad, Formeln).
 *
 * SPDX-License-Identifier: GPL-3.0-only
 */
#include <math.h>
#include <stdlib.h>
#include <string.h>
#include "drv2605l.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

static const char *TAG = "drv2605l";

#define REG_STATUS      0x00
#define REG_MODE        0x01
#define REG_RTPIN       0x02
#define REG_LIBRARY     0x03
#define REG_WAVESEQ1    0x04
#define REG_GO          0x0C
#define REG_RATED_V     0x16
#define REG_OD_CLAMP    0x17
#define REG_CAL_COMP    0x18
#define REG_CAL_BEMF    0x19
#define REG_FEEDBACK    0x1A
#define REG_CONTROL1    0x1B
#define REG_CONTROL2    0x1C
#define REG_CONTROL3    0x1D
#define REG_CONTROL4    0x1E

#define MODE_INTERNAL_TRIGGER 0x00
#define MODE_AUTOCAL          0x07
#define MODE_STANDBY_BIT      0x40
#define MODE_RESET_BIT        0x80

#define I2C_TIMEOUT_MS 20

struct drv2605l {
    i2c_master_dev_handle_t dev;
    drv2605l_config_t cfg;
    uint8_t loaded_effect;  ///< Effekt in Slot 1, Slot 2 = 0 (Ende); 0 = unbekannt
};

esp_err_t drv2605l_write_reg(drv2605l_handle_t h, uint8_t reg, uint8_t val)
{
    uint8_t buf[2] = {reg, val};
    return i2c_master_transmit(h->dev, buf, 2, I2C_TIMEOUT_MS);
}

esp_err_t drv2605l_read_reg(drv2605l_handle_t h, uint8_t reg, uint8_t *val)
{
    return i2c_master_transmit_receive(h->dev, &reg, 1, val, 1, I2C_TIMEOUT_MS);
}

/* Formeln nach Datenblatt SLOS854 (Rated Voltage / Overdrive Clamp), mit SAMPLE_TIME = 300 us (Control2 = 0xF5).
 * RATED_VOLTAGE = V_rms * sqrt(1 - (4*300 us + 300 us) * f) / 21,32 mV. Gegenprobe mit Tangara: 1,8 V RMS bei
 * 235 Hz ergibt 68, Tangara schreibt 0x46 = 70. (Die frühere Version dieser Datei hatte sqrt im Nenner: Fehler.)
 * OD_CLAMP = V_peak / (21,96 mV * sqrt(1 - 800 us * f)); Tangara nimmt für 2,6 V den festen Wert 0x7B (123),
 * die Formel ergibt 131, wir begrenzen auf den Tangara-Wert, solange nicht am Motor gemessen ist. */
static uint8_t rated_voltage_reg(uint32_t mvrms, uint32_t f_hz)
{
    float k = 1.0f - (4.0f * 300e-6f + 300e-6f) * (float)f_hz;
    if (k < 0.05f) k = 0.05f;
    float v = (float)mvrms * sqrtf(k) / 21.32f;
    if (v > 255.f) v = 255.f;
    return (uint8_t)(v + 0.5f);
}

static uint8_t od_clamp_reg(uint32_t mvpeak, uint32_t f_hz)
{
    float k = 1.0f - 800e-6f * (float)f_hz;
    if (k < 0.05f) k = 0.05f;
    float v = (float)mvpeak / (21.96f * sqrtf(k));
    if (v > 255.f) v = 255.f;
    return (uint8_t)v;
}

/* ERM wie Tangara: offener Regelkreis, N_ERM_LRA = 0, ERM_OPEN_LOOP = 1, Bibliothek C. */
static esp_err_t setup_erm(drv2605l_handle_t h)
{
    esp_err_t e;
    if ((e = drv2605l_write_reg(h, REG_MODE, MODE_INTERNAL_TRIGGER)) != ESP_OK) return e;
    if ((e = drv2605l_write_reg(h, REG_FEEDBACK, 0xB6 & ~0x80)) != ESP_OK) return e;
    if ((e = drv2605l_write_reg(h, REG_CONTROL3, 0x20)) != ESP_OK) return e;
    return drv2605l_write_reg(h, REG_LIBRARY, 3);
}

static esp_err_t setup_lra(drv2605l_handle_t h)
{
    const drv2605l_config_t *c = &h->cfg;
    esp_err_t e;
    /* Aus Standby, interne Trigger */
    if ((e = drv2605l_write_reg(h, REG_MODE, MODE_INTERNAL_TRIGGER)) != ESP_OK) return e;
    if ((e = drv2605l_write_reg(h, REG_LIBRARY, 6)) != ESP_OK) return e;       /* LRA-Bibliothek */
    if ((e = drv2605l_write_reg(h, REG_RATED_V, rated_voltage_reg(c->rated_mvrms, c->lra_freq_hz))) != ESP_OK) return e;
    uint8_t od = od_clamp_reg(c->overdrive_mvpeak, c->lra_freq_hz);
    if (c->overdrive_mvpeak == 2600 && c->lra_freq_hz == 235) od = 0x7B;  /* Tangara-Wert */
    if ((e = drv2605l_write_reg(h, REG_OD_CLAMP, od)) != ESP_OK) return e;
    /* DRIVE_TIME = (0,5/f - 0,5 ms) / 0,1 ms; Bits 4:0. Control1 Bit 7 = STARTUP_BOOST (Tangara: 0b10010000
     * für 235 Hz = DRIVE_TIME 16, also 2,1 ms). */
    float dt = (0.5f / (float)c->lra_freq_hz - 0.0005f) / 0.0001f;
    if (dt < 0) dt = 0;
    if (dt > 31) dt = 31;
    if ((e = drv2605l_write_reg(h, REG_CONTROL1, 0x80 | (uint8_t)(dt + 0.5f))) != ESP_OK) return e;
    /* Control2: Reset-Wert 0xF5 (BIDIR_INPUT, BRAKE_STAB, SAMPLE_TIME 300 us, BLANKING, IDISS) wie Tangara */
    if ((e = drv2605l_write_reg(h, REG_CONTROL2, 0xF5)) != ESP_OK) return e;
    /* Control3: Tangara 0b10000000 = NG_THRESH 4 % (Rauschgrenze), LRA im geschlossenen Regelkreis */
    if ((e = drv2605l_write_reg(h, REG_CONTROL3, 0x80)) != ESP_OK) return e;
    /* Control4: AUTO_CAL_TIME = 3 (1000 ms; Tangara lässt den Reset-Wert) */
    if ((e = drv2605l_write_reg(h, REG_CONTROL4, 0x30)) != ESP_OK) return e;
    /* Feedback: N_ERM_LRA=1, BRAKE_FACTOR=3 (Bits 6:4), LOOP_GAIN=1 (3:2), BEMF_GAIN=2 (1:0) = 0b10110110
     * wie Tangara (mit gespeicherter Kalibrierung: 0b10110100 | gain) */
    uint8_t gain = c->use_stored_cal ? (c->cal_bemf_gain & 3) : 2;
    if ((e = drv2605l_write_reg(h, REG_FEEDBACK, 0x80 | (3 << 4) | (1 << 2) | gain)) != ESP_OK) return e;
    if (c->use_stored_cal) {
        if ((e = drv2605l_write_reg(h, REG_CAL_COMP, c->cal_comp)) != ESP_OK) return e;
        if ((e = drv2605l_write_reg(h, REG_CAL_BEMF, c->cal_bemf)) != ESP_OK) return e;
    }
    return ESP_OK;
}

esp_err_t drv2605l_init(i2c_master_bus_handle_t bus, const drv2605l_config_t *cfg,
                        drv2605l_handle_t *out)
{
    if (!bus || !cfg || !out || cfg->lra_freq_hz < 50) return ESP_ERR_INVALID_ARG;
    drv2605l_handle_t h = calloc(1, sizeof(*h));
    if (!h) return ESP_ERR_NO_MEM;
    h->cfg = *cfg;
    const i2c_device_config_t dc = {
        .dev_addr_length = I2C_ADDR_BIT_LEN_7,
        .device_address = DRV2605L_ADDR,
        .scl_speed_hz = 400000,
        /* Tangara: "Why does the driver sometimes NACK?" -> ACK-Prüfung abschaltbar (Kconfig) */
        .flags.disable_ack_check = cfg->disable_ack_check,
    };
    esp_err_t e = i2c_master_bus_add_device(bus, &dc, &h->dev);
    if (e != ESP_OK) goto fail;

    /* Reset; danach ~1 ms warten, bis das Mode-Register wieder lesbar ist */
    e = drv2605l_write_reg(h, REG_MODE, MODE_RESET_BIT);
    if (e != ESP_OK) { ESP_LOGE(TAG, "kein Chip auf 0x%02X (EN-Pin auf 3V3? Verkabelung?)", DRV2605L_ADDR); goto fail_dev; }
    vTaskDelay(pdMS_TO_TICKS(5));

    uint8_t status = 0;
    e = drv2605l_read_reg(h, REG_STATUS, &status);
    if (e != ESP_OK) goto fail_dev;
    uint8_t dev_id = status >> 5; /* 3 = DRV2605, 4 = DRV2604, 5 = DRV2604L, 6 = DRV2605L, 7 = DRV2605 mit LRA */
    ESP_LOGI(TAG, "Status 0x%02X, Geräte-ID %u (6 = DRV2605L)", status, dev_id);
    if (dev_id != 6 && dev_id != 3) ESP_LOGW(TAG, "unerwartete Geräte-ID %u", dev_id);

    e = cfg->motor_erm ? setup_erm(h) : setup_lra(h);
    if (e != ESP_OK) goto fail_dev;
    *out = h;
    return ESP_OK;
fail_dev:
    i2c_master_bus_rm_device(h->dev);
fail:
    free(h);
    return e;
}

esp_err_t drv2605l_autocalibrate(drv2605l_handle_t h, drv2605l_cal_result_t *result)
{
    esp_err_t e = drv2605l_write_reg(h, REG_MODE, MODE_AUTOCAL);
    if (e != ESP_OK) return e;
    if ((e = drv2605l_write_reg(h, REG_GO, 1)) != ESP_OK) return e;
    uint8_t go = 1;
    for (int i = 0; i < 300 && go; i++) { /* max. 3 s */
        vTaskDelay(pdMS_TO_TICKS(10));
        if ((e = drv2605l_read_reg(h, REG_GO, &go)) != ESP_OK) return e;
    }
    if (go) return ESP_ERR_TIMEOUT;
    uint8_t status = 0, comp = 0, bemf = 0, fb = 0;
    drv2605l_read_reg(h, REG_STATUS, &status);
    drv2605l_read_reg(h, REG_CAL_COMP, &comp);
    drv2605l_read_reg(h, REG_CAL_BEMF, &bemf);
    drv2605l_read_reg(h, REG_FEEDBACK, &fb);
    bool ok = (status & 0x1F) == 0;  /* wie Tangara: DIAG_RESULT und Fehlerbits */
    ESP_LOGI(TAG, "Auto-Kalibrierung %s: comp=0x%02X bemf=0x%02X gain=%u", ok ? "OK" : "FEHLGESCHLAGEN",
             comp, bemf, fb & 3);
    if (result) { result->ok = ok; result->comp = comp; result->bemf = bemf; result->bemf_gain = fb & 3; }
    /* Zurück in den Normalbetrieb */
    h->loaded_effect = 0;
    e = drv2605l_write_reg(h, REG_MODE, MODE_INTERNAL_TRIGGER);
    if (e != ESP_OK) return e;
    return ok ? ESP_OK : ESP_FAIL;
}

esp_err_t drv2605l_select_library(drv2605l_handle_t h, uint8_t lib)
{
    return drv2605l_write_reg(h, REG_LIBRARY, lib & 7);
}

esp_err_t drv2605l_play_effect(drv2605l_handle_t h, uint8_t effect)
{
    if (effect == 0 || effect > 123) return ESP_ERR_INVALID_ARG;
    /* Wie Tangara: einen noch laufenden Effekt zuerst abbrechen, das fühlt sich direkter an. */
    if (h->cfg.interrupt_running) drv2605l_write_reg(h, REG_GO, 0);
    if (h->loaded_effect == effect) {
        return drv2605l_write_reg(h, REG_GO, 1);
    }
    /* Register 0x04..0x0B = Sequenz, 0x0C = GO, in einem Burst */
    uint8_t buf[1 + 9] = {REG_WAVESEQ1, effect, 0, 0, 0, 0, 0, 0, 0, 1};
    esp_err_t e = i2c_master_transmit(h->dev, buf, sizeof(buf), I2C_TIMEOUT_MS);
    if (e == ESP_OK) h->loaded_effect = effect;
    return e;
}

esp_err_t drv2605l_play_sequence(drv2605l_handle_t h, const uint8_t *effects, size_t n)
{
    if (n > 8) return ESP_ERR_INVALID_ARG;
    uint8_t buf[1 + 9] = {REG_WAVESEQ1, 0, 0, 0, 0, 0, 0, 0, 0, 1};
    memcpy(&buf[1], effects, n);
    h->loaded_effect = 0;
    return i2c_master_transmit(h->dev, buf, sizeof(buf), I2C_TIMEOUT_MS);
}

esp_err_t drv2605l_stop(drv2605l_handle_t h)
{
    return drv2605l_write_reg(h, REG_GO, 0);
}

esp_err_t drv2605l_standby(drv2605l_handle_t h, bool standby)
{
    return drv2605l_write_reg(h, REG_MODE, standby ? MODE_STANDBY_BIT : MODE_INTERNAL_TRIGGER);
}
