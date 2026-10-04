package dev.playeremu

enum class PanelType { LCD, AMOLED }

/** Ein Display-Kandidat für die Hardware. Schrift- und Zeilenhöhe sind in Display-Pixeln angegeben. */
data class DisplayPreset(
    val name: String,
    val diagonalInch: Float,
    val widthPx: Int,
    val heightPx: Int,
    val panel: PanelType,
    val fontPx: Float,
    val rowPx: Float,
)

val DisplayPresets = listOf(
    DisplayPreset("Tangara-Original (1,8\" LCD, 160×128)", 1.8f, 160, 128, PanelType.LCD, 10f, 14f),
    DisplayPreset("IPS 2,4\" (320×240)", 2.4f, 320, 240, PanelType.LCD, 17f, 26f),
    DisplayPreset("AMOLED 1,8\" (368×448)", 1.8f, 368, 448, PanelType.AMOLED, 24f, 40f),
    DisplayPreset("AMOLED 2,06\" (410×502)", 2.06f, 410, 502, PanelType.AMOLED, 26f, 44f),
)

/** Alles, was man im Emulator einstellen kann, um das Bediengefühl zu tunen. */
data class EmuSettings(
    val preset: DisplayPreset = DisplayPresets[2],
    val realSize: Boolean = true,
    val detentDegrees: Float = 15f,
    val hapticMode: HapticMode = HapticMode.PRIMITIVE_TICK,
    val intensity: Float = 0.8f,
    val minTickIntervalMs: Int = 20,
    val endStop: Boolean = true,
)
