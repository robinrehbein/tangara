idf_component_register(SRCS "drv2605l.c"
                       INCLUDE_DIRS "include"
                       REQUIRES esp_driver_i2c esp_timer
                       PRIV_REQUIRES log)
