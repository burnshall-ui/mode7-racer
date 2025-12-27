# Settings for the Mode7 renderer

# Basis-Auflösung (Original-Design)
BASE_WIDTH, BASE_HEIGHT = 400, 225

# Skalierungsfaktor für höhere Auflösungen
# 1.0 = Original (400x225), 1.6 = 640x360, 3.2 = 1280x720
RENDER_SCALE = 1.6  # Ergibt 640x360

# Window resolution (berechnet aus Basis × Skalierung)
WIDTH = int(BASE_WIDTH * RENDER_SCALE)
HEIGHT = int(BASE_HEIGHT * RENDER_SCALE)
WIN_RES = (WIDTH, HEIGHT)
HALF_WIDTH, HALF_HEIGHT = WIDTH // 2, HEIGHT // 2

# Focal length (skaliert proportional zur Auflösung)
BASE_FOCAL_LEN = 250
FOCAL_LEN = int(BASE_FOCAL_LEN * RENDER_SCALE)

# The default height of the horizon for mode-7 scenes if none else is specified.
# Choosing a quarter of the height of the frame has proven to be good in terms of perspective
# (consider the first F-Zero game on the Super Nintendo as an example).
STD_HORIZON = HALF_HEIGHT // 2

# the distance that the camera keeps from the player by default
CAM_DISTANCE = 4

# the pixel position that the player sprite has on the screen
# when the player is driving on the track (i.e. not jumping/falling off)
# Basis-Werte (für 400x225)
BASE_PLAYER_POSITION_X = 176
BASE_PLAYER_POSITION_Y = 120
# Skalierte Werte
NORMAL_ON_SCREEN_PLAYER_POSITION_X = int(BASE_PLAYER_POSITION_X * RENDER_SCALE)
NORMAL_ON_SCREEN_PLAYER_POSITION_Y = int(BASE_PLAYER_POSITION_Y * RENDER_SCALE)

# scale factor for height of the stage (z axis in virtual coordinate system of environment)
SCALE = 20

# how dense the fog is in foggy scenes
FOG_DENSITY = 100

# how fast the background moves when the player rotates
BACKGROUND_ROTATION_SPEED = 120

