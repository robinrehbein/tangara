#include "haptics.h"
#include "board_config.h"
#include "drv2605l.h"
#include "esp_log.h"
#include "esp_timer.h"
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

esp_err_t haptics_init(i2c_master_bus_handle_t bus)
{
#if CONFIG_NANO_LATENCY_PROBE
    gpio_config_t g = {.pin_bit_mask = 1ULL << PROBE_HAPTIC_GPIO, .mode = GPIO_MODE_OUTPUT};
    gpio_config(&g);
#endif
    drv2605l_config_t cfg = {
        .lra_freq_hz = CONFIG_NANO_LRA_FREQ_HZ,
        .rated_mvrms = CONFIG_NANO_LRA_RATED_MVRMS,
        .overdrive_mvpeak = CONFIG_NANO_LRA_OVERDRIVE_MVPEAK,
    };
    esp_err_t e = drv2605l_init(bus, &cfg, &s_drv);
    if (e != ESP_OK) { ESP_LOGE(TAG, "DRV2605L Init: %s", esp_err_to_name(e)); return e; }
#if CONFIG_NANO_HAPTIC_AUTOCAL
    drv2605l_cal_result_t r;
    e = drv2605l_autocalibrate(s_drv, &r);
    if (e != ESP_OK) ESP_LOGW(TAG, "Auto-Kalibrierung: %s (LRA-Werte in Kconfig pruefen)", esp_err_to_name(e));
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
