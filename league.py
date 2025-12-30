# Eine Liga besteht aus 5 aufeinanderfolgenden Rennen (als Liste gespeichert),
# die der Spieler abschließen muss, um die Liga zu vervollständigen.
class League:
    def __init__(self, races):
        self.races = races
        self.current_race_index = 0 # Index des Rennens, das der Spieler derzeit fährt
        self.total_time_ms = 0 # Gesamtzeit über alle abgeschlossenen Rennen (in Millisekunden)

    # Gibt die Anzahl der Rennen zurück, aus denen diese Liga besteht.
    def length(self):
        return len(self.races)

    # Gibt das Datenobjekt zurück, das das Rennen repräsentiert, das der Spieler derzeit fährt.
    def current_race(self):
        return self.races[self.current_race_index]

    # Bewegt den Index zum nächsten Rennen und gibt dieses Rennen zurück.
    def next_race(self):
        self.current_race_index += 1
        return self.current_race()

    # Gibt genau dann True zurück, wenn der Spieler diese Liga abgeschlossen hat.
    def is_completed(self):
        return self.current_race_index >= self.length()

    # Setzt den Index auf das erste Rennen der Liga zurück.
    def reset(self):
        self.current_race_index = 0
        self.total_time_ms = 0

    # Fügt die Gesamtzeit eines abgeschlossenen Rennens zur Liga-Gesamtzeit hinzu.
    # Sollte aufgerufen werden, wenn ein Rennen beendet wurde.
    def add_race_time(self, race_time_ms):
        self.total_time_ms += race_time_ms
        print(f"Liga-Gesamtzeit: {self.total_time_ms:.0f}ms")