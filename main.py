# Importe externer Module
import pygame, time
from pygame import mixer # Modul zum Abspielen von Sound
import sys

# Import der Spiel-Einstellungen
from settings.debug_settings import *
from settings.machine_settings import *
from settings.renderer_settings import *
from settings.track_settings import *
from settings.ui_settings import *
from settings.ui_settings import GAME_OVER_OVERLAY_ALPHA, GAME_OVER_IMAGE, PRESS_SPACE_IMAGE
from settings.ui_settings import FINISH_OVERLAY_ALPHA, get_pixel_font
from settings.key_settings import STD_CONFIRM_KEY, STD_DEBUG_RESTART_KEY
from settings.league_settings import *
from settings.music_settings import *

# Weitere Importe aus diesem Projekt
from mode7 import Mode7
from player import Player
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

        # Initialisiert das Modul, das für das Abspielen von Sounds verantwortlich ist
        mixer.init()
        mixer.music.set_volume(MUSIC_VOLUME)

        # Highscore-Manager initialisieren
        self.highscore_manager = HighscoreManager()

        # Rekord-Infos für aktuelles Rennen (wird nach Rennende gesetzt)
        self.current_race_record_info = None

        # ------------- Ende der allgemeinen Initialisierung -------------



        # ------------- Menü anzeigen -----------------------

        # Zeige Startbildschirm und Streckenauswahl
        menu = Menu(self.screen)
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

        # Deklariert den Mode-7-Renderer.
        # Wird später beim Laden des Rennens initialisiert.
        self.mode7 = None

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
            current_race = next_race
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
        pygame.display.set_caption(f'{self.clock.get_fps(): 0.1f}')

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

        # Musik neu starten
        mixer.music.load(race.music_track_path)
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

    def draw(self):
        # Zeichnet die Mode-7-Umgebung
        self.mode7.draw()

        # Zeichnet statische Sprites (z.B. Spieler-Schatten) auf den Bildschirm
        self.static_sprites.draw(self.screen)

        # Zeichnet bewegliche Sprites (z.B. Spieler) auf den Bildschirm
        self.moving_sprites.draw(self.screen)

        # Zeichnet UI-Sprites auf den Bildschirm
        self.ui_sprites.draw(self.screen)

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
            self.draw_race_finished_overlay()

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

            # Prüft auf Tastendrücke in Menübildschirmen
            if event.type == pygame.KEYDOWN:
                # ESC: Pause-Menü während des Rennens
                if event.key == pygame.K_ESCAPE and self.in_racing_mode and not self.player.finished and not self.player.destroyed:
                    self.show_pause_menu()

                if event.key == STD_CONFIRM_KEY and self.player.finished:
                    self.should_load_next_race = True
                # Game Over: Leertaste zum Neustarten
                if event.key == STD_CONFIRM_KEY and self.player.destroyed:
                    self.load_race(self.current_league.current_race())
                if event.key == STD_DEBUG_RESTART_KEY and DEBUG_RESTART_RACE_ON_R:
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
                ENERGY_METER_LEFT_X, # links
                ENERGY_METER_TOP_Y, # oben
                (RIGHT_MOST_TIMER_DIGIT_SCREEN_X_COORD - ENERGY_METER_LEFT_X) * (self.player.current_energy / self.player.machine.max_energy), # pos x
                ENERGY_METER_TOP_Y + (ENERGY_METER_HEIGHT / 2) # pos y
            )
        )

    # Zeichnet das Game Over Overlay wenn der Spieler zerstört wurde (SNES-Style)
    def draw_game_over_overlay(self):
        # Halbtransparentes dunkles Overlay
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(GAME_OVER_OVERLAY_ALPHA)
        self.screen.blit(overlay, (0, 0))

        # "GAME OVER" Sprite zentriert
        game_over_rect = GAME_OVER_IMAGE.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 20))
        self.screen.blit(GAME_OVER_IMAGE, game_over_rect)

        # "PRESS SPACE" Sprite zentriert darunter
        press_space_rect = PRESS_SPACE_IMAGE.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 30))
        self.screen.blit(PRESS_SPACE_IMAGE, press_space_rect)

    # Zeichnet das Finish Screen Overlay wenn der Spieler das Rennen beendet hat
    def draw_race_finished_overlay(self):
        # Fonts (kleinere Größen)
        title_font = get_pixel_font(int(36 * RENDER_SCALE))
        text_font = get_pixel_font(int(20 * RENDER_SCALE))
        small_font = get_pixel_font(int(16 * RENDER_SCALE))
        tiny_font = get_pixel_font(int(14 * RENDER_SCALE))

        # "RACE FINISHED!" Titel
        title_text = title_font.render("RACE FINISHED!", True, (255, 255, 100))
        title_rect = title_text.get_rect(center=(WIDTH // 2, int(HEIGHT * 0.3)))
        self.screen.blit(title_text, title_rect)

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
                    True, (150, 150, 200)
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

    def show_pause_menu(self):
        """Zeigt das Pause-Menü und behandelt die Menü-Navigation"""
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

        while paused:
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