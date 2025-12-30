# Generierter Code für track_settings.py
# Kopiere die passenden Rechtecke in deine Track-Funktion

# ========== STRECKE (track_surface_rects) ==========
track_1 = CollisionRect(
    pos = numpy.array([27.30, -99.80]),
    w = 13.76,
    h = 145.05
)

track_2 = CollisionRect(
    pos = numpy.array([50.74, -33.10]),
    w = 42.80,
    h = 11.34
)

track_3 = CollisionRect(
    pos = numpy.array([32.22, -162.87]),
    w = 23.29,
    h = 18.91
)

track_4 = CollisionRect(
    pos = numpy.array([51.12, -157.73]),
    w = 19.96,
    h = 8.62
)

track_5 = CollisionRect(
    pos = numpy.array([56.87, -138.14]),
    w = 8.47,
    h = 33.58
)

track_6 = CollisionRect(
    pos = numpy.array([63.52, -125.36]),
    w = 10.59,
    h = 8.02
)

track_7 = CollisionRect(
    pos = numpy.array([68.14, -91.48]),
    w = 8.32,
    h = 110.56
)

# ========== RAMPEN (ramp_rects) ==========
ramp_1 = CollisionRect(
    pos = numpy.array([68.06, -146.00]),
    w = 8.17,
    h = 1.21
)

# ========== RECOVERY ZONES (recovery_rects) ==========
recovery_1 = CollisionRect(
    pos = numpy.array([68.29, -75.29]),
    w = 3.18,
    h = 62.77
)

# ========== DASH PLATES (dash_plate_rects) ==========
dash_1 = CollisionRect(
    pos = numpy.array([32.49, -150.89]),
    w = 2.19,
    h = 2.82
)

# ========== ZIELLINIE (finish_line_collider) ==========
finish_1 = CollisionRect(
    pos = numpy.array([27.30, -116.43]),
    w = 13.16,
    h = 1.97
)

# ========== CHECKPOINTS (key_checkpoint_rects) ==========
checkpoint_1 = CollisionRect(
    pos = numpy.array([47.04, -33.17]),
    w = 23.29,
    h = 11.19
)

checkpoint_2 = CollisionRect(
    pos = numpy.array([28.66, -157.88]),
    w = 16.18,
    h = 8.92
)

# ========== STARTPOSITION (für league_settings.py) ==========
init_player_pos_x = 27.73
init_player_pos_y = -119.20
init_player_angle = 1.60  # Radians
