# Eine Liga besteht aus 5 aufeinanderfolgenden Rennen (als Liste gespeichert),
# die der Spieler abschließen muss, um die Liga zu vervollständigen.
class League:
    def __init__(self, races):
        self.races = races
        self.current_race_index = 0 # Index des Rennens, das der Spieler derzeit fährt

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