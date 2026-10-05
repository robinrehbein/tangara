/* Copyright 2026 Nano-Player-Projekt
 * SPDX-License-Identifier: GPL-3.0-only */
#include "display.h"
#include "board.h"
#include "board_config.h"
#include "driver/spi_master.h"
#include "esp_lcd_panel_io.h"
#include "esp_lcd_panel_ops.h"
#include "esp_lcd_panel_vendor.h"
#include "esp_log.h"
#include "esp_lvgl_port.h"
#include "sdkconfig.h"
#if CONFIG_NANO_PANEL_CO5300
#include "esp_lcd_co5300.h"
#else
#include "esp_lcd_sh8601.h"
#endif

static const char *TAG = "display";
#if CONFIG_NANO_PANEL_CO5300
#define PANEL_NAME "CO5300"
#else
#define PANEL_NAME "SH8601"
#endif

#define BUF_LINES 40

#if CONFIG_NANO_PANEL_CO5300
/* Initialisierung wie im Waveshare-Beispiel für V2 */
static const co5300_lcd_init_cmd_t s_init_cmds[] = {
    {0xFE, (uint8_t[]){0x00}, 1, 0},
    {0xC4, (uint8_t[]){0x80}, 1, 0},
    {0x3A, (uint8_t[]){0x55}, 1, 0},   /* RGB565 */
    {0x35, (uint8_t[]){0x00}, 1, 0},
    {0x53, (uint8_t[]){0x20}, 1, 0},
    {0x51, (uint8_t[]){0xFF}, 1, 0},
    {0x63, (uint8_t[]){0xFF}, 1, 0},
    {0x2A, (uint8_t[]){0x00, 0x00, (BOARD_LCD_H_RES - 1) >> 8, (BOARD_LCD_H_RES - 1) & 0xFF}, 4, 0},
    {0x2B, (uint8_t[]){0x00, 0x00, (BOARD_LCD_V_RES - 1) >> 8, (BOARD_LCD_V_RES - 1) & 0xFF}, 4, 0},
    {0x11, NULL, 0, 100},
    {0x29, NULL, 0, 0},
};
#endif

/* SH8601/CO5300 verlangen gerade Startkoordinaten und gerade Größen */
static void rounder_cb(lv_area_t *a)
{
    a->x1 &= ~1;
    a->y1 &= ~1;
    a->x2 |= 1;
    a->y2 |= 1;
}

esp_err_t display_init(lv_display_t **out)
{
    const size_t buf_bytes = BOARD_LCD_H_RES * BUF_LINES * sizeof(uint16_t);
#if CONFIG_NANO_PANEL_CO5300
    spi_bus_config_t bus = CO5300_PANEL_BUS_QSPI_CONFIG(BOARD_LCD_SCLK, BOARD_LCD_D0, BOARD_LCD_D1,
                                                        BOARD_LCD_D2, BOARD_LCD_D3, buf_bytes);
#else
    spi_bus_config_t bus = SH8601_PANEL_BUS_QSPI_CONFIG(BOARD_LCD_SCLK, BOARD_LCD_D0, BOARD_LCD_D1,
                                                        BOARD_LCD_D2, BOARD_LCD_D3, buf_bytes);
#endif
    ESP_ERROR_CHECK(spi_bus_initialize(BOARD_LCD_HOST, &bus, SPI_DMA_CH_AUTO));

    esp_lcd_panel_io_handle_t io = NULL;
#if CONFIG_NANO_PANEL_CO5300
    esp_lcd_panel_io_spi_config_t io_cfg = CO5300_PANEL_IO_QSPI_CONFIG(BOARD_LCD_CS, NULL, NULL);
#else
    esp_lcd_panel_io_spi_config_t io_cfg = SH8601_PANEL_IO_QSPI_CONFIG(BOARD_LCD_CS, NULL, NULL);
#endif
    ESP_ERROR_CHECK(esp_lcd_new_panel_io_spi((esp_lcd_spi_bus_handle_t)BOARD_LCD_HOST, &io_cfg, &io));

    esp_lcd_panel_handle_t panel = NULL;
#if CONFIG_NANO_PANEL_CO5300
    co5300_vendor_config_t vendor = {
        .init_cmds = s_init_cmds,
        .init_cmds_size = sizeof(s_init_cmds) / sizeof(s_init_cmds[0]),
        .flags.use_qspi_interface = 1,
    };
    esp_lcd_panel_dev_config_t pc = {
        .reset_gpio_num = BOARD_LCD_RST_GPIO,
        .rgb_ele_order = LCD_RGB_ELEMENT_ORDER_RGB,
        .bits_per_pixel = 16,
        .vendor_config = &vendor,
    };
    ESP_ERROR_CHECK(esp_lcd_new_panel_co5300(io, &pc, &panel));
    const int gap_x = BOARD_LCD_GAP_X_V2;
#else
    sh8601_vendor_config_t vendor = {
        .flags.use_qspi_interface = 1,
    };
    esp_lcd_panel_dev_config_t pc = {
        .reset_gpio_num = BOARD_LCD_RST_GPIO,
        .rgb_ele_order = LCD_RGB_ELEMENT_ORDER_RGB,
        .bits_per_pixel = 16,
        .vendor_config = &vendor,
    };
    ESP_ERROR_CHECK(esp_lcd_new_panel_sh8601(io, &pc, &panel));
    const int gap_x = BOARD_LCD_GAP_X_V1;
#endif
    ESP_ERROR_CHECK(esp_lcd_panel_reset(panel));
    ESP_ERROR_CHECK(esp_lcd_panel_init(panel));
    ESP_ERROR_CHECK(esp_lcd_panel_set_gap(panel, gap_x, 0));
    /* Helligkeit (0x51); im QSPI-Modus wird der Befehl als 0x02 00 <cmd> 00 gesendet */
    uint8_t br = CONFIG_NANO_DISPLAY_BRIGHTNESS;
    esp_lcd_panel_io_tx_param(io, (0x02 << 24) | (0x51 << 8), &br, 1);
    ESP_ERROR_CHECK(esp_lcd_panel_disp_on_off(panel, true));

    const lvgl_port_cfg_t lvgl_cfg = {
        .task_priority = 4, .task_stack = 8192, .task_affinity = 0,
        .task_max_sleep_ms = 20, .task_stack_caps = MALLOC_CAP_INTERNAL | MALLOC_CAP_DEFAULT,
        .timer_period_ms = 2,
    };
    ESP_ERROR_CHECK(lvgl_port_init(&lvgl_cfg));

    const lvgl_port_display_cfg_t dcfg = {
        .io_handle = io,
        .panel_handle = panel,
        .buffer_size = BOARD_LCD_H_RES * BUF_LINES,
        .double_buffer = true,
        .hres = BOARD_LCD_H_RES,
        .vres = BOARD_LCD_V_RES,
        .monochrome = false,
        .rotation = {.swap_xy = false, .mirror_x = false, .mirror_y = false},
        .rounder_cb = rounder_cb,
        .color_format = LV_COLOR_FORMAT_RGB565,
        .flags = {.buff_dma = true, .buff_spiram = false, .swap_bytes = true},
    };
    *out = lvgl_port_add_disp(&dcfg);
    if (!*out) return ESP_FAIL;
    ESP_LOGI(TAG, "Display %dx%d bereit (%s)", BOARD_LCD_H_RES, BOARD_LCD_V_RES,
             PANEL_NAME);
    return ESP_OK;
}
