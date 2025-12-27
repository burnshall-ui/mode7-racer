# Modul für alles, was mit Kollisionen zu tun hat.
# Beachte, dass wir das eingebaute Kollisionssystem von pygame nicht verwenden können,
# da die Formen nicht im Bildschirmraum sind, sondern in einem benutzerdefinierten logischen 3D-Raum,
# von dem pygame nichts weiß.

# Eine Klasse, die ein rechteckiges Kollisionsrechteck um ein Spielobjekt modelliert.
# Eine numpy-Liste wird verwendet, um die Position des Kollisionsrechtecks zu modellieren.
class CollisionRect:
    def __init__(self, pos, w, h):
        self.position = pos
        self.width = w
        self.height = h

    # Bestimmt, ob dieses rechteckige Kollisionsrechteck mit dem übergebenen anderen überlappt.
    def overlap(self, other):
        return (
            # x-Position nah genug?
            abs(self.position[0] - other.position[0]) <= self.width / 2 + other.width / 2 and
            # y-Positionen nah genug?
            abs(self.position[1] - other.position[1]) <= self.height / 2 + other.height / 2
        )


    def __str__(self):
        return "(" + str(self.position[0]) + ", " + str(self.position[1]) + "), " + str(self.width) + ", " + str(self.height)