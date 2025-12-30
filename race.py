# Eine Datenklasse, die alle Daten enthält, die zu einem Rennen gehören.
# Dies umfasst:
# - Dateipfade zu Boden- und Hintergrund-Sprites
# - die Funktion, die die Kollisionskarte für die Strecke erstellt, die in diesem Rennen gefahren wird
# - die Anzahl der Runden, die erforderlich sind, um das Rennen zu gewinnen
# - den Modus des Rennens (Grand-Prix, Zeitangriff, ...)
# - den Dateipfad des Musiktitels, der während des Rennens abgespielt werden soll
class Race:
    def __init__(self, race_track_creator, floor_tex_path, bg_tex_path, required_laps, 
            init_player_pos_x, init_player_pos_y, init_player_angle, is_foggy, race_mode, music_track_path):
        # Kollisionskarte für gefahrene Strecke mit der übergebenen Funktion erstellen
        self.race_track = race_track_creator()
        
        # Umgebungstexturen
        self.floor_texture_path = floor_tex_path
        self.bg_texture_path = bg_tex_path
        
        # Rundenzählung
        self.player_completed_laps = 0
        self.required_laps = required_laps

        # Flag für Rennstart (wird beim ersten Ziellinienkontakt auf True gesetzt)
        self.race_started = False
        self.race_start_timestamp = None

        # Rundenzeiten (in Millisekunden)
        self.lap_times = []
        self.last_lap_timestamp = None

        # Initiale Spielerposition und Rotation
        self.init_player_pos_x = init_player_pos_x
        self.init_player_pos_y = init_player_pos_y
        self.init_player_angle = init_player_angle

        # Ob der Renderer während dieses Rennens einen Nebeleffekt anwenden soll
        self.is_foggy = is_foggy
        
        self.race_mode = race_mode

        self.music_track_path = music_track_path

    # Gibt True zurück genau dann, wenn der registrierte Spieler
    # das Rennen auf dieser Strecke beendet hat
    # (d.h. die erforderliche Anzahl von Runden abgeschlossen hat).
    def player_finished_race(self):
        return self.player_completed_laps >= self.required_laps

    # API für die App-Klasse, um abzufragen, ob der Spieler mindestens eine Runde abgeschlossen hat.
    # Idee: Spieler sollte nur nach Abschluss der ersten Runde boosten können
    def player_completed_first_lap(self):
        return self.player_completed_laps >= 1

    # Aktualisiert zuerst die übergebenen Flags der Schlüssel-Checkpoints der Strecke, auf der dieses Rennen gefahren wird.
    # Prüft dann, ob der Spieler die Ziellinie überquert hat.
    # Wenn ja, werden alle Schlüssel-Checkpoints zurückgesetzt, nachdem geprüft wurde, ob der Spieler alle passiert hat
    # (wenn ja, wird dem Spieler eine abgeschlossene Runde gutgeschrieben).
    #
    # Parameter:
    # player_coll - Kollisionsrechteck des Spielers
    # current_time - Aktueller Zeitstempel (wird benötigt, um den Rennstart-Zeitstempel zu setzen)
    #
    # Rückgabewert: True wenn das Rennen in diesem Frame gestartet wurde, sonst False
    def update_lap_count(self, player_coll, current_time):
        self.race_track.update_key_checkpoints(player_coll)

        race_just_started = False

        # Wenn Spieler die Ziellinie überquert hat
        if self.race_track.is_on_finish_line(player_coll):
            # Rennen beim ersten Ziellinienkontakt starten
            if not self.race_started:
                self.race_started = True
                self.race_start_timestamp = current_time
                self.last_lap_timestamp = current_time
                race_just_started = True
                print("Rennen gestartet!")

            # Wenn Spieler ehrlich eine Runde beendet hat
            if self.race_track.all_key_checkpoints_passed():
                # Rundenzeit berechnen und speichern
                lap_time_ms = (current_time - self.last_lap_timestamp) * 1000
                self.lap_times.append(lap_time_ms)
                self.last_lap_timestamp = current_time

                # Abgeschlossene Runden erhöhen.
                # Wenn Spieler genug Runden abgeschlossen hat, Finish-Sequenz initialisieren.
                self.player_completed_laps += 1
                print(f"{self.player_completed_laps} Runden abgeschlossen! Rundenzeit: {lap_time_ms:.0f}ms")

                if self.player_finished_race():
                    total_time_ms = sum(self.lap_times)
                    print(f"Rennen beendet! Gesamtzeit: {total_time_ms:.0f}ms")
            self.race_track.reset_key_checkpoints()

        return race_just_started

    # Startet das Rennen neu und setzt alle Renndaten auf ihre initialen Werte zurück.
    # Z.B. abgeschlossene Runden des Spielers, passierte Schlüssel-Checkpoints, ...
    def reset_data(self):
        self.player_completed_laps = 0
        self.race_started = False
        self.race_start_timestamp = None
        self.lap_times = []
        self.last_lap_timestamp = None
        self.race_track.reset_key_checkpoints()

    # ------------- Verfügbarmachung der RaceTrack-API ---------------------

    def is_on_track(self, other):
        return self.race_track.is_on_track(other)

    def is_on_dash_plate(self, other):
        return self.race_track.is_on_dash_plate(other)

    def is_on_recovery_zone(self, other):
        return self.race_track.is_on_recovery_zone(other)
    
    def is_on_ramp(self, other):
        return self.race_track.is_on_ramp(other)

    def guard_rails_active(self):
        return self.race_track.guard_rails_active()

    # ------------- Ende der Verfügbarmachung der RaceTrack-API --------------