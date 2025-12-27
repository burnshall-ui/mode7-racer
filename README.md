# mode7-racer (Fork)

Prototyp eines F-Zero-artigen Rennspiels, entwickelt mit Python/pygame.

**Dies ist ein Fork von [pschuermann97/mode7-racer](https://github.com/pschuermann97/mode7-racer) mit Gameplay-Verbesserungen.**

<p float="left">
  <img width="448" alt="0" src="https://user-images.githubusercontent.com/28012017/235456613-3b90fb13-49b9-4e57-9858-cec4e5bd37cd.png">
  <img width="448" alt="1" src="https://user-images.githubusercontent.com/28012017/235456656-672e1c48-5d49-4b36-acf8-dbaac1d18623.png">
</p>

<p float="left">
  <img width="448" alt="2" src="https://user-images.githubusercontent.com/28012017/235456666-2fbcc8e8-52da-46f9-be8d-3eae1fcce96b.png">
  <img width="449" alt="3" src="https://user-images.githubusercontent.com/28012017/235456683-48ec5b33-b2ac-4ee9-9655-f82cf4b70983.png">
</p>

## Änderungen in diesem Fork

- Höhere Auflösung mit dynamischem Skalierungssystem
- Pfeiltasten-Steuerung (intuitiver)
- Angepasste Spielgeschwindigkeit für bessere Spielbarkeit
- SNES-Style Game Over Bildschirm
- Rückwärtssprung-Bug behoben

Das in dieser Implementierung verwendete Mode7-Rendering-Modul basiert auf dem Mode7-Tutorial von Coder Space (https://www.youtube.com/watch?v=D0MPYZYe40E).

Wenn du mit dem Code des Spielprototyps experimentieren möchtest, siehe Abschnitt "Installationsanweisungen" unten.
Wenn du den Prototyp nur ausprobieren möchtest und die erforderlichen Abhängigkeiten nicht auf deinem Computer installieren möchtest, siehe "Test-Build".

Bitte beachte, dass der ursprüngliche Inhalt dieses Repositories unter der Creative Commons Lizenz CC BY-NC-ND 4.0 (https://creativecommons.org/licenses/by-nc-nd/4.0/) verfügbar ist.
Ursprünglicher Autor: [pschuermann97](https://github.com/pschuermann97)

## Installationsanweisungen

1. Installiere Python Version 3.10 auf deinem Computer (https://www.python.org/downloads/release/python-31011/). In diesem Projekt wurde Python 3.10.10 verwendet. Beachte, dass die Skripte des Projekts NICHT mit dem Python 3.11 Interpreter laufen, da nicht alle Abhängigkeiten mit Python 3.11 funktionieren.
2. Installiere pygame 2.2.0. Wenn du pip zur Verwaltung deiner Python-Pakete verwendest, kann dies durch Ausführen des Befehls `pip install pygame==2.2.0` erfolgen.
3. Zur Leistungsoptimierung und um den Mode7-Renderer in Echtzeit ausführen zu können, verwendet diese Implementierung den Python Just-in-Time-Compiler numba (https://numba.pydata.org/), der numerische Funktionen zur Laufzeit in Maschinencode kompiliert, um ihre Ausführung erheblich zu beschleunigen.
Für diese Implementierung wurde numba Version 0.56.4 verwendet, die du über pip installieren kannst, indem du den Befehl `pip install numba==0.56.4` ausführst.
Hinweis: numba funktioniert noch nicht mit Python 3.11 (Stand: 1. Mai 2023).
4. Klone dieses Repository auf deinen Computer mit `git clone`.
5. Navigiere zum Hauptordner dieses Repositories und führe das Skript `main.py` mit dem Python-Interpreter aus.

## Test-Build

Du findest den ursprünglichen Test-Build unter https://pschuermann97.itch.io/mode7-racer, der 4 aufeinanderfolgende Rennen bietet.

## Steuerung (dieser Fork)

- **Pfeil Links/Rechts**: Lenken
- **Pfeil Hoch**: Beschleunigen
- **Pfeil Runter**: Bremsen
- **Leertaste**: Booster verwenden (freigeschaltet nach Abschluss einer Runde)
- **R**: Rennen neu starten (Debug)

Jedes Rennen erfordert 3 Runden zum Abschluss.
Nach Abschluss eines Rennens drücke Leertaste, um zum nächsten zu springen.
Wenn deine Energie auf null sinkt, drücke Leertaste zum Neustart.
