/* Copyright 2026 Nano-Player-Projekt
 * SPDX-License-Identifier: GPL-3.0-only */
#pragma once
#include "esp_err.h"
#include "driver/i2c_master.h"

/** DRV2605L initialisieren (und kalibrieren). Ruft man nur im Input-Task auf. */
esp_err_t haptics_init(i2c_master_bus_handle_t bus);

/** Raster-Tick. Zu schnelle Ticks (Rate-Limit) werden ausgelassen. Liefert true, wenn ausgelöst. */
bool haptics_tick(void);
/** Bestätigungsklick (Mitteltaste, Tippen). */
void haptics_click(void);
/** Anschlag am Listenende (eigenes Rate-Limit). */
bool haptics_endstop(void);

uint32_t haptics_tick_count(void);
uint32_t haptics_skipped_count(void);
