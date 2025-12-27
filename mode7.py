import pygame
import numpy

# JIT-Compiler und prange-Funktion für Leistungssteigerung
from numba import njit, prange

from settings.renderer_settings import *

class Mode7:
    # Initialisierungsmethode, die die Texturen lädt (spezifiziert über den an den Konstruktor übergebenen Pfad),
    # diesen Mode-7-Renderer mit der App verknüpft
    # und einige Statusvariablen setzt.
    # 
    # Der horizon-Parameter beschreibt die Horizonthöhe der mit diesem Renderer gerenderten Szenen,
    # d.h. die minimale Höhe der Bodentextur-Pixel
    # (dabei beachten, dass die y-Koordinate nach unten auf dem Bildschirm abnimmt). 
    def __init__(self, app, floor_tex_path, bg_tex_path, is_foggy, horizon = STD_HORIZON):
        # Renderer mit der App verknüpfen
        self.app = app

        # Statusvariablen initialisieren
        self.is_foggy = is_foggy
        self.horizon = horizon

        # Bodentextur laden
        self.floor_tex = pygame.image.load(floor_tex_path).convert()
        
        # Bodentexturgröße für spätere Verwendung speichern
        self.floor_tex_size = self.floor_tex.get_size()

        # 3D-Array erstellen, das die Pixel des Bodens darstellt.
        # Genauer: Kopiert die Pixel von der Oberfläche, die die Bodentextur darstellt,
        # in ein neues 3D-Array.
        self.floor_array = pygame.surfarray.array3d(self.floor_tex)

        # Hintergrundtextur laden
        self.bg_tex = pygame.image.load(bg_tex_path).convert()

        # Decken-Textur auf Bodentexturgröße skalieren
        self.bg_tex_size = self.bg_tex.get_size()

        # Decke durch 3D-Array analog zum Boden darstellen
        self.bg_array = pygame.surfarray.array3d(self.bg_tex)

        # Array erstellen, das die Bildschirmpixel darstellt
        self.screen_array = pygame.surfarray.array3d(pygame.Surface(WIN_RES))

    # Aktualisiert die mode7-basierte Umgebung.
    # Eine Kamera-Referenz wird übergeben, um
    # den Frame basierend auf der aktuellen Position und Rotation der Kamera (und damit des Spielers) rendern zu können.
    def update(self, camera):
        # Dynamischer FOV-Zoom basierend auf Spielergeschwindigkeit
        # Je schneller, desto höher der Focal Length (Zoom-Effekt)
        player_speed = camera.tracked_player.current_speed
        max_speed = camera.tracked_player.machine.max_speed

        # Speed-Faktor zwischen 0 und 1
        speed_factor = min(player_speed / max_speed, 1.0) if max_speed > 0 else 0

        # FOV erhöht sich subtil bei maximaler Geschwindigkeit
        # 30% mehr bei max Speed - spürbar aber nicht zu krass
        dynamic_focal_len = FOCAL_LEN * (1.0 + speed_factor * 0.3)

        # Dynamische Background-Rotation - ganz leicht schneller
        dynamic_bg_rotation = BACKGROUND_ROTATION_SPEED * (1.0 + speed_factor * 0.15)

        # Frame rendern mit dynamischen Werten
        self.screen_array = self.render_frame(
            floor_array = self.floor_array,
            bg_array = self.bg_array,
            screen_array = self.screen_array,
            floor_tex_size = self.floor_tex_size,
            bg_tex_size = self.bg_tex_size,
            is_foggy = self.is_foggy,
            pos = camera.position,
            angle = camera.angle,
            horizon = self.horizon,
            focal_len = dynamic_focal_len,
            bg_rotation_speed = dynamic_bg_rotation
        )

    # Berechnet einen einzelnen Frame der Mode-7-Umgebung Pixel für Pixel.
    # Benötigt numba Just-in-Time-Compiler-Unterstützung (Dekoratoren),
    # um eine vernünftige Framerate zu erreichen, wenn es jeden Frame ausgeführt wird.
    # 
    # Parameter:
    # floor_array: Array, das die Pixel der Bodentextur enthält
    # bg_array: Array, das die Pixel der Hintergrundtextur enthält
    # screen_array: Array, das den gerenderten Frame enthält (Pixel für Pixel aktualisiert)
    # floor_tex_size: Größe der Bodentextur
    # bg_tex_size: Größe der Hintergrundtextur
    # is_foggy: ob die Szene, von der ein Frame gerendert wird, einen Nebeleffekt hat
    # pos: aktuelle Position der Kamera
    # angle: aktueller Winkel, um den die Kamera rotiert ist
    # horizon: die minimale y-Koordinate der Bodenpixel (beachten: y nimmt nach unten auf dem Bildschirm zu)
    @staticmethod
    @njit(fastmath=True, parallel=True)
    def render_frame(floor_array, bg_array, screen_array, floor_tex_size, bg_tex_size,
        is_foggy, pos, angle, horizon, focal_len, bg_rotation_speed):
        # Sinus- und Kosinuswerte des Spielerwinkels berechnen,
        # um sie zum Rendern der Umgebung basierend auf der Rotation des Spielers zu verwenden.
        sin, cos = numpy.sin(angle), numpy.cos(angle)

        # Farbwert für jedes einzelne Pixel (i, j) berechnen.
        # prange-Funktion (anstatt range-Funktion) für äußere Schleife aus Leistungsgründen verwendet.
        for i in prange(WIDTH):
            # Hintergrundbild-Rendering berechnen
            for j in range(0, horizon):
                # Hintergrundbild wird um den Winkel verschoben, um den der Spieler rotiert ist
                # Verwendet dynamische bg_rotation_speed
                screen_array[i][j] = bg_array[(i - int(angle * bg_rotation_speed)) % bg_tex_size[0]][j % bg_tex_size[1]]
            # Boden-Rendering berechnen
            for j in range(horizon, HEIGHT):
                # Stellen wir uns vor, dass die Bodentextur unendlich
                # sowohl horizontal als auch vertikal auf einer 2D-Ebene gekachelt ist.
                # Nehmen wir an, dass die horizontalen und vertikalen Achsen dieser Ebene
                # mit px und py bezeichnet sind.
                # Nehmen wir weiter an, dass die horizontalen und vertikalen Achsen des Bildschirms
                # mit x und z bezeichnet sind,
                # während y eine imaginäre Achse ist, die aus dem Bildschirm herauskommt.
                #
                # Idee: Um den Mode-7-Effekt zu emulieren, berechnen, welches Pixel der Bodentextur
                # über dem Pixel (i, j) des Bildschirms in diesem Frame liegt

                # Erster Schritt: Rohe x, y, z Koordinaten berechnen
                # ohne Mode-7-Style-Projektion.
                #
                # Wir passen die x-Koordinate an, sodass die Textur in der Mitte des Bildschirms ist.
                # Außerdem wird die Tiefenkoordinate (y) immer um die Brennweite der Kamera verschoben.
                # Schließlich müssen wir eine kleine Konstante zur Bildschirmhöhenkoordinate (z) hinzufügen,
                # um Division-durch-0-Fehler im nächsten Schritt zu verhindern.
                x = HALF_WIDTH - i
                y = j + focal_len  # Verwendet dynamischen focal_len
                z = j - horizon + 0.01 

                # Spielerrotation anwenden (die aus dem Winkel berechnet wird, um den sie rotiert sind),
                # "Standardformel für Rotation im 2D-Raum".
                rx = x * cos + y * sin
                ry = x * -sin + y * cos

                # Mode-7-Style-Projektion anwenden.
                # Kameraposition wird hier als Offset verwendet, um Bewegung zu ermöglichen
                px = (rx / z + pos[1]) * SCALE
                py = (ry / z + pos[0]) * SCALE

                # Berechnen, welches Pixel der Bodentextur über dem Punkt (i, j) liegt
                floor_pos = int(px % floor_tex_size[0]), int(py % floor_tex_size[1])

                # Den entsprechenden Farbwert im Boden-Array nachschlagen
                floor_col = floor_array[floor_pos]

                # Um hässliche Artefakte am Horizont zu verhindern:
                # Einen Dämpfungskoeffizienten im Intervall [0, 1] basierend auf dem "Tiefen"-Wert berechnen
                attenuation = min(max(7.5 * (abs(z) / HALF_HEIGHT), 0), 1)

                # Nebeleffekt berechnen, abhängig davon, ob die gerenderte Szene neblig ist.
                fog = (1 - attenuation) * FOG_DENSITY if is_foggy else 0
                
                # Dämpfung und optionalen Nebeleffekt anwenden (komponentenweise auf Farbvektor)
                floor_col = (floor_col[0] * attenuation + fog,
                    floor_col[1] * attenuation + fog,
                    floor_col[2] * attenuation + fog)

                # Das berechnete Pixel in das Bildschirm-Array füllen
                screen_array[i, j] = floor_col

        return screen_array

    def draw(self):
        # Zeichnet den Bildschirminhalt, der in der render_frame-Methode berechnet wurde.
        #
        # Kopiert Werte aus dem Array, das den Bildschirm darstellt,
        # in die Oberfläche, die den Bildschirm darstellt.
        # Diese Oberfläche wird automatisch von pygame gerendert.
        pygame.surfarray.blit_array(self.app.screen, self.screen_array)
