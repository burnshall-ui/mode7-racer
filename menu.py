# Startbildschirm und Menü-System
import pygame
from pygame import mixer
import sys
import math
import time
from settings.renderer_settings import WIDTH, HEIGHT, WIN_RES
from settings.league_settings import SINGLE_MODE_RACES
from settings.music_settings import BGM_DICT, MUSIC_VOLUME
from highscores import HighscoreManager

class Menu:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()

        # Pygame Font initialisieren
        pygame.font.init()

        # Menü-Musik vorbereiten (aber noch nicht starten - erst nach Intro)
        mixer.music.load(BGM_DICT["menu"])
        mixer.music.set_volume(MUSIC_VOLUME * 0.70)  # 30% leiser als Standard

        # Menü-Navigation Sound laden
        try:
            self.beep_sound = mixer.Sound("sounds/beep-menu.mp3")
            self.beep_sound.set_volume(0.6)  # 60% Lautstärke
        except Exception as e:
            print(f"Beep-Sound konnte nicht geladen werden: {e}")
            self.beep_sound = None

        # Bestätigungs-Sound laden
        try:
            self.confirm_sound = mixer.Sound("sounds/beep-auswahl.mp3")
            self.confirm_sound.set_volume(1.2)  # 120% Lautstärke
        except Exception as e:
            print(f"Bestätigungs-Sound konnte nicht geladen werden: {e}")
            self.confirm_sound = None

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

        # Gradient-Hintergrund einmalig berechnen (Performance-Optimierung)
        self.gradient_surface = pygame.Surface((WIDTH, HEIGHT))
        for y in range(HEIGHT):
            ratio = y / HEIGHT
            r = int(self.COLOR_BG_TOP[0] * (1 - ratio) + self.COLOR_BG_BOTTOM[0] * ratio)
            g = int(self.COLOR_BG_TOP[1] * (1 - ratio) + self.COLOR_BG_BOTTOM[1] * ratio)
            b = int(self.COLOR_BG_TOP[2] * (1 - ratio) + self.COLOR_BG_BOTTOM[2] * ratio)
            pygame.draw.line(self.gradient_surface, (r, g, b), (0, y), (WIDTH, y))

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
        self.current_screen = "main"  # "main", "track_select" oder "highscores"
        self.selected_index = 0
        self.selected_race = 0

        # Track-Namen (nur funktionierende Strecken)
        self.track_names = [
            "Funktioniert1",
            "Event Horizon I",
            "Space 3"
        ]

        # Highscore-Manager initialisieren
        self.highscore_manager = HighscoreManager()

    def show_intro(self):
        """Zeigt das animierte Logo-Intro"""
        intro_start = time.time()
        zoom_duration = 1.5  # Zoom-Animation Dauer (langsamer, passt zum Sound)
        music_started = False  # Flag für Musik-Start

        # Intro-Logo laden (falls nicht schon geladen)
        try:
            intro_logo_original = pygame.image.load("gfx/ui/mode7_logo.png").convert_alpha()
            logo_width = int(400 * (WIDTH / 640))
            logo_height = int(intro_logo_original.get_height() * (logo_width / intro_logo_original.get_width()))
            intro_logo_base = pygame.transform.smoothscale(intro_logo_original, (logo_width, logo_height))
        except:
            return  # Kein Logo, kein Intro

        # Logo-Sound abspielen
        try:
            logo_sound = mixer.Sound("sounds/efect-logo.mp3")
            logo_sound.set_volume(0.8)
            logo_sound.play()
        except Exception as e:
            print(f"Logo-Sound konnte nicht geladen werden: {e}")

        while True:
            elapsed = time.time() - intro_start

            # Schwarzer Hintergrund
            self.screen.fill((0, 0, 0))

            # Zoom-Animation mit Bounce
            if elapsed < zoom_duration:
                # Zoom von 0.3 zu 1.1 (overshoot)
                progress = elapsed / zoom_duration
                # Easing: schnell rein, dann bounce
                if progress < 0.7:
                    scale = 0.3 + (progress / 0.7) * 1.1  # Zu 1.1 zoomen
                else:
                    # Bounce zurück zu 1.0
                    bounce_progress = (progress - 0.7) / 0.3
                    scale = 1.1 - (bounce_progress * 0.1)
                logo_alpha = int(255 * progress)
            else:
                # Finale Größe
                scale = 1.0
                logo_alpha = 255

            # Logo skalieren
            scaled_width = int(intro_logo_base.get_width() * scale)
            scaled_height = int(intro_logo_base.get_height() * scale)
            intro_logo = pygame.transform.smoothscale(intro_logo_base, (scaled_width, scaled_height))

            logo_x = WIDTH // 2 - intro_logo.get_width() // 2
            logo_y = HEIGHT // 2 - intro_logo.get_height() // 2

            # Logo rendern
            logo_copy = intro_logo.copy()
            logo_copy.set_alpha(logo_alpha)
            self.screen.blit(logo_copy, (logo_x, logo_y))

            # Schwarze Streifen über das Logo legen (Sliced-Effekt)
            stripe_height = 2  # Dicke der schwarzen Streifen
            stripe_spacing = 8  # Abstand zwischen den Streifen

            for y in range(0, intro_logo.get_height(), stripe_spacing):
                stripe_alpha = int(255 * (logo_alpha / 255))
                stripe_surface = pygame.Surface((intro_logo.get_width(), stripe_height), pygame.SRCALPHA)
                stripe_surface.fill((0, 0, 0, stripe_alpha))
                self.screen.blit(stripe_surface, (logo_x, logo_y + y))

            # Menü-Musik starten nach der Animation
            if elapsed >= zoom_duration and not music_started:
                mixer.music.play(-1)  # -1 = Endlosschleife
                music_started = True

            # "PRESS ANY KEY" Text - nur anzeigen nach Zoom-Animation
            if elapsed >= zoom_duration:
                # Blinken wie im Hauptmenü
                if int(elapsed * 2) % 2 == 0:
                    press_text = self.font_small.render("PRESS ANY KEY TO CONTINUE", True, self.COLOR_SELECTED)
                    text_x = WIDTH // 2 - press_text.get_width() // 2
                    text_y = HEIGHT - 40  # 40px vom unteren Rand
                    self.screen.blit(press_text, (text_x, text_y))

            pygame.display.flip()
            self.clock.tick(60)

            # Events behandeln
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN and elapsed >= zoom_duration:
                    return  # Intro beenden, nur nach Zoom-Animation

    def run(self):
        """Hauptschleife des Menüs - gibt die gewählte Strecke zurück"""
        # Intro anzeigen (Musik wird automatisch nach der Animation gestartet)
        self.show_intro()

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
                    elif self.current_screen == "highscores":
                        running = self.handle_highscores_input(event.key)

            # Bildschirm zeichnen
            if self.current_screen == "main":
                self.draw_main_menu()
            elif self.current_screen == "track_select":
                self.draw_track_select()
            elif self.current_screen == "highscores":
                self.draw_highscores()

            pygame.display.flip()
            self.clock.tick(60)

        # Menü-Musik stoppen bevor Rennen startet
        mixer.music.stop()
        return self.selected_race

    def handle_main_menu_input(self, key):
        """Behandelt Eingaben im Hauptmenü"""
        if key == pygame.K_UP:
            self.selected_index = (self.selected_index - 1) % 3
            if self.beep_sound:
                self.beep_sound.play()
        elif key == pygame.K_DOWN:
            self.selected_index = (self.selected_index + 1) % 3
            if self.beep_sound:
                self.beep_sound.play()
        elif key == pygame.K_RETURN or key == pygame.K_SPACE:
            if self.confirm_sound:
                self.confirm_sound.play()
            if self.selected_index == 0:  # Start Race
                self.current_screen = "track_select"
                self.selected_index = 0
            elif self.selected_index == 1:  # Highscore
                self.current_screen = "highscores"
                self.selected_index = 0
            elif self.selected_index == 2:  # Quit
                pygame.quit()
                sys.exit()

        return True

    def handle_track_select_input(self, key):
        """Behandelt Eingaben in der Streckenauswahl"""
        if key == pygame.K_UP:
            self.selected_race = (self.selected_race - 1) % len(SINGLE_MODE_RACES)
            if self.beep_sound:
                self.beep_sound.play()
        elif key == pygame.K_DOWN:
            self.selected_race = (self.selected_race + 1) % len(SINGLE_MODE_RACES)
            if self.beep_sound:
                self.beep_sound.play()
        elif key == pygame.K_RETURN or key == pygame.K_SPACE:
            if self.confirm_sound:
                self.confirm_sound.play()
            return False  # Menü beenden, Rennen starten
        elif key == pygame.K_ESCAPE:
            self.current_screen = "main"
            self.selected_index = 0

        return True

    def draw_gradient_background(self):
        """Zeichnet einen Farbverlauf-Hintergrund (gecacht für Performance)"""
        self.screen.blit(self.gradient_surface, (0, 0))

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
        menu_items = ["START RACE", "HIGHSCORE", "QUIT"]
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
                # Animierter Pfeil links
                arrow_offset = int(math.sin(elapsed * 5) * 10)
                arrow_left = self.font_menu.render(">>", True, self.COLOR_SELECTED)
                self.screen.blit(arrow_left, (text_x - 60 + arrow_offset, text_y))

                # Animierter Pfeil rechts
                arrow_right = self.font_menu.render("<<", True, self.COLOR_SELECTED)
                self.screen.blit(arrow_right, (text_x + text.get_width() + 20 - arrow_offset, text_y))

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

    def handle_highscores_input(self, key):
        """Behandelt Eingaben im Highscore-Screen"""
        if key == pygame.K_ESCAPE or key == pygame.K_RETURN or key == pygame.K_SPACE:
            self.current_screen = "main"
            self.selected_index = 0

        return True

    def draw_highscores(self):
        """Zeichnet den Highscore-Screen"""
        # Gradient-Hintergrund
        self.draw_gradient_background()

        # Animations-Werte
        elapsed = time.time() - self.start_time

        # Titel mit Glow
        title_text = "HIGHSCORES"
        for offset in [6, 4, 2]:
            glow = self.font_title.render(title_text, True, self.COLOR_TITLE)
            glow.set_alpha(80)
            self.screen.blit(glow, (WIDTH // 2 - glow.get_width() // 2 + offset, 30 + offset))

        title = self.font_title.render(title_text, True, self.COLOR_TITLE)
        self.screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 30))

        # Highscores anzeigen
        y_offset = 110

        # Alle Highscores holen
        all_highscores = self.highscore_manager.highscores

        if not all_highscores:
            # Keine Highscores vorhanden
            no_scores_text = self.font_menu.render("NO RECORDS YET", True, self.COLOR_TEXT)
            no_scores_rect = no_scores_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            self.screen.blit(no_scores_text, no_scores_rect)
        else:
            # Kompakteres Layout: 60px pro Track statt 70px
            track_height = 60
            frame_height = len(all_highscores) * track_height + 20
            frame_rect = pygame.Rect(30, y_offset - 10, WIDTH - 60, frame_height)
            pygame.draw.rect(self.screen, self.COLOR_BORDER, frame_rect, 3)

            # Highscores anzeigen
            for i, (track_name, scores) in enumerate(all_highscores.items()):
                track_y = y_offset + i * track_height

                # Track-Name in Cyan
                track_text = self.font_small.render(track_name.upper(), True, self.COLOR_ACCENT)
                self.screen.blit(track_text, (50, track_y))

                # Best Lap in Weiß
                best_lap = scores.get("best_lap")
                if best_lap:
                    lap_time_str = self.format_time(best_lap)
                    lap_text = self.font_small.render(f"LAP: {lap_time_str}", True, self.COLOR_TEXT)
                    self.screen.blit(lap_text, (50, track_y + 25))

                # Best Total in Magenta
                best_total = scores.get("best_total")
                if best_total:
                    total_time_str = self.format_time(best_total)
                    total_text = self.font_small.render(f"TOTAL: {total_time_str}", True, self.COLOR_SELECTED)
                    self.screen.blit(total_text, (280, track_y + 25))

        # "PRESS ESC TO RETURN" am unteren Rand
        return_text = self.font_small.render("PRESS ESC TO RETURN", True, self.COLOR_TEXT)
        return_rect = return_text.get_rect(center=(WIDTH // 2, HEIGHT - 30))
        self.screen.blit(return_text, return_rect)

        # Scan-Lines
        self.draw_scanlines()

    def format_time(self, time_ms):
        """Formatiert Millisekunden zu MM:SS.mmm"""
        total_seconds = int(time_ms // 1000)
        milliseconds = int(time_ms % 1000)
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        return f"{minutes:02d}:{seconds:02d}.{milliseconds:03d}"
