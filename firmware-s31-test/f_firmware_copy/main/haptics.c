/* Copyright 2026 Nano-Player-Projekt
 * SPDX-License-Identifier: GPL-3.0-only */
#include "haptics.h"
#include "board_config.h"
#include "drv2605l.h"
#include "esp_log.h"
#include "esp_timer.h"
#include "nvs.h"
#include "nvs_flash.h"
#include "sdkconfig.h"

static const char *TAG = "haptics";
static drv2605l_handle_t s_drv;
static int64_t s_last_tick_us, s_last_stop_us;
static uint32_t s_ticks, s_skipped;

#if CONFIG_NANO_LATENCY_PROBE
static int s_probe_level;
#define PROBE_AFTER_I2C() do { s_probe_level ^= 1; gpio_set_level(PROBE_HAPTIC_GPIO, s_probe_level); } while (0)
#else
#define PROBE_AFTER_I2C() do {} while (0)
#endif

/* LRA-Kalibrierung im NVS ablegen wie Tangara (NvsStorage::LraCalibration): nur beim ersten Start kalibrieren. */
#define NVS_NS "nano"
#define NVS_KEY "lra_cal"

static bool cal_load(uint8_t out[3])
{
    nvs_handle_t n;
    if (nvs_open(NVS_NS, NVS_READONLY, &n) != ESP_OK) return false;
    size_t len = 3;
    bool ok = nvs_get_blob(n, NVS_KEY, out, &len) == ESP_OK && len == 3;
    nvs_close(n);
    return ok;
}

static void cal_store(const uint8_t v[3])
{
    nvs_handle_t n;
    if (nvs_open(NVS_NS, NVS_READWRITE, &n) != ESP_OK) return;
    nvs_set_blob(n, NVS_KEY, v, 3);
    nvs_commit(n);
    nvs_close(n);
}

static void nvs_ready(void)
{
    esp_err_t e = nvs_flash_init();
    if (e == ESP_ERR_NVS_NO_FREE_PAGES || e == ESP_ERR_NVS_NEW_VERSION_FOUND) {
        nvs_flash_erase();
        nvs_flash_init();
    }
}

#ifdef CONFIG_NANO_HAPTIC_ERM
#define HAPTIC_ERM 1
#else
#define HAPTIC_ERM 0
#endif
#ifdef CONFIG_NANO_HAPTIC_IGNORE_NACK
#define HAPTIC_IGNORE_NACK 1
#else
#define HAPTIC_IGNORE_NACK 0
#endif
#ifdef CONFIG_NANO_HAPTIC_INTERRUPT
#define HAPTIC_INTERRUPT 1
#else
#define HAPTIC_INTERRUPT 0
#endif

esp_err_t haptics_init(i2c_master_bus_handle_t bus)
{
#if CONFIG_NANO_LATENCY_PROBE
    gpio_config_t g = {.pin_bit_mask = 1ULL << PROBE_HAPTIC_GPIO, .mode = GPIO_MODE_OUTPUT};
    gpio_config(&g);
#endif
    nvs_ready();
    uint8_t cal[3];
    bool have_cal = cal_load(cal);
    drv2605l_config_t cfg = {
        .lra_freq_hz = CONFIG_NANO_LRA_FREQ_HZ,
        .rated_mvrms = CONFIG_NANO_LRA_RATED_MVRMS,
        .overdrive_mvpeak = CONFIG_NANO_LRA_OVERDRIVE_MVPEAK,
        .use_stored_cal = have_cal,
        .cal_comp = have_cal ? cal[0] : 0,
        .cal_bemf = have_cal ? cal[1] : 0,
        .cal_bemf_gain = have_cal ? cal[2] : 0,
        .motor_erm = HAPTIC_ERM,
        .disable_ack_check = HAPTIC_IGNORE_NACK,
        .interrupt_running = HAPTIC_INTERRUPT,
    };
    esp_err_t e = drv2605l_init(bus, &cfg, &s_drv);
    if (e != ESP_OK) { ESP_LOGE(TAG, "DRV2605L Init: %s", esp_err_to_name(e)); return e; }
#if CONFIG_NANO_HAPTIC_AUTOCAL
    if (have_cal) {
        ESP_LOGI(TAG, "gespeicherte LRA-Kalibrierung: comp=0x%02X bemf=0x%02X gain=%u", cal[0], cal[1], cal[2]);
    } else if (!HAPTIC_ERM) {
        drv2605l_cal_result_t r;
        e = drv2605l_autocalibrate(s_drv, &r);
        if (e != ESP_OK) {
            ESP_LOGW(TAG, "Auto-Kalibrierung: %s (LRA-Werte in Kconfig pruefen)", esp_err_to_name(e));
        } else {
            uint8_t v[3] = {r.comp, r.bemf, r.bemf_gain};
            cal_store(v);
        }
    }
#endif
    /* Klick-Effekt vorladen (spielt einmal beim Start als Lebenszeichen) */
    drv2605l_play_effect(s_drv, CONFIG_NANO_EFFECT_CLICK);
    return ESP_OK;
}

bool haptics_tick(void)
{
    int64_t now = esp_timer_get_time();
    if (now - s_last_tick_us < CONFIG_NANO_TICK_MIN_INTERVAL_MS * 1000LL) { s_skipped++; return false; }
    s_last_tick_us = now;
    s_ticks++;
    if (s_drv) drv2605l_play_effect(s_drv, CONFIG_NANO_EFFECT_TICK);
    PROBE_AFTER_I2C();
    return true;
}

void haptics_click(void)
{
    if (s_drv) drv2605l_play_effect(s_drv, CONFIG_NANO_EFFECT_CLICK);
    PROBE_AFTER_I2C();
}

bool haptics_endstop(void)
{
    int64_t now = esp_timer_get_time();
    if (now - s_last_stop_us < CONFIG_NANO_ENDSTOP_MIN_INTERVAL_MS * 1000LL) return false;
    s_last_stop_us = now;
    s_last_tick_us = now;   /* wie im Emulator: danach kurz kein Tick */
    if (s_drv) drv2605l_play_effect(s_drv, CONFIG_NANO_EFFECT_ENDSTOP);
    PROBE_AFTER_I2C();
    return true;
}

uint32_t haptics_tick_count(void) { return s_ticks; }
uint32_t haptics_skipped_count(void) { return s_skipped; }
