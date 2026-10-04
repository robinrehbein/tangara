/* Machbarkeitstest S31: QSPI-Display (CO5300) + LVGL 9 ueber esp_lvgl_port. Pins willkuerlich, nie ausgefuehrt. */
#include "driver/spi_master.h"
#include "esp_lcd_panel_io.h"
#include "esp_lcd_panel_ops.h"
#include "esp_lcd_panel_vendor.h"
#include "esp_lcd_co5300.h"
#include "esp_lvgl_port.h"
#include "lvgl.h"

#define H_RES 368
#define V_RES 448
void app_main(void)
{
    spi_bus_config_t bus = CO5300_PANEL_BUS_QSPI_CONFIG(1, 2, 3, 4, 5, H_RES * 40 * 2);
    ESP_ERROR_CHECK(spi_bus_initialize(SPI2_HOST, &bus, SPI_DMA_CH_AUTO));
    esp_lcd_panel_io_handle_t io = NULL;
    esp_lcd_panel_io_spi_config_t io_cfg = CO5300_PANEL_IO_QSPI_CONFIG(6, NULL, NULL);
    ESP_ERROR_CHECK(esp_lcd_new_panel_io_spi((esp_lcd_spi_bus_handle_t)SPI2_HOST, &io_cfg, &io));
    co5300_vendor_config_t vendor = {.flags.use_qspi_interface = 1};
    esp_lcd_panel_dev_config_t pc = {.reset_gpio_num = 7, .rgb_ele_order = LCD_RGB_ELEMENT_ORDER_RGB,
                                     .bits_per_pixel = 16, .vendor_config = &vendor};
    esp_lcd_panel_handle_t panel = NULL;
    ESP_ERROR_CHECK(esp_lcd_new_panel_co5300(io, &pc, &panel));
    ESP_ERROR_CHECK(esp_lcd_panel_reset(panel));
    ESP_ERROR_CHECK(esp_lcd_panel_init(panel));
    const lvgl_port_cfg_t lcfg = ESP_LVGL_PORT_INIT_CONFIG();
    ESP_ERROR_CHECK(lvgl_port_init(&lcfg));
    const lvgl_port_display_cfg_t d = {
        .io_handle = io, .panel_handle = panel, .buffer_size = H_RES * 40, .double_buffer = true,
        .hres = H_RES, .vres = V_RES, .color_format = LV_COLOR_FORMAT_RGB565,
        .flags = {.buff_dma = true, .swap_bytes = true}};
    lv_display_t *disp = lvgl_port_add_disp(&d);
    lvgl_port_lock(0);
    lv_obj_t *l = lv_label_create(lv_screen_active());
    lv_label_set_text(l, "S31 test");
    lvgl_port_unlock();
    (void)disp;
}
