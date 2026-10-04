package dev.playeremu

import android.content.Context
import android.os.Build
import android.os.VibrationEffect
import android.os.Vibrator
import android.os.VibratorManager
import android.view.HapticFeedbackConstants
import android.view.View
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.setValue

/**
 * Die Haptik-Varianten, die Android anbietet. Die "Primitives" (ab Android 11) kommen
 * einer Taptic Engine am nächsten, sofern das Handy einen guten LRA-Motor hat.
 */
enum class HapticMode(val label: String, val minSdk: Int) {
    PRIMITIVE_TICK("Primitive: Tick", 30),
    PRIMITIVE_LOW_TICK("Primitive: Low Tick", 31),
    PRIMITIVE_CLICK("Primitive: Click", 30),
    PREDEFINED_TICK("Predefined: Tick", 29),
    PREDEFINED_CLICK("Predefined: Click", 29),
    VIEW_CLOCK_TICK("View: CLOCK_TICK", 26),
    ONE_SHOT("One-Shot 8 ms", 26),
}

class Haptics(context: Context) {
    private val vibrator: Vibrator = if (Build.VERSION.SDK_INT >= 31) {
        context.getSystemService(VibratorManager::class.java).defaultVibrator
    } else {
        @Suppress("DEPRECATION")
        context.getSystemService(Context.VIBRATOR_SERVICE) as Vibrator
    }

    /** Wird für [HapticMode.VIEW_CLOCK_TICK] gebraucht. */
    var view: View? = null

    var ticks by mutableIntStateOf(0)
        private set
    var skippedTicks by mutableIntStateOf(0)
        private set

    private var lastTickNanos = 0L

    val hasAmplitudeControl: Boolean get() = vibrator.hasAmplitudeControl()

    fun isSupported(mode: HapticMode): Boolean {
        if (Build.VERSION.SDK_INT < mode.minSdk) return false
        return when (mode) {
            HapticMode.PRIMITIVE_TICK -> primitiveSupported(VibrationEffect.Composition.PRIMITIVE_TICK)
            HapticMode.PRIMITIVE_LOW_TICK -> primitiveSupported(VibrationEffect.Composition.PRIMITIVE_LOW_TICK)
            HapticMode.PRIMITIVE_CLICK -> primitiveSupported(VibrationEffect.Composition.PRIMITIVE_CLICK)
            else -> true
        }
    }

    /** Raster-Tick beim Drehen. Zu schnelle Ticks werden ausgelassen, sonst "brummt" es. */
    fun tick(settings: EmuSettings) {
        val now = System.nanoTime()
        if (now - lastTickNanos < settings.minTickIntervalMs * 1_000_000L) {
            skippedTicks++
            return
        }
        lastTickNanos = now
        ticks++
        play(settings.hapticMode, settings.intensity)
    }

    /** Bestätigung beim Drücken einer Taste. */
    fun click(settings: EmuSettings) {
        if (Build.VERSION.SDK_INT >= 30 && isSupported(HapticMode.PRIMITIVE_CLICK)) {
            composition(VibrationEffect.Composition.PRIMITIVE_CLICK, settings.intensity)
        } else {
            predefined(VibrationEffect.EFFECT_CLICK)
        }
    }

    /** Spürbarer "Anschlag" am Listenende. */
    fun endStop(settings: EmuSettings) {
        val now = System.nanoTime()
        if (now - lastTickNanos < 80_000_000L) return
        lastTickNanos = now
        if (Build.VERSION.SDK_INT >= 31 && primitiveSupported(VibrationEffect.Composition.PRIMITIVE_THUD)) {
            composition(VibrationEffect.Composition.PRIMITIVE_THUD, settings.intensity)
        } else {
            predefined(VibrationEffect.EFFECT_HEAVY_CLICK)
        }
    }

    private fun play(mode: HapticMode, intensity: Float) {
        val effective = if (isSupported(mode)) mode else fallback()
        when (effective) {
            HapticMode.PRIMITIVE_TICK ->
                composition(VibrationEffect.Composition.PRIMITIVE_TICK, intensity)
            HapticMode.PRIMITIVE_LOW_TICK ->
                composition(VibrationEffect.Composition.PRIMITIVE_LOW_TICK, intensity)
            HapticMode.PRIMITIVE_CLICK ->
                composition(VibrationEffect.Composition.PRIMITIVE_CLICK, intensity)
            HapticMode.PREDEFINED_TICK -> predefined(VibrationEffect.EFFECT_TICK)
            HapticMode.PREDEFINED_CLICK -> predefined(VibrationEffect.EFFECT_CLICK)
            HapticMode.VIEW_CLOCK_TICK -> view?.performHapticFeedback(HapticFeedbackConstants.CLOCK_TICK)
            HapticMode.ONE_SHOT -> {
                val amplitude = if (hasAmplitudeControl) {
                    (intensity * 255).toInt().coerceIn(1, 255)
                } else {
                    VibrationEffect.DEFAULT_AMPLITUDE
                }
                vibrator.vibrate(VibrationEffect.createOneShot(8, amplitude))
            }
        }
    }

    private fun fallback(): HapticMode =
        if (Build.VERSION.SDK_INT >= 29) HapticMode.PREDEFINED_TICK else HapticMode.ONE_SHOT

    private fun predefined(effect: Int) {
        if (Build.VERSION.SDK_INT >= 29) {
            vibrator.vibrate(VibrationEffect.createPredefined(effect))
        } else {
            vibrator.vibrate(VibrationEffect.createOneShot(10, VibrationEffect.DEFAULT_AMPLITUDE))
        }
    }

    private fun primitiveSupported(primitive: Int): Boolean {
        if (Build.VERSION.SDK_INT < 30) return false
        return vibrator.arePrimitivesSupported(primitive).all { it }
    }

    private fun composition(primitive: Int, intensity: Float) {
        if (Build.VERSION.SDK_INT < 30) return
        vibrator.vibrate(
            VibrationEffect.startComposition()
                .addPrimitive(primitive, intensity.coerceIn(0f, 1f))
                .compose()
        )
    }
}
