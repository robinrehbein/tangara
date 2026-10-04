/*
 * Copyright 2023 jacqueline <me@jacqueline.id.au>
 * (Portierung nach C für den Nano-Player: Register, Init-Sequenz und Statuslogik aus Tangara,
 *  src/drivers/touchwheel.cpp, cool tech zone)
 *
 * SPDX-License-Identifier: GPL-3.0-only
 */
#include <stdlib.h>
#include "at42qt2120.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

static const char *TAG = "at42qt2120";

/* Registeradressen aus Tangara (Datenblatt Abschnitt 5) */
enum {
    REG_FIRMWARE_VERSION    = 1,
    REG_DETECTION_STATUS    = 2,
    REG_KEY_STATUS_A        = 3,
    REG_KEY_STATUS_B        = 4,
    REG_SLIDER_POSITION     = 5,
    REG_CALIBRATE           = 6,
    REG_RESET               = 7,
    REG_LOW_POWER           = 8,
    REG_RECALIBRATION_DELAY = 12,
    REG_SLIDER_OPTIONS      = 14,
    REG_CHARGE_TIME         = 15,
    REG_DETECT_THRESHOLD_BASE = 16,
    REG_KEY_CONTROL_BASE    = 28,
    REG_PULSE_SCALE_BASE    = 40,
};

#define I2C_TIMEOUT_MS 100

struct at42qt2120 {
    i2c_master_dev_handle_t dev;
};

esp_err_t at42qt2120_write_reg(at42qt2120_handle_t h, uint8_t reg, uint8_t val)
{
    /* Register <= 5 sind nicht beschreibbar (Tangara: assert) */
    if (reg <= 5) return ESP_ERR_INVALID_ARG;
    uint8_t cmd[2] = {reg, val};
    esp_err_t e = i2c_master_transmit(h->dev, cmd, 2, I2C_TIMEOUT_MS);
    if (e != ESP_OK) ESP_LOGW(TAG, "write 0x%02X failed: %s", reg, esp_err_to_name(e));
    return e;
}

esp_err_t at42qt2120_read_reg(at42qt2120_handle_t h, uint8_t reg, uint8_t *val)
{
    return i2c_master_transmit_receive(h->dev, &reg, 1, val, 1, I2C_TIMEOUT_MS);
}

bool at42qt2120_angle_within(int16_t wheel_angle, int16_t target_angle, int threshold)
{
    int16_t difference = (wheel_angle - target_angle + 127 + 255) % 255 - 127;
    return difference <= threshold && difference >= -threshold;
}

esp_err_t at42qt2120_init(i2c_master_bus_handle_t bus, at42qt2120_handle_t *out)
{
    if (!bus || !out) return ESP_ERR_INVALID_ARG;
    at42qt2120_handle_t h = calloc(1, sizeof(*h));
    if (!h) return ESP_ERR_NO_MEM;
    const i2c_device_config_t dc = {
        .dev_addr_length = I2C_ADDR_BIT_LEN_7,
        .device_address = AT42QT2120_ADDR,
        .scl_speed_hz = 400000,
    };
    esp_err_t e = i2c_master_bus_add_device(bus, &dc, &h->dev);
    if (e != ESP_OK) { free(h); return e; }

    uint8_t fw = 0;
    e = at42qt2120_read_reg(h, REG_FIRMWARE_VERSION, &fw);
    if (e != ESP_OK) {
        ESP_LOGE(TAG, "kein Chip auf 0x%02X (Klickrad angeschlossen?)", AT42QT2120_ADDR);
        i2c_master_bus_rm_device(h->dev);
        free(h);
        return e;
    }
    ESP_LOGI(TAG, "Firmware-Version 0x%02X", fw);

    at42qt2120_write_reg(h, REG_RESET, 1);
    vTaskDelay(pdMS_TO_TICKS(300));

    /* Tasten 0, 1 und 2 als Wheel konfigurieren (Bit 7 = Slider/Wheel an, Bit 6 = Wheel). */
    at42qt2120_write_reg(h, REG_SLIDER_OPTIONS, 0b11000000);

    /* Adjacent Key Suppression: Wheel-Tasten in Gruppe 1. */
    at42qt2120_write_reg(h, REG_KEY_CONTROL_BASE + 0, 0b100);
    at42qt2120_write_reg(h, REG_KEY_CONTROL_BASE + 1, 0b100);
    at42qt2120_write_reg(h, REG_KEY_CONTROL_BASE + 2, 0b100);
    /* Mitteltaste: keine AKS-Gruppe (Tangara behandelt das in Software). */
    at42qt2120_write_reg(h, REG_KEY_CONTROL_BASE + 3, 0b0);
    /* Touch-Guard: als Guard, Gruppe 1. */
    at42qt2120_write_reg(h, REG_KEY_CONTROL_BASE + 4, 0b10100);

    /* Langes Auflegen des Fingers ist normal: automatische Rekalibrierung aus, sonst wird der
     * Finger "wegkalibriert". */
    at42qt2120_write_reg(h, REG_RECALIBRATION_DELAY, 0);

    at42qt2120_write_reg(h, REG_CHARGE_TIME, 0x10);

    /* Unbenutzte Zusatztasten: alle abgeschaltet. */
    for (int i = 5; i < 12; i++) at42qt2120_write_reg(h, REG_KEY_CONTROL_BASE + i, 1);

    *out = h;
    return ESP_OK;
}

esp_err_t at42qt2120_read(at42qt2120_handle_t h, at42qt2120_data_t *d)
{
    uint8_t reg = REG_DETECTION_STATUS;
    uint8_t buf[4];  /* 2 = Detection Status, 3 = Key Status A, 4 = Key Status B, 5 = Slider Position */
    esp_err_t e = i2c_master_transmit_receive(h->dev, &reg, 1, buf, sizeof buf, I2C_TIMEOUT_MS);
    if (e != ESP_OK) return e;
    uint8_t status = buf[0];
    d->calibrating = (status & 0x80) != 0;
    if (d->calibrating) {
        d->wheel_touched = d->button_touched = false;
        return ESP_OK;
    }
    /* Bit 1 = Slider/Wheel erkannt, Bit 0 = mindestens eine Taste. Wheel-Tasten lösen Bit 0 ebenfalls aus. */
    if (status & 0b10) d->wheel_position = buf[3];
    if (status & 0b1) {
        d->button_touched = (buf[1] & 0b1000) != 0;
        d->wheel_touched = (buf[1] & 0b111) != 0;
    } else {
        d->button_touched = false;
        d->wheel_touched = false;
    }
    return ESP_OK;
}

esp_err_t at42qt2120_recalibrate(at42qt2120_handle_t h) { return at42qt2120_write_reg(h, REG_CALIBRATE, 1); }

esp_err_t at42qt2120_low_power(at42qt2120_handle_t h, bool en)
{
    return at42qt2120_write_reg(h, REG_LOW_POWER, en ? 0 : 1);
}
