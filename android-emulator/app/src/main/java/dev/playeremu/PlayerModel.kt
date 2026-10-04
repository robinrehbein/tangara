package dev.playeremu

import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableLongStateOf
import androidx.compose.runtime.mutableStateListOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue

class Entry(val label: String, val detail: String = "", val onSelect: () -> Unit = {})

sealed interface Page {
    val title: String
}

class ListPage(override val title: String, val entries: List<Entry>) : Page {
    var selected by mutableIntStateOf(0)

    /** Erster sichtbarer Eintrag. Wird beim Rendern angepasst, damit die Auswahl sichtbar bleibt. */
    var top by mutableIntStateOf(0)
}

object NowPlayingPage : Page {
    override val title = "Wird gespielt"
}

/**
 * Die Logik des Geräts, unabhängig von Android-UI. Diese Klasse entspricht dem, was später
 * in der Firmware passiert: Eingaben vom Rad verarbeiten, Haptik auslösen, Seiten wechseln.
 */
class PlayerModel(private val haptics: Haptics, val playback: Playback) {
    var settings by mutableStateOf(EmuSettings())

    val stack = mutableStateListOf<Page>()

    /** Bis zu diesem Zeitpunkt (ms) wird die Lautstärkeanzeige eingeblendet. */
    var volumeOverlayUntil by mutableLongStateOf(0L)
        private set

    private var library: List<Track> = emptyList()
    private val demo = demoTracks()

    init {
        setLibrary(emptyList())
    }

    fun setLibrary(tracks: List<Track>) {
        library = tracks
        stack.clear()
        stack += mainMenu()
    }

    fun onStep(delta: Int) {
        when (val page = stack.last()) {
            is ListPage -> {
                if (page.entries.isEmpty()) return
                val target = page.selected + delta
                if (target < 0 || target > page.entries.lastIndex) {
                    if (settings.endStop) haptics.endStop(settings)
                    page.selected = target.coerceIn(0, page.entries.lastIndex)
                } else {
                    page.selected = target
                    haptics.tick(settings)
                }
            }
            NowPlayingPage -> {
                volumeOverlayUntil = System.currentTimeMillis() + 1500
                if (playback.changeVolume(delta * 2)) {
                    haptics.tick(settings)
                } else if (settings.endStop) {
                    haptics.endStop(settings)
                }
            }
        }
    }

    fun onButton(button: WheelButton) {
        haptics.click(settings)
        when (button) {
            WheelButton.CENTER -> {
                val page = stack.last()
                if (page is ListPage) page.entries.getOrNull(page.selected)?.onSelect?.invoke()
            }
            WheelButton.MENU -> if (stack.size > 1) stack.removeAt(stack.lastIndex)
            WheelButton.PLAY_PAUSE -> playback.togglePause()
            WheelButton.NEXT -> playback.next()
            WheelButton.PREVIOUS -> playback.previous()
        }
    }

    private fun push(page: Page) {
        stack += page
    }

    private fun mainMenu(): ListPage {
        val source = library.ifEmpty { demo }
        val sourceHint = if (library.isEmpty()) " (Demo)" else ""
        return ListPage(
            "Musik",
            listOf(
                Entry("Wird gespielt") { push(NowPlayingPage) },
                Entry("Titel$sourceHint", source.size.toString()) { push(trackList("Titel", source)) },
                Entry("Alben$sourceHint") { push(groupList("Alben", source) { it.album }) },
                Entry("Künstler$sourceHint") { push(groupList("Künstler", source) { it.artist }) },
                Entry("Scroll-Test (1000)") { push(trackList("Scroll-Test", demo)) },
            ),
        )
    }

    private fun trackList(title: String, tracks: List<Track>): ListPage =
        ListPage(
            title,
            tracks.mapIndexed { i, track ->
                Entry(track.title, formatTime(track.durationMs)) {
                    playback.play(tracks, i)
                    push(NowPlayingPage)
                }
            },
        )

    private fun groupList(title: String, tracks: List<Track>, key: (Track) -> String): ListPage {
        val groups = tracks.groupBy(key).toSortedMap(String.CASE_INSENSITIVE_ORDER)
        return ListPage(
            title,
            groups.map { (name, groupTracks) ->
                Entry(name, groupTracks.size.toString()) { push(trackList(name, groupTracks)) }
            },
        )
    }
}

fun formatTime(ms: Long): String {
    val totalSeconds = ms / 1000
    return "%d:%02d".format(totalSeconds / 60, totalSeconds % 60)
}
