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
        # Wir nutzen aus, dass ein Einzelrennen als League-Objekt betrachtet werden kann,
        # dessen Rennliste nur ein Rennen enthält.
        self.current_league = League( [SINGLE_MODE_RACES[race_choice]] )
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

        # Initialen Zeitstempel nehmen, der
        # für den Timer verwendet wird, der die Zeit seit Rennstart verfolgt.
        # Muss die Methode get_time verwenden, da das Feld self.time zu diesem Zeitpunkt nicht initialisiert ist.
        self.race_start_timestamp = self.time

        # Status-Flag setzen
        self.in_racing_mode = True

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
            if not self.player.finished and not self.player.destroyed:
                seconds_since_race_start = self.time - self.race_start_timestamp
                self.ui.update(
                    elapsed_milliseconds = seconds_since_race_start * 1000
                )

            # Prüft, ob der Spieler das Rennen beendet hat.
            # Wenn ja, wird ein Status-Flag in der Spielerinstanz gesetzt, falls noch nicht geschehen.
            if self.current_league.current_race().player_finished_race() and not self.player.finished:
                self.player.finished = True

            # Nächstes Rennen laden, wenn der Spieler das aktuelle beendet hat und die Bestätigungstaste gedrückt hat (was das Flag setzt)
            if self.should_load_next_race:
                self.player.finished = False
                self.load_race(self.current_league.next_race())

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

        # Timer zurücksetzen
        self.race_start_timestamp = self.time

        # Musik neu starten
        mixer.music.load(race.music_track_path)
        mixer.music.play()

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

        # Zeichnet Debug-Objekte wie Energieleiste
        if self.in_racing_mode:
            self.draw_racing_mode_debug_objects()

        # Game Over Overlay zeichnen wenn Spieler zerstört wurde
        if self.in_racing_mode and self.player.destroyed:
            self.draw_game_over_overlay()

        # Inhalt der gesamten Anzeige aktualisieren
        pygame.display.flip()

    def get_time(self):
        self.time = time.time()

    def check_event(self):
        for event in pygame.event.get():
            # Prozess beenden, der das Spiel ausführt,
            # wenn Escape-Taste gedrückt wird oder etwas anderes das Beenden-Ereignis verursacht
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Prüft auf Tastendrücke in Menübildschirmen
            if event.type == pygame.KEYDOWN:
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

# Ausführung der Spielschleife, wenn als Skript ausgeführt.
if __name__ == '__main__':
    app = App()
    app.run()