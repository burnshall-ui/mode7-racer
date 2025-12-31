# Einstellungen für den Mode7-Renderer

# Basis-Auflösung (Original-Design)
BASE_WIDTH, BASE_HEIGHT = 400, 225

# Skalierungsfaktor für höhere Auflösungen
# 1.0 = Original (400x225), 1.6 = 640x360, 3.2 = 1280x720
RENDER_SCALE = 1.6  # Ergibt 640x360

# Fenster-Auflösung (berechnet aus Basis × Skalierung)
WIDTH = int(BASE_WIDTH * RENDER_SCALE)
HEIGHT = int(BASE_HEIGHT * RENDER_SCALE)
WIN_RES = (WIDTH, HEIGHT)
HALF_WIDTH, HALF_HEIGHT = WIDTH // 2, HEIGHT // 2

# Brennweite (skaliert proportional zur Auflösung)
BASE_FOCAL_LEN = 250
FOCAL_LEN = int(BASE_FOCAL_LEN * RENDER_SCALE)

# Default-Höhe des Horizonts für Mode7-Szenen, falls nichts anderes angegeben ist.
# Ein Viertel der Frame-Höhe hat sich in Sachen Perspektive als gut erwiesen
# (siehe z.B. das erste F-Zero auf dem Super Nintendo).
STD_HORIZON = HALF_HEIGHT // 2

# Abstand, den die Kamera per Default zum Player hält
CAM_DISTANCE = 4

# Pixel-Position, an der das Player-Sprite auf dem Screen sitzt
# wenn der Player auf dem Track fährt (d.h. nicht springt / von der Strecke fällt)
# Basis-Werte (für 400x225)
BASE_PLAYER_POSITION_X = 176
BASE_PLAYER_POSITION_Y = 120
# Skalierte Werte
NORMAL_ON_SCREEN_PLAYER_POSITION_X = int(BASE_PLAYER_POSITION_X * RENDER_SCALE)
NORMAL_ON_SCREEN_PLAYER_POSITION_Y = int(BASE_PLAYER_POSITION_Y * RENDER_SCALE)

# Scale-Faktor für die Höhe der Stage (z-Achse im virtuellen Koordinatensystem der Umgebung)
SCALE = 20

# Wie dicht der Fog in nebligen Szenen ist
FOG_DENSITY = 100

# Wie schnell sich der Background bewegt, wenn der Player rotiert
BACKGROUND_ROTATION_SPEED = 120

