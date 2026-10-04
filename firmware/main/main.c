/* Copyright 2026 Nano-Player-Projekt
 * SPDX-License-Identifier: GPL-3.0-only */
#include "esp_log.h"
#include "board.h"
#include "display.h"
#include "input.h"
#include "model.h"
#include "ui.h"

static const char *TAG = "main";

void app_main(void)
{
    ESP_ERROR_CHECK(board_init());
    model_init();

    lv_display_t *disp = NULL;
    ESP_ERROR_CHECK(display_init(&disp));
    ui_start(disp);

    /* Ohne angeschlossenes Klickrad läuft die Anzeige trotzdem */
    if (input_start() != ESP_OK) ESP_LOGE(TAG, "Klickrad nicht verfügbar");
    ESP_LOGI(TAG, "bereit");
}
