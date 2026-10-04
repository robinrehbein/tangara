idf_component_register(SRCS "main.c" "board.c" "display.c" "haptics.c" "input.c" "ui.c"
                       INCLUDE_DIRS "."
                       REQUIRES esp_driver_i2c esp_driver_gpio esp_driver_spi esp_lcd esp_timer
                                drv2605l mpr121 clickwheel)
