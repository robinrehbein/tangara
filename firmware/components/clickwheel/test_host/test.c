/* Copyright 2026 Nano-Player-Projekt
 * SPDX-License-Identifier: GPL-3.0-only */
/* Host-Test: gcc -Wall -I../include test.c ../clickwheel.c -lm -o t && ./t */
#include <stdio.h>
#include <math.h>
#include <string.h>
#include <assert.h>
#include "clickwheel.h"

static void finger(const cw_config_t *c, float deg, uint16_t *sig)
{
    memset(sig, 0, sizeof(uint16_t) * 12);
    for (int i = 0; i < c->num_segments; i++) {
        float a = c->first_segment_deg + i * 360.f / c->num_segments;
        float d = fabsf(cw_angle_diff(deg, a));
        float w = 200.f * expf(-d * d / (2 * 25.f * 25.f));
        sig[i] = (uint16_t)w;
    }
}

int main(void)
{
    cw_config_t c = CW_CONFIG_DEFAULT();
    cw_t w; cw_init(&w, &c);
    uint16_t s[12]; cw_output_t o;
    /* Test 1: Winkel-Rekonstruktion */
    for (float a = -180; a < 180; a += 7.3f) {
        finger(&c, a, s); float r; uint16_t st;
        assert(cw_compute_angle(&c, s, &r, &st));
        assert(fabsf(cw_angle_diff(r, a)) < 6.f);
    }
    /* Test 2: Drehen um 90 Grad im Uhrzeigersinn => 6 Schritte (+-1) */
    int total = 0;
    for (float a = -90; a <= 0; a += 1.f) { finger(&c, a, s); cw_update(&w, s, &o); total += o.steps; }
    printf("steps cw 90deg: %d\n", total); assert(total >= 4 && total <= 6);
    memset(s, 0, sizeof s); cw_update(&w, s, &o); assert(!o.touching);
    /* Test 3: gegen den Uhrzeigersinn */
    total = 0;
    for (float a = 0; a >= -90; a -= 1.f) { finger(&c, a, s); cw_update(&w, s, &o); total += o.steps; }
    printf("steps ccw 90deg: %d\n", total); assert(total <= -4 && total >= -6);
    memset(s, 0, sizeof s); cw_update(&w, s, &o);
    /* Test 4: Tippen oben => MENU */
    cw_tap_t tap = CW_TAP_NONE;
    for (int i = 0; i < 8; i++) { finger(&c, -90, s); cw_update(&w, s, &o); }
    memset(s, 0, sizeof s); cw_update(&w, s, &o); tap = o.tap;
    printf("tap oben: %d\n", tap); assert(tap == CW_TAP_MENU);
    /* Test 5: Klickrad-v2-Konvention (AT42QT2120): Position 0 oben, steigt gegen den Uhrzeigersinn,
     * Position 128 = unten = Stecker bei 270 Grad. Finger im Uhrzeigersinn => Position FAELLT. */
    cw_config_t pc = CW_CONFIG_DEFAULT(); cw_config_wheel_v2(&pc, 0.f, false);
    cw_t pw; cw_init(&pw, &pc);
    assert(fabsf(cw_position_to_angle(&pc, 0) - (-90.f)) < 0.01f);    /* oben */
    assert(fabsf(cw_position_to_angle(&pc, 64) - 180.f) < 0.01f);     /* links */
    assert(fabsf(cw_position_to_angle(&pc, 128) - 90.f) < 0.01f);     /* unten (Stecker) */
    assert(fabsf(cw_position_to_angle(&pc, 192) - 0.f) < 0.01f);      /* rechts */
    /* Im Uhrzeigersinn (oben -> rechts, Position 0 -> 255 -> 192): positive Schritte = nach unten scrollen */
    total = 0;
    for (int p = 256; p >= 192; p--) { cw_update_position(&pw, true, (uint8_t)(p & 255), &o); total += o.steps; }
    printf("steps v2 cw 90deg (Pos 0->192): %d\n", total); assert(total >= 4 && total <= 6);
    cw_update_position(&pw, false, 192, &o); assert(!o.touching);
    /* Gegen den Uhrzeigersinn (rechts -> oben, Position 192 -> 256): negative Schritte = nach oben */
    total = 0;
    for (int p = 192; p <= 256; p++) { cw_update_position(&pw, true, (uint8_t)(p & 255), &o); total += o.steps; }
    printf("steps v2 ccw 90deg (Pos 192->0): %d\n", total); assert(total <= -4 && total >= -6);
    cw_update_position(&pw, false, 0, &o);
    /* Rundlauf 0 -> 255 -> 250 (im Uhrzeigersinn ueber oben): kein Sprung */
    total = 0;
    for (int i = 0; i < 20; i++) { cw_update_position(&pw, true, (uint8_t)((10 - i) & 255), &o); total += o.steps; }
    printf("steps ueber den Nullpunkt cw (20 Positionen, ca. 28 Grad): %d\n", total); assert(total >= 1 && total <= 2);
    cw_update_position(&pw, false, 0, &o);
    /* Tippen: Position 0 = oben = MENU, 128 = unten = PLAY, 64 = links = PREV, 192 = rechts = NEXT */
    const uint8_t tp[4] = {0, 128, 64, 192};
    const cw_tap_t te[4] = {CW_TAP_MENU, CW_TAP_PLAY, CW_TAP_PREV, CW_TAP_NEXT};
    for (int k = 0; k < 4; k++) {
        for (int i = 0; i < 6; i++) cw_update_position(&pw, true, tp[k], &o);
        cw_update_position(&pw, false, tp[k], &o); printf("tap pos %d: %d\n", tp[k], o.tap); assert(o.tap == te[k]);
    }
    /* Einbau-Offset: Modul um 90 Grad im Uhrzeigersinn gedreht => Position 0 zeigt nach rechts (0 Grad) */
    cw_config_wheel_v2(&pc, 90.f, false);
    assert(fabsf(cw_position_to_angle(&pc, 0) - 0.f) < 0.01f);
    /* gespiegeltes Rad: Position steigt im Uhrzeigersinn */
    cw_config_wheel_v2(&pc, 0.f, true);
    assert(fabsf(cw_position_to_angle(&pc, 64) - 0.f) < 0.01f);
    puts("OK");
    return 0;
}
