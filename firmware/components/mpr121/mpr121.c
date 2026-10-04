/* Copyright 2026 Nano-Player-Projekt
 * SPDX-License-Identifier: GPL-3.0-only */
#include <stdlib.h>
#include "mpr121.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

static const char *TAG = "mpr121";

#define REG_TOUCH_STATUS 0x00
#define REG_FILTERED     0x04  /* 2 Byte je Elektrode, LSB zuerst */
#define REG_BASELINE     0x1E  /* 1 Byte je Elektrode (Wert << 2) */
#define REG_MHDR 0x2B
#define REG_TTH0 0x41
#define REG_DEBOUNCE 0x5B
#define REG_CONFIG1 0x5C
#define REG_CONFIG2 0x5D
#define REG_ECR 0x5E
#define REG_AUTOCFG0 0x7B
#define REG_USL 0x7D
#define REG_LSL 0x7E
#define REG_TL 0x7F
#define REG_SOFTRESET 0x80

#define TMO 20

struct mpr121 {
    i2c_master_dev_handle_t dev;
    mpr121_config_t cfg;
};

esp_err_t mpr121_write_reg(mpr121_handle_t h, uint8_t reg, uint8_t val)
{
    uint8_t b[2] = {reg, val};
    return i2c_master_transmit(h->dev, b, 2, TMO);
}

esp_err_t mpr121_read_reg(mpr121_handle_t h, uint8_t reg, uint8_t *val)
{
    return i2c_master_transmit_receive(h->dev, &reg, 1, val, 1, TMO);
}

esp_err_t mpr121_init(i2c_master_bus_handle_t bus, const mpr121_config_t *cfg, mpr121_handle_t *out)
{
    if (!bus || !cfg || !out || cfg->num_electrodes < 1 || cfg->num_electrodes > MPR121_MAX_ELECTRODES)
        return ESP_ERR_INVALID_ARG;
    mpr121_handle_t h = calloc(1, sizeof(*h));
    if (!h) return ESP_ERR_NO_MEM;
    h->cfg = *cfg;
    const i2c_device_config_t dc = {
        .dev_addr_length = I2C_ADDR_BIT_LEN_7,
        .device_address = cfg->address,
        .scl_speed_hz = 400000,
    };
    esp_err_t e = i2c_master_bus_add_device(bus, &dc, &h->dev);
    if (e != ESP_OK) { free(h); return e; }

#define W(r, v) do { e = mpr121_write_reg(h, (r), (v)); if (e != ESP_OK) goto fail; } while (0)
    W(REG_SOFTRESET, 0x63);
    vTaskDelay(pdMS_TO_TICKS(5));
    uint8_t v = 0;
    e = mpr121_read_reg(h, REG_CONFIG2, &v);   /* Default nach Reset: 0x24 */
    if (e != ESP_OK || v != 0x24) {
        ESP_LOGE(TAG, "MPR121 auf 0x%02X antwortet nicht wie erwartet (CONFIG2=0x%02X, err=%s)",
                 cfg->address, v, esp_err_to_name(e));
        if (e == ESP_OK) e = ESP_ERR_INVALID_RESPONSE;
        goto fail;
    }
    W(REG_ECR, 0x00); /* Stop-Modus, Konfiguration nur dort schreibbar */

    /* Baseline-Filter: Standardwerte aus dem NXP-Applikationshinweis AN3944 */
    W(REG_MHDR + 0, 0x01); W(REG_MHDR + 1, 0x01); W(REG_MHDR + 2, 0x0E); W(REG_MHDR + 3, 0x00); /* steigend */
    W(REG_MHDR + 4, 0x01); W(REG_MHDR + 5, 0x05); W(REG_MHDR + 6, 0x01); W(REG_MHDR + 7, 0x00); /* fallend */
    W(0x33, 0x00); W(0x34, 0x00); W(0x35, 0x00); W(0x36, 0x00);                                                 /* Touched */

    for (int i = 0; i < cfg->num_electrodes; i++) {
        W(REG_TTH0 + 2 * i, cfg->touch_threshold);
        W(REG_TTH0 + 2 * i + 1, cfg->release_threshold);
    }
    W(REG_DEBOUNCE, 0x00);
    /* CONFIG1: FFI = 6 Samples (00), CDC. CONFIG2: CDT, SFI = 4 Samples (00), ESI = 1 ms (000)
     * => gefilterter Wert alle 4 ms. */
    uint8_t cdc = cfg->cdc ? cfg->cdc : 16;
    uint8_t cdt = cfg->cdt ? cfg->cdt : 1;
    W(REG_CONFIG1, cdc & 0x3F);
    W(REG_CONFIG2, (cdt & 7) << 5);
    if (cfg->auto_config) {
        /* 3,3 V: USL = 202, TL = 0,9 * USL = 182, LSL = 0,65 * USL = 131; ACE + ARE + AFES=00, SCTS=0 */
        W(REG_USL, 202); W(REG_TL, 182); W(REG_LSL, 131);
        W(REG_AUTOCFG0, 0x0B);  /* FFI(=00 aus Config1), RETRY=00, BVA=10, ARE=1, ACE=1 */
        W(0x7C, 0x00);
    }
    /* ECR: CL = 10 (Baseline-Tracking, Start mit 5 MSB), ELEPROX_EN = 0, ELE_EN = n */
    W(REG_ECR, 0x80 | cfg->num_electrodes);
    vTaskDelay(pdMS_TO_TICKS(20));
#undef W
    *out = h;
    return ESP_OK;
fail:
    i2c_master_bus_rm_device(h->dev);
    free(h);
    return e;
}

esp_err_t mpr121_read_touch(mpr121_handle_t h, uint16_t *mask)
{
    uint8_t reg = REG_TOUCH_STATUS, b[2];
    esp_err_t e = i2c_master_transmit_receive(h->dev, &reg, 1, b, 2, TMO);
    if (e == ESP_OK) *mask = (uint16_t)(b[0] | (b[1] << 8)) & 0x0FFF;
    return e;
}

esp_err_t mpr121_read_filtered(mpr121_handle_t h, uint16_t *out, size_t n)
{
    if (n > MPR121_MAX_ELECTRODES) return ESP_ERR_INVALID_ARG;
    uint8_t reg = REG_FILTERED, b[24];
    esp_err_t e = i2c_master_transmit_receive(h->dev, &reg, 1, b, 2 * n, TMO);
    if (e != ESP_OK) return e;
    for (size_t i = 0; i < n; i++) out[i] = (uint16_t)(b[2 * i] | (b[2 * i + 1] << 8)) & 0x3FF;
    return ESP_OK;
}

esp_err_t mpr121_read_baseline(mpr121_handle_t h, uint16_t *out, size_t n)
{
    if (n > MPR121_MAX_ELECTRODES) return ESP_ERR_INVALID_ARG;
    uint8_t reg = REG_BASELINE, b[12];
    esp_err_t e = i2c_master_transmit_receive(h->dev, &reg, 1, b, n, TMO);
    if (e != ESP_OK) return e;
    for (size_t i = 0; i < n; i++) out[i] = (uint16_t)b[i] << 2;
    return ESP_OK;
}

esp_err_t mpr121_read_status_filtered(mpr121_handle_t h, uint16_t *mask, uint16_t *filtered, size_t n)
{
    if (n > MPR121_MAX_ELECTRODES) return ESP_ERR_INVALID_ARG;
    uint8_t reg = REG_TOUCH_STATUS, b[4 + 24];
    esp_err_t e = i2c_master_transmit_receive(h->dev, &reg, 1, b, 4 + 2 * n, TMO);
    if (e != ESP_OK) return e;
    if (mask) *mask = (uint16_t)(b[0] | (b[1] << 8)) & 0x0FFF;
    for (size_t i = 0; i < n; i++)
        filtered[i] = (uint16_t)(b[4 + 2 * i] | (b[5 + 2 * i] << 8)) & 0x3FF;
    return ESP_OK;
}
