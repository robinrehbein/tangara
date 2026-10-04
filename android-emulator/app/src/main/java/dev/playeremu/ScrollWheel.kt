package dev.playeremu

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.gestures.awaitEachGesture
import androidx.compose.foundation.gestures.awaitFirstDown
import androidx.compose.foundation.layout.aspectRatio
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberUpdatedState
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.drawText
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.rememberTextMeasurer
import androidx.compose.ui.unit.sp
import kotlin.math.atan2
import kotlin.math.cos
import kotlin.math.sin

enum class WheelButton { MENU, PLAY_PAUSE, PREVIOUS, NEXT, CENTER }

private const val CENTER_RATIO = 0.38f

/**
 * Ein Scrollrad wie beim iPod bzw. Tangara: Drehen auf dem Ring erzeugt Rasterschritte,
 * Tippen auf den Ring (oben, unten, links, rechts) oder die Mitte löst Tasten aus.
 */
@Composable
fun ScrollWheel(
    detentDegrees: Float,
    onStep: (Int) -> Unit,
    onButton: (WheelButton) -> Unit,
    modifier: Modifier = Modifier,
) {
    val detent by rememberUpdatedState(detentDegrees)
    val step by rememberUpdatedState(onStep)
    val button by rememberUpdatedState(onButton)
    var touchAngle by remember { mutableStateOf<Float?>(null) }
    var centerPressed by remember { mutableStateOf(false) }
    val textMeasurer = rememberTextMeasurer()

    Canvas(
        modifier
            .aspectRatio(1f)
            .pointerInput(Unit) {
                awaitEachGesture {
                    val down = awaitFirstDown()
                    val center = Offset(size.width / 2f, size.height / 2f)
                    val outer = size.width / 2f
                    val inner = outer * CENTER_RATIO
                    val startDistance = (down.position - center).getDistance()
                    if (startDistance > outer) return@awaitEachGesture

                    val inCenter = startDistance < inner
                    var lastAngle = angleOf(down.position, center)
                    var accumulated = 0f
                    var rotating = false
                    centerPressed = inCenter
                    down.consume()

                    while (true) {
                        val event = awaitPointerEvent()
                        val change = event.changes.firstOrNull { it.id == down.id } ?: break
                        if (!change.pressed) {
                            if (!rotating) button(buttonAt(down.position, center, inner))
                            break
                        }
                        change.consume()
                        if (inCenter) continue

                        val angle = angleOf(change.position, center)
                        var delta = angle - lastAngle
                        if (delta > 180f) delta -= 360f
                        if (delta < -180f) delta += 360f
                        lastAngle = angle
                        accumulated += delta

                        if (!rotating &&
                            (change.position - down.position).getDistance() > viewConfiguration.touchSlop
                        ) {
                            rotating = true
                        }
                        if (rotating) {
                            touchAngle = angle
                            while (accumulated >= detent) {
                                step(1)
                                accumulated -= detent
                            }
                            while (accumulated <= -detent) {
                                step(-1)
                                accumulated += detent
                            }
                        }
                    }
                    touchAngle = null
                    centerPressed = false
                }
            }
    ) {
        val c = center
        val outer = size.minDimension / 2f
        val inner = outer * CENTER_RATIO
        drawCircle(Color(0xFFE9E9EC), outer, c)
        drawCircle(if (centerPressed) Color(0xFFBFC1C6) else Color(0xFFD3D5DA), inner, c)

        val labelStyle = TextStyle(color = Color(0xFF6B6E75), fontSize = 13.sp, fontWeight = FontWeight.SemiBold)
        val labelRadius = (outer + inner) / 2f
        fun label(text: String, angleDeg: Float) {
            val layout = textMeasurer.measure(text, labelStyle)
            val rad = Math.toRadians(angleDeg.toDouble())
            val pos = Offset(
                c.x + labelRadius * cos(rad).toFloat() - layout.size.width / 2f,
                c.y + labelRadius * sin(rad).toFloat() - layout.size.height / 2f,
            )
            drawText(layout, topLeft = pos)
        }
        label("MENU", -90f)
        label("▶ ❚❚", 90f)
        label("◀◀", 180f)
        label("▶▶", 0f)

        touchAngle?.let {
            val rad = Math.toRadians(it.toDouble())
            val dot = Offset(
                c.x + labelRadius * cos(rad).toFloat(),
                c.y + labelRadius * sin(rad).toFloat(),
            )
            drawCircle(Color(0x33000000), outer * 0.14f, dot)
        }
    }
}

/** Winkel in Grad, 0° = rechts, im Uhrzeigersinn steigend (Bildschirm-y zeigt nach unten). */
private fun angleOf(p: Offset, center: Offset): Float =
    Math.toDegrees(atan2((p.y - center.y).toDouble(), (p.x - center.x).toDouble())).toFloat()

private fun buttonAt(p: Offset, center: Offset, inner: Float): WheelButton {
    if ((p - center).getDistance() < inner) return WheelButton.CENTER
    val a = angleOf(p, center)
    return when {
        a in -135f..-45f -> WheelButton.MENU
        a in 45f..135f -> WheelButton.PLAY_PAUSE
        a > -45f && a < 45f -> WheelButton.NEXT
        else -> WheelButton.PREVIOUS
    }
}
