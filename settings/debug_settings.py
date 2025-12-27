# Debug-Modus-Einstellungen

from settings.machine_settings import MACHINES

# Ob das Spiel derzeit im "Entwicklermodus" ist, in dem die Kamera sich frei in der Szene bewegen kann
IN_DEV_MODE = False

# Ob Kollisionen mit den Streckengrenzen und Hindernissen erkannt werden (d.h. fest)
COLLISION_DETECTION_OFF = False

# Framerate, die wenn möglich erreicht werden soll
# (auch eine Obergrenze für die Framerate)
TARGET_FPS = 100

# Ob das Debug-Menü zur Auswahl einer Maschine vor Spielstart erscheint.
# Wenn auf False gesetzt, wird die Standardmaschine verwendet.
DEBUG_CHOOSE_MACHINE = False
DEFAULT_MACHINE = MACHINES[0]

# Ob das Debug-Menü zur Auswahl eines Spielmodus vor Spielstart erscheint.
# Wenn auf False gesetzt, wird der Standard-Spielmodus geladen.
DEBUG_CHOOSE_GAME_MODE = False
DEFAULT_GAME_MODE = 2 # 1: Liga-Rennen, 2: Einzelrennen
DEFAULT_SINGLE_RACE_CHOICE = 3 # 3: Event Horizon Track 2 (längste funktionierende Strecke)

# Ob es möglich sein soll, das aktuelle Rennen mit der R-Taste neu zu starten
DEBUG_RESTART_RACE_ON_R = True

# Ob Debug-Informationen in die Standardausgabe protokolliert werden sollen
SHOULD_DEBUG_LOG = False