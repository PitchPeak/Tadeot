# „I Want You“ – Thinking Head für den Tag der offenen Tür

Eigenständige Kiosk-Seite, unabhängig von der PitchPeak-App. Ein Thinking Head im Uncle-Sam-Stil erkennt per Webcam die Person vor dem Bildschirm. Er folgt ihr mit den Augen, zeigt auf sie und spricht sie an.

## Ablauf

| Situation | Reaktion |
| --- | --- |
| Niemand da | Kopf schaut herum und führt ab und zu ein Selbstgespräch |
| Person weiter weg im Raum | „Hey, du da hinten! Ja, genau du! Schau mal kurz her!“ |
| Person steht nah davor | Zeigt auf sie: „Hey, DU! Genau dich such ich!“, danach ein paar Sätze zu PitchPeak und zur HTL |
| Person geht während des Pitches | „Bis später! Schau gern nochmal vorbei!“, danach kurze Pause |

Bei mehreren Personen wird immer die nächste angesprochen. Bleibt jemand weiter weg stehen, ruft der Kopf alle 12 Sekunden erneut.

Erkannt wird auf zwei Wegen, beide laufen lokal im Browser (MediaPipe):

- **Gesichtserkennung**: genau, aber nur bis etwa 2 m.
- **Personenerkennung (ganzer Körper)**: findet Leute auch weiter hinten im Raum. Getestet mit Fotos, auf denen die Person 36 % bzw. 68 % der Bildhöhe füllt. Das entspricht grob 3 bis 6 m Abstand.

„Nah“ heißt: Das Gesicht ist mindestens 14 % der Bildbreite breit, oder der Körper füllt mindestens 85 % der Bildhöhe.

## Starten

**Online:** https://pitchpeak.github.io/Tadeot/ (läuft auf jedem Gerät mit Browser und Webcam)

1. Link in Chrome oder Edge öffnen.
2. **Starten** klicken. Das schaltet Vollbild und Ton frei und fragt nach der Kamera.
3. Webcam oben mittig am Bildschirm befestigen.

Beim Start braucht die Seite Internet, um die Erkennungsmodelle (MediaPipe) und den QR-Code zu laden.

Jeder Push auf `main` veröffentlicht die Seite automatisch neu (`.github/workflows/pages.yml`).

**Lokal testen:** Die Kamera braucht HTTPS oder `localhost`:

```bash
npx serve .
```

## Tasten

| Taste | Funktion |
| --- | --- |
| P | **Pause**: Kopf chillt, reagiert auf niemanden und sagt nichts. Nochmal P = weiter |
| Leertaste | Person manuell ansprechen |
| 1 / 2 / 3 | Fachperson / kritischer Zuhörer / Anfänger |
| V | Notfall-Browserstimme wechseln (nur relevant, wenn MP3s fehlen) |
| M | Ton aus/an |
| F | Vollbild |
| C | Kamera-Vorschau und Statusanzeige (zum Einrichten) |
| H | Hilfe |

Ohne Kamera folgt der Kopf der Maus. Gedrückte Maustaste simuliert eine Person, die nah davorsteht.

## Stimme

Gesprochen wird mit fertigen MP3-Dateien im Ordner `audio/`. Die Stimme ist **„Thorsten“**, eine männliche deutsche Open-Source-Stimme (Piper TTS, Lizenz CC0). Das funktioniert in jedem Browser, auch offline, und ist unabhängig davon, welche Stimmen auf dem Laptop installiert sind.

| Rolle | Stimme | Gemessene Tonhöhe |
| --- | --- | --- |
| Fachperson | Thorsten (hohe Qualität) | ca. 115 Hz |
| Kritiker | Thorsten „neutral“ | ca. 122 Hz |
| Anfänger | Thorsten „überrascht“ | ca. 129 Hz |

Männerstimmen liegen typischerweise bei 85–155 Hz.

Nur wenn zu einem Text keine MP3 existiert, springt die Browserstimme ein. Taste `V` probiert diese Notfallstimme aus.

### Texte ändern

Alle Sprüche stehen in `lines.js`. Nach einer Änderung die MP3s neu erzeugen (Python 3.10+ und ffmpeg nötig):

```bash
pip install piper-tts
```

```bash
python generate_voices.py
```

Beim ersten Lauf lädt das Skript die Stimmmodelle (~190 MB) nach `.voices/`. Dieser Ordner wird nicht committet. Unveränderte Texte werden übersprungen. Welche Stimme welche Rolle bekommt, steht oben im Skript (`ROLE_VOICES`).

## Anpassen

Texte stehen in `lines.js`, Aussehen und Schwellenwerte oben im Skript von `index.html` (`ROLES`, `T`). Ist der Abstand am Stand anders als gedacht, mit `C` die Werte `w` (Gesicht) bzw. `h` (Körper) ablesen und `nearFace` oder `nearPerson` anpassen.

## Datenschutz

Das Kamerabild wird nur lokal im Browser ausgewertet. Nichts wird gespeichert oder hochgeladen. Nur die Erkennungsmodelle werden beim Start aus dem Internet geladen.
