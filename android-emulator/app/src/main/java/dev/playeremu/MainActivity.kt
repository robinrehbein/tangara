package dev.playeremu

import android.Manifest
import android.content.pm.PackageManager
import android.os.Build
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.BoxWithConstraints
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.aspectRatio
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.safeDrawingPadding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.selection.selectable
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.ModalBottomSheet
import androidx.compose.material3.RadioButton
import androidx.compose.material3.Slider
import androidx.compose.material3.Switch
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.material3.darkColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalDensity
import androidx.compose.ui.platform.LocalView
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.min
import androidx.core.content.ContextCompat
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import kotlin.math.hypot

class MainActivity : ComponentActivity() {
    private lateinit var haptics: Haptics
    private lateinit var playback: Playback
    private lateinit var model: PlayerModel

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        haptics = Haptics(this)
        playback = Playback(this)
        model = PlayerModel(haptics, playback)
        setContent {
            MaterialTheme(colorScheme = darkColorScheme()) {
                EmulatorScreen(model, haptics)
            }
        }
    }

    override fun onDestroy() {
        playback.release()
        super.onDestroy()
    }
}

private val audioPermission =
    if (Build.VERSION.SDK_INT >= 33) Manifest.permission.READ_MEDIA_AUDIO
    else Manifest.permission.READ_EXTERNAL_STORAGE

@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun EmulatorScreen(model: PlayerModel, haptics: Haptics) {
    val context = LocalContext.current
    val view = LocalView.current
    DisposableEffect(view) {
        haptics.view = view
        onDispose { haptics.view = null }
    }

    var permissionGranted by remember {
        mutableStateOf(
            ContextCompat.checkSelfPermission(context, audioPermission) == PackageManager.PERMISSION_GRANTED
        )
    }
    val launcher = rememberLauncherForActivityResult(ActivityResultContracts.RequestPermission()) {
        permissionGranted = it
    }
    LaunchedEffect(Unit) {
        if (!permissionGranted) launcher.launch(audioPermission)
    }
    LaunchedEffect(permissionGranted) {
        if (permissionGranted) {
            val tracks = withContext(Dispatchers.IO) { loadTracks(context) }
            model.setLibrary(tracks)
        }
    }

    var showSettings by remember { mutableStateOf(false) }
    val settings = model.settings

    Column(
        Modifier
            .fillMaxSize()
            .background(Color(0xFF0E0F12))
            .safeDrawingPadding()
            .padding(16.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
    ) {
        Row(Modifier.fillMaxWidth(), verticalAlignment = Alignment.CenterVertically) {
            Text("Player-Emulator", color = Color.White, modifier = Modifier.weight(1f))
            TextButton(onClick = { showSettings = true }) { Text("Einstellungen") }
        }

        // Gerätegehäuse
        Column(
            Modifier
                .weight(1f)
                .fillMaxWidth()
                .clip(RoundedCornerShape(28.dp))
                .background(Color(0xFF2B2F36))
                .border(1.dp, Color(0xFF3C414A), RoundedCornerShape(28.dp))
                .padding(20.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.SpaceEvenly,
        ) {
            DisplayFrame(model)
            ScrollWheel(
                detentDegrees = settings.detentDegrees,
                onStep = model::onStep,
                onButton = model::onButton,
                modifier = Modifier.fillMaxWidth(0.72f),
            )
        }

        Text(
            "Ticks: ${haptics.ticks}  ·  ausgelassen: ${haptics.skippedTicks}  ·  " +
                settings.hapticMode.label +
                if (haptics.isSupported(settings.hapticMode)) "" else " (nicht unterstützt, Fallback)",
            color = Color(0xFF8A8F98),
            style = MaterialTheme.typography.bodySmall,
            modifier = Modifier.padding(top = 8.dp),
        )
        if (!permissionGranted) {
            Text(
                "Kein Zugriff auf Musik: es werden Demo-Einträge ohne Audio angezeigt.",
                color = Color(0xFFFF8A3D),
                style = MaterialTheme.typography.bodySmall,
            )
        }
    }

    if (showSettings) {
        ModalBottomSheet(onDismissRequest = { showSettings = false }) {
            SettingsPanel(model, haptics)
        }
    }
}

/** Display in echter physischer Größe (sofern eingestellt) mit schwarzem Rahmen. */
@Composable
private fun DisplayFrame(model: PlayerModel) {
    val preset = model.settings.preset
    val metrics = LocalContext.current.resources.displayMetrics
    val density = LocalDensity.current

    BoxWithConstraints(Modifier.fillMaxWidth(), contentAlignment = Alignment.Center) {
        val maxDisplayWidth = maxWidth - 24.dp
        val width = if (model.settings.realSize) {
            val widthInch = preset.diagonalInch * preset.widthPx /
                hypot(preset.widthPx.toFloat(), preset.heightPx.toFloat())
            val widthPhysicalPx = widthInch * metrics.xdpi
            min(with(density) { widthPhysicalPx.toDp() }, maxDisplayWidth)
        } else {
            maxDisplayWidth
        }
        Box(
            Modifier
                .clip(RoundedCornerShape(10.dp))
                .background(Color.Black)
                .padding(12.dp)
        ) {
            DeviceDisplay(
                model,
                Modifier
                    .width(width)
                    .aspectRatio(preset.widthPx.toFloat() / preset.heightPx)
            )
        }
    }
}

@Composable
private fun SettingsPanel(model: PlayerModel, haptics: Haptics) {
    val s = model.settings
    fun update(block: (EmuSettings) -> EmuSettings) {
        model.settings = block(model.settings)
    }

    Column(
        Modifier
            .fillMaxWidth()
            .verticalScroll(rememberScrollState())
            .padding(horizontal = 20.dp, vertical = 8.dp)
    ) {
        Section("Display")
        DisplayPresets.forEach { preset ->
            RadioRow(preset.name, preset == s.preset) { update { it.copy(preset = preset) } }
        }
        SwitchRow("Echte Größe (in cm wie auf dem Gerät)", s.realSize) { v -> update { it.copy(realSize = v) } }

        Section("Scrollrad")
        Text("Raster: alle ${s.detentDegrees.toInt()}° ein Schritt (${(360 / s.detentDegrees).toInt()} pro Umdrehung)")
        Slider(
            value = s.detentDegrees,
            onValueChange = { v -> update { it.copy(detentDegrees = v) } },
            valueRange = 6f..45f,
        )

        Section("Haptik")
        HapticMode.entries.forEach { mode ->
            val label = mode.label + if (haptics.isSupported(mode)) "" else "  (nicht unterstützt)"
            RadioRow(label, mode == s.hapticMode) { update { it.copy(hapticMode = mode) } }
        }
        Text("Stärke: ${(s.intensity * 100).toInt()} %")
        Slider(
            value = s.intensity,
            onValueChange = { v -> update { it.copy(intensity = v) } },
            valueRange = 0.05f..1f,
        )
        Text("Mindestabstand zwischen Ticks: ${s.minTickIntervalMs} ms")
        Slider(
            value = s.minTickIntervalMs.toFloat(),
            onValueChange = { v -> update { it.copy(minTickIntervalMs = v.toInt()) } },
            valueRange = 0f..80f,
        )
        SwitchRow("Anschlag am Listenende spüren", s.endStop) { v -> update { it.copy(endStop = v) } }
        Text(
            "Amplitudensteuerung: " + if (haptics.hasAmplitudeControl) "ja" else "nein",
            color = Color(0xFF8A8F98),
            style = MaterialTheme.typography.bodySmall,
        )
        Spacer(Modifier.height(32.dp))
    }
}

@Composable
private fun Section(title: String) {
    Text(
        title,
        style = MaterialTheme.typography.titleMedium,
        modifier = Modifier.padding(top = 16.dp, bottom = 4.dp),
    )
}

@Composable
private fun RadioRow(label: String, selected: Boolean, onClick: () -> Unit) {
    Row(
        Modifier
            .fillMaxWidth()
            .selectable(selected = selected, onClick = onClick)
            .padding(vertical = 2.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        RadioButton(selected = selected, onClick = onClick)
        Spacer(Modifier.width(4.dp))
        Text(label)
    }
}

@Composable
private fun SwitchRow(label: String, checked: Boolean, onChange: (Boolean) -> Unit) {
    Row(
        Modifier
            .fillMaxWidth()
            .padding(vertical = 4.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Text(label, modifier = Modifier.weight(1f))
        Switch(checked = checked, onCheckedChange = onChange)
    }
}
