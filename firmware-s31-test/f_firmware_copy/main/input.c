/* Copyright 2026 Nano-Player-Projekt
 * SPDX-License-Identifier: GPL-3.0-only */
#include <string.h>
#include "sdkconfig.h"
#include "input.h"
#include "board.h"
#include "board_config.h"
#include "clickwheel.h"
#include "driver/gpio.h"
#include "esp_log.h"
#include "esp_timer.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "haptics.h"
#include "model.h"
#if CONFIG_NANO_WHEEL_MPR121
#include "mpr121.h"
#else
#include "at42qt2120.h"
#endif
#include "sdkconfig.h"

static const char *TAG = "input";

#if CONFIG_NANO_WHEEL_MPR121
#define N CONFIG_NANO_WHEEL_SEGMENTS
#else
#define N 12  /* nur für Konstanten der Logik; die Segmente werden beim QT2120 nicht benutzt */
#endif
#define BTN_DEBOUNCE_US 15000

static TaskHandle_t s_task;
#if CONFIG_NANO_WHEEL_MPR121
static mpr121_handle_t s_mpr;
#else
static at42qt2120_handle_t s_qt;
#endif

#if CONFIG_NANO_LATENCY_PROBE
static int s_probe_step_level;
#define PROBE_STEP() do { s_probe_step_level ^= 1; gpio_set_level(PROBE_STEP_GPIO, s_probe_step_level); } while (0)
#else
#define PROBE_STEP() do {} while (0)
#endif

static void IRAM_ATTR isr(void *arg)
{
    BaseType_t woken = pdFALSE;
    vTaskNotifyGiveFromISR(s_task, &woken);
    portYIELD_FROM_ISR(woken);
}

/* Haptik zuerst, direkt hier im Eingabe-Task; das UI zieht sich den Zustand später aus dem Modell. */
static void handle_steps(int steps)
{
    PROBE_STEP();
    model_step_result_t total = {0};
    int dir = steps < 0 ? -1 : 1;
    for (int n = steps < 0 ? -steps : steps; n > 0; n--) {
        model_step_result_t r = model_step(dir);
        total.moved |= r.moved;
        total.hit_end |= r.hit_end;
    }
    if (total.moved) haptics_tick();
    else if (total.hit_end) haptics_endstop();
}

static void input_task(void *arg)
{
    cw_config_t cc = {
        .num_segments = N,
        .first_segment_deg = CONFIG_NANO_WHEEL_FIRST_SEGMENT_DEG,
#if CONFIG_NANO_WHEEL_CLOCKWISE
        .clockwise = true,
#else
        .clockwise = false,
#endif
        .detent_deg = CONFIG_NANO_WHEEL_DETENT_DEG,
#if CONFIG_NANO_WHEEL_MPR121
        .touch_on = CONFIG_NANO_WHEEL_TOUCH_ON,
        .touch_off = CONFIG_NANO_WHEEL_TOUCH_OFF,
        .noise_floor = CONFIG_NANO_WHEEL_NOISE_FLOOR,
#endif
        .tap_slop_deg = CONFIG_NANO_WHEEL_TAP_SLOP_DEG,
        .settle_frames = 2,
    };
    cw_t wheel;
    cw_init(&wheel, &cc);

#if CONFIG_NANO_WHEEL_MPR121
    uint16_t baseline[N], filtered[N], signal[N];
    memset(baseline, 0, sizeof baseline);
    mpr121_read_baseline(s_mpr, baseline, N);
    int baseline_age = 0;
#else
    at42qt2120_data_t qd = {0};
#endif

    bool btn_stable = true;   /* true = nicht gedrückt (aktiv low) */
    int64_t btn_change_us = 0;
    bool touching = false;
    TickType_t last = xTaskGetTickCount();
    int log_div = 0;
    bool extra_active = false;   /* QT2120: Tastenzustand weicht noch vom entprellten Zustand ab */

    for (;;) {
#if CONFIG_NANO_WHEEL_BTN_GPIO
        bool btn_raw = gpio_get_level(WHEEL_BTN_GPIO);
#else
        bool btn_raw = true;
#endif
#if !CONFIG_NANO_WHEEL_MPR121
        if (qd.button_touched) btn_raw = false;   /* Mitteltaste = Taste 3 des QT2120 */
#endif
        int64_t now = esp_timer_get_time();
        bool btn_pending = (btn_raw != btn_stable);
        if (btn_pending) {
            if (btn_change_us == 0) btn_change_us = now;
            if (now - btn_change_us >= BTN_DEBOUNCE_US) {
                btn_stable = btn_raw;
                btn_change_us = 0;
                if (!btn_stable) {              /* gedrückt */
                    haptics_click();
                    if (model_center()) { /* UI zieht Zustand */ }
                }
            }
        } else {
            btn_change_us = 0;
        }

#if CONFIG_NANO_WHEEL_MPR121
        uint16_t mask;
        if (mpr121_read_status_filtered(s_mpr, &mask, filtered, N) == ESP_OK) {
            if (++baseline_age >= 25 || !touching) {   /* Baseline ändert sich langsam */
                mpr121_read_baseline(s_mpr, baseline, N);
                baseline_age = 0;
            }
            for (int i = 0; i < N; i++)
                signal[i] = baseline[i] > filtered[i] ? baseline[i] - filtered[i] : 0;
            cw_output_t out;
            cw_update(&wheel, signal, &out);
            touching = out.touching;
            if (out.steps) handle_steps(out.steps);
            if (out.tap != CW_TAP_NONE) {
                haptics_click();
                model_tap(out.tap);
            }
#if CONFIG_NANO_WHEEL_LOG_RAW
            if (out.touching && ++log_div >= 10) {
                log_div = 0;
                ESP_LOGI(TAG, "ang=%6.1f str=%u sig0..=%u %u %u %u %u %u", out.angle_deg, out.strength,
                         signal[0], signal[1], signal[2], signal[3], signal[4], signal[5]);
            }
#else
            (void)log_div;
#endif
        }

#else
        if (at42qt2120_read(s_qt, &qd) == ESP_OK) {
            cw_output_t out;
            cw_update_position(&wheel, qd.wheel_touched && !qd.calibrating, qd.wheel_position, &out);
            touching = out.touching;
            extra_active = (qd.button_touched == btn_stable);
            if (out.steps) handle_steps(out.steps);
            if (out.tap != CW_TAP_NONE) {
                haptics_click();
                model_tap(out.tap);
            }
#if CONFIG_NANO_WHEEL_LOG_RAW
            if (out.touching && ++log_div >= 10) {
                log_div = 0;
                ESP_LOGI(TAG, "pos=%3u ang=%6.1f btn=%d", qd.wheel_position, out.angle_deg, qd.button_touched);
            }
#else
            (void)log_div;
#endif
        }
#endif

        if (touching || btn_pending || extra_active) {
            vTaskDelayUntil(&last, pdMS_TO_TICKS(btn_pending && !touching ? 2 : CONFIG_NANO_WHEEL_POLL_MS));
        } else {
            /* Leerlauf: bis zur nächsten INT-/BTN-Flanke schlafen (oder 50 ms) */
            ulTaskNotifyTake(pdTRUE, pdMS_TO_TICKS(50));
            last = xTaskGetTickCount();
        }
    }
}

esp_err_t input_start(void)
{
#if CONFIG_NANO_LATENCY_PROBE
    gpio_config_t pg = {.pin_bit_mask = 1ULL << PROBE_STEP_GPIO, .mode = GPIO_MODE_OUTPUT};
    gpio_config(&pg);
#endif
#if CONFIG_NANO_WHEEL_MPR121
    mpr121_config_t mc = MPR121_CONFIG_DEFAULT();
    mc.address = WHEEL_ADDR_MPR121;
    mc.num_electrodes = N;
    esp_err_t e = mpr121_init(board_wheel_i2c(), &mc, &s_mpr);
    if (e != ESP_OK) { ESP_LOGE(TAG, "MPR121 Init: %s - Klickrad angeschlossen?", esp_err_to_name(e)); return e; }
#else
    esp_err_t e = at42qt2120_init(board_wheel_i2c(), &s_qt);
    if (e != ESP_OK) { ESP_LOGE(TAG, "AT42QT2120 Init: %s - Klickrad angeschlossen?", esp_err_to_name(e)); return e; }
#endif
    e = haptics_init(board_wheel_i2c());
    if (e != ESP_OK) ESP_LOGW(TAG, "weiter ohne Haptik");

    gpio_config_t in = {
        .pin_bit_mask = (1ULL << WHEEL_BTN_GPIO) | (1ULL << WHEEL_INT_GPIO),
        .mode = GPIO_MODE_INPUT,
        .pull_up_en = GPIO_PULLUP_ENABLE,
        .intr_type = GPIO_INTR_ANYEDGE,
    };
    gpio_config(&in);

    BaseType_t ok = xTaskCreatePinnedToCore(input_task, "input", 4096, NULL, 10, &s_task, 1);
    if (ok != pdPASS) return ESP_ERR_NO_MEM;
    gpio_install_isr_service(0);
    gpio_isr_handler_add(WHEEL_BTN_GPIO, isr, NULL);
    gpio_isr_handler_add(WHEEL_INT_GPIO, isr, NULL);
    return ESP_OK;
}
