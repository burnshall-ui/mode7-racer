# Settings for the in-race UI.

import pygame
from settings.renderer_settings import WIDTH, HEIGHT, RENDER_SCALE
from settings.machine_settings import PURPLE_COMET_MAX_SPEED # for speed display factor

# Hilfsfunktion zum Laden und Skalieren von UI-Sprites
def load_scaled_ui_image(path):
    """Lädt ein UI-Bild und skaliert es entsprechend RENDER_SCALE."""
    img = pygame.image.load(path)
    if RENDER_SCALE != 1.0:
        new_width = int(img.get_width() * RENDER_SCALE)
        new_height = int(img.get_height() * RENDER_SCALE)
        img = pygame.transform.scale(img, (new_width, new_height))
    return img

# UI screen coordinates

# speed meter (Basis-Werte skaliert)
BASE_DIGIT_SPRITE_WIDTH = 16
BASE_DIGIT_SPRITE_HEIGHT = 16
SPEED_METER_DIGIT_SPRITE_WIDTH = int(BASE_DIGIT_SPRITE_WIDTH * RENDER_SCALE)
SPEED_METER_DIGIT_SPRITE_HEIGHT = int(BASE_DIGIT_SPRITE_HEIGHT * RENDER_SCALE)
RIGHT_MOST_SPEEDMETER_DIGIT_SCREEN_X_COORD = WIDTH - SPEED_METER_DIGIT_SPRITE_WIDTH
SPEED_METER_DIGIT_SCREEN_Y_COORD = HEIGHT - 1.5 * SPEED_METER_DIGIT_SPRITE_HEIGHT # no padding in sprite so we add one of 12px in code

# energy meter
NUM_TIMER_DIGITS = 7 # some timer-related variables need to be defined here since timer and energy bar are aligned
TIMER_DIGIT_SPRITE_WIDTH = SPEED_METER_DIGIT_SPRITE_WIDTH
RIGHT_MOST_TIMER_DIGIT_SCREEN_X_COORD = WIDTH - TIMER_DIGIT_SPRITE_WIDTH
ENERGY_METER_HEIGHT = int(16 * RENDER_SCALE)
ENERGY_METER_TOP_Y = int(4 * RENDER_SCALE) # offset of the energy meter from the top of the screen
ENERGY_METER_LEFT_X = RIGHT_MOST_TIMER_DIGIT_SCREEN_X_COORD - TIMER_DIGIT_SPRITE_WIDTH * NUM_TIMER_DIGITS

# timer

TIMER_DIGIT_SPRITE_HEIGHT = SPEED_METER_DIGIT_SPRITE_HEIGHT
TIMER_DIGIT_SCREEN_Y_COORD = ENERGY_METER_TOP_Y + ENERGY_METER_HEIGHT # timer should be right below the shield meter
TIMER_PADDING = TIMER_DIGIT_SPRITE_WIDTH / 2 # padding between minutes and seconds, seconds and milliseconds
# Computes the individual x offset for the timer digits
# (note that there are gaps 
# between the digits for the minutes and seconds + seconds and milliseconds)
def TIMER_DIGIT_X_OFFSET(i):
    if i <= 2: # milliseconds digits
        return RIGHT_MOST_TIMER_DIGIT_SCREEN_X_COORD - TIMER_DIGIT_SPRITE_WIDTH * i
    if i > 2 and i <= 4: # seconds digits
        return RIGHT_MOST_TIMER_DIGIT_SCREEN_X_COORD - TIMER_DIGIT_SPRITE_WIDTH * i - TIMER_PADDING
    return RIGHT_MOST_TIMER_DIGIT_SCREEN_X_COORD - TIMER_DIGIT_SPRITE_WIDTH * i - TIMER_PADDING * 2 # minute digits

# end of UI screen coordinates

# other UI configuration
SPEED_DISPLAY_MULTIPLIER = 1426 / PURPLE_COMET_MAX_SPEED # so max speed of Purple Comet will be shown as 1426 km/h



# Game Over Overlay Einstellungen
GAME_OVER_OVERLAY_ALPHA = 180  # Transparenz des dunklen Overlays (0-255)
GAME_OVER_IMAGE = load_scaled_ui_image('gfx/ui/game_over.png')
PRESS_SPACE_IMAGE = load_scaled_ui_image('gfx/ui/press_space.png')

# standard paths for the number sprites used in the game
NUMBER_IMAGES = [ # index = pictured number
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