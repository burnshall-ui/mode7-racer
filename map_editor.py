"""
Map Editor - Erstelle und bearbeite Kollisionsrechtecke für Strecken

Steuerung:
- Pfeiltasten: Karte verschieben
- +/-: Zoomen
- Q/E: Textur wechseln (vorher/nächste)

Maus:
- Linksklick + Ziehen: Neues Rechteck zeichnen
- Rechtsklick: Rechteck löschen
- Mittelklick + Ziehen: Karte verschieben
- Mausrad: Zoom

Tasten:
- T: Typ wechseln (Strecke/Rampe/Recovery/Dash/Finish/Checkpoint)
- P: Startposition setzen (dann auf Karte klicken)
- A/D: Startwinkel drehen
- C: Code in Konsole ausgeben
- S: Code in Datei speichern
- L: Track-Kollisionsdaten laden (falls vorhanden)
- N: Alles löschen (Rechtecke + Startposition)
- ESC: Beenden
"""

import pygame
import json
import os
import glob
import math

pygame.init()

# Fenster
WIDTH, HEIGHT = 1400, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Map Editor - Mode7 Racer")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Consolas", 14)
font_big = pygame.font.SysFont("Consolas", 18, bold=True)

# Konstanten
SCALE = 20  # Mode7 Scale-Faktor

# Rechteck-Typen mit Farben
RECT_TYPES = [
    ("track", "Strecke", (0, 200, 0)),
    ("ramp", "Rampe", (255, 255, 0)),
    ("recovery", "Recovery", (0, 255, 255)),
    ("dash", "Dash Plate", (255, 0, 255)),
    ("dirt", "Dirt", (139, 90, 43)),  # Braun - verlangsamt den Spieler
    ("finish", "Ziellinie", (255, 0, 0)),
    ("checkpoint", "Checkpoint", (0, 100, 255)),
]

# Texturen dynamisch aus gfx-Ordner laden
def load_textures_from_folder():
    """Lädt alle PNG-Dateien aus dem gfx-Ordner"""
    textures = []
    gfx_path = "gfx"

    # Alle PNG-Dateien finden
    png_files = glob.glob(os.path.join(gfx_path, "*.png"))
    png_files.sort()  # Alphabetisch sortieren

    for filepath in png_files:
        filename = os.path.basename(filepath)
        # Name ohne Endung als Anzeigename
        name = os.path.splitext(filename)[0]
        textures.append((filepath, name))

    return textures

TEXTURES = load_textures_from_folder()
print(f"Gefunden: {len(TEXTURES)} Texturen im gfx-Ordner")

# Editor-Zustand
class Editor:
    def __init__(self):
        self.offset_x = 50
        self.offset_y = 50
        self.zoom = 0.4
        self.current_type = 0  # Index in RECT_TYPES
        self.current_texture_idx = 0
        self.texture = None
        self.texture_name = ""

        # Gezeichnete Rechtecke: Liste von dicts
        # {type, x, y, w, h} - alles in Pixel-Koordinaten
        self.rects = []

        # Zeichnen
        self.drawing = False
        self.draw_start = None

        # Panning
        self.panning = False
        self.pan_start = None

        # Startposition (Pixel-Koordinaten)
        self.start_pos = None  # (px, py) oder None
        self.start_angle = -1.57  # Radians (-90° = nach oben)
        self.setting_start_pos = False  # True wenn P gedrückt wurde

        self.load_texture(0)

    def load_texture(self, idx):
        if idx < 0 or idx >= len(TEXTURES):
            return
        self.current_texture_idx = idx
        path, name = TEXTURES[idx]
        self.texture_name = name
        try:
            self.texture = pygame.image.load(path)
            print(f"Textur geladen: {name} ({self.texture.get_width()}x{self.texture.get_height()})")
        except Exception as e:
            print(f"Fehler: {e}")
            self.texture = None

    def screen_to_pixel(self, sx, sy):
        """Bildschirm -> Textur-Pixel"""
        px = (sx - self.offset_x) / self.zoom
        py = (sy - self.offset_y) / self.zoom
        return px, py

    def pixel_to_screen(self, px, py):
        """Textur-Pixel -> Bildschirm"""
        sx = px * self.zoom + self.offset_x
        sy = py * self.zoom + self.offset_y
        return sx, sy

    def pixel_to_mode7(self, px, py, pw, ph):
        """Pixel-Rechteck -> Mode7 CollisionRect Parameter"""
        # Mittelpunkt
        cx = px + pw / 2
        cy = py + ph / 2
        # Nur horizontal spiegeln zurück
        tex_w = 4000
        cx = tex_w - cx
        # Mode7 Koordinaten
        mx = cy / SCALE
        my = -(cx / SCALE)
        mw = ph / SCALE
        mh = pw / SCALE
        return mx, my, mw, mh

    def pixel_to_mode7_pos(self, px, py):
        """Pixel-Position -> Mode7 Koordinaten"""
        tex_w = 4000
        cx = tex_w - px
        mx = py / SCALE
        my = -(cx / SCALE)
        return mx, my

    def add_rect(self, screen_x1, screen_y1, screen_x2, screen_y2):
        """Fügt ein neues Rechteck hinzu"""
        px1, py1 = self.screen_to_pixel(screen_x1, screen_y1)
        px2, py2 = self.screen_to_pixel(screen_x2, screen_y2)

        x = min(px1, px2)
        y = min(py1, py2)
        w = abs(px2 - px1)
        h = abs(py2 - py1)

        if w > 5 and h > 5:  # Mindestgröße
            rect_type = RECT_TYPES[self.current_type][0]
            self.rects.append({
                'type': rect_type,
                'x': x, 'y': y, 'w': w, 'h': h
            })
            print(f"Rechteck hinzugefügt: {rect_type} ({w:.0f}x{h:.0f})")

    def delete_rect_at(self, screen_x, screen_y):
        """Löscht Rechteck an Position"""
        px, py = self.screen_to_pixel(screen_x, screen_y)

        # Von hinten durchgehen (neueste zuerst)
        for i in range(len(self.rects) - 1, -1, -1):
            r = self.rects[i]
            if r['x'] <= px <= r['x'] + r['w'] and r['y'] <= py <= r['y'] + r['h']:
                del self.rects[i]
                print(f"Rechteck gelöscht")
                return True
        return False

    def draw(self, surface):
        """Zeichnet alles"""
        surface.fill((30, 30, 30))

        # Textur
        if self.texture:
            w = int(self.texture.get_width() * self.zoom)
            h = int(self.texture.get_height() * self.zoom)
            if w > 0 and h > 0:
                scaled = pygame.transform.scale(self.texture, (w, h))
                surface.blit(scaled, (self.offset_x, self.offset_y))

        # Rechtecke zeichnen
        for rect in self.rects:
            self.draw_rect(surface, rect)

        # Startposition zeichnen
        self.draw_start_position(surface)

        # Aktuelles Rechteck beim Zeichnen
        if self.drawing and self.draw_start:
            mx, my = pygame.mouse.get_pos()
            x1, y1 = self.draw_start
            x = min(x1, mx)
            y = min(y1, my)
            w = abs(mx - x1)
            h = abs(my - y1)
            color = RECT_TYPES[self.current_type][2]
            pygame.draw.rect(surface, color, (x, y, w, h), 2)

        # UI
        self.draw_ui(surface)

    def draw_rect(self, surface, rect):
        """Zeichnet ein Rechteck"""
        # Farbe finden
        color = (100, 100, 100)
        for t, _, c in RECT_TYPES:
            if t == rect['type']:
                color = c
                break

        sx, sy = self.pixel_to_screen(rect['x'], rect['y'])
        sw = rect['w'] * self.zoom
        sh = rect['h'] * self.zoom

        # Halbtransparent füllen
        s = pygame.Surface((max(1, int(sw)), max(1, int(sh))), pygame.SRCALPHA)
        s.fill((*color, 80))
        surface.blit(s, (sx, sy))

        # Rahmen
        pygame.draw.rect(surface, color, (sx, sy, sw, sh), 2)

    def draw_start_position(self, surface):
        """Zeichnet die Startposition als Pfeil"""
        if self.start_pos is None:
            return

        px, py = self.start_pos
        sx, sy = self.pixel_to_screen(px, py)

        # Pfeil-Größe
        size = 20 * self.zoom
        if size < 10:
            size = 10

        # Pfeil-Punkte berechnen (Dreieck)
        angle = self.start_angle
        # Spitze
        tip_x = sx + math.cos(angle) * size
        tip_y = sy + math.sin(angle) * size
        # Basis-Punkte (links und rechts hinten)
        back_angle1 = angle + 2.5  # ~140 Grad
        back_angle2 = angle - 2.5
        base1_x = sx + math.cos(back_angle1) * size * 0.6
        base1_y = sy + math.sin(back_angle1) * size * 0.6
        base2_x = sx + math.cos(back_angle2) * size * 0.6
        base2_y = sy + math.sin(back_angle2) * size * 0.6

        # Pfeil zeichnen (orange)
        points = [(tip_x, tip_y), (base1_x, base1_y), (sx, sy), (base2_x, base2_y)]
        pygame.draw.polygon(surface, (255, 150, 0), points)
        pygame.draw.polygon(surface, (255, 255, 255), points, 2)

        # Winkel-Anzeige
        angle_deg = math.degrees(self.start_angle)
        text = font.render(f"{angle_deg:.0f}°", True, (255, 255, 255))
        surface.blit(text, (sx + 15, sy - 10))

    def draw_ui(self, surface):
        """Zeichnet die UI"""
        # Mausposition
        mx, my = pygame.mouse.get_pos()
        px, py = self.screen_to_pixel(mx, my)
        # Mode7 Koordinaten (horizontal gespiegelt)
        tex_w = 4000
        rx = tex_w - px
        m7x = py / SCALE
        m7y = -(rx / SCALE)

        # Startposition-Info
        if self.start_pos:
            sp_m7x, sp_m7y = self.pixel_to_mode7_pos(self.start_pos[0], self.start_pos[1])
            start_info = f"Start: ({sp_m7x:.1f}, {sp_m7y:.1f}) @ {self.start_angle:.2f} rad"
        else:
            start_info = "Start: nicht gesetzt"

        # Modus-Anzeige
        if self.setting_start_pos:
            mode_info = ">>> STARTPOSITION SETZEN (Klicken) <<<"
        else:
            mode_info = f"Aktueller Typ: {RECT_TYPES[self.current_type][1]}"

        # Info-Panel links oben
        lines = [
            f"Textur [{self.current_texture_idx+1}/{len(TEXTURES)}]: {self.texture_name}",
            f"Zoom: {self.zoom:.2f}x  |  Rechtecke: {len(self.rects)}",
            f"Pixel: {px:.0f}, {py:.0f}  |  Mode7: {m7x:.1f}, {m7y:.1f}",
            start_info,
            "",
            mode_info,
            "",
            "--- Steuerung ---",
            "Pfeile: Bewegen  |  +/-: Zoom  |  Q/E: Textur",
            "Linksklick+Ziehen: Rechteck zeichnen",
            "Rechtsklick: Löschen  |  Mittelklick: Bewegen",
            "",
            "T: Typ wechseln  |  N: Alles löschen",
            "P: Startposition setzen  |  A/D: Winkel drehen",
            "L: Track laden  |  S/C: Code speichern/ausgeben",
        ]

        # Hintergrund
        pygame.draw.rect(surface, (0, 0, 0, 200), (5, 5, 350, len(lines) * 18 + 10))

        y = 10
        for line in lines:
            text = font.render(line, True, (255, 255, 255))
            surface.blit(text, (10, y))
            y += 18

        # Typ-Leiste unten
        bar_y = HEIGHT - 50
        pygame.draw.rect(surface, (20, 20, 20), (0, bar_y, WIDTH, 50))

        x = 10
        for i, (_, name, color) in enumerate(RECT_TYPES):
            # Ausgewählt?
            if i == self.current_type:
                pygame.draw.rect(surface, (255, 255, 255), (x - 3, bar_y + 7, 110, 36), 2)

            pygame.draw.rect(surface, color, (x, bar_y + 10, 30, 30))
            text = font.render(name, True, (255, 255, 255))
            surface.blit(text, (x + 35, bar_y + 15))
            x += 120

    def generate_code(self):
        """Generiert Python-Code für alle Rechtecke"""
        code_lines = []
        code_lines.append("# Generierter Code für track_settings.py")
        code_lines.append("# Kopiere die passenden Rechtecke in deine Track-Funktion")
        code_lines.append("")

        # Nach Typ gruppieren
        by_type = {}
        for rect in self.rects:
            t = rect['type']
            if t not in by_type:
                by_type[t] = []
            by_type[t].append(rect)

        type_comments = {
            'track': '# ========== STRECKE (track_surface_rects) ==========',
            'ramp': '# ========== RAMPEN (ramp_rects) ==========',
            'recovery': '# ========== RECOVERY ZONES (recovery_rects) ==========',
            'dash': '# ========== DASH PLATES (dash_plate_rects) ==========',
            'dirt': '# ========== DIRT ZONES (dirt_rects) ==========',
            'finish': '# ========== ZIELLINIE (finish_line_collider) ==========',
            'checkpoint': '# ========== CHECKPOINTS (key_checkpoint_rects) ==========',
        }

        for rect_type in ['track', 'ramp', 'recovery', 'dash', 'dirt', 'finish', 'checkpoint']:
            if rect_type in by_type:
                code_lines.append(type_comments.get(rect_type, f'# {rect_type}'))
                for i, rect in enumerate(by_type[rect_type]):
                    mx, my, mw, mh = self.pixel_to_mode7(rect['x'], rect['y'], rect['w'], rect['h'])
                    var_name = f"{rect_type}_{i+1}"
                    code_lines.append(f"{var_name} = CollisionRect(")
                    code_lines.append(f"    pos = numpy.array([{mx:.2f}, {my:.2f}]),")
                    code_lines.append(f"    w = {mw:.2f},")
                    code_lines.append(f"    h = {mh:.2f}")
                    code_lines.append(f")")
                    code_lines.append("")

        # Startposition
        code_lines.append("# ========== STARTPOSITION (für league_settings.py) ==========")
        if self.start_pos:
            sp_x, sp_y = self.pixel_to_mode7_pos(self.start_pos[0], self.start_pos[1])
            # Winkel um 90° (π/2) korrigieren für Mode7-Koordinatensystem
            game_angle = self.start_angle + 1.5708  # +π/2
            code_lines.append(f"init_player_pos_x = {sp_x:.2f}")
            code_lines.append(f"init_player_pos_y = {sp_y:.2f}")
            code_lines.append(f"init_player_angle = {game_angle:.2f}  # Radians")
        else:
            code_lines.append("# Startposition nicht gesetzt! Drücke P im Editor.")
        code_lines.append("")

        return "\n".join(code_lines)

    def save_code(self):
        """Speichert Code in Datei"""
        code = self.generate_code()
        filename = f"generated_track_{self.texture_name.replace(' ', '_').lower()}.py"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(code)
        print(f"\nCode gespeichert in: {filename}")
        return filename

    def load_existing_track(self):
        """Lädt einen bestehenden Track basierend auf dem Textur-Namen"""
        try:
            from settings.track_settings import TrackCreator

            # Zuordnung: Textur-Dateiname -> Track-Creator-Funktion
            texture_to_creator = {
                "track_2023": TrackCreator.create_track_2023,
                "track_2023_II": TrackCreator.create_track_2023_II,
                "event_horizon_track1": TrackCreator.create_event_horizon_track2,
                "event_horizon_track2": TrackCreator.create_event_horizon_track2,
                "new_track": TrackCreator.create_funktioniert1,
                "monochrome_track": TrackCreator.create_monochrome_track,
            }

            # Finde passenden Creator für aktuelle Textur
            creator = texture_to_creator.get(self.texture_name)

            if creator is None:
                print(f"Kein Track-Daten für '{self.texture_name}' gefunden")
                print(f"Verfügbar: {list(texture_to_creator.keys())}")
                return

            track = creator()
            self.rects = []

            # Streckenrechtecke
            for r in track.track_surface_rects:
                self.add_rect_from_mode7(r, 'track')

            # Rampen
            for r in track.ramp_rects:
                self.add_rect_from_mode7(r, 'ramp')

            # Recovery
            for r in track.recovery_zone_rects:
                self.add_rect_from_mode7(r, 'recovery')

            # Dash
            for r in track.dash_plate_rects:
                self.add_rect_from_mode7(r, 'dash')

            # Finish
            if track.finish_line_collider:
                self.add_rect_from_mode7(track.finish_line_collider, 'finish')

            # Checkpoints
            for cp in track.key_checkpoints:
                self.add_rect_from_mode7(cp.collider, 'checkpoint')

            print(f"Track geladen: {len(self.rects)} Rechtecke")

        except Exception as e:
            print(f"Fehler beim Laden: {e}")

    def add_rect_from_mode7(self, collision_rect, rect_type):
        """Fügt Rechteck aus Mode7-Koordinaten hinzu"""
        mx, my = collision_rect.position[0], collision_rect.position[1]
        mw, mh = collision_rect.width, collision_rect.height

        # Mode7 -> Pixel (nur Spiegeln)
        tex_w, tex_h = 4000, 2000
        cx = -my * SCALE
        cy = mx * SCALE
        # Nur horizontal spiegeln
        cx = tex_w - cx
        pw = mh * SCALE
        ph = mw * SCALE

        px = cx - pw / 2
        py = cy - ph / 2

        self.rects.append({
            'type': rect_type,
            'x': px, 'y': py, 'w': pw, 'h': ph
        })


# Editor starten
editor = Editor()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

            # Textur wechseln mit Q/E
            elif event.key == pygame.K_q:
                new_idx = (editor.current_texture_idx - 1) % len(TEXTURES)
                editor.load_texture(new_idx)
            elif event.key == pygame.K_e:
                new_idx = (editor.current_texture_idx + 1) % len(TEXTURES)
                editor.load_texture(new_idx)

            # Zoom
            elif event.key == pygame.K_PLUS or event.key == pygame.K_KP_PLUS:
                editor.zoom = min(3.0, editor.zoom + 0.1)
            elif event.key == pygame.K_MINUS or event.key == pygame.K_KP_MINUS:
                editor.zoom = max(0.1, editor.zoom - 0.1)

            # Typ wechseln
            elif event.key == pygame.K_t:
                editor.current_type = (editor.current_type + 1) % len(RECT_TYPES)
                print(f"Typ: {RECT_TYPES[editor.current_type][1]}")

            # Code ausgeben
            elif event.key == pygame.K_c:
                print("\n" + "=" * 60)
                print(editor.generate_code())
                print("=" * 60)

            # Code speichern
            elif event.key == pygame.K_s:
                editor.save_code()

            # Track laden (wenn Kollisionsdaten existieren)
            elif event.key == pygame.K_l:
                editor.load_existing_track()

            # Alles löschen
            elif event.key == pygame.K_n:
                editor.rects = []
                editor.start_pos = None
                print("Alle Rechtecke und Startposition gelöscht")

            # Startposition-Modus
            elif event.key == pygame.K_p:
                editor.setting_start_pos = True
                print("Startposition setzen: Klicke auf die Karte")

            # Winkel drehen mit A/D
            elif event.key == pygame.K_a:
                editor.start_angle -= 0.1  # ~6 Grad
                print(f"Winkel: {editor.start_angle:.2f} rad ({math.degrees(editor.start_angle):.0f}°)")
            elif event.key == pygame.K_d:
                editor.start_angle += 0.1  # ~6 Grad
                print(f"Winkel: {editor.start_angle:.2f} rad ({math.degrees(editor.start_angle):.0f}°)")

        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Linksklick
            if event.button == 1:
                if editor.setting_start_pos:
                    # Startposition setzen
                    px, py = editor.screen_to_pixel(*event.pos)
                    editor.start_pos = (px, py)
                    editor.setting_start_pos = False
                    m7x, m7y = editor.pixel_to_mode7_pos(px, py)
                    print(f"Startposition gesetzt: Mode7 ({m7x:.2f}, {m7y:.2f})")
                else:
                    # Rechteck zeichnen
                    editor.drawing = True
                    editor.draw_start = event.pos

            # Rechtsklick: Löschen
            elif event.button == 3:
                editor.delete_rect_at(*event.pos)

            # Mittelklick: Panning
            elif event.button == 2:
                editor.panning = True
                editor.pan_start = event.pos

            # Mausrad
            elif event.button == 4:
                editor.zoom = min(3.0, editor.zoom * 1.1)
            elif event.button == 5:
                editor.zoom = max(0.1, editor.zoom / 1.1)

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and editor.drawing:
                editor.drawing = False
                if editor.draw_start:
                    editor.add_rect(*editor.draw_start, *event.pos)
                editor.draw_start = None

            elif event.button == 2:
                editor.panning = False

        elif event.type == pygame.MOUSEMOTION:
            if editor.panning and editor.pan_start:
                dx = event.pos[0] - editor.pan_start[0]
                dy = event.pos[1] - editor.pan_start[1]
                editor.offset_x += dx
                editor.offset_y += dy
                editor.pan_start = event.pos

    # Tastatur-Bewegung
    keys = pygame.key.get_pressed()
    speed = 10
    if keys[pygame.K_LEFT]:
        editor.offset_x += speed
    if keys[pygame.K_RIGHT]:
        editor.offset_x -= speed
    if keys[pygame.K_UP]:
        editor.offset_y += speed
    if keys[pygame.K_DOWN]:
        editor.offset_y -= speed

    # Zeichnen
    editor.draw(screen)
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
print("\nEditor beendet.")
