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
    puts("OK");
    return 0;
}
