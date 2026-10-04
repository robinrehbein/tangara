# Player-Emulator (Android)

Grober Prototyp, um das Bediengefühl des Players auf dem Handy zu testen, bevor Hardware gekauft wird.

## Bauen und installieren

Mit Android Studio: den Ordner `android-emulator` öffnen und auf „Run“ klicken.

Auf der Kommandozeile (Android SDK nötig):

```sh
cd android-emulator
./gradlew assembleDebug
adb install app/build/outputs/apk/debug/app-debug.apk
```

Voraussetzung: Android 8.0 oder neuer. Die beste Haptik gibt es ab Android 11 auf Handys mit gutem LRA-Motor (z. B. aktuelle Pixel- oder Samsung-Galaxy-S-Modelle).

## Bedienung

- **Auf dem Ring drehen:** durch Listen scrollen, auf „Wird gespielt“ die Lautstärke ändern
- **Mitte:** auswählen
- **MENU (oben):** zurück
- **▶ ❚❚ (unten):** Play/Pause
- **◀◀ / ▶▶:** vorheriger bzw. nächster Titel
- **Einstellungen (oben rechts):** Display, Raster, Haptik

Beim Start fragt die App nach Zugriff auf deine Musik. Ohne Zugriff zeigt sie Demo-Einträge ohne Audio.

## Was du testen solltest

- [ ] Display-Kandidaten in echter Größe vergleichen: Ist die Schrift lesbar? Reichen die Zeilen?
- [ ] Raster einstellen: Wie viele Schritte pro Umdrehung fühlen sich gut an?
- [ ] Haptik-Typen vergleichen, vor allem „Primitive: Tick“ gegen „Primitive: Low Tick“
- [ ] Im Scroll-Test schnell drehen: Welcher Mindestabstand zwischen Ticks fühlt sich gut an?
- [ ] Anschlag am Listenende: hilfreich oder störend?
- [ ] Die gefundenen Werte in `KONZEPT.md` eintragen

## Aufbau des Codes

| Datei | Inhalt |
|---|---|
| `PlayerModel.kt` | Gerätelogik: Seiten, Auswahl, Reaktion auf Rad und Tasten. Entspricht später der Firmware-UI. |
| `ScrollWheel.kt` | Scrollrad: Winkel, Rasterschritte, Tasten |
| `Haptics.kt` | Haptik-Varianten, Ratenbegrenzung, Anschlag |
| `DeviceDisplay.kt` | Rendering des emulierten Displays in Display-Pixeln |
| `Library.kt` | Musik vom Handy laden, Wiedergabe |
| `Settings.kt` | Display-Presets und einstellbare Parameter |
| `MainActivity.kt` | Gehäuse, Einstellungen, Berechtigungen |
