/* Copyright 2026 Nano-Player-Projekt
 * SPDX-License-Identifier: GPL-3.0-only */
#pragma once
#include "esp_err.h"
#include "lvgl.h"

/** Panel (CO5300 oder SH8601, QSPI) und LVGL 9 via esp_lvgl_port, Hochformat 368x448. */
esp_err_t display_init(lv_display_t **out);
