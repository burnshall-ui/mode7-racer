# Startbildschirm und Menü-System
import pygame
from pygame import mixer
import sys
import math
import time
from settings.renderer_settings import WIDTH, HEIGHT, WIN_RES
from settings.league_settings import SINGLE_MODE_RACES
from settings.music_settings import BGM_DICT, MUSIC_VOLUME

class Menu:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()

        # Pygame Font initialisieren
        pygame.font.init()

        # Menü-Musik starten
        mixer.music.load(BGM_DICT["menu"])
        mixer.music.set_volume(MUSIC_VOLUME)
        mixer.music.play(-1)  # -1 = Endlosschleife

        # Farben im Retro-Style (SNES F-Zero inspiriert)
        self.COLOR_BG_TOP = (10, 5, 30)  # Dunkelblau-Violett
        self.COLOR_BG_BOTTOM = (0, 0, 0)  # Schwarz
        self.COLOR_TITLE = (255, 220, 0)  # Gold
        self.COLOR_TEXT = (180, 200, 255)  # Helles Blau-Weiß
        self.COLOR_SELECTED = (255, 50, 200)  # Magenta
        self.COLOR_ACCENT = (0, 255, 255)  # Cyan
        self.COLOR_BORDER = (100, 100, 150)  # Grau-Blau

        # Fonts - Feste Größen für die aktuelle Auflösung
        self.font_title = pygame.font.Font(None, 100)  # Titel
        self.font_menu = pygame.font.Font(None, 50)    # Menü-Items
        self.font_small = pygame.font.Font(None, 28)   # Kleine Texte

        # Animations-Timer
        self.start_time = time.time()

        # Logo-Image laden
        try:
            self.logo_image = pygame.image.load("gfx/ui/mode7_logo.png").convert_alpha()
            # Auf passende Größe skalieren (ca. 320px breit für 640x360 Auflösung)
            logo_width = int(320 * (WIDTH / 640))  # Skaliert mit der Auflösung
            logo_height = int(self.logo_image.get_height() * (logo_width / self.logo_image.get_width()))
            self.logo_image = pygame.transform.smoothscale(self.logo_image, (logo_width, logo_height))
            self.has_logo_image = True
        except Exception as e:
            self.has_logo_image = False
            print(f"Logo-Image nicht gefunden: {e}, verwende Text-Fallback")

        # Menü-Zustand
        self.current_screen = "main"  # "main" oder "track_select"
        self.selected_index = 0
        self.selected_race = 0

        # Track-Namen (nur funktionierende Strecken)
        self.track_names = [
            "Funktioniert1",
            "Event Horizon I"
        ]

    def run(self):
        """Hauptschleife des Menüs - gibt die gewählte Strecke zurück"""
        running = True

        while running:
            # Events behandeln
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if self.current_screen == "main":
                        running = self.handle_main_menu_input(event.key)
                    elif self.current_screen == "track_select":
                        running = self.handle_track_select_input(event.key)

            # Bildschirm zeichnen
            if self.current_screen == "main":
                self.draw_main_menu()
            elif self.current_screen == "track_select":
                self.draw_track_select()

            pygame.display.flip()
            self.clock.tick(60)

        # Menü-Musik stoppen bevor Rennen startet
        mixer.music.stop()
        return self.selected_race

    def handle_main_menu_input(self, key):
        """Behandelt Eingaben im Hauptmenü"""
        if key == pygame.K_UP:
            self.selected_index = (self.selected_index - 1) % 3
        elif key == pygame.K_DOWN:
            self.selected_index = (self.selected_index + 1) % 3
        elif key == pygame.K_RETURN or key == pygame.K_SPACE:
            if self.selected_index == 0:  # Start Race
                self.current_screen = "track_select"
                self.selected_index = 0
            elif self.selected_index == 1:  # Options (noch nicht implementiert)
                pass
            elif self.selected_index == 2:  # Quit
                pygame.quit()
                sys.exit()

        return True

    def handle_track_select_input(self, key):
        """Behandelt Eingaben in der Streckenauswahl"""
        if key == pygame.K_UP:
            self.selected_race = (self.selected_race - 1) % len(SINGLE_MODE_RACES)
        elif key == pygame.K_DOWN:
            self.selected_race = (self.selected_race + 1) % len(SINGLE_MODE_RACES)
        elif key == pygame.K_RETURN or key == pygame.K_SPACE:
            return False  # Menü beenden, Rennen starten
        elif key == pygame.K_ESCAPE:
            self.current_screen = "main"
            self.selected_index = 0

        return True

    def draw_gradient_background(self):
        """Zeichnet einen Farbverlauf-Hintergrund"""
        for y in range(HEIGHT):
            # Interpoliere zwischen Top und Bottom Farbe
            ratio = y / HEIGHT
            r = int(self.COLOR_BG_TOP[0] * (1 - ratio) + self.COLOR_BG_BOTTOM[0] * ratio)
            g = int(self.COLOR_BG_TOP[1] * (1 - ratio) + self.COLOR_BG_BOTTOM[1] * ratio)
            b = int(self.COLOR_BG_TOP[2] * (1 - ratio) + self.COLOR_BG_BOTTOM[2] * ratio)
            pygame.draw.line(self.screen, (r, g, b), (0, y), (WIDTH, y))

    def draw_scanlines(self):
        """Zeichnet CRT-Scanlines für Retro-Effekt"""
        for y in range(0, HEIGHT, 4):
            pygame.draw.line(self.screen, (0, 0, 0, 30), (0, y), (WIDTH, y), 1)

    def draw_main_menu(self):
        """Zeichnet das Hauptmenü"""
        # Gradient-Hintergrund
        self.draw_gradient_background()

        # Animations-Werte
        elapsed = time.time() - self.start_time
        pulse = abs(math.sin(elapsed * 2)) * 0.2 + 0.8  # Pulsiert zwischen 0.8 und 1.0

        # Logo rendern (Image oder Text-Fallback)
        if self.has_logo_image:
            # Logo mit leichtem Pulsier-Effekt
            logo_alpha = int(255 * pulse)
            logo_copy = self.logo_image.copy()
            logo_copy.set_alpha(logo_alpha)
            logo_x = WIDTH // 2 - logo_copy.get_width() // 2
            logo_y = int(20 * (HEIGHT / 360))  # Oben positioniert, skaliert mit Auflösung

            # Hauptlogo zeichnen (ohne extra Glow - das PNG hat bereits einen)
            self.screen.blit(logo_copy, (logo_x, logo_y))

            # Y-Position nach dem Logo für weitere Elemente (mehr Abstand)
            after_logo_y = logo_y + logo_copy.get_height() + int(15 * (HEIGHT / 360))
        else:
            # Text-Fallback mit dem originalen pulsierenden Glow-Effekt
            title_text = "MODE7 RACER"
            
            # Mehrfache Schatten für Glow-Effekt
            for offset in [8, 6, 4, 2]:
                glow_alpha = int(100 * pulse)
                glow = self.font_title.render(title_text, True, (255, 200, 0))
                glow.set_alpha(glow_alpha)
                self.screen.blit(glow, (WIDTH // 2 - glow.get_width() // 2 + offset, 50 + offset))

            # Haupttitel mit Pulsieren
            title_color = (
                int(255 * pulse),
                int(220 * pulse),
                0
            )
            title = self.font_title.render(title_text, True, title_color)
            self.screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 50))
            
            after_logo_y = 150

        # Untertitel mit Blink-Effekt
        if int(elapsed * 2) % 2 == 0:
            subtitle = self.font_small.render("F-ZERO STYLE RACING", True, self.COLOR_ACCENT)
            self.screen.blit(subtitle, (WIDTH // 2 - subtitle.get_width() // 2, after_logo_y))

        # Menü-Box Hintergrund - kompakt und zentriert
        menu_box_y = after_logo_y + 40
        menu_box_rect = pygame.Rect(WIDTH // 2 - 200, menu_box_y, 400, 150)
        pygame.draw.rect(self.screen, (20, 10, 40, 180), menu_box_rect)
        pygame.draw.rect(self.screen, self.COLOR_BORDER, menu_box_rect, 3)

        # Menü-Optionen - kompakt mit gleichmäßigem Padding
        menu_items = ["START RACE", "OPTIONS", "QUIT"]
        start_y = menu_box_y + 25

        for i, item in enumerate(menu_items):
            is_selected = i == self.selected_index
            color = self.COLOR_SELECTED if is_selected else self.COLOR_TEXT

            # Text zuerst rendern
            text = self.font_menu.render(item, True, color)
            text_x = WIDTH // 2 - text.get_width() // 2
            text_y = start_y + i * 45  # Kompaktere Abstände

            # Nur Pfeil für ausgewähltes Item - KEINE BOX!
            if is_selected:
                # Animierter Pfeil
                arrow_offset = int(math.sin(elapsed * 5) * 10)
                arrow = self.font_menu.render(">>", True, self.COLOR_SELECTED)
                self.screen.blit(arrow, (text_x - 60 + arrow_offset, text_y))

            # Text zeichnen
            self.screen.blit(text, (text_x, text_y))

        # Scan-Lines
        self.draw_scanlines()

    def draw_track_select(self):
        """Zeichnet die Streckenauswahl"""
        # Gradient-Hintergrund
        self.draw_gradient_background()

        # Animations-Werte
        elapsed = time.time() - self.start_time

        # Titel mit Glow
        title_text = "TRACK SELECT"
        for offset in [6, 4, 2]:
            glow = self.font_title.render(title_text, True, (255, 200, 0))
            glow.set_alpha(80)
            self.screen.blit(glow, (WIDTH // 2 - glow.get_width() // 2 + offset, 30 + offset))

        title = self.font_title.render(title_text, True, self.COLOR_TITLE)
        self.screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 30))

        # Track-Liste Box - muss in HEIGHT=360 passen!
        # Box startet bei 130, Screen endet bei 360 → max 210px Höhe
        list_box_rect = pygame.Rect(40, 130, WIDTH - 80, 210)
        pygame.draw.rect(self.screen, (20, 10, 40, 200), list_box_rect)
        pygame.draw.rect(self.screen, self.COLOR_BORDER, list_box_rect, 3)

        # Strecken-Liste (scrollbar wenn zu viele)
        visible_tracks = 5
        start_y = 145  # 15px Top-Padding
        track_spacing = 38  # Etwas mehr Luft zwischen den Tracks

        # Berechne welche Tracks angezeigt werden sollen
        start_index = max(0, self.selected_race - visible_tracks // 2)
        end_index = min(len(self.track_names), start_index + visible_tracks)

        if end_index - start_index < visible_tracks:
            start_index = max(0, end_index - visible_tracks)

        for i in range(start_index, end_index):
            is_selected = i == self.selected_race
            color = self.COLOR_SELECTED if is_selected else self.COLOR_TEXT

            # Track-Name - kleinerer Font
            track_text = f"{i + 1}. {self.track_names[i]}"
            text = self.font_small.render(track_text, True, color)
            text_x = 110
            text_y = start_y + (i - start_index) * track_spacing

            # Nur Pfeil für ausgewählte Strecke - KEINE ROSA BOX!
            if is_selected:
                # Animierter Pfeil
                arrow_offset = int(math.sin(elapsed * 5) * 8)
                arrow = self.font_small.render(">>", True, self.COLOR_SELECTED)
                self.screen.blit(arrow, (60 + arrow_offset, text_y))

            # Track-Name zeichnen
            self.screen.blit(text, (text_x, text_y))

        # Scan-Lines
        self.draw_scanlines()
