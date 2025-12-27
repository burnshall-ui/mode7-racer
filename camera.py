import numpy # für numpy Array-Typ für Kamera-Position und sin, cos

from settings.renderer_settings import CAM_DISTANCE

class Camera:
    def __init__(self, player, cam_dist = CAM_DISTANCE):
        # Deklariert Positions- und Winkel-Variablen der Kamera.
        # Mit Dummy-Werten initialisiert,
        # die im ersten Frame des Spiels überschrieben werden.
        self.position = numpy.array([0.0, 0.0])
        self.angle = 0

        self.tracked_player = player # der Spieler, dem diese Kamera folgen soll
        self.camera_distance = cam_dist # Abstand, den die Kamera zum Spieler halten soll

    # Die Kamera sollte immer hinter dem Spieler sein,
    # in einem bestimmten Abstand.
    def update(self):
        # Der Offset kann auf dieselbe Weise berechnet werden, wie die Position des Spielers
        # aktualisiert wird, wenn der Spieler sich rückwärts bewegt.
        offset = numpy.array([
            - self.camera_distance * numpy.cos(self.tracked_player.angle), 
            - self.camera_distance * numpy.sin(self.tracked_player.angle)
        ])

        # der Einfachheit halber ist Kamera-Pos = Spieler-Pos für jetzt
        self.position = self.tracked_player.position + offset

        # Kamera schaut immer in dieselbe Richtung wie der Spieler
        self.angle = self.tracked_player.angle