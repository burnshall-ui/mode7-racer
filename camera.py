import numpy # für numpy-Array-Typ für Kameraposition und sin, cos

from settings.renderer_settings import CAM_DISTANCE

class Camera:
    def __init__(self, player, cam_dist = CAM_DISTANCE):
        # Positions- und Winkelvariablen der Kamera deklarieren.
        # Mit Dummy-Werten initialisiert,
        # die im ersten Frame des Spiels überschrieben werden.
        self.position = numpy.array([0.0, 0.0])
        self.angle = 0

        self.tracked_player = player # der Spieler, dem diese Kamera folgen soll
        self.camera_distance = cam_dist # Abstand, den die Kamera zum Spieler halten soll

    # Kamera sollte immer hinter dem Spieler sein,
    # in einem bestimmten Abstand.
    def update(self):
        # Dynamischer Kamera-Abstand basierend auf Geschwindigkeit
        # Je schneller, desto weiter weg (für bessere Übersicht bei Speed)
        player_speed = self.tracked_player.current_speed
        max_speed = self.tracked_player.machine.max_speed

        # Speed-Faktor zwischen 0 und 1
        speed_factor = min(player_speed / max_speed, 1.0) if max_speed > 0 else 0

        # Kamera-Abstand erhöht sich moderat bei maximaler Geschwindigkeit
        # 50% weiter weg bei max Speed für bessere Übersicht
        dynamic_distance = self.camera_distance * (1.0 + speed_factor * 0.5)

        # Der Offset kann auf die gleiche Weise berechnet werden, wie die Position des Spielers
        # aktualisiert wird, wenn der Spieler rückwärts fährt.
        offset = numpy.array([
            - dynamic_distance * numpy.cos(self.tracked_player.angle),
            - dynamic_distance * numpy.sin(self.tracked_player.angle)
        ])

        # Der Einfachheit halber: Kamera-Pos = Spieler-Pos für jetzt
        self.position = self.tracked_player.position + offset

        # Kamera schaut immer in dieselbe Richtung wie der Spieler
        self.angle = self.tracked_player.angle