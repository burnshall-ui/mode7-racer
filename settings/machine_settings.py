# Einstellungen für die Maschinen, die im Spiel steuerbar sind.

import pygame
from machine import Machine
from animation import Animation
from settings.renderer_settings import RENDER_SCALE

# Hilfsfunktion zum Laden und Skalieren von Sprites
def load_scaled_image(path):
    """Lädt ein Bild und skaliert es entsprechend RENDER_SCALE."""
    img = pygame.image.load(path)
    if RENDER_SCALE != 1.0:
        new_width = int(img.get_width() * RENDER_SCALE)
        new_height = int(img.get_height() * RENDER_SCALE)
        img = pygame.transform.scale(img, (new_width, new_height))
    return img

# Physik-Variablen der Spieler-Maschine
PLAYER_COLLISION_RECT_WIDTH = 1 # Breite des Spieler-Kollisions-Rechtecks (gleich für alle Maschinen)
PLAYER_COLLISION_RECT_HEIGHT = 1 # Höhe des Spieler-Kollisions-Rechtecks
BASE_JUMP_HEIGHT = 100 # Maximale Höhe, die der Spieler während eines Sprungs erreicht (Basis-Wert)
JUMP_HEIGHT = int(BASE_JUMP_HEIGHT * RENDER_SCALE) # skalierte Sprunghöhe
OBSTACLE_HIT_SPEED_RETENTION = 0.5 # Prozentsatz der Geschwindigkeit, den die Spieler-Maschine beim Aufprall auf ein Hindernis behält
MIN_BOUNCE_BACK_FORCE = 0.005 # Minimale Kraft, die in entgegengesetzter Richtung angewendet wird, wenn der Spieler gegen eine Wand prallt (um zu verhindern, dass der Spieler knapp außerhalb der Streckengrenzen stecken bleibt)

# Geschwindigkeits-Skalierung (1.0 = Original, 0.8 = 80%)
# Auf 1.1 erhöht für gutes Speed-Gefühl (sweet spot!)
SPEED_SCALE = 1.1

# Referenzwerte für Maschinen-Statistiken
PURPLE_COMET_ACCELERATION = (5000 / 750) * SPEED_SCALE
PURPLE_COMET_MAX_SPEED = 25 * SPEED_SCALE

# Maximale Energie, die eine Maschine normalerweise hat
STD_MAX_ENERGY = 100

# Faktor, der verwendet wird, um die Menge an Energie zu berechnen,
# die die Maschine beim Aufprall auf ein normales Hindernis verliert,
# basierend auf der aktuellen Geschwindigkeit des Spielers.
# Idee: Bei einer Geschwindigkeit von 1426 km/h (Höchstgeschwindigkeit des Purple Comet, 0.05 in den Interna der Physik-Engine)
# würde eine Maschine normalerweise 5 Energieleinheiten verlieren
# (ohne die individuelle Schildstärke der Maschine anzuwenden (Machine.hit_cost)).
HIT_COST_SPEED_FACTOR = 5 / PURPLE_COMET_MAX_SPEED

# Quadratische Funktion, die die Höhe des Spielers während eines Sprungs berechnet,
# basierend auf der Zeit seit dem Sprung von der Strecke.
# 
# Parameter:
# time: Zeit seit dem Abheben des Spielers (in Sekunden)
# jump_duration: die Dauer des gesamten Sprungs vom Start bis zur Landung
def HEIGHT_DURING_JUMP(time, jump_duration):
    return - ( time * ( time - jump_duration ) ) * JUMP_HEIGHT

# Geschwindigkeit der Animationen der Maschinen
DRIVING_ANIM_SPEED = 12
IDLE_ANIM_SPEED = 12

# Maschinen, die im Spiel spielbar sind

PURPLE_COMET_GRAPHICS_ROOT_PATH = "gfx/machines/purple_comet/"

PURPLE_COMET_SHADOW_IMAGE_PATH = PURPLE_COMET_GRAPHICS_ROOT_PATH + "violet_machine_shadow.png"

PURPLE_COMET_DRIVING_ANIMATION = Animation(
    frames = [
        load_scaled_image(PURPLE_COMET_GRAPHICS_ROOT_PATH + "violet_machine0001.png"),
        load_scaled_image(PURPLE_COMET_GRAPHICS_ROOT_PATH + "violet_machine0002.png"),
        load_scaled_image(PURPLE_COMET_GRAPHICS_ROOT_PATH + "violet_machine0003.png"),
        load_scaled_image(PURPLE_COMET_GRAPHICS_ROOT_PATH + "violet_machine0004.png")
    ],
    speed = DRIVING_ANIM_SPEED
)

PURPLE_COMET_IDLE_ANIMATION = Animation(
    frames = [
        load_scaled_image(PURPLE_COMET_GRAPHICS_ROOT_PATH + "violet_machine0000.png")
    ],
    speed = IDLE_ANIM_SPEED
)

PURPLE_COMET = Machine(
    max_speed = PURPLE_COMET_MAX_SPEED,
    boosted_max_speed = PURPLE_COMET_MAX_SPEED * 1.4,
    acceleration = PURPLE_COMET_ACCELERATION, # 750 Frame-Update-Einheiten, um Höchstgeschwindigkeit zu erreichen
    boosted_acceleration = PURPLE_COMET_ACCELERATION * 10,
    brake = PURPLE_COMET_ACCELERATION * 2, # Bremse ist doppelt so stark wie der Beschleuniger
    speed_loss = PURPLE_COMET_ACCELERATION / 3, # Geschwindigkeitsverlust ist ein Drittel der Stärke des Beschleunigers
    boosted_speed_loss = PURPLE_COMET_ACCELERATION * 6,
    max_centri = 20, 
    centri_increase = 10,
    centri_decrease = 50,
    jump_duration_multiplier = 2 / PURPLE_COMET_MAX_SPEED, # Sprung sollte 2 Sekunden dauern, wenn Maschine bei Höchstgeschwindigkeit ist
    boost_duration = 2,
    max_energy = STD_MAX_ENERGY,
    boost_cost = 19,
    hit_cost = 1,
    recover_speed = 13,
    rotation_speed = 2.5,
    idle_anim = PURPLE_COMET_IDLE_ANIMATION,
    driving_anim = PURPLE_COMET_DRIVING_ANIMATION,
    shadow_image_path = PURPLE_COMET_SHADOW_IMAGE_PATH
)

FASTER_PURPLE_COMET = Machine(
    max_speed = PURPLE_COMET.max_speed * 1.1,
    boosted_max_speed = PURPLE_COMET.max_speed * 1.4,
    acceleration = PURPLE_COMET.acceleration / 2,
    boosted_acceleration = PURPLE_COMET.boosted_acceleration,
    brake = PURPLE_COMET.brake,
    speed_loss = PURPLE_COMET.speed_loss / 2,
    boosted_speed_loss = PURPLE_COMET.boosted_speed_loss / 20,
    max_centri = PURPLE_COMET.max_centri,
    centri_increase = PURPLE_COMET.centri_increase,
    centri_decrease = PURPLE_COMET.centri_decrease,
    jump_duration_multiplier = PURPLE_COMET.jump_duration_multiplier,
    boost_duration = 1.75,
    max_energy = STD_MAX_ENERGY,
    boost_cost = 14,
    hit_cost = 0.5,
    recover_speed = PURPLE_COMET.recover_speed / 2,
    rotation_speed = PURPLE_COMET.rotation_speed * 0.75,
    idle_anim = PURPLE_COMET_IDLE_ANIMATION,
    driving_anim = PURPLE_COMET_DRIVING_ANIMATION,
    shadow_image_path = PURPLE_COMET_SHADOW_IMAGE_PATH
)

SLOWER_PURPLE_COMET = Machine(
    max_speed = PURPLE_COMET.max_speed * 0.9,
    boosted_max_speed = PURPLE_COMET.max_speed * 1.5, # starker Booster
    acceleration = PURPLE_COMET.acceleration * 2,
    boosted_acceleration = PURPLE_COMET.boosted_acceleration,
    brake = PURPLE_COMET.brake,
    speed_loss = PURPLE_COMET.speed_loss,
    boosted_speed_loss = PURPLE_COMET.boosted_speed_loss,
    boost_duration = 1,
    max_energy = STD_MAX_ENERGY,
    boost_cost = 22,
    hit_cost = 2,
    recover_speed = PURPLE_COMET.recover_speed * 2,
    max_centri = PURPLE_COMET.max_centri * 2,
    centri_increase = PURPLE_COMET.centri_increase * 1.5,
    centri_decrease = PURPLE_COMET.centri_decrease * 1.5,
    jump_duration_multiplier = PURPLE_COMET.jump_duration_multiplier,
    rotation_speed = PURPLE_COMET.rotation_speed * 1.3,
    idle_anim = PURPLE_COMET_IDLE_ANIMATION,
    driving_anim = PURPLE_COMET_DRIVING_ANIMATION,
    shadow_image_path = PURPLE_COMET_SHADOW_IMAGE_PATH
)

MACHINES = [PURPLE_COMET, FASTER_PURPLE_COMET, SLOWER_PURPLE_COMET]