/* Copyright 2026 Nano-Player-Projekt
 * SPDX-License-Identifier: GPL-3.0-only */
#include <stdio.h>
#include "model.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#define SCROLL_TEST_COUNT 1000

static const char *k_main[] = {"Wird gespielt", "Scroll-Test (1000)", "Info"};
#define MAIN_COUNT 3

static portMUX_TYPE s_lock = portMUX_INITIALIZER_UNLOCKED;
static page_id_t s_stack[8];
static int s_sel_stack[8];
static int s_depth;
static int s_volume = 50;
static uint32_t s_version;

static int count_of(page_id_t p)
{
    switch (p) {
    case PAGE_MAIN: return MAIN_COUNT;
    case PAGE_SCROLL_TEST: return SCROLL_TEST_COUNT;
    default: return 0;
    }
}

void model_init(void)
{
    s_depth = 1;
    s_stack[0] = PAGE_MAIN;
    s_sel_stack[0] = 0;
    s_version = 1;
}

model_step_result_t model_step(int delta)
{
    model_step_result_t r = {0};
    portENTER_CRITICAL(&s_lock);
    page_id_t p = s_stack[s_depth - 1];
    int dir = delta < 0 ? -1 : 1;
    for (int n = delta < 0 ? -delta : delta; n > 0; n--) {
        if (p == PAGE_NOW_PLAYING) {
            int v = s_volume + dir * 2;
            if (v < 0 || v > 100) { r.hit_end = true; v = v < 0 ? 0 : 100; }
            else r.moved = true;
            s_volume = v;
        } else if (count_of(p) > 0) {
            int t = s_sel_stack[s_depth - 1] + dir;
            if (t < 0 || t >= count_of(p)) { r.hit_end = true; }
            else { s_sel_stack[s_depth - 1] = t; r.moved = true; }
        }
    }
    if (r.moved || r.hit_end) s_version++;
    portEXIT_CRITICAL(&s_lock);
    return r;
}

static void push(page_id_t p)
{
    if (s_depth < 8) { s_stack[s_depth] = p; s_sel_stack[s_depth] = 0; s_depth++; }
}

bool model_center(void)
{
    bool changed = true;
    portENTER_CRITICAL(&s_lock);
    page_id_t p = s_stack[s_depth - 1];
    int sel = s_sel_stack[s_depth - 1];
    if (p == PAGE_MAIN) {
        push(sel == 0 ? PAGE_NOW_PLAYING : sel == 1 ? PAGE_SCROLL_TEST : PAGE_INFO);
    } else if (p == PAGE_SCROLL_TEST) {
        push(PAGE_NOW_PLAYING);
    } else {
        changed = false;
    }
    if (changed) s_version++;
    portEXIT_CRITICAL(&s_lock);
    return changed;
}

bool model_tap(cw_tap_t tap)
{
    bool changed = false;
    portENTER_CRITICAL(&s_lock);
    if (tap == CW_TAP_MENU && s_depth > 1) { s_depth--; changed = true; }
    if (changed) s_version++;
    portEXIT_CRITICAL(&s_lock);
    return changed;   /* PLAY/PREV/NEXT: noch ohne Funktion in Phase 1 */
}

void model_get(model_view_t *v)
{
    portENTER_CRITICAL(&s_lock);
    v->page = s_stack[s_depth - 1];
    v->selected = s_sel_stack[s_depth - 1];
    v->count = count_of(v->page);
    v->volume = s_volume;
    v->version = s_version;
    portEXIT_CRITICAL(&s_lock);
}

const char *model_page_title(page_id_t p)
{
    switch (p) {
    case PAGE_MAIN: return "Musik";
    case PAGE_SCROLL_TEST: return "Scroll-Test";
    case PAGE_NOW_PLAYING: return "Wird gespielt";
    default: return "Info";
    }
}

void model_row_text(page_id_t p, int idx, char *label, int ll, char *detail, int dl)
{
    detail[0] = 0;
    if (p == PAGE_MAIN) {
        snprintf(label, ll, "%s", k_main[idx]);
    } else {
        snprintf(label, ll, "Titel %04d", idx + 1);
        int sec = 90 + (idx * 37) % 300;
        snprintf(detail, dl, "%d:%02d", sec / 60, sec % 60);
    }
}
