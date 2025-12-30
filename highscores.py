# Highscore-Manager für Mode7 Racer
# Speichert und lädt beste Zeiten pro Track

import json
import os

class HighscoreManager:
    def __init__(self, filepath="highscores.json"):
        """Initialisiert den Highscore-Manager"""
        self.filepath = filepath
        self.highscores = self.load_highscores()

    def load_highscores(self):
        """Lädt Highscores aus der JSON-Datei"""
        if not os.path.exists(self.filepath):
            return {}

        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Fehler beim Laden der Highscores: {e}")
            return {}

    def save_highscores(self):
        """Speichert Highscores in die JSON-Datei"""
        try:
            with open(self.filepath, 'w', encoding='utf-8') as f:
                json.dump(self.highscores, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Fehler beim Speichern der Highscores: {e}")

    def get_track_highscores(self, track_name):
        """Holt die Highscores für einen bestimmten Track"""
        if track_name not in self.highscores:
            self.highscores[track_name] = {
                "best_lap": None,
                "best_total": None
            }
        return self.highscores[track_name]

    def update_highscores(self, track_name, lap_times):
        """
        Aktualisiert die Highscores für einen Track basierend auf den Rundenzeiten.

        Parameter:
        - track_name: Name des Tracks
        - lap_times: Liste der Rundenzeiten in Millisekunden

        Rückgabe: Dictionary mit Infos über neue Rekorde
        {
            "new_best_lap": bool,
            "new_best_total": bool,
            "best_lap": float oder None,
            "best_total": float oder None
        }
        """
        if not lap_times:
            return {
                "new_best_lap": False,
                "new_best_total": False,
                "best_lap": self.get_best_lap(track_name),
                "best_total": self.get_best_total(track_name)
            }

        track_scores = self.get_track_highscores(track_name)

        # Beste Rundenzeit in diesem Rennen
        current_best_lap = min(lap_times)
        total_time = sum(lap_times)

        # Flags für neue Rekorde
        new_best_lap = False
        new_best_total = False

        # Prüfe beste Rundenzeit
        if track_scores["best_lap"] is None or current_best_lap < track_scores["best_lap"]:
            track_scores["best_lap"] = current_best_lap
            new_best_lap = True

        # Prüfe beste Gesamtzeit
        if track_scores["best_total"] is None or total_time < track_scores["best_total"]:
            track_scores["best_total"] = total_time
            new_best_total = True

        # Speichern, wenn neue Rekorde
        if new_best_lap or new_best_total:
            self.save_highscores()

        return {
            "new_best_lap": new_best_lap,
            "new_best_total": new_best_total,
            "best_lap": track_scores["best_lap"],
            "best_total": track_scores["best_total"]
        }

    def get_best_lap(self, track_name):
        """Gibt die beste Rundenzeit für einen Track zurück (oder None)"""
        track_scores = self.get_track_highscores(track_name)
        return track_scores["best_lap"]

    def get_best_total(self, track_name):
        """Gibt die beste Gesamtzeit für einen Track zurück (oder None)"""
        track_scores = self.get_track_highscores(track_name)
        return track_scores["best_total"]

    def reset_track_highscores(self, track_name):
        """Setzt die Highscores für einen Track zurück"""
        if track_name in self.highscores:
            del self.highscores[track_name]
            self.save_highscores()

    def reset_all_highscores(self):
        """Setzt alle Highscores zurück"""
        self.highscores = {}
        self.save_highscores()
