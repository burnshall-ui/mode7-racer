# mode7-racer (Fork)

Prototyp eines F-Zero-artigen Rennspiels, entwickelt mit Python/pygame.

**Dies ist ein Fork von [pschuermann97/mode7-racer](https://github.com/pschuermann97/mode7-racer) mit Gameplay-Verbesserungen.**

<p float="left">
  <img width="448" alt="0" src="https://user-images.githubusercontent.com/28012017/235456613-3b90fb13-49b9-4e57-9858-cec4e5bd37cd.png">
  <img width="448" alt="1" src="https://user-images.githubusercontent.com/28012017/235456656-672e1c48-5d49-4b36-acf8-dbaac1d18623.png">
</p>

<p float="left">
  <img width="448" alt="2" src="https://user-images.githubusercontent.com/28012017/235456666-2fbcc8e8-52da-46f9-be8d-3eae1fcce96b.png">
  <img width="449" alt="3" src="https://user-images.githubusercontent.com/28012017/235456683-48ec5b33-b2ad-4ee9-9655-f82cf4b70983.png">
</p>

## Aktueller Status

**Testversion mit 2 funktionierenden Strecken:**
- Funktioniert1 (neue selbst erstellte Strecke)
- Event Horizon I

Die anderen Strecken sind noch in Arbeit - die Kollisionsdaten passen noch nicht zur Textur.

## Änderungen in diesem Fork

- **Animiertes Logo-Intro** mit Zoom-Effekt und Sound
- **Retro-Menüsystem** mit Logo, Streckenauswahl und Sound-Effekten
  - Navigation-Sounds beim Blättern
  - Bestätigungs-Sound bei Auswahl
  - Animierte Pfeile von beiden Seiten (SNES-Style)
- **Mini-Map (unten links)**: Statische Streckenübersicht mit Spielerpunkt
  - Optional pro Strecke eigenes Minimap-Bild (siehe Abschnitt „Mini-Map“ unten)
- **Pause-Menü** (ESC während des Rennens) mit Continue/Restart/Quit
- Menü-Musik mit angepasster Lautstärke
- Höhere Auflösung mit dynamischem Skalierungssystem
- Pfeiltasten-Steuerung (intuitiver)
- Angepasste Spielgeschwindigkeit für bessere Spielbarkeit
- SNES-Style Game Over Bildschirm
- Rückwärtssprung-Bug behoben
- **Map Editor** zum visuellen Erstellen von Strecken-Kollisionen
- **Bobbing-Effekt** beim Fahren (F-Zero-Style Auf-und-Ab)
- **Dirt-Zonen** als neues Streckenelement (verlangsamt den Spieler)
- **Partikel-Effekte** bei der Landung nach Sprüngen (Funkenflug)
- Verbesserte Sprungphysik (kürzere, präzisere Sprünge)

Das in dieser Implementierung verwendete Mode7-Rendering-Modul basiert auf dem Mode7-Tutorial von Coder Space (https://www.youtube.com/watch?v=D0MPYZYe40E).

Wenn du mit dem Code des Spielprototyps experimentieren möchtest, siehe Abschnitt "Installationsanweisungen" unten.
Wenn du den Prototyp nur ausprobieren möchtest und die erforderlichen Abhängigkeiten nicht auf deinem Computer installieren möchtest, siehe "Test-Build".

Bitte beachte, dass der ursprüngliche Inhalt dieses Repositories unter der Creative Commons Lizenz CC BY-NC-ND 4.0 (https://creativecommons.org/licenses/by-nc-nd/4.0/) verfügbar ist.
Ursprünglicher Autor: [pschuermann97](https://github.com/pschuermann97)

## Map Editor

Der Map Editor ermöglicht das visuelle Erstellen und Bearbeiten von Strecken-Kollisionsdaten.

### Starten

```bash
python map_editor.py
```

### Steuerung

| Taste | Funktion |
|-------|----------|
| **Q / E** | Textur wechseln (vorher/nächste) |
| **Pfeiltasten** | Karte verschieben |
| **+ / -** | Zoom |
| **T** | Rechteck-Typ wechseln (Strecke/Rampe/Recovery/Dash/Finish/Checkpoint) |
| **P** | Startposition setzen (dann auf Karte klicken) |
| **A / D** | Startwinkel drehen |
| **L** | Bestehende Track-Kollisionsdaten laden |
| **C** | Python-Code in Konsole ausgeben |
| **S** | Python-Code in Datei speichern |
| **N** | Alles löschen (Rechtecke + Startposition) |
| **ESC** | Beenden |

### Maus

| Aktion | Funktion |
|--------|----------|
| **Linksklick + Ziehen** | Neues Rechteck zeichnen |
| **Rechtsklick** | Rechteck löschen |
| **Mittelklick + Ziehen** | Karte bewegen |
| **Mausrad** | Zoom |

### Workflow: Neue Strecke erstellen

1. Erstelle eine PNG-Textur (4000x2000 Pixel) und lege sie in `gfx/`
2. Starte den Map Editor und wähle die Textur mit Q/E
3. Zeichne die Strecken-Rechtecke (Typ: Strecke)
4. Füge Ziellinie, Checkpoints, Rampen etc. hinzu
5. Setze die Startposition mit **P** + Klick und drehe den Winkel mit **A/D**
6. Drücke **C** um den Code zu sehen oder **S** um ihn zu speichern
7. Kopiere den Code in `settings/track_settings.py` als neue Track-Funktion
8. Kopiere die Startposition (`init_player_pos_x/y/angle`) in `settings/league_settings.py`
9. Aktualisiere die Track-Namen in `menu.py`

### Rechteck-Typen

| Typ | Farbe | Beschreibung |
|-----|-------|--------------|
| Strecke | Grün | Fahrbare Fläche |
| Rampe | Gelb | Sprungschanze |
| Recovery | Cyan | Heilzone (regeneriert Energie) |
| Dash Plate | Magenta | Speed-Booster |
| Dirt | Braun | Verlangsamungszone (Damping-Effekt) |
| Ziellinie | Rot | Start/Ziel |
| Checkpoint | Blau | Muss passiert werden für gültige Runde |

### Startposition

Die Startposition wird als oranger Pfeil angezeigt und zeigt Position und Blickrichtung des Spielers beim Rennstart.

- **P** drücken, dann auf die Karte klicken um die Position zu setzen
- **A/D** um den Startwinkel zu drehen
- Der generierte Code enthält `init_player_pos_x`, `init_player_pos_y` und `init_player_angle`

## Installationsanweisungen

1. Installiere Python Version 3.10+ auf deinem Computer (https://www.python.org/downloads/)
2. Installiere pygame: `pip install pygame`
3. Installiere numba für Performance-Optimierung: `pip install numba`
4. Klone dieses Repository: `git clone`
5. Starte das Spiel: `python main.py`

## Test-Build

Du findest den ursprünglichen Test-Build unter https://pschuermann97.itch.io/mode7-racer, der 4 aufeinanderfolgende Rennen bietet.

## Steuerung (Spiel)

| Taste | Funktion |
|-------|----------|
| **Pfeil Links/Rechts** | Lenken |
| **Pfeil Hoch** | Beschleunigen |
| **Pfeil Runter** | Bremsen |
| **Leertaste** | Booster verwenden (nach 1 Runde freigeschaltet) |
| **ESC** | Pause-Menü öffnen |
| **R** | Rennen neu starten (Debug) |

### Menü-Steuerung

| Taste | Funktion |
|-------|----------|
| **Pfeil Hoch/Runter** | Menü-Navigation |
| **Enter / Leertaste** | Bestätigen |
| **ESC** | Pause-Menü schließen |

Jedes Rennen erfordert 3 Runden zum Abschluss.
Nach Abschluss eines Rennens drücke Leertaste, um zum nächsten zu springen.
Wenn deine Energie auf null sinkt, drücke Leertaste zum Neustart.

## Mini-Map

Während eines Rennens wird unten links eine **statische Mini-Map** angezeigt.

- **Eigene Mini-Map pro Strecke (empfohlen)**:
  - Lege ein Bild unter `gfx/ui/minimaps/` ab.
  - Namenskonvention: `gfx/ui/minimaps/<floor_texture_basename>_minimap.png`
  - Beispiel: `gfx/event_horizon_track2.png` → `gfx/ui/minimaps/event_horizon_track2_minimap.png`
- **Fallback**: Wenn kein Bild vorhanden ist, rendert das Spiel eine einfache Mini-Map aus den Kollisions-Rechtecken.
- **Konfiguration**: Siehe `settings/ui_settings.py` (z.B. `MINIMAP_ENABLED`, Skalierung/Größe, Marker-Verhalten).
