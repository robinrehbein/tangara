package dev.playeremu

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.BoxWithConstraints
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.offset
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.SideEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableLongStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalDensity
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.TextUnit
import kotlinx.coroutines.delay

private val Accent = Color(0xFFFF8A3D)

private class DisplayScale(val unit: Dp, val font: TextUnit, val smallFont: TextUnit, val row: Dp)

/**
 * Rendert den Inhalt des emulierten Displays. Alle Größen sind in Display-Pixeln des gewählten
 * Presets gedacht und werden auf die tatsächliche Fläche skaliert. So sieht man, wie viel Text
 * und wie viele Zeilen auf das echte Display passen.
 */
@Composable
fun DeviceDisplay(model: PlayerModel, modifier: Modifier = Modifier) {
    val preset = model.settings.preset
    val background = if (preset.panel == PanelType.AMOLED) Color.Black else Color(0xFF15181D)

    BoxWithConstraints(modifier.background(background)) {
        val unit = maxWidth / preset.widthPx
        val density = LocalDensity.current
        val scale = with(density) {
            DisplayScale(
                unit = unit,
                font = (unit * preset.fontPx).toSp(),
                smallFont = (unit * preset.fontPx * 0.75f).toSp(),
                row = unit * preset.rowPx,
            )
        }
        val page = model.stack.last()

        Column(Modifier.fillMaxSize()) {
            StatusBar(page.title, model.playback.isPlaying, scale)
            when (page) {
                is ListPage -> ListContent(page, scale, Modifier.weight(1f))
                NowPlayingPage -> NowPlayingContent(model, scale, Modifier.weight(1f))
            }
        }
    }
}

@Composable
private fun StatusBar(title: String, playing: Boolean, s: DisplayScale) {
    Row(
        Modifier
            .fillMaxWidth()
            .height(s.row * 0.8f)
            .background(Color(0xFF2A2D33))
            .padding(horizontal = s.unit * 4),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Text(
            title,
            style = TextStyle(color = Color.White, fontSize = s.smallFont, fontWeight = FontWeight.Bold),
            maxLines = 1,
            overflow = TextOverflow.Ellipsis,
            modifier = Modifier.weight(1f),
        )
        Text(
            if (playing) "▶  87%" else "❚❚  87%",
            style = TextStyle(color = Color(0xFFB8BCC4), fontSize = s.smallFont),
        )
    }
}

@Composable
private fun ListContent(page: ListPage, s: DisplayScale, modifier: Modifier) {
    BoxWithConstraints(modifier.fillMaxWidth()) {
        val visible = (maxHeight / s.row).toInt().coerceAtLeast(1)
        // Auswahl im sichtbaren Bereich halten (springt wie bei LVGL auf dem Gerät).
        val top = when {
            page.selected < page.top -> page.selected
            page.selected >= page.top + visible -> page.selected - visible + 1
            else -> page.top
        }
        SideEffect { page.top = top }
        val end = minOf(page.entries.size, top + visible)

        Column(Modifier.fillMaxSize().padding(end = s.unit * 4)) {
            for (i in top until end) {
                val entry = page.entries[i]
                val selected = i == page.selected
                Row(
                    Modifier
                        .fillMaxWidth()
                        .height(s.row)
                        .background(if (selected) Accent else Color.Transparent)
                        .padding(horizontal = s.unit * 4),
                    verticalAlignment = Alignment.CenterVertically,
                ) {
                    Text(
                        entry.label,
                        style = TextStyle(
                            color = if (selected) Color.Black else Color.White,
                            fontSize = s.font,
                        ),
                        maxLines = 1,
                        overflow = TextOverflow.Ellipsis,
                        modifier = Modifier.weight(1f),
                    )
                    if (entry.detail.isNotEmpty()) {
                        Text(
                            entry.detail,
                            style = TextStyle(
                                color = if (selected) Color(0xFF3A2010) else Color(0xFF8A8F98),
                                fontSize = s.smallFont,
                            ),
                            modifier = Modifier.padding(start = s.unit * 4),
                        )
                    }
                }
            }
        }

        // Scrollbalken
        if (page.entries.size > visible) {
            val trackHeight = maxHeight
            val thumbHeight = trackHeight * (visible.toFloat() / page.entries.size)
            val thumbOffset = (trackHeight - thumbHeight) *
                (top.toFloat() / (page.entries.size - visible))
            Box(
                Modifier
                    .align(Alignment.TopEnd)
                    .offset(y = thumbOffset)
                    .width(s.unit * 3)
                    .height(thumbHeight)
                    .background(Color(0xFF8A8F98))
            )
        }
    }
}

@Composable
private fun NowPlayingContent(model: PlayerModel, s: DisplayScale, modifier: Modifier) {
    val playback = model.playback
    val track = playback.current
    var now by remember { mutableLongStateOf(System.currentTimeMillis()) }
    LaunchedEffect(Unit) {
        while (true) {
            playback.updatePosition()
            now = System.currentTimeMillis()
            delay(250)
        }
    }

    Column(
        modifier
            .fillMaxWidth()
            .padding(s.unit * 8),
        verticalArrangement = Arrangement.Center,
    ) {
        if (track == null) {
            Text("Nichts in der Warteschlange", style = TextStyle(Color.White, s.font))
            return@Column
        }
        Text(
            track.title,
            style = TextStyle(Color.White, s.font, FontWeight.Bold),
            maxLines = 2,
            overflow = TextOverflow.Ellipsis,
        )
        Text(track.artist, style = TextStyle(Color(0xFFB8BCC4), s.smallFont), maxLines = 1)
        Text(track.album, style = TextStyle(Color(0xFF8A8F98), s.smallFont), maxLines = 1)
        if (track.uri == null) {
            Text("Demo-Eintrag ohne Audio", style = TextStyle(Accent, s.smallFont))
        }
        Spacer(Modifier.height(s.unit * 8))

        val showVolume = now < model.volumeOverlayUntil
        val fraction = if (showVolume) {
            playback.volume / 100f
        } else if (track.durationMs > 0) {
            (playback.positionMs.toFloat() / track.durationMs).coerceIn(0f, 1f)
        } else {
            0f
        }
        Box(
            Modifier
                .fillMaxWidth()
                .height(s.unit * 4)
                .background(Color(0xFF3A3D44))
        ) {
            Box(
                Modifier
                    .fillMaxWidth(fraction)
                    .height(s.unit * 4)
                    .background(if (showVolume) Color.White else Accent)
            )
        }
        Row(Modifier.fillMaxWidth().padding(top = s.unit * 2)) {
            val left = if (showVolume) "Lautstärke" else formatTime(playback.positionMs)
            val right = if (showVolume) "${playback.volume}%" else formatTime(track.durationMs)
            Text(left, style = TextStyle(Color(0xFF8A8F98), s.smallFont), modifier = Modifier.weight(1f))
            Text(right, style = TextStyle(Color(0xFF8A8F98), s.smallFont))
        }
        Text(
            "${playback.index + 1} / ${playback.queue.size}",
            style = TextStyle(Color(0xFF8A8F98), s.smallFont),
            modifier = Modifier.padding(top = s.unit * 4),
        )
    }
}
