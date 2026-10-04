/* Copyright 2026 Nano-Player-Projekt
 * SPDX-License-Identifier: GPL-3.0-only */
#include <math.h>
#include <string.h>
#include "clickwheel.h"

#define DEG2RAD 0.017453292519943295f
#define RAD2DEG 57.29577951308232f

float cw_angle_diff(float a, float b)
{
    float d = a - b;
    while (d > 180.f) d -= 360.f;
    while (d <= -180.f) d += 360.f;
    return d;
}

cw_tap_t cw_tap_for_angle(float a)
{
    /* wie buttonAt() in ScrollWheel.kt: oben -135..-45 = MENU, unten 45..135 = PLAY, rechts = NEXT */
    while (a > 180.f) a -= 360.f;
    while (a <= -180.f) a += 360.f;
    if (a >= -135.f && a <= -45.f) return CW_TAP_MENU;
    if (a >= 45.f && a <= 135.f) return CW_TAP_PLAY;
    if (a > -45.f && a < 45.f) return CW_TAP_NEXT;
    return CW_TAP_PREV;
}

void cw_init(cw_t *w, const cw_config_t *cfg)
{
    memset(w, 0, sizeof(*w));
    w->cfg = *cfg;
    if (w->cfg.num_segments > CW_MAX_SEGMENTS) w->cfg.num_segments = CW_MAX_SEGMENTS;
    if (w->cfg.num_segments < 3) w->cfg.num_segments = 3;
    if (w->cfg.detent_deg < 1.f) w->cfg.detent_deg = 1.f;
}

void cw_set_detent(cw_t *w, float detent_deg)
{
    w->cfg.detent_deg = detent_deg < 1.f ? 1.f : detent_deg;
}

static float segment_angle(const cw_config_t *c, int i)
{
    float step = 360.f / (float)c->num_segments;
    return c->first_segment_deg + (c->clockwise ? 1.f : -1.f) * step * (float)i;
}

bool cw_compute_angle(const cw_config_t *c, const uint16_t *signal, float *angle_deg, uint16_t *strength)
{
    int n = c->num_segments, peak = 0;
    for (int i = 1; i < n; i++)
        if (signal[i] > signal[peak]) peak = i;
    if (strength) *strength = signal[peak];
    if (signal[peak] <= c->noise_floor) return false;

    float sx = 0.f, sy = 0.f;
    for (int k = -1; k <= 1; k++) {
        int i = (peak + k + n) % n;
        float wgt = signal[i] > c->noise_floor ? (float)(signal[i] - c->noise_floor) : 0.f;
        float a = segment_angle(c, i) * DEG2RAD;
        sx += wgt * cosf(a);
        sy += wgt * sinf(a);
    }
    *angle_deg = atan2f(sy, sx) * RAD2DEG;
    return true;
}

/* Gemeinsamer Kern: Berührungszustand und Winkel sind bekannt (egal ob aus Segmenten oder Wheel-Position). */
static void feed(cw_t *w, bool now_touch, float angle, uint16_t strength, cw_output_t *out)
{
    out->strength = strength;
    if (!now_touch) {
        if (w->touching) {
            if (!w->rotating && w->settle == 0) out->tap = cw_tap_for_angle(w->start_angle);
            w->touching = w->rotating = false;
        }
        return;
    }

    if (!w->touching) {
        w->touching = true;
        w->rotating = false;
        w->settle = w->cfg.settle_frames;
        w->accumulated = 0.f;
        w->last_angle = w->start_angle = angle;
    } else if (w->settle > 0) {
        /* Die ersten Messungen eines Fingers sind ungenau (Segmentrand): Startwinkel nachführen */
        w->settle--;
        w->last_angle = w->start_angle = angle;
    } else {
        float d = cw_angle_diff(angle, w->last_angle);
        w->last_angle = angle;
        w->accumulated += d;
        if (!w->rotating && fabsf(cw_angle_diff(angle, w->start_angle)) > w->cfg.tap_slop_deg)
            w->rotating = true;
        if (w->rotating) {
            while (w->accumulated >= w->cfg.detent_deg) { out->steps++; w->accumulated -= w->cfg.detent_deg; }
            while (w->accumulated <= -w->cfg.detent_deg) { out->steps--; w->accumulated += w->cfg.detent_deg; }
        }
    }
    out->touching = true;
    out->rotating = w->rotating;
    out->angle_deg = angle;
}

void cw_update(cw_t *w, const uint16_t *signal, cw_output_t *out)
{
    memset(out, 0, sizeof(*out));
    float angle = 0.f;
    uint16_t strength = 0;
    bool valid = cw_compute_angle(&w->cfg, signal, &angle, &strength);
    bool now_touch = w->touching ? (strength >= w->cfg.touch_off) : (strength >= w->cfg.touch_on);
    feed(w, now_touch && valid, angle, strength, out);
}

float cw_position_to_angle(const cw_config_t *c, uint8_t position)
{
    float a = c->first_segment_deg + (c->clockwise ? 1.f : -1.f) * (float)position * (360.f / 256.f);
    while (a > 180.f) a -= 360.f;
    while (a <= -180.f) a += 360.f;
    return a;
}

void cw_update_position(cw_t *w, bool touched, uint8_t position, cw_output_t *out)
{
    memset(out, 0, sizeof(*out));
    feed(w, touched, cw_position_to_angle(&w->cfg, position), touched ? 255 : 0, out);
}
