idf_component_register(SRCS "main.c" "board.c" "display.c" "haptics.c" "input.c" "ui.c" "model.c"
                       INCLUDE_DIRS "."
                       REQUIRES esp_driver_i2c esp_lcd espressif__esp_lvgl_port lvgl__lvgl esp_driver_gpio esp_driver_spi esp_lcd esp_timer
                                drv2605l mpr121 at42qt2120 clickwheel nvs_flash)
