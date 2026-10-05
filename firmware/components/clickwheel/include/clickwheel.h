/* Copyright 2026 Nano-Player-Projekt
 * SPDX-License-Identifier: GPL-3.0-only */
#pragma once
/**
 * Klickrad-Logik ohne Hardwarebezug (portabel, auch auf dem PC testbar).
 * Eingang entweder Segment-Signale (MPR121, Klickrad v1) oder Wheel-Position 0..255 (AT42QT2120).
 *
 * Gleiche Logik wie ScrollWheel.kt der Emulator-App:
 *  - Winkel: 0 Grad = rechts, im Uhrzeigersinn steigend (Bildschirm-Konvention)
 *  - Winkeldifferenzen werden akkumuliert, jeder volle Rasterschritt (detent_deg) ergibt einen Schritt
 *  - Drehen beginnt erst, wenn der Finger mehr als tap_slop_deg vom Startwinkel entfernt ist; vorher
 *    gilt ein kurzes Antippen als Taste (oben MENU, unten PLAY, rechts NEXT, links PREV)
 */
#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

#define CW_MAX_SEGMENTS 12

typedef enum {
    CW_TAP_NONE = 0,
    CW_TAP_MENU,
    CW_TAP_PLAY,
    CW_TAP_PREV,
    CW_TAP_NEXT,
} cw_tap_t;

typedef struct {
    uint8_t num_segments;      ///< 3..12
    float   first_segment_deg; ///< Winkel von Segment 0 (Bildschirm-Konvention), z. B. -90 = oben
    bool    clockwise;         ///< true: Segmentnummern steigen im Uhrzeigersinn
    float   detent_deg;        ///< Rasterschritt in Grad (Default 15)
    uint16_t touch_on;         ///< Signalstärke (Baseline - Messwert) ab der "berührt" gilt
    uint16_t touch_off;        ///< darunter gilt "losgelassen" (Hysterese, < touch_on)
    uint16_t noise_floor;      ///< wird von jedem Segment abgezogen, bevor gewichtet wird
    float   tap_slop_deg;      ///< Bewegung, ab der es ein Drehen und kein Tippen mehr ist
    uint8_t settle_frames;     ///< Messungen nach Touch-Beginn, die ignoriert werden (Winkel stabilisiert sich)
} cw_config_t;

#define CW_CONFIG_DEFAULT() { \
    .num_segments = 12, .first_segment_deg = -90.f, .clockwise = true, .detent_deg = 15.f, \
    .touch_on = 40, .touch_off = 20, .noise_floor = 8, .tap_slop_deg = 20.f, .settle_frames = 2 }

typedef struct {
    int      steps;       ///< Rasterschritte seit dem letzten Aufruf (+ = im Uhrzeigersinn)
    cw_tap_t tap;         ///< wurde beim Loslassen als Tippen erkannt
    bool     touching;
    bool     rotating;
    float    angle_deg;   ///< aktueller Winkel (nur gültig bei touching)
    uint16_t strength;    ///< Stärke des stärksten Segments
} cw_output_t;

typedef struct {
    cw_config_t cfg;
    bool touching, rotating;
    uint8_t settle;
    float last_angle, start_angle, accumulated;
} cw_t;

void cw_init(cw_t *w, const cw_config_t *cfg);
void cw_set_detent(cw_t *w, float detent_deg);

/**
 * Berechnet aus den Segment-Signalen (>= 0, Baseline - gefilterter Wert) den Winkel als gewichteten
 * Schwerpunkt (Vektorsumme) des stärksten Segments und seiner zwei Nachbarn. Rückgabe false, wenn
 * kein Segment über noise_floor liegt.
 */
bool cw_compute_angle(const cw_config_t *cfg, const uint16_t *signal, float *angle_deg, uint16_t *strength);

/** Einen neuen Messdurchgang verarbeiten. */
void cw_update(cw_t *w, const uint16_t *signal, cw_output_t *out);

/**
 * Variante für Controller mit fertiger Wheel-Position (AT42QT2120, Tangara-Klickrad): position 0..255
 * läuft einmal um den Kreis. Der Winkel von Position 0 ist first_segment_deg, der Drehsinn clockwise
 * (num_segments, touch_on/off und noise_floor werden nicht benutzt). touched kommt vom Controller.
 */
void cw_update_position(cw_t *w, bool touched, uint8_t position, cw_output_t *out);

/**
 * Klickrad-v2-Konvention (TEILE.md "Klickrad v2", Tangara-Footprint, nicht gemessen):
 * Wheel-Position 0 liegt oben, die Position steigt gegen den Uhrzeigersinn (64 = links, 128 = unten,
 * 192 = rechts); der Stecker sitzt bei 270 Grad (unten) = Position 128, wenn das Modul mit dem
 * Stecker nach unten eingebaut ist. Bildschirm-Winkel von Position 0 daher -90 Grad, clockwise = false.
 * mount_offset_deg: Drehung des Moduls gegenueber "Stecker unten" (positiv = im Uhrzeigersinn gedreht);
 * mirrored: Rad liegt spiegelverkehrt (Position steigt im Uhrzeigersinn).
 * Wirkung auf die UI: Finger im Uhrzeigersinn -> Winkel steigt -> positive Schritte -> nach unten scrollen.
 */
#define CW_V2_POS0_DEG (-90.f)
void cw_config_wheel_v2(cw_config_t *cfg, float mount_offset_deg, bool mirrored);

/** Wheel-Position 0..255 in einen Winkel (Bildschirm-Konvention, -180..180] umrechnen. */
float cw_position_to_angle(const cw_config_t *cfg, uint8_t position);

/** Winkeldifferenz auf (-180, 180] normieren. */
float cw_angle_diff(float a, float b);

/** Taste (MENU/PLAY/PREV/NEXT) für einen Tipp-Winkel. */
cw_tap_t cw_tap_for_angle(float angle_deg);

#ifdef __cplusplus
}
#endif
