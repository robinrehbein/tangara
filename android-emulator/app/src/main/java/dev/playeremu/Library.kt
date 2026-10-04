package dev.playeremu

import android.content.ContentUris
import android.content.Context
import android.media.AudioAttributes
import android.media.MediaPlayer
import android.net.Uri
import android.provider.MediaStore
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableLongStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue

data class Track(
    val title: String,
    val artist: String,
    val album: String,
    val durationMs: Long,
    /** null bei Demo-Einträgen ohne Audiodatei. */
    val uri: Uri?,
)

/** Liest die Musik vom Handy, so wie das Gerät später die SD-Karte indiziert. */
fun loadTracks(context: Context): List<Track> {
    val collection = MediaStore.Audio.Media.EXTERNAL_CONTENT_URI
    val projection = arrayOf(
        MediaStore.Audio.Media._ID,
        MediaStore.Audio.Media.TITLE,
        MediaStore.Audio.Media.ARTIST,
        MediaStore.Audio.Media.ALBUM,
        MediaStore.Audio.Media.DURATION,
    )
    val tracks = mutableListOf<Track>()
    context.contentResolver.query(
        collection,
        projection,
        "${MediaStore.Audio.Media.IS_MUSIC} != 0",
        null,
        "${MediaStore.Audio.Media.TITLE} COLLATE NOCASE ASC",
    )?.use { cursor ->
        val id = cursor.getColumnIndexOrThrow(MediaStore.Audio.Media._ID)
        val title = cursor.getColumnIndexOrThrow(MediaStore.Audio.Media.TITLE)
        val artist = cursor.getColumnIndexOrThrow(MediaStore.Audio.Media.ARTIST)
        val album = cursor.getColumnIndexOrThrow(MediaStore.Audio.Media.ALBUM)
        val duration = cursor.getColumnIndexOrThrow(MediaStore.Audio.Media.DURATION)
        while (cursor.moveToNext()) {
            tracks += Track(
                title = cursor.getString(title) ?: "Unbekannt",
                artist = cursor.getString(artist) ?: "Unbekannt",
                album = cursor.getString(album) ?: "Unbekannt",
                durationMs = cursor.getLong(duration),
                uri = ContentUris.withAppendedId(collection, cursor.getLong(id)),
            )
        }
    }
    return tracks
}

fun demoTracks(count: Int = 1000): List<Track> = List(count) { i ->
    Track(
        title = "Demo-Titel ${i + 1}",
        artist = "Künstler ${i % 37 + 1}",
        album = "Album ${i % 83 + 1}",
        durationMs = 120_000L + (i * 7919L % 180_000L),
        uri = null,
    )
}

/** Einfache Wiedergabe mit Warteschlange. */
class Playback(private val context: Context) {
    var queue by mutableStateOf<List<Track>>(emptyList())
        private set
    var index by mutableIntStateOf(-1)
        private set
    var isPlaying by mutableStateOf(false)
        private set
    var positionMs by mutableLongStateOf(0L)
        private set

    /** 0..100 */
    var volume by mutableIntStateOf(70)
        private set

    private var player: MediaPlayer? = null
    private var prepared = false

    val current: Track? get() = queue.getOrNull(index)

    fun play(tracks: List<Track>, start: Int) {
        queue = tracks
        playIndex(start)
    }

    fun togglePause() {
        val p = player ?: return
        if (!prepared) return
        if (p.isPlaying) {
            p.pause()
            isPlaying = false
        } else {
            p.start()
            isPlaying = true
        }
    }

    fun next() {
        if (index + 1 < queue.size) playIndex(index + 1)
    }

    fun previous() {
        if (positionMs > 3_000 || index <= 0) {
            if (prepared) player?.seekTo(0)
            positionMs = 0
        } else {
            playIndex(index - 1)
        }
    }

    /** Gibt false zurück, wenn die Grenze (0 oder 100) schon erreicht ist. */
    fun changeVolume(delta: Int): Boolean {
        val newVolume = (volume + delta).coerceIn(0, 100)
        if (newVolume == volume) return false
        volume = newVolume
        applyVolume()
        return true
    }

    fun updatePosition() {
        val p = player ?: return
        if (prepared && isPlaying) positionMs = p.currentPosition.toLong()
    }

    fun release() {
        player?.release()
        player = null
        prepared = false
        isPlaying = false
    }

    private fun playIndex(i: Int) {
        release()
        val track = queue.getOrNull(i) ?: return
        index = i
        positionMs = 0
        val uri = track.uri ?: return
        val p = MediaPlayer()
        player = p
        try {
            setUp(p, uri)
        } catch (e: Exception) {
            release()
        }
    }

    private fun setUp(p: MediaPlayer, uri: Uri) {
        p.apply {
            setAudioAttributes(
                AudioAttributes.Builder()
                    .setUsage(AudioAttributes.USAGE_MEDIA)
                    .setContentType(AudioAttributes.CONTENT_TYPE_MUSIC)
                    .build()
            )
            setDataSource(context, uri)
            setOnPreparedListener {
                prepared = true
                applyVolume()
                it.start()
                this@Playback.isPlaying = true
            }
            setOnCompletionListener { next() }
            setOnErrorListener { _, _, _ ->
                this@Playback.isPlaying = false
                true
            }
            prepareAsync()
        }
    }

    private fun applyVolume() {
        // Quadratische Kurve, damit leise Stufen feiner sind (wie bei echten Lautstärkereglern).
        val v = (volume / 100f).let { it * it }
        player?.setVolume(v, v)
    }
}
