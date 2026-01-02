# Einstellungen für die UI während des Rennens.

import pygame
from settings.renderer_settings import WIDTH, HEIGHT, RENDER_SCALE
from settings.machine_settings import PURPLE_COMET_MAX_SPEED # für Geschwindigkeitsanzeigefaktor

# Hilfsfunktion zum Laden und Skalieren von UI-Sprites
def load_scaled_ui_image(path):
    """Lädt ein UI-Bild und skaliert es entsprechend RENDER_SCALE."""
    img = pygame.image.load(path)
    if RENDER_SCALE != 1.0:
        new_width = int(img.get_width() * RENDER_SCALE)
        new_height = int(img.get_height() * RENDER_SCALE)
        img = pygame.transform.scale(img, (new_width, new_height))
    return img

# UI-Bildschirmkoordinaten

# Geschwindigkeitsmesser (Basis-Werte skaliert)
BASE_DIGIT_SPRITE_WIDTH = 16
BASE_DIGIT_SPRITE_HEIGHT = 16
SPEED_METER_DIGIT_SPRITE_WIDTH = int(BASE_DIGIT_SPRITE_WIDTH * RENDER_SCALE)
SPEED_METER_DIGIT_SPRITE_HEIGHT = int(BASE_DIGIT_SPRITE_HEIGHT * RENDER_SCALE)
RIGHT_MOST_SPEEDMETER_DIGIT_SCREEN_X_COORD = WIDTH - SPEED_METER_DIGIT_SPRITE_WIDTH
SPEED_METER_DIGIT_SCREEN_Y_COORD = HEIGHT - 1.5 * SPEED_METER_DIGIT_SPRITE_HEIGHT # kein Padding im Sprite, daher fügen wir eines von 12px im Code hinzu

# Energiemesser
NUM_TIMER_DIGITS = 7 # Einige Timer-bezogene Variablen müssen hier definiert werden, da Timer und Energieleiste ausgerichtet sind
TIMER_DIGIT_SPRITE_WIDTH = SPEED_METER_DIGIT_SPRITE_WIDTH
RIGHT_MOST_TIMER_DIGIT_SCREEN_X_COORD = WIDTH - TIMER_DIGIT_SPRITE_WIDTH
ENERGY_METER_HEIGHT = int(16 * RENDER_SCALE)
ENERGY_METER_TOP_Y = int(4 * RENDER_SCALE) # Versatz des Energiemessers von der Oberseite des Bildschirms
ENERGY_METER_LEFT_X = RIGHT_MOST_TIMER_DIGIT_SCREEN_X_COORD - TIMER_DIGIT_SPRITE_WIDTH * NUM_TIMER_DIGITS

# Timer

TIMER_DIGIT_SPRITE_HEIGHT = SPEED_METER_DIGIT_SPRITE_HEIGHT
TIMER_DIGIT_SCREEN_Y_COORD = ENERGY_METER_TOP_Y + ENERGY_METER_HEIGHT # Timer sollte direkt unter dem Schildmesser sein
TIMER_PADDING = TIMER_DIGIT_SPRITE_WIDTH / 2 # Padding zwischen Minuten und Sekunden, Sekunden und Millisekunden
# Berechnet den individuellen x-Versatz für die Timer-Ziffern
# (beachten, dass es Lücken
# zwischen den Ziffern für Minuten und Sekunden + Sekunden und Millisekunden gibt)
def TIMER_DIGIT_X_OFFSET(i):
    if i <= 2: # Millisekunden-Ziffern
        return RIGHT_MOST_TIMER_DIGIT_SCREEN_X_COORD - TIMER_DIGIT_SPRITE_WIDTH * i
    if i > 2 and i <= 4: # Sekunden-Ziffern
        return RIGHT_MOST_TIMER_DIGIT_SCREEN_X_COORD - TIMER_DIGIT_SPRITE_WIDTH * i - TIMER_PADDING
    return RIGHT_MOST_TIMER_DIGIT_SCREEN_X_COORD - TIMER_DIGIT_SPRITE_WIDTH * i - TIMER_PADDING * 2 # Minuten-Ziffern

# Ende der UI-Bildschirmkoordinaten

# Andere UI-Konfiguration
SPEED_DISPLAY_MULTIPLIER = 1426 / PURPLE_COMET_MAX_SPEED # damit die Maximalgeschwindigkeit von Purple Comet als 1426 km/h angezeigt wird



# Game Over Overlay Einstellungen
GAME_OVER_OVERLAY_ALPHA = 180  # Transparenz des dunklen Overlays (0-255)
GAME_OVER_IMAGE = load_scaled_ui_image('gfx/ui/game_over.png')
PRESS_SPACE_IMAGE = load_scaled_ui_image('gfx/ui/press_space.png')

# Finish Screen Einstellungen
FINISH_OVERLAY_ALPHA = 200  # Transparenz des dunklen Overlays (0-255)

# Font für Text-Rendering (wird beim ersten Gebrauch initialisiert)
_font_cache = {}
def get_pixel_font(size):
    """Gibt einen Pixel-Style Font zurück (gecached)"""
    if size not in _font_cache:
        # Versuche einen Pixel-Font zu laden, fallback zu Default
        try:
            _font_cache[size] = pygame.font.Font(None, size)
        except:
            _font_cache[size] = pygame.font.SysFont('courier', size)
    return _font_cache[size]

# Standardpfade für die im Spiel verwendeten Zahlen-Sprites
NUMBER_IMAGES = [ # Index = dargestellte Zahl
    load_scaled_ui_image('gfx/numbers/small_numbers0.png'),
    load_scaled_ui_image('gfx/numbers/small_numbers1.png'),
    load_scaled_ui_image('gfx/numbers/small_numbers2.png'),
    load_scaled_ui_image('gfx/numbers/small_numbers3.png'),
    load_scaled_ui_image('gfx/numbers/small_numbers4.png'),
    load_scaled_ui_image('gfx/numbers/small_numbers5.png'),
    load_scaled_ui_image('gfx/numbers/small_numbers6.png'),
    load_scaled_ui_image('gfx/numbers/small_numbers7.png'),
    load_scaled_ui_image('gfx/numbers/small_numbers8.png'),
    load_scaled_ui_image('gfx/numbers/small_numbers9.png'),
]

# ---------------- Mini-Map (unten links) ----------------
#
# Idee: Du kannst pro Strecke eine kleine Minimap als Bild zeichnen.
# Konvention (Standard):
# - `gfx/ui/minimaps/<floor_texture_basename>_minimap.png`
#   Beispiel: Floor-Textur `gfx/event_horizon_track2.png` -> `gfx/ui/minimaps/event_horizon_track2_minimap.png`
#
# Wenn kein Bild gefunden wird, rendert das Spiel eine einfache Fallback-Minimap aus den Kollisions-Rechtecken.

MINIMAP_ENABLED = True

# Abstand der Minimap zum Bildschirmrand
MINIMAP_MARGIN_LEFT = int(8 * RENDER_SCALE)
MINIMAP_MARGIN_BOTTOM = int(8 * RENDER_SCALE)

# Falls kein Minimap-Bild existiert: diese Größe wird verwendet
MINIMAP_FALLBACK_SIZE = (int(64 * RENDER_SCALE), int(64 * RENDER_SCALE))

# Soll die Minimap (falls vorhanden) mit RENDER_SCALE skaliert werden?
# - True: Zeichne Minimap einmal in Basis-Auflösung, sie skaliert automatisch mit.
# - False: Minimap-Datei ist bereits in der finalen Pixelgröße.
MINIMAP_SCALE_WITH_RENDER_SCALE = True

# Zusätzliche Skalierung der Mini-Map bei der Anzeige
# 1.0 = original, 0.9 = 10% kleiner
MINIMAP_DISPLAY_SCALE = 0.75

# Zusätzliche Skalierung für den Marker (Punkt + Richtung)
# 1.0 = original, 0.9 = 10% kleiner
MINIMAP_MARKER_SCALE = 1.0

# Wenn False: kein Richtungs-Strich (nur Punkt)
MINIMAP_SHOW_HEADING = False

# Wenn True: Marker wird auf die „Mittellinie“ des aktuellen Strecken-Segments projiziert,
# damit er keine seitlichen Abweichungen (links/rechts) darstellt, sondern primär den Fortschritt entlang der Strecke.
MINIMAP_MARKER_CLAMP_TO_TRACK_CENTER = True

# Pfad-Konvention für Minimap-Bilder
MINIMAP_IMAGE_DIR = 'gfx/ui/minimaps'
MINIMAP_IMAGE_SUFFIX = '_minimap'

# Optional: Weltkoordinaten-Bounds leicht vergrößern (in Welt-Einheiten),
# damit der Marker nicht am Rand „klebt“ und etwas Padding vorhanden ist.
MINIMAP_WORLD_PADDING = 0.0

# Farben/Style
MINIMAP_BG_COLOR = (0, 0, 0)
MINIMAP_BG_ALPHA = 0
MINIMAP_BORDER_COLOR = (230, 230, 230)
MINIMAP_BORDER_WIDTH = max(1, int(2 * RENDER_SCALE))

MINIMAP_TRACK_COLOR = (190, 190, 190)
MINIMAP_TRACK_ALPHA = 255
MINIMAP_FINISH_COLOR = (255, 80, 80)
MINIMAP_FINISH_ALPHA = 220

MINIMAP_PLAYER_COLOR = (255, 240, 80)
MINIMAP_PLAYER_OUTLINE_COLOR = (20, 20, 20)
MINIMAP_PLAYER_RADIUS = max(2, int(2 * RENDER_SCALE))
MINIMAP_HEADING_LENGTH = max(6, int(10 * RENDER_SCALE))