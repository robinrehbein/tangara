#include <stdio.h>
#include "ui.h"
#include "haptics.h"
#include "model.h"
#include "esp_lvgl_port.h"

#define SCREEN_W 368
#define SCREEN_H 448
#define BAR_H 44
#define ROW_H 58
#define ROWS ((SCREEN_H - BAR_H) / ROW_H)   /* 6 volle Zeilen */

#define COL_BG      lv_color_hex(0x000000)
#define COL_TEXT    lv_color_hex(0xF2F2F2)
#define COL_DIM     lv_color_hex(0x8A8A8E)
#define COL_ACCENT  lv_color_hex(0xFF8A3D)
#define COL_BAR     lv_color_hex(0x1C1C1E)

static lv_obj_t *s_title, *s_pos;
static lv_obj_t *s_rows[ROWS], *s_label[ROWS], *s_detail[ROWS];
static lv_obj_t *s_play_cont, *s_vol_bar, *s_vol_label, *s_stats;
static int s_top;
static uint32_t s_seen_version;
static page_id_t s_seen_page = (page_id_t)-1;

static lv_obj_t *make_label(lv_obj_t *parent, lv_color_t col, const lv_font_t *font)
{
    lv_obj_t *l = lv_label_create(parent);
    lv_obj_set_style_text_color(l, col, 0);
    lv_obj_set_style_text_font(l, font, 0);
    return l;
}

static void build(lv_obj_t *scr)
{
    lv_obj_set_style_bg_color(scr, COL_BG, 0);
    lv_obj_set_style_bg_opa(scr, LV_OPA_COVER, 0);
    lv_obj_remove_flag(scr, LV_OBJ_FLAG_SCROLLABLE);

    lv_obj_t *bar = lv_obj_create(scr);
    lv_obj_remove_style_all(bar);
    lv_obj_set_size(bar, SCREEN_W, BAR_H);
    lv_obj_set_style_bg_color(bar, COL_BAR, 0);
    lv_obj_set_style_bg_opa(bar, LV_OPA_COVER, 0);
    s_title = make_label(bar, COL_TEXT, &lv_font_montserrat_20);
    lv_obj_align(s_title, LV_ALIGN_LEFT_MID, 16, 0);
    s_pos = make_label(bar, COL_ACCENT, &lv_font_montserrat_20);
    lv_obj_align(s_pos, LV_ALIGN_RIGHT_MID, -16, 0);

    for (int i = 0; i < ROWS; i++) {
        lv_obj_t *r = lv_obj_create(scr);
        lv_obj_remove_style_all(r);
        lv_obj_set_size(r, SCREEN_W, ROW_H);
        lv_obj_set_pos(r, 0, BAR_H + i * ROW_H);
        lv_obj_set_style_bg_opa(r, LV_OPA_COVER, 0);
        s_rows[i] = r;
        s_label[i] = make_label(r, COL_TEXT, &lv_font_montserrat_24);
        lv_obj_align(s_label[i], LV_ALIGN_LEFT_MID, 16, 0);
        s_detail[i] = make_label(r, COL_DIM, &lv_font_montserrat_20);
        lv_obj_align(s_detail[i], LV_ALIGN_RIGHT_MID, -16, 0);
    }

    s_play_cont = lv_obj_create(scr);
    lv_obj_remove_style_all(s_play_cont);
    lv_obj_set_size(s_play_cont, SCREEN_W, SCREEN_H - BAR_H);
    lv_obj_set_pos(s_play_cont, 0, BAR_H);
    s_vol_label = make_label(s_play_cont, COL_TEXT, &lv_font_montserrat_24);
    lv_obj_align(s_vol_label, LV_ALIGN_CENTER, 0, -40);
    s_vol_bar = lv_bar_create(s_play_cont);
    lv_obj_set_size(s_vol_bar, 280, 14);
    lv_obj_align(s_vol_bar, LV_ALIGN_CENTER, 0, 10);
    lv_bar_set_range(s_vol_bar, 0, 100);
    lv_obj_set_style_bg_color(s_vol_bar, COL_BAR, LV_PART_MAIN);
    lv_obj_set_style_bg_color(s_vol_bar, COL_ACCENT, LV_PART_INDICATOR);
    s_stats = make_label(s_play_cont, COL_DIM, &lv_font_montserrat_20);
    lv_obj_align(s_stats, LV_ALIGN_BOTTOM_MID, 0, -20);
}

static void refresh(lv_timer_t *t)
{
    model_view_t v;
    model_get(&v);
    if (v.version == s_seen_version) return;
    s_seen_version = v.version;

    bool list = v.count > 0;
    if (v.page != s_seen_page) {
        s_seen_page = v.page;
        lv_label_set_text(s_title, model_page_title(v.page));
        s_top = 0;
    }
    for (int i = 0; i < ROWS; i++) {
        if (list) lv_obj_remove_flag(s_rows[i], LV_OBJ_FLAG_HIDDEN);
        else lv_obj_add_flag(s_rows[i], LV_OBJ_FLAG_HIDDEN);
    }
    if (list) lv_obj_add_flag(s_play_cont, LV_OBJ_FLAG_HIDDEN);
    else lv_obj_remove_flag(s_play_cont, LV_OBJ_FLAG_HIDDEN);

    if (list) {
        /* Auswahl sichtbar halten (wie "top" in ListPage) */
        if (v.selected < s_top) s_top = v.selected;
        if (v.selected >= s_top + ROWS) s_top = v.selected - ROWS + 1;
        char pos[24];
        snprintf(pos, sizeof pos, "%d/%d", v.selected + 1, v.count);
        lv_label_set_text(s_pos, pos);
        for (int i = 0; i < ROWS; i++) {
            int idx = s_top + i;
            if (idx >= v.count) { lv_obj_add_flag(s_rows[i], LV_OBJ_FLAG_HIDDEN); continue; }
            char lab[32], det[16];
            model_row_text(v.page, idx, lab, sizeof lab, det, sizeof det);
            bool sel = idx == v.selected;
            lv_obj_set_style_bg_color(s_rows[i], sel ? COL_ACCENT : COL_BG, 0);
            lv_obj_set_style_text_color(s_label[i], sel ? COL_BG : COL_TEXT, 0);
            lv_obj_set_style_text_color(s_detail[i], sel ? COL_BG : COL_DIM, 0);
            lv_label_set_text(s_label[i], lab);
            lv_label_set_text(s_detail[i], det);
        }
    } else if (v.page == PAGE_NOW_PLAYING) {
        char b[48];
        snprintf(b, sizeof b, "Lautstaerke %d", v.volume);
        lv_label_set_text(s_vol_label, b);
        lv_bar_set_value(s_vol_bar, v.volume, LV_ANIM_OFF);
        lv_label_set_text(s_pos, "");
        lv_label_set_text(s_stats, "");
    } else {
        char b[96];
        snprintf(b, sizeof b, "Ticks %u\nausgelassen %u", (unsigned)haptics_tick_count(), (unsigned)haptics_skipped_count());
        lv_label_set_text(s_vol_label, "Phase 1: Haptik-Test");
        lv_bar_set_value(s_vol_bar, 0, LV_ANIM_OFF);
        lv_label_set_text(s_stats, b);
        lv_label_set_text(s_pos, "");
    }
}

void ui_start(lv_display_t *disp)
{
    lvgl_port_lock(0);
    build(lv_display_get_screen_active(disp));
    lv_timer_create(refresh, 10, NULL);
    lvgl_port_unlock();
}
