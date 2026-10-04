#include "board.h"
#include "board_config.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "sdkconfig.h"

static const char *TAG = "board";
static i2c_master_bus_handle_t s_bus, s_wheel_bus;

static esp_err_t new_bus(i2c_port_num_t port, gpio_num_t sda, gpio_num_t scl, i2c_master_bus_handle_t *out)
{
    const i2c_master_bus_config_t cfg = {
        .i2c_port = port,
        .sda_io_num = sda,
        .scl_io_num = scl,
        .clk_source = I2C_CLK_SRC_DEFAULT,
        .glitch_ignore_cnt = 7,
        .flags.enable_internal_pullup = BOARD_I2C_INTERNAL_PULLUP,
    };
    return i2c_new_master_bus(&cfg, out);
}

static esp_err_t expander_release_resets(void)
{
    i2c_master_dev_handle_t dev;
    const i2c_device_config_t dc = {
        .dev_addr_length = I2C_ADDR_BIT_LEN_7,
        .device_address = BOARD_ADDR_TCA9554,
        .scl_speed_hz = BOARD_I2C_FREQ_HZ,
    };
    esp_err_t e = i2c_master_bus_add_device(s_bus, &dc, &dev);
    if (e != ESP_OK) return e;
    /* Reihenfolge wie im Waveshare-Beispiel: erst nur SD_CS, 20 ms, dann Display/Touch aus dem Reset */
    uint8_t cfg[] = {TCA_REG_CONFIG, (uint8_t)~TCA_OUTPUT_MASK};
    uint8_t o1[] = {TCA_REG_OUTPUT, TCA_BIT_SD_CS};
    uint8_t o2[] = {TCA_REG_OUTPUT, TCA_OUTPUT_MASK};
    e = i2c_master_transmit(dev, cfg, 2, 100);
    if (e == ESP_OK) e = i2c_master_transmit(dev, o1, 2, 100);
    vTaskDelay(pdMS_TO_TICKS(20));
    if (e == ESP_OK) e = i2c_master_transmit(dev, o2, 2, 100);
    vTaskDelay(pdMS_TO_TICKS(150));
    i2c_master_bus_rm_device(dev);
    return e;
}

esp_err_t board_init(void)
{
    esp_err_t e = new_bus(BOARD_I2C_PORT, BOARD_I2C_SDA, BOARD_I2C_SCL, &s_bus);
    if (e != ESP_OK) return e;
    e = expander_release_resets();
    if (e != ESP_OK) ESP_LOGE(TAG, "IO-Expander 0x%02X: %s (Display bleibt evtl. im Reset)", BOARD_ADDR_TCA9554, esp_err_to_name(e));

#if CONFIG_NANO_WHEEL_SEPARATE_I2C
    ESP_ERROR_CHECK(new_bus(WHEEL_I2C_PORT2, WHEEL_I2C2_SDA, WHEEL_I2C2_SCL, &s_wheel_bus));
#else
    s_wheel_bus = s_bus;
#endif

#if CONFIG_NANO_I2C_SCAN
    for (int a = 0x08; a < 0x78; a++) {
        if (i2c_master_probe(s_bus, a, 20) == ESP_OK) ESP_LOGI(TAG, "I2C 0x%02X antwortet", a);
    }
#if CONFIG_NANO_WHEEL_SEPARATE_I2C
    for (int a = 0x08; a < 0x78; a++) {
        if (i2c_master_probe(s_wheel_bus, a, 20) == ESP_OK) ESP_LOGI(TAG, "Klickrad-I2C 0x%02X antwortet", a);
    }
#endif
#endif
    return ESP_OK;
}

i2c_master_bus_handle_t board_i2c(void) { return s_bus; }
i2c_master_bus_handle_t board_wheel_i2c(void) { return s_wheel_bus; }
bool board_touch_is_v2(void) { return i2c_master_probe(s_bus, BOARD_ADDR_TOUCH_V2, 50) == ESP_OK; }
