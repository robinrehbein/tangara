/* Copyright 2026 Nano-Player-Projekt
 * SPDX-License-Identifier: GPL-3.0-only */
#pragma once
#include "esp_err.h"
#include "driver/i2c_master.h"

/** Gemeinsamen I2C-Bus anlegen, IO-Expander (Display-Reset/-Versorgung) schalten, optional scannen. */
esp_err_t board_init(void);

/** Bus mit Board-Chips (Expander, Touch, PMU ...). */
i2c_master_bus_handle_t board_i2c(void);

/** Bus für das Klickrad (gleicher Bus, außer Kconfig verlangt einen eigenen). */
i2c_master_bus_handle_t board_wheel_i2c(void);

/** true, wenn auf 0x15 ein Touch-Controller (CST820, V2) antwortet. */
bool board_touch_is_v2(void);
