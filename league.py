# Eine Liga besteht aus 5 aufeinanderfolgenden Rennen (gespeichert als Liste),
# die der Spieler absolvieren muss, um die Liga abzuschließen.
class League:
    def __init__(self, races):
        self.races = races
        self.current_race_index = 0 # Index des Rennens, das der Spieler aktuell fährt

    # Gibt die Anzahl der Rennen zurück, aus der diese Liga besteht.
    def length(self):
        return len(self.races)

    # Gibt das Datenobjekt zurück, das das Rennen repräsentiert, das der Spieler aktuell fährt.
    def current_race(self):
        return self.races[self.current_race_index]

    # Bewegt den Index zum nächsten Rennen und gibt dieses Rennen zurück.
    def next_race(self):
        self.current_race_index += 1
        return self.current_race()

    # Gibt True zurück genau dann, wenn der Spieler diese Liga abgeschlossen hat.
    def is_completed(self):
        return self.current_race_index >= self.length()

    # Setzt den Index auf das erste Rennen der Liga zurück.
    def reset(self):
        self.current_race_index = 0