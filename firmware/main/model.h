/* Copyright 2026 Nano-Player-Projekt
 * SPDX-License-Identifier: GPL-3.0-only */
#pragma once
/**
 * Bedienlogik wie PlayerModel.kt der Emulator-App, ohne LVGL. Wird vom Input-Task verändert
 * (damit die Haptik sofort weiß, ob ein Schritt wirkt oder am Anschlag endet) und vom UI gelesen.
 */
#include <stdbool.h>
#include <stdint.h>
#include "clickwheel.h"

typedef enum { PAGE_MAIN = 0, PAGE_SCROLL_TEST, PAGE_NOW_PLAYING, PAGE_INFO } page_id_t;

typedef struct {
    page_id_t page;
    int selected;
    int count;       ///< Anzahl Einträge (Listenseiten)
    int volume;      ///< 0..100 (Seite "Wird gespielt")
    uint32_t version;
} model_view_t;

typedef struct { bool moved; bool hit_end; } model_step_result_t;

void model_init(void);
model_step_result_t model_step(int delta);
/** center = Mitteltaste gedrückt; sonst Tipp-Taste des Rings. true, wenn sich etwas geändert hat. */
bool model_center(void);
bool model_tap(cw_tap_t tap);
void model_get(model_view_t *v);

/** Text einer Zeile der Seite. */
const char *model_page_title(page_id_t p);
void model_row_text(page_id_t p, int idx, char *label, int label_len, char *detail, int detail_len);
