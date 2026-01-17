# Importe externer Module
import pygame, time
from pygame import mixer # Modul zum Abspielen von Sound
import sys
import os
import math

# Import der Spiel-Einstellungen
from settings.debug_settings import *
from settings.machine_settings import *
from settings.renderer_settings import *
from settings.track_settings import *
from settings.ui_settings import *
from settings.ui_settings import GAME_OVER_OVERLAY_ALPHA, GAME_OVER_IMAGE, PRESS_SPACE_IMAGE
from settings.ui_settings import FINISH_OVERLAY_ALPHA, RACE_FINISHED_IMAGE, get_pixel_font
from settings.key_settings import STD_CONFIRM_KEY, STD_DEBUG_RESTART_KEY
from settings.league_settings import *
from settings.music_settings import *
from settings.gamepad_settings import GAMEPAD_DEBUG

# Weitere Importe aus diesem Projekt
from mode7 import Mode7
from player import Player
from particles import SparkParticle
from camera import Camera
from track import Track
from race import Race
from league import League
from settings.track_settings import TrackCreator
from ui import UI
from menu import Menu
from highscores import HighscoreManager

# Nur für Debug-Importe
from collision import CollisionRect

# Die Klasse, die alle Aufgaben zur Ausführung des Spiels verwaltet/koordiniert.
# Dies umfasst das Rendern des Bildschirms,
# das Abhören von Ereignissen (z.B. gedrückte Tasten, ...),
# das Aktualisieren des Spielzustands und
# das Verwalten der internen Spieluhr.
class App:
    def __init__(self):
        # ------------- Allgemeine Initialisierung --------------------

        # pygame.font muss initialisiert werden, bevor Fonts geladen werden
        pygame.font.init()
        
        self.screen = pygame.display.set_mode(WIN_RES)
        self.clock = pygame.time.Clock()

        self.in_racing_mode = False

        # Erstellt eine Gruppe von Sprites, die alle Sprites enthält,
        # die sich über den Bildschirm bewegen.
        self.moving_sprites = pygame.sprite.Group()

        # Erstellt eine Gruppe von Sprites für alle, die sich nicht bewegen
        self.static_sprites = pygame.sprite.Group()

        # Erstellt eine Gruppe von Sprites für alle Sprites in der UI.
        self.ui_sprites = pygame.sprite.Group()

        # Partikel-Gruppe
        self.particles = pygame.sprite.Group()

        # Initialisiert das Modul, das für das Abspielen von Sounds verantwortlich ist
        mixer.init()
        mixer.music.set_volume(MUSIC_VOLUME)

        # Gamepad/Controller initialisieren
        pygame.joystick.init()
        self.gamepad = None
        if pygame.joystick.get_count() > 0:
            self.gamepad = pygame.joystick.Joystick(0)
            self.gamepad.init()
            print(f"Gamepad gefunden: {self.gamepad.get_name()}")
            print(f"  Achsen: {self.gamepad.get_numaxes()}, Buttons: {self.gamepad.get_numbuttons()}")
        else:
            print("Kein Gamepad gefunden - nur Tastatursteuerung aktiv")

        # Highscore-Manager initialisieren
        self.highscore_manager = HighscoreManager()

        # Rekord-Infos für aktuelles Rennen (wird nach Rennende gesetzt)
        self.current_race_record_info = None

        # Gecachte Overlay-Surfaces (Performance-Optimierung)
        self.game_over_overlay = None
        
        # Gecachte Fonts für Finish-Screen (Performance-Optimierung)
        self.race_finished_fonts = {
            'title': get_pixel_font(int(36 * RENDER_SCALE)),
            'text': get_pixel_font(int(20 * RENDER_SCALE)),
            'small': get_pixel_font(int(16 * RENDER_SCALE)),
            'tiny': get_pixel_font(int(14 * RENDER_SCALE))
        }

        # ------------- Ende der allgemeinen Initialisierung -------------



        # ------------- Menü anzeigen -----------------------

        # Zeige Startbildschirm und Streckenauswahl
        menu = Menu(self.screen, gamepad=self.gamepad)
        selected_race_index = menu.run()

        # Einzelrennen-Modus (über Menü ausgewählt)
        game_mode_choice = 2

        # ------------- Ende der Menü-Auswahl ----------------



        # ------------- Spiel initialisieren (abhängig vom Modus) -------

        if game_mode_choice == 1:
            self.init_league_race_mode()
        if game_mode_choice == 2:
            self.init_single_race_mode(race_choice=selected_race_index)


        # ------------- Ende der modusabhängigen Spielinitialisierung -------

        

    # Initialisierung für den Liga-Rennen-Modus:
    # Eine Liga besteht aus fünf aufeinanderfolgenden Rennen, die der Spieler absolvieren muss.
    def init_league_race_mode(self):
        # Sprite-Gruppen als leere Gruppen neu initialisieren (zum Aufräumen)
        self.initialize_sprite_groups()

        # Liga-Auswahl (todo)
        self.current_league = LEAGUES[0]

        # Den eigentlichen Rennmodus initialisieren
        self.init_race_mode(
            next_race = self.current_league.current_race()
        )

    # Initialisierung für den Einzelrennen-Modus
    def init_single_race_mode(self, race_choice=None):
        # Sprites aufräumen
        self.initialize_sprite_groups()

        # ------------- Streckenauswahl -------------

        if race_choice is None:
            race_choice = DEFAULT_SINGLE_RACE_CHOICE

        # ------------- Ende der Streckenauswahl -------------

        # Rennmodus initialisieren und Rennen laden.
        # Liga mit allen verfügbaren Rennen erstellen, aber beim ausgewählten Rennen starten
        self.current_league = League(SINGLE_MODE_RACES)
        self.current_league.current_race_index = race_choice
        self.init_race_mode(next_race = self.current_league.current_race())
        
    # Enthält allgemeine (Neu-)Initialisierungslogik für jeden Spielmodus,
    # in dem Rennen gefahren werden.
    # Dies umfasst das Erstellen der jeweiligen Gruppen für Sprites,
    # das Initialisieren einiger Status-Flags,
    # das Initialisieren der Renn-UI, ...
    #
    # Parameter:
    # next_race - Nächstes Rennen, das nach der (Neu-)Initialisierung gespielt werden soll
    def init_race_mode(self, next_race):
        # Spieler kann dieses Flag über einen Tastendruck auf True setzen, um anzuzeigen, dass das nächste Rennen geladen werden soll
        self.should_load_next_race = False
        # Trackt welcher Finish-Screen gerade angezeigt wird: "race_finished", "new_record", oder None
        self.finish_screen_state = None 

        # Deklariert den Mode-7-Renderer.
        # Wird später beim Laden des Rennens initialisiert.
        self.mode7 = None

        # Mini-Map (wird beim Laden des Rennens initialisiert)
        self.minimap_bg = None
        self.minimap_world_bounds = None

        # Nur für Debug: Spieler wählt eine Maschine
        # Außerhalb des Debug-Modus verwendet der Spieler Purple Comet
        if DEBUG_CHOOSE_MACHINE:
            print("0: Purple Comet")
            print("1: Schnelleres Purple Comet")
            print("2: Langsameres Purple Comet")
            choice = int(input("Wähle eine Maschine: "))
            player_machine = MACHINES[choice]
        else:
            player_machine = DEFAULT_MACHINE # Standardmaschine kann in settings.machine_settings geändert werden

        # Zeitstempel des zuletzt gerenderten Frames.
        # Wird benötigt, um unterschiedliche Framerate auf verschiedenen Maschinen auszugleichen.
        # Wenn physikbezogene Operationen wie Beschleunigen, Bremsen, Energie wiederherstellen, ...
        # nicht mit der Zeit zwischen diesem Frame und dem letzten Frame skaliert werden,
        # beschleunigen Spieler mit höherer Framerate schneller usw.,
        # weil mehr Frame-Updates in derselben Zeit berechnet werden.
        self.get_time()
        self.last_frame = self.time

        # Erstellt eine Spielerinstanz und
        # weist die Rennstrecke dem Spieler zu.
        # Der Spieler muss wissen, auf welcher Rennstrecke er fährt,
        # damit er prüfen kann, ob er mit seiner Bewegung im aktuellen Frame die Strecke verlassen würde
        # oder ein Strecken-Gimmick trifft.
        self.player = Player(
            machine = player_machine,
            current_race = next_race,
            gamepad = self.gamepad
        )

        # Spielerinstanz und Spieler-Schatten-Sprite zur Sprite-Gruppe hinzufügen, um es rendern zu können
        # Reihenfolge ist wichtig, da der Spieler "vor" dem Schatten sein muss
        self.static_sprites.add(self.player.shadow_sprite)
        self.moving_sprites.add(self.player)

        # Erstellt eine Kamera-Instanz,
        # die dem Spieler folgt.
        self.camera = Camera(
            self.player,
            CAM_DISTANCE
        )

        # Erstellt Sprites für den Geschwindigkeitsmesser der UI.
        self.speed_meter_sprites = [None, None, None, None]
        for i in range(0, 4):
            self.speed_meter_sprites[i] = pygame.sprite.Sprite() # Ziffern sind von rechts nach links nummeriert
            self.speed_meter_sprites[i].image = NUMBER_IMAGES[0] # Anfangs sind alle Ziffern 0
            self.speed_meter_sprites[i].rect = self.speed_meter_sprites[i].image.get_rect()
            self.speed_meter_sprites[i].rect.topleft = [
                RIGHT_MOST_SPEEDMETER_DIGIT_SCREEN_X_COORD - SPEED_METER_DIGIT_SPRITE_WIDTH * i, # Sprites einzeln basierend auf der x-Koordinate des linkesten verschieben. 24px ist Sprite-Breite
                SPEED_METER_DIGIT_SCREEN_Y_COORD
            ]

            # Zur Sprite-Gruppe für UI-Sprites hinzufügen (zum Rendern, erledigt in App-Klasse)
            self.ui_sprites.add(self.speed_meter_sprites[i])

        # Erstellt Sprites für den Timer der UI (analog zu denen für den Geschwindigkeitsmesser).
        self.timer_sprites = [None, None, None, None, None, None, None]
        for i in range(0, 7):
            self.timer_sprites[i] = pygame.sprite.Sprite()
            self.timer_sprites[i].image = NUMBER_IMAGES[0]
            self.timer_sprites[i].rect = self.timer_sprites[i].image.get_rect()
            self.timer_sprites[i].rect.topleft = [
                TIMER_DIGIT_X_OFFSET(i),
                TIMER_DIGIT_SCREEN_Y_COORD
            ]

            self.ui_sprites.add(self.timer_sprites[i])

        # Instanz der UI-Manager-Klasse erstellen
        self.ui = UI(
            player = self.player,
            speed_meter_sprites = self.speed_meter_sprites,
            timer_sprites = self.timer_sprites
        )

        # Status-Flag setzen
        self.in_racing_mode = True

        # Rundenzeit-Anzeige (zeigt die letzte Rundenzeit für einige Sekunden an)
        self.last_lap_time_display = None
        self.lap_time_display_timestamp = None
        self.LAP_TIME_DISPLAY_DURATION = 4.0  # Sekunden
        self.previous_lap_count = 0  # Um zu erkennen, wann eine neue Runde abgeschlossen wurde

        # Nächste Rennstrecke laden
        self.load_race(next_race)

    def update(self):
        # Berechnet die Zeit seit dem letzten Frame
        delta = self.time - self.last_frame

        # Zeitstempel des aktuellen Frame-Starts (!) für Delta-Berechnung im nächsten Frame
        self.last_frame = self.time
        
        # Für Dinge, die nur während eines Rennens erledigt werden müssen.
        if self.in_racing_mode:
            # Aktualisiert den Spieler basierend auf der seit Spielstart verstrichenen Zeit
            self.player.update(self.time, delta)

            # Aktualisiert die Kameraposition (wird hauptsächlich basierend auf der Spielerposition durchgeführt)
            self.camera.update()

            # Veranlasst die Mode7-gerenderte Umgebung zur Aktualisierung
            self.mode7.update(self.camera)

            # --- PARTIKEL UPDATE ---
            self.particles.update()
            
            # Partikel-Limit für Performance (maximal 100 gleichzeitig)
            MAX_PARTICLES = 100
            if len(self.particles) > MAX_PARTICLES:
                # Älteste Partikel entfernen (niedrigste lifetime)
                particles_list = list(self.particles)
                particles_list.sort(key=lambda p: p.lifetime)
                for p in particles_list[:len(particles_list) - MAX_PARTICLES]:
                    p.kill()

            # Prüfen auf Landung für Funken-Effekt
            if self.player.just_landed:
                self.player.just_landed = False
                
                # Funkenregen erzeugen
                # Position: Unten am Raumschiff (beim Schatten)
                spawn_x = self.player.rect.centerx
                spawn_y = self.player.rect.bottom - 5
                
                for _ in range(20):
                    spark = SparkParticle(spawn_x, spawn_y)
                    self.particles.add(spark)

            # Timer in der UI aktualisieren, wenn der Spieler das aktuelle Rennen noch nicht beendet hat
            # und nicht zerstört wurde (Game Over).
            # Timer startet erst, wenn das Rennen begonnen hat (erste Ziellinie überquert).
            if not self.player.finished and not self.player.destroyed:
                current_race = self.current_league.current_race()
                if current_race.race_started:
                    seconds_since_race_start = self.time - current_race.race_start_timestamp
                    self.ui.update(
                        elapsed_milliseconds = seconds_since_race_start * 1000
                    )
                else:
                    # Timer bleibt auf 0, bis das Rennen startet
                    self.ui.update(elapsed_milliseconds = 0)

            # Prüft, ob eine neue Runde abgeschlossen wurde
            current_race = self.current_league.current_race()
            current_lap_count = current_race.player_completed_laps
            if current_lap_count > self.previous_lap_count and len(current_race.lap_times) > 0:
                # Neue Runde abgeschlossen! Zeige die Rundenzeit an
                self.last_lap_time_display = current_race.lap_times[-1]  # Letzte Rundenzeit
                self.lap_time_display_timestamp = self.time
                self.previous_lap_count = current_lap_count

            # Prüft, ob der Spieler das Rennen beendet hat.
            # Wenn ja, wird ein Status-Flag in der Spielerinstanz gesetzt, falls noch nicht geschehen.
            if self.current_league.current_race().player_finished_race() and not self.player.finished:
                self.player.finished = True
                self.finish_screen_state = "race_finished"  # Zeige zuerst den Race Finished Screen

                # Musik ausfaden und race-end Sound abspielen
                mixer.music.fadeout(1500)  # Fade out über 1.5 Sekunden
                pygame.time.set_timer(pygame.USEREVENT + 1, 1500)  # Timer für race-end Sound nach Fade

                # Füge die Gesamtzeit des abgeschlossenen Rennens zur Liga-Gesamtzeit hinzu
                race_total_time = sum(self.current_league.current_race().lap_times)
                self.current_league.add_race_time(race_total_time)

                # Highscores aktualisieren
                current_race = self.current_league.current_race()
                self.current_race_record_info = self.highscore_manager.update_highscores(
                    track_name=current_race.race_track.name,
                    lap_times=current_race.lap_times
                )

            # Nächstes Rennen laden, wenn der Spieler das aktuelle beendet hat und die Bestätigungstaste gedrückt hat (was das Flag setzt)
            if self.should_load_next_race:
                self.player.finished = False
                # Prüfen, ob es noch ein nächstes Rennen gibt
                if self.current_league.current_race_index + 1 < self.current_league.length():
                    # Nächstes Rennen laden
                    self.load_race(self.current_league.next_race())
                else:
                    # Liga ist beendet - zurück zum ersten Rennen
                    print(f"Liga abgeschlossen! Finale Gesamtzeit: {self.current_league.total_time_ms:.0f}ms")
                    self.current_league.reset()
                    self.load_race(self.current_league.current_race())

            # Prüft, ob der Spieler mindestens eine Runde absolviert hat
            # und aktiviert seine Boost-Kraft, falls ja (und noch nicht aktiviert).
            if self.current_league.current_race().player_completed_first_lap() and not self.player.has_boost_power:
                self.player.has_boost_power = True

        # Uhr aktualisieren.
        # Das übergebene Framerate-Argument verlangsamt die Zeit im Spiel künstlich,
        # sodass das Spiel nie mit einer höheren Framerate als der übergebenen läuft.
        self.clock.tick(TARGET_FPS)

        # Beschriftung des Fensters zeigt aktuelle Framerate an
        # (f'...' ist eine lesbarere + schnellere Art, Formatstrings zu schreiben als mit "%")
        pygame.display.set_caption(f'{self.clock.get_fps():.1f}')

        # Log-Ausgabe für Debug
        if SHOULD_DEBUG_LOG:
            self.debug_logs()

    # (Neu-)Lädt das übergebene Rennen.
    def load_race(self, race):
        # Alle Fortschrittsdaten für dieses Rennen zurücksetzen
        race.reset_data()

        # Spieler das neue Rennen zuweisen
        self.player.current_race = race
        
        # Spieler auf Startposition der (neuen) Rennstrecke zurücksetzen
        self.player.reinitialize()

        # Renderer-Feld durch Mode-7-Renderer für die neue Rennstrecke ersetzen.
        # Dritter Parameter bestimmt, ob der Renderer einen Nebeleffekt anwendet oder nicht.
        self.mode7 = Mode7(
            app = self,
            floor_tex_path = race.floor_texture_path,
            bg_tex_path = race.bg_texture_path,
            is_foggy = race.is_foggy
        )

        # Mini-Map für dieses Rennen vorbereiten (einmalig)
        self.init_minimap(race)

        # Musik neu starten
        mixer.music.load(race.music_track_path)
        mixer.music.set_volume(MUSIC_VOLUME * 0.4)  # 40% Lautstärke im Rennen
        mixer.music.play()

        # Rundenzeit-Anzeige zurücksetzen
        self.last_lap_time_display = None
        self.lap_time_display_timestamp = None
        self.previous_lap_count = 0

        # Rekord-Infos zurücksetzen
        self.current_race_record_info = None

        # Flag zurücksetzen
        self.should_load_next_race = False

    # (Neu-)Initialisiert alle Sprite-Gruppen als leere Gruppen.
    # Kann zum Aufräumen beim Wechseln zwischen Spielmodi verwendet werden.
    def initialize_sprite_groups(self):
        self.moving_sprites = pygame.sprite.Group()
        self.static_sprites = pygame.sprite.Group()
        self.ui_sprites = pygame.sprite.Group()
        self.particles = pygame.sprite.Group()

    # ---------------- Mini-Map ----------------

    def _compute_track_world_bounds(self, track):
        """Berechnet die Welt-Bounding-Box der Strecke (x/y), basierend auf allen relevanten CollisionRects."""
        min_x = float("inf")
        max_x = float("-inf")
        min_y = float("inf")
        max_y = float("-inf")

        def consume_rect(rect):
            nonlocal min_x, max_x, min_y, max_y
            x = float(rect.position[0])
            y = float(rect.position[1])
            half_w = float(rect.width) / 2.0
            half_h = float(rect.height) / 2.0

            min_x = min(min_x, x - half_w)
            max_x = max(max_x, x + half_w)
            min_y = min(min_y, y - half_h)
            max_y = max(max_y, y + half_h)

        # Track-Oberfläche ist Pflicht
        for r in track.track_surface_rects:
            consume_rect(r)

        # Optional: weitere Elemente einbeziehen, damit Marker-Bounds nicht "abschneiden"
        for r in track.ramp_rects:
            consume_rect(r)
        for r in track.dash_plate_rects:
            consume_rect(r)
        for r in track.recovery_zone_rects:
            consume_rect(r)
        for r in track.dirt_rects:
            consume_rect(r)

        # Ziellinie / Checkpoints
        consume_rect(track.finish_line_collider)
        for kc in track.key_checkpoints:
            consume_rect(kc.collider)

        # Fallback, falls irgendwas schief lief
        if min_x == float("inf"):
            return (0.0, 1.0, 0.0, 1.0)

        # Optionales Padding
        pad = float(MINIMAP_WORLD_PADDING)
        return (min_x - pad, max_x + pad, min_y - pad, max_y + pad)

    def _load_minimap_image(self, race):
        """Lädt optional ein Minimap-Bild gemäß Konvention. Gibt Surface oder None zurück."""
        base = os.path.splitext(os.path.basename(race.floor_texture_path))[0]
        candidates = [
            os.path.join(MINIMAP_IMAGE_DIR, f"{base}{MINIMAP_IMAGE_SUFFIX}.png"),
            os.path.join(MINIMAP_IMAGE_DIR, f"{base}.png"),
        ]

        for path in candidates:
            if not os.path.isfile(path):
                continue

            img = pygame.image.load(path).convert_alpha()

            if MINIMAP_SCALE_WITH_RENDER_SCALE and RENDER_SCALE != 1.0:
                new_w = int(img.get_width() * RENDER_SCALE)
                new_h = int(img.get_height() * RENDER_SCALE)
                if new_w > 0 and new_h > 0:
                    img = pygame.transform.scale(img, (new_w, new_h))
            return img

        return None

    def _blit_rect_with_alpha(self, surface, rect, color, alpha):
        """Blittet ein halbtransparentes Rechteck ohne per-frame Allokationen (nur beim Init genutzt)."""
        w = max(1, int(rect.width))
        h = max(1, int(rect.height))
        tmp = pygame.Surface((w, h), pygame.SRCALPHA)
        tmp.fill((color[0], color[1], color[2], int(alpha)))
        surface.blit(tmp, (int(rect.left), int(rect.top)))

    def _render_fallback_minimap(self, track, bounds, size):
        """Rendert eine einfache Minimap aus den Kollisions-Rechtecken (einmalig beim Laden)."""
        w, h = int(size[0]), int(size[1])
        w = max(1, w)
        h = max(1, h)

        bg = pygame.Surface((w, h), pygame.SRCALPHA)
        bg.fill((MINIMAP_BG_COLOR[0], MINIMAP_BG_COLOR[1], MINIMAP_BG_COLOR[2], int(MINIMAP_BG_ALPHA)))

        x_min, x_max, y_min, y_max = bounds
        span_x = (x_max - x_min) if (x_max - x_min) != 0 else 1.0
        span_y = (y_max - y_min) if (y_max - y_min) != 0 else 1.0

        def world_rect_to_minimap_rect(rect):
            # Minimap-x entspricht Welt-y, Minimap-y entspricht Welt-x (siehe Map-Editor / Mode7-Mapping)
            left_y = float(rect.position[1]) - float(rect.height) / 2.0
            right_y = float(rect.position[1]) + float(rect.height) / 2.0
            top_x = float(rect.position[0]) - float(rect.width) / 2.0
            bottom_x = float(rect.position[0]) + float(rect.width) / 2.0

            u0 = (left_y - y_min) / span_y
            u1 = (right_y - y_min) / span_y
            v0 = (top_x - x_min) / span_x
            v1 = (bottom_x - x_min) / span_x

            px0 = int(u0 * (w - 1))
            px1 = int(u1 * (w - 1))
            py0 = int(v0 * (h - 1))
            py1 = int(v1 * (h - 1))

            left = min(px0, px1)
            top = min(py0, py1)
            width = max(1, abs(px1 - px0))
            height = max(1, abs(py1 - py0))
            return pygame.Rect(left, top, width, height)

        # Trackfläche
        for r in track.track_surface_rects:
            self._blit_rect_with_alpha(bg, world_rect_to_minimap_rect(r), MINIMAP_TRACK_COLOR, MINIMAP_TRACK_ALPHA)

        # Ziellinie hervorheben
        self._blit_rect_with_alpha(bg, world_rect_to_minimap_rect(track.finish_line_collider), MINIMAP_FINISH_COLOR, MINIMAP_FINISH_ALPHA)

        return bg

    def _get_centerline_marker_world_pos(self, track, px_world, py_world):
        """Projiziert die Position auf die Mittellinie des aktuellen Strecken-Segments (Track-Rect)."""
        rects = track.track_surface_rects
        if not rects:
            return px_world, py_world

        # 1) Bevorzugt: Rechteck, in dem der Punkt liegt (falls mehrere: kleinstes Flächenmaß -> meist das "Segment")
        best_rect = None
        best_area = None

        for r in rects:
            cx = float(r.position[0])
            cy = float(r.position[1])
            half_w = float(r.width) / 2.0
            half_h = float(r.height) / 2.0

            if abs(px_world - cx) <= half_w and abs(py_world - cy) <= half_h:
                area = float(r.width) * float(r.height)
                if best_rect is None or area < best_area:
                    best_rect = r
                    best_area = area

        # 2) Fallback: nächstes Segment per Distanz zum Mittelpunkt
        if best_rect is None:
            best_dist2 = None
            for r in rects:
                cx = float(r.position[0])
                cy = float(r.position[1])
                dx = px_world - cx
                dy = py_world - cy
                dist2 = dx * dx + dy * dy
                if best_rect is None or dist2 < best_dist2:
                    best_rect = r
                    best_dist2 = dist2

        cx = float(best_rect.position[0])
        cy = float(best_rect.position[1])
        half_w = float(best_rect.width) / 2.0
        half_h = float(best_rect.height) / 2.0

        # "Länge" = längere Kante; "Breite" = kürzere Kante -> diese klemmen wir auf die Mitte.
        if float(best_rect.width) >= float(best_rect.height):
            # Horizontaler Abschnitt: x frei, y auf Mitte
            x = min(max(px_world, cx - half_w), cx + half_w)
            y = cy
        else:
            # Vertikaler Abschnitt: y frei, x auf Mitte
            x = cx
            y = min(max(py_world, cy - half_h), cy + half_h)

        return x, y

    def init_minimap(self, race):
        """Initialisiert die Mini-Map für das übergebene Rennen (einmalig pro Track)."""
        if not MINIMAP_ENABLED:
            self.minimap_bg = None
            self.minimap_world_bounds = None
            return

        track = race.race_track
        bounds = self._compute_track_world_bounds(track)
        self.minimap_world_bounds = bounds

        # Wenn es ein schönes Minimap-Bild gibt: verwenden. Sonst Fallback rendern.
        img = self._load_minimap_image(race)
        if img is not None:
            self.minimap_bg = img
        else:
            self.minimap_bg = self._render_fallback_minimap(track, bounds, MINIMAP_FALLBACK_SIZE)

        # Zusätzliche Anzeige-Skalierung (z.B. 0.9 = 10% kleiner)
        if self.minimap_bg is not None and MINIMAP_DISPLAY_SCALE != 1.0:
            new_w = max(1, int(round(self.minimap_bg.get_width() * float(MINIMAP_DISPLAY_SCALE))))
            new_h = max(1, int(round(self.minimap_bg.get_height() * float(MINIMAP_DISPLAY_SCALE))))
            if new_w != self.minimap_bg.get_width() or new_h != self.minimap_bg.get_height():
                # Nearest-Neighbor für Retro-Look
                self.minimap_bg = pygame.transform.scale(self.minimap_bg, (new_w, new_h))

    def draw_minimap(self):
        """Zeichnet die Mini-Map unten links + Spieler-Marker."""
        if not MINIMAP_ENABLED:
            return
        if not self.in_racing_mode:
            return
        if self.minimap_bg is None or self.minimap_world_bounds is None:
            return

        bg = self.minimap_bg
        bg_w, bg_h = bg.get_width(), bg.get_height()

        # Screen-Position unten links
        x0 = int(MINIMAP_MARGIN_LEFT)
        y0 = int(HEIGHT - MINIMAP_MARGIN_BOTTOM - bg_h)

        # Background
        self.screen.blit(bg, (x0, y0))

        # Spieler-Marker
        x_min, x_max, y_min, y_max = self.minimap_world_bounds
        span_x = (x_max - x_min) if (x_max - x_min) != 0 else 1.0
        span_y = (y_max - y_min) if (y_max - y_min) != 0 else 1.0

        px_world = float(self.player.position[0])
        py_world = float(self.player.position[1])

        if MINIMAP_MARKER_CLAMP_TO_TRACK_CENTER:
            track = self.player.current_race.race_track
            px_world, py_world = self._get_centerline_marker_world_pos(track, px_world, py_world)

        # Minimap-x entspricht Welt-y, Minimap-y entspricht Welt-x
        u = (py_world - y_min) / span_y
        v = (px_world - x_min) / span_x

        # Clampen, falls Spieler kurz außerhalb ist
        if u < 0.0: u = 0.0
        if u > 1.0: u = 1.0
        if v < 0.0: v = 0.0
        if v > 1.0: v = 1.0

        mx = x0 + int(u * (bg_w - 1))
        my = y0 + int(v * (bg_h - 1))

        radius = max(2, int(MINIMAP_PLAYER_RADIUS * MINIMAP_MARKER_SCALE))

        # Optional: Richtungs-Strich (Blickrichtung)
        if MINIMAP_SHOW_HEADING:
            # Heading: (sin, cos) passt zur Welt->Minimap-Achsenbelegung
            hx = math.sin(self.player.angle)
            hy = math.cos(self.player.angle)
            heading_len = max(4, int(MINIMAP_HEADING_LENGTH * MINIMAP_MARKER_SCALE))

            ex = mx + int(hx * heading_len)
            ey = my + int(hy * heading_len)

            pygame.draw.line(self.screen, MINIMAP_PLAYER_OUTLINE_COLOR, (mx, my), (ex, ey), 2)
            pygame.draw.line(self.screen, MINIMAP_PLAYER_COLOR, (mx, my), (ex, ey), 1)

        pygame.draw.circle(self.screen, MINIMAP_PLAYER_OUTLINE_COLOR, (mx, my), radius + 1)
        pygame.draw.circle(self.screen, MINIMAP_PLAYER_COLOR, (mx, my), radius)

    def draw(self):
        # Zeichnet die Mode-7-Umgebung
        self.mode7.draw()

        # Zeichnet statische Sprites (z.B. Spieler-Schatten) auf den Bildschirm
        self.static_sprites.draw(self.screen)

        # Zeichnet bewegliche Sprites (z.B. Spieler) auf den Bildschirm
        self.moving_sprites.draw(self.screen)

        # Zeichnet Partikel
        self.particles.draw(self.screen)

        # Zeichnet UI-Sprites auf den Bildschirm
        self.ui_sprites.draw(self.screen)

        # Mini-Map (unten links)
        if self.in_racing_mode:
            self.draw_minimap()

        # Zeichnet Rundenzeit-Benachrichtigung (falls aktiv)
        if self.in_racing_mode:
            self.draw_lap_time_notification()

        # Zeichnet Debug-Objekte wie Energieleiste
        if self.in_racing_mode:
            self.draw_racing_mode_debug_objects()

        # Game Over Overlay zeichnen wenn Spieler zerstört wurde
        if self.in_racing_mode and self.player.destroyed:
            self.draw_game_over_overlay()

        # Finish Screen Overlay zeichnen wenn Spieler das Rennen beendet hat
        if self.in_racing_mode and self.player.finished:
            if self.finish_screen_state == "race_finished":
                self.draw_race_finished_overlay()
            elif self.finish_screen_state == "new_record":
                self.draw_new_record_screen()

        # Inhalt der gesamten Anzeige aktualisieren
        pygame.display.flip()

    def get_time(self):
        self.time = time.time()

    def check_event(self):
        for event in pygame.event.get():
            # Prozess beenden, der das Spiel ausführt,
            # wenn etwas das Beenden-Ereignis verursacht
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Race-End Sound abspielen nach Musik-Fade
            if event.type == pygame.USEREVENT + 1:
                mixer.music.load(BGM_DICT["race-end"])
                mixer.music.play()
                pygame.time.set_timer(pygame.USEREVENT + 1, 0)  # Timer deaktivieren

            # Prüft auf Tastendrücke in Menübildschirmen
            if event.type == pygame.KEYDOWN:
                # ESC: Pause-Menü während des Rennens
                if event.key == pygame.K_ESCAPE and self.in_racing_mode and not self.player.finished and not self.player.destroyed:
                    self.show_pause_menu()

                if event.key == STD_CONFIRM_KEY and self.player.finished:
                    # Wenn auf dem race_finished Screen: prüfen ob neuer Rekord
                    if self.finish_screen_state == "race_finished":
                        # Prüfe ob ein neuer Rekord aufgestellt wurde
                        has_new_record = False
                        if self.current_race_record_info:
                            has_new_record = (self.current_race_record_info.get("new_best_lap", False) or
                                            self.current_race_record_info.get("new_best_total", False))

                        if has_new_record:
                            # Wechsel zum New Record Screen
                            self.finish_screen_state = "new_record"
                        else:
                            # Kein neuer Rekord: direkt zum nächsten Rennen
                            self.should_load_next_race = True
                            self.finish_screen_state = None
                    # Wenn auf dem new_record Screen: zum nächsten Rennen
                    elif self.finish_screen_state == "new_record":
                        self.should_load_next_race = True
                        self.finish_screen_state = None
                # Game Over: Leertaste zum Neustarten
                if event.key == STD_CONFIRM_KEY and self.player.destroyed:
                    self.load_race(self.current_league.current_race())
                if event.key == STD_DEBUG_RESTART_KEY and DEBUG_RESTART_RACE_ON_R:
                    self.load_race(self.current_league.current_race())

            # Gamepad-Button-Events (nur sichere Buttons 0-3 und 8-9)
            if event.type == pygame.JOYBUTTONDOWN and self.gamepad:
                from settings.gamepad_settings import GAMEPAD_CONFIRM_BUTTON, GAMEPAD_PAUSE_BUTTON
                # Ignoriere Trigger-Buttons (4-7)
                if event.button >= 4 and event.button <= 7:
                    continue
                # Start-Button: Pause-Menü öffnen
                if event.button == GAMEPAD_PAUSE_BUTTON and self.in_racing_mode and not self.player.finished and not self.player.destroyed:
                    self.show_pause_menu()
                # Confirm-Button bei Finish
                if event.button == GAMEPAD_CONFIRM_BUTTON and self.player.finished:
                    if self.finish_screen_state == "race_finished":
                        has_new_record = False
                        if self.current_race_record_info:
                            has_new_record = (self.current_race_record_info.get("new_best_lap", False) or
                                            self.current_race_record_info.get("new_best_total", False))
                        if has_new_record:
                            self.finish_screen_state = "new_record"
                        else:
                            self.should_load_next_race = True
                            self.finish_screen_state = None
                    elif self.finish_screen_state == "new_record":
                        self.should_load_next_race = True
                        self.finish_screen_state = None
                # Confirm-Button bei Game Over
                if event.button == GAMEPAD_CONFIRM_BUTTON and self.player.destroyed:
                    self.load_race(self.current_league.current_race())

    # Hauptspielschleife, läuft bis zur Beendigung des Prozesses.
    def run(self):
        while True:
            # Ereignisse behandeln
            self.check_event()

            # Feld aktualisieren, das die Millisekunden seit Spielstart zählt
            self.get_time()

            # Spielzustand aktualisieren
            self.update()

            # Frame rendern
            self.draw()

    # Protokolliert verschiedene Spielzustandsinformationen in der Konsole, wenn Taste P gedrückt wird.
    def debug_logs(self):
        keys = pygame.key.get_pressed()

        # Protokoll der Spielerposition für Debug-Zwecke
        if keys[pygame.K_p]:
            print("Spielerposition/Winkel: " + str(self.player.position[0]) + " " + str(self.player.position[1]) + ", " + str(self.player.angle))

        # Protokoll der Kameraposition für Debug-Zwecke
        # if keys[pygame.K_p]:
        #     print("Kameraposition/Winkel: " + str(self.camera.position[0]) + " " + str(self.camera.position[1]) + ", " + str(self.camera.angle))

        # Protokoll, ob Spieler auf der Strecke ist
        # if keys[pygame.K_p]:
        #     if self.race_track.is_on_track( CollisionRect(self.player.position, PLAYER_COLLISION_RECT_WIDTH, PLAYER_COLLISION_RECT_HEIGHT) ):
        #         print("Spieler auf Strecke!")

        # Protokoll der Spielergeschwindigkeit
        # if keys[pygame.K_p]:
        #     print("Spielergeschwindigkeit:" + str(self.player.current_speed))

    def draw_racing_mode_debug_objects(self):
        # Debug-Modus-Energieleiste auf den Bildschirm zeichnen
        pygame.draw.rect(
            self.screen,
            pygame.Color(160, 0, 0),
            pygame.Rect(
                ENERGY_METER_LEFT_X, # X-Position (links)
                ENERGY_METER_TOP_Y, # Y-Position (oben)
                (RIGHT_MOST_TIMER_DIGIT_SCREEN_X_COORD - ENERGY_METER_LEFT_X) * (self.player.current_energy / self.player.machine.max_energy), # Breite (dynamisch)
                ENERGY_METER_HEIGHT # Höhe (konstant)
            )
        )

    # Zeichnet das Game Over Overlay wenn der Spieler zerstört wurde (SNES-Style)
    def draw_game_over_overlay(self):
        # Halbtransparentes dunkles Overlay (gecacht für Performance)
        if self.game_over_overlay is None:
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.fill((0, 0, 0))
            overlay.set_alpha(GAME_OVER_OVERLAY_ALPHA)
            self.game_over_overlay = overlay
        self.screen.blit(self.game_over_overlay, (0, 0))

        # "GAME OVER" Sprite zentriert
        game_over_rect = GAME_OVER_IMAGE.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 20))
        self.screen.blit(GAME_OVER_IMAGE, game_over_rect)

        # "PRESS SPACE" Sprite zentriert darunter
        press_space_rect = PRESS_SPACE_IMAGE.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 30))
        self.screen.blit(PRESS_SPACE_IMAGE, press_space_rect)

    # Zeichnet das Finish Screen Overlay wenn der Spieler das Rennen beendet hat
    def draw_race_finished_overlay(self):
        # Fonts (gecacht für Performance)
        title_font = self.race_finished_fonts['title']
        text_font = self.race_finished_fonts['text']
        small_font = self.race_finished_fonts['small']
        tiny_font = self.race_finished_fonts['tiny']

        # "RACE FINISHED!" Grafik
        title_rect = RACE_FINISHED_IMAGE.get_rect(center=(WIDTH // 2, int(HEIGHT * 0.3)))
        self.screen.blit(RACE_FINISHED_IMAGE, title_rect)

        # Gesamtzeit
        current_race = self.current_league.current_race()
        y_offset = int(HEIGHT * 0.42)

        total_time = sum(current_race.lap_times)
        total_text = text_font.render(
            f"TOTAL: {self.format_time(total_time)}",
            True, (100, 255, 100)
        )
        total_rect = total_text.get_rect(center=(WIDTH // 2, y_offset))
        self.screen.blit(total_text, total_rect)

        # Best Lap anzeigen (falls vorhanden)
        if self.current_race_record_info:
            y_offset += 30 * RENDER_SCALE
            best_lap = self.current_race_record_info["best_lap"]

            if best_lap:
                best_lap_text = small_font.render(
                    f"Best Lap: {self.format_time(best_lap)}",
                    True, (255, 255, 100)
                )
                best_lap_rect = best_lap_text.get_rect(center=(WIDTH // 2, y_offset))
                self.screen.blit(best_lap_text, best_lap_rect)

        # Optionen
        y_offset = HEIGHT - int(HEIGHT * 0.15)
        option1 = tiny_font.render("SPACE: Next Race", True, (200, 200, 200))
        option1_rect = option1.get_rect(center=(WIDTH // 2, y_offset))
        self.screen.blit(option1, option1_rect)

        option2 = tiny_font.render("R: Restart", True, (200, 200, 200))
        option2_rect = option2.get_rect(center=(WIDTH // 2, y_offset + 18 * RENDER_SCALE))
        self.screen.blit(option2, option2_rect)

    # Zeichnet den New Record Screen (im Menü-Stil)
    def draw_new_record_screen(self):
        """Zeigt den New Record Screen im Retro-Menü-Stil an"""
        # Menü-Farben (wie im Hauptmenü)
        COLOR_BG_TOP = (10, 5, 30)
        COLOR_BG_BOTTOM = (0, 0, 0)
        COLOR_TITLE = (255, 220, 0)  # Gold
        COLOR_TEXT = (180, 200, 255)  # Helles Blau-Weiß
        COLOR_ACCENT = (0, 255, 255)  # Cyan
        COLOR_BORDER = (100, 100, 150)
        COLOR_RECORD = (255, 50, 200)  # Magenta für neue Rekorde

        # Gradienten-Hintergrund zeichnen
        for y in range(HEIGHT):
            ratio = y / HEIGHT
            r = int(COLOR_BG_TOP[0] * (1 - ratio) + COLOR_BG_BOTTOM[0] * ratio)
            g = int(COLOR_BG_TOP[1] * (1 - ratio) + COLOR_BG_BOTTOM[1] * ratio)
            b = int(COLOR_BG_TOP[2] * (1 - ratio) + COLOR_BG_BOTTOM[2] * ratio)
            pygame.draw.line(self.screen, (r, g, b), (0, y), (WIDTH, y))

        # Fonts
        font_title = pygame.font.Font(None, 80)
        font_text = pygame.font.Font(None, 40)
        font_small = pygame.font.Font(None, 28)

        # "NEW RECORD!" Titel mit Glow
        title_text = "NEW RECORD!"
        for offset in [6, 4, 2]:
            glow = font_title.render(title_text, True, COLOR_TITLE)
            glow.set_alpha(80)
            self.screen.blit(glow, (WIDTH // 2 - glow.get_width() // 2 + offset, 50 + offset))

        title = font_title.render(title_text, True, COLOR_TITLE)
        self.screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 50))

        # Rekord-Informationen
        y_offset = 150

        if self.current_race_record_info:
            new_best_lap = self.current_race_record_info.get("new_best_lap", False)
            new_best_total = self.current_race_record_info.get("new_best_total", False)
            best_lap = self.current_race_record_info.get("best_lap")
            best_total = self.current_race_record_info.get("best_total")

            # Rahmen um die Rekorde
            records_to_show = []
            if new_best_lap:
                records_to_show.append(("BEST LAP", best_lap))
            if new_best_total:
                records_to_show.append(("BEST TOTAL", best_total))

            if records_to_show:
                # Rahmen zeichnen
                frame_height = len(records_to_show) * 60 + 40
                frame_rect = pygame.Rect(WIDTH // 2 - 220, y_offset - 20, 440, frame_height)
                pygame.draw.rect(self.screen, COLOR_BORDER, frame_rect, 3)

                # Rekorde anzeigen
                for i, (label, time_val) in enumerate(records_to_show):
                    record_y = y_offset + i * 60

                    # Label in Cyan
                    label_text = font_text.render(label, True, COLOR_ACCENT)
                    label_rect = label_text.get_rect(center=(WIDTH // 2, record_y))
                    self.screen.blit(label_text, label_rect)

                    # Zeit in Magenta
                    time_text = font_text.render(self.format_time(time_val), True, COLOR_RECORD)
                    time_rect = time_text.get_rect(center=(WIDTH // 2, record_y + 30))
                    self.screen.blit(time_text, time_rect)

        # "PRESS SPACE TO CONTINUE" am unteren Rand
        continue_text = font_small.render("PRESS SPACE TO CONTINUE", True, COLOR_TEXT)
        continue_rect = continue_text.get_rect(center=(WIDTH // 2, HEIGHT - 40))
        self.screen.blit(continue_text, continue_rect)

        # Scanlines für Retro-Effekt
        for y in range(0, HEIGHT, 4):
            pygame.draw.line(self.screen, (0, 0, 0, 30), (0, y), (WIDTH, y), 1)

    # Hilfsfunktion zum Formatieren von Zeit in Millisekunden zu MM:SS.mmm
    def format_time(self, time_ms):
        """Formatiert Millisekunden zu MM:SS.mmm"""
        total_seconds = int(time_ms // 1000)
        milliseconds = int(time_ms % 1000)
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        return f"{minutes:02d}:{seconds:02d}.{milliseconds:03d}"

    # Zeichnet die Rundenzeit-Anzeige nach Abschluss einer Runde
    def draw_lap_time_notification(self):
        """Zeigt die Rundenzeit für einige Sekunden nach Abschluss einer Runde an"""
        # Nicht anzeigen, wenn das Rennen beendet ist
        if self.player.finished:
            return

        if self.last_lap_time_display is None or self.lap_time_display_timestamp is None:
            return

        # Prüfen, ob die Anzeigedauer abgelaufen ist
        elapsed = self.time - self.lap_time_display_timestamp
        if elapsed > self.LAP_TIME_DISPLAY_DURATION:
            self.last_lap_time_display = None
            self.lap_time_display_timestamp = None
            return

        # Fade-out-Effekt in den letzten 1.5 Sekunden
        alpha = 255
        if elapsed > self.LAP_TIME_DISPLAY_DURATION - 1.5:
            fade_progress = (self.LAP_TIME_DISPLAY_DURATION - elapsed) / 1.5
            alpha = int(255 * fade_progress)

        # Text-Rendering (OHNE Hintergrund)
        y_position = int(HEIGHT * 0.12)

        title_font = get_pixel_font(int(20 * RENDER_SCALE))
        time_font = get_pixel_font(int(32 * RENDER_SCALE))

        # "LAP TIME" Text
        lap_text = title_font.render("LAP TIME", True, (200, 200, 255))
        lap_text.set_alpha(alpha)
        lap_rect = lap_text.get_rect(center=(WIDTH // 2, y_position))
        self.screen.blit(lap_text, lap_rect)

        # Zeit
        time_text = time_font.render(self.format_time(self.last_lap_time_display), True, (100, 255, 100))
        time_text.set_alpha(alpha)
        time_rect = time_text.get_rect(center=(WIDTH // 2, y_position + 30 * RENDER_SCALE))
        self.screen.blit(time_text, time_rect)

    def _wait_for_button_release(self, button_id):
        """Wartet bis ein Gamepad-Button losgelassen wird"""
        if not self.gamepad:
            return
        # Kurz warten und Events leeren
        pygame.time.wait(50)
        pygame.event.clear()
        # Warten bis Button losgelassen (max 500ms)
        start = time.time()
        while time.time() - start < 0.5:
            pygame.event.pump()
            try:
                if not self.gamepad.get_button(button_id):
                    break
            except:
                break
            pygame.time.wait(10)
        pygame.event.clear()

    def show_pause_menu(self):
        """Zeigt das Pause-Menü und behandelt die Menü-Navigation"""
        from settings.gamepad_settings import GAMEPAD_CONFIRM_BUTTON, GAMEPAD_PAUSE_BUTTON, GAMEPAD_DEADZONE

        paused = True
        selected_option = 0
        menu_options = ["CONTINUE", "RESTART", "QUIT"]

        # Fonts (20% kleiner)
        title_font = get_pixel_font(int(38 * RENDER_SCALE))
        menu_font = get_pixel_font(int(19 * RENDER_SCALE))

        # Farben (wie im Hauptmenü)
        COLOR_SELECTED = (255, 50, 200)  # Magenta
        COLOR_TEXT = (180, 200, 255)     # Helles Blau-Weiß
        COLOR_BG = (20, 10, 40)          # Dunkelblau-Violett
        COLOR_BORDER = (100, 100, 150)   # Grau-Blau

        # Sound laden (falls vorhanden)
        try:
            beep_sound = mixer.Sound("sounds/beep-menu.mp3")
            beep_sound.set_volume(0.6)
            confirm_sound = mixer.Sound("sounds/beep-auswahl.mp3")
            confirm_sound.set_volume(1.2)
        except:
            beep_sound = None
            confirm_sound = None

        clock = pygame.time.Clock()
        gamepad_cooldown = 0.3  # Initialer Cooldown um "klebende" Buttons zu ignorieren
        GAMEPAD_COOLDOWN_TIME = 0.25
        last_time = time.time()

        while paused:
            # Delta für Cooldown
            current_time = time.time()
            delta = current_time - last_time
            last_time = current_time
            if gamepad_cooldown > 0:
                gamepad_cooldown -= delta

            # Events behandeln
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        selected_option = (selected_option - 1) % len(menu_options)
                        if beep_sound:
                            beep_sound.play()
                    elif event.key == pygame.K_DOWN:
                        selected_option = (selected_option + 1) % len(menu_options)
                        if beep_sound:
                            beep_sound.play()
                    elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        if confirm_sound:
                            confirm_sound.play()

                        if selected_option == 0:  # Continue
                            paused = False
                        elif selected_option == 1:  # Restart
                            self.load_race(self.current_league.current_race())
                            paused = False
                        elif selected_option == 2:  # Quit
                            pygame.quit()
                            sys.exit()
                    elif event.key == pygame.K_ESCAPE:
                        # ESC schließt das Pause-Menü
                        paused = False

                # Gamepad-Button Events (in der gleichen Schleife!)
                if event.type == pygame.JOYBUTTONDOWN and gamepad_cooldown <= 0:
                    # Nur sichere Buttons (0-3 für Face, 8-9 für Select/Start)
                    if event.button <= 3 or event.button >= 8:
                        if event.button == GAMEPAD_CONFIRM_BUTTON:
                            if confirm_sound:
                                confirm_sound.play()
                            gamepad_cooldown = GAMEPAD_COOLDOWN_TIME
                            if selected_option == 0:  # Continue
                                paused = False
                                self._wait_for_button_release(GAMEPAD_CONFIRM_BUTTON)
                            elif selected_option == 1:  # Restart
                                self.load_race(self.current_league.current_race())
                                paused = False
                                self._wait_for_button_release(GAMEPAD_CONFIRM_BUTTON)
                            elif selected_option == 2:
                                pygame.quit()
                                sys.exit()
                        elif event.button == GAMEPAD_PAUSE_BUTTON:
                            gamepad_cooldown = GAMEPAD_COOLDOWN_TIME
                            paused = False
                            self._wait_for_button_release(GAMEPAD_PAUSE_BUTTON)

            # Gamepad D-Pad für Navigation (mit Cooldown)
            if self.gamepad and gamepad_cooldown <= 0:
                try:
                    nav_up = False
                    nav_down = False

                    # D-Pad (Hat) prüfen
                    if self.gamepad.get_numhats() > 0:
                        hat = self.gamepad.get_hat(0)
                        nav_up = hat[1] > 0
                        nav_down = hat[1] < 0
                    else:
                        # Fallback: Stick
                        stick_y = self.gamepad.get_axis(1)
                        nav_up = stick_y < -0.6
                        nav_down = stick_y > 0.6

                    if nav_up:
                        selected_option = (selected_option - 1) % len(menu_options)
                        if beep_sound:
                            beep_sound.play()
                        gamepad_cooldown = GAMEPAD_COOLDOWN_TIME
                    elif nav_down:
                        selected_option = (selected_option + 1) % len(menu_options)
                        if beep_sound:
                            beep_sound.play()
                        gamepad_cooldown = GAMEPAD_COOLDOWN_TIME
                except:
                    pass

            # Halbtransparentes Overlay über das Spiel zeichnen
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.fill((0, 0, 0))
            overlay.set_alpha(180)
            self.screen.blit(overlay, (0, 0))

            # "PAUSED" Titel
            title_text = title_font.render("PAUSED", True, (255, 255, 100))
            title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 64))
            self.screen.blit(title_text, title_rect)

            # Menü-Box (20% kleiner)
            box_width = int(224 * RENDER_SCALE)
            box_height = len(menu_options) * int(32 * RENDER_SCALE) + int(32 * RENDER_SCALE)
            box_x = WIDTH // 2 - box_width // 2
            box_y = HEIGHT // 2 - int(16 * RENDER_SCALE)

            box_surface = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
            box_surface.fill((*COLOR_BG, 200))
            self.screen.blit(box_surface, (box_x, box_y))

            # Border
            pygame.draw.rect(self.screen, COLOR_BORDER,
                           pygame.Rect(box_x, box_y, box_width, box_height), 3)

            # Menü-Optionen
            for i, option in enumerate(menu_options):
                is_selected = i == selected_option
                color = COLOR_SELECTED if is_selected else COLOR_TEXT

                option_text = menu_font.render(option, True, color)
                text_x = WIDTH // 2 - option_text.get_width() // 2
                text_y = box_y + int(16 * RENDER_SCALE) + i * int(32 * RENDER_SCALE)

                # Pfeile für ausgewählte Option
                if is_selected:
                    arrow_left = menu_font.render(">>", True, COLOR_SELECTED)
                    arrow_right = menu_font.render("<<", True, COLOR_SELECTED)
                    self.screen.blit(arrow_left, (text_x - int(32 * RENDER_SCALE), text_y))
                    self.screen.blit(arrow_right, (text_x + option_text.get_width() + int(16 * RENDER_SCALE), text_y))

                self.screen.blit(option_text, (text_x, text_y))

            pygame.display.flip()
            clock.tick(60)

# Ausführung der Spielschleife, wenn als Skript ausgeführt.
if __name__ == '__main__':
    app = App()
    app.run()