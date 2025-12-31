# Einstellungen für die Race-Tracks und ihre Collision-Maps.

import numpy # numpy-Arrays für Positionen von Rechteck-Collidern
from collision import CollisionRect
from track import Track, KeyCheckpoint 

# Race-Konfiguration
STD_REQUIRED_LAPS = 3 # Anzahl Runden, die normalerweise nötig sind, um ein Race zu beenden

# Hindernis-Größen für "Prefab"-Obstacles
DASH_PLATE_HEIGHT = 1.5
DASH_PLATE_WIDTH = 1.5

# Eine Klasse, die die Erstellung der Objekte kapselt, die die Race-Tracks im Speicher repräsentieren,
# um das Hauptmodul nicht zu überladen.
#
# Enthält mehrere statische Methoden, um die verschiedenen Tracks zu erzeugen.
class TrackCreator:
    # Erstellt die Collision-Shape für den Track, dessen Sprite "track_2023.png" heißt
    def create_track_2023():
        # Track-Collider erstellen

        # linkestes Rect
        rect1 = CollisionRect(
            pos = numpy.array([27.165, -99.615]),
            w = 14.33,
            h = 144.77
        )

        # Rect neben rect1 (an dessen unterem Ende)
        rect2 = CollisionRect(
            pos = numpy.array([39.17, -162.635]),
            w = 9.68,
            h = 18.73
        )

        # unterstes horizontales Rect
        rect3 = CollisionRect(
            pos = numpy.array([47.815, -157.725]),
            w = 26.97,
            h = 8.91
        )

        # zweites vertikales Rect von rechts
        rect4 = CollisionRect(
            pos = numpy.array([56.925, -142.14]),
            w = 8.69,
            h = 40.08
        )

        # mittleres horizontales Rect
        rect5 = CollisionRect(
            pos = numpy.array([62.385, -125.59]),
            w = 19.55,
            h = 8.98
        )

        # rechtestes vertikales Rect
        rect6 = CollisionRect(
            pos = numpy.array([67.95, -86.495]),
            w = 8.42,
            h = 118.53
        )

        # oberstes horizontales Rect
        rect7 = CollisionRect(
            pos = numpy.array([46.08, -33.24]),
            w = 52.16,
            h = 11.86
        )

        # Ende der Track-Collider-Erstellung

        # Ziellinien-Collider
        finish_line_coll = CollisionRect(
            pos = numpy.array([27.165, -116.6325]),
            w = 14.33,
            h = 1.145
        )

        # (die einzige) Sprungrampe
        ramp1 = CollisionRect(
            pos = numpy.array([67.95, -145.82]),
            w = 8.42,
            h = 0.12
        )

        # (die einzige) Dash-Plate
        dash_plate1 = CollisionRect(
            pos = numpy.array([32.4, -150.965]),
            w = DASH_PLATE_WIDTH,
            h = DASH_PLATE_HEIGHT
        )

        # (die einzige) Recovery-Zone
        recovery_zone_1 = CollisionRect(
            pos = numpy.array([67.99, -75.64]),
            w = 2.28,
            h = 61.54
        )

        return Track(
            name = "track 2023",
            track_surface_rects = [rect1, rect2, rect3, rect4, rect5, rect6, rect7],
            key_checkpoint_rects = [rect7, rect5],
            ramp_rects = [ramp1],
            finish_line_collider = finish_line_coll,
            dash_plate_rects = [dash_plate1],
            recovery_rects = [recovery_zone_1],
            has_guard_rails = True
        )

    # Vorerst ist das nur ein leerer Track mit gesetzter monochromer Environment-Textur
    def create_monochrome_track():
        finish_line_coll = CollisionRect(
            pos = numpy.array([1127.165, -116.6325]),
            w = 14.33,
            h = 1.145
        )

        track_surface = CollisionRect(
            pos = numpy.array([27.165, -116.6325]),
            w = 10000,
            h = 10000
        )

        return Track(
            name = "monochrome_track",
            track_surface_rects = [track_surface],
            key_checkpoint_rects = [],
            ramp_rects = [],
            finish_line_collider = finish_line_coll,
            dash_plate_rects = [],
            recovery_rects = [],
            has_guard_rails = False
        )

    # Erstellt die Collision-Shape für den Track, dessen Sprite "track_2023_II.png" heißt.
    # Vorerst ist das nur die Collision-Shape des ersten Tracks (für Testzwecke).
    def create_track_2023_II():
        # ------------ Track-Collider erstellen ----------------------

        # ------------ Rects aus der ersten Track-Version übernommen ----

        # oberstes linkes Rect
        rect1 = CollisionRect(
            pos = numpy.array([27.165, -99.615]),
            w = 14.33,
            h = 144.77
        )

        # Rect neben rect1 (an dessen unterem Ende)
        rect2 = CollisionRect(
            pos = numpy.array([39.17, -162.635]),
            w = 9.68,
            h = 18.73
        )

        # zweitunterstes horizontales Rect
        rect3 = CollisionRect(
            pos = numpy.array([47.815, -157.725]),
            w = 26.97,
            h = 8.91
        )

        # zweites vertikales Rect von rechts
        rect4 = CollisionRect(
            pos = numpy.array([56.925, -142.14]),
            w = 8.69,
            h = 40.08
        )

        # drittunterstes horizontales Rect
        rect5 = CollisionRect(
            pos = numpy.array([62.385, -125.59]),
            w = 19.55,
            h = 8.98
        )

        # oberstes horizontales Rect
        rect7 = CollisionRect(
            pos = numpy.array([46.08, -33.24]),
            w = 52.16,
            h = 11.86
        )

        # ------------ Ende der übernommenen Rects aus der ersten Track-Version ----

        # oberstes rechtes vertikales Rect
        rect8 = CollisionRect(
            pos = numpy.array([67.95, -45.725]),
            w = 8.42,
            h = 36.99
        )

        # unterstes rechtes vertikales Rect
        rect9 = CollisionRect(
            pos = numpy.array([67.95, -147.03]),
            w = 8.42,
            h = 97.135
        )

        # unterstes horizontales Rect
        rect10 = CollisionRect(
            pos = numpy.array([46.08, -191.55]),
            w = 52.16,
            h = 8.105
        )

        # unterstes linkes vertikales Rect
        rect11 = CollisionRect(
            pos = numpy.array([27.165, -186.8]),
            w = 14.33,
            h = 17.605
        )

        # zweitoberstes horizontales Rect
        rect12 = CollisionRect(
            pos = numpy.array([56.43, -60.21]),
            w = 31.42,
            h = 8.01
        )

        # vertikales Rect, das Rect 12 und 14 verbindet
        rect13 = CollisionRect(
            pos = numpy.array([44.82, -81.24]),
            w = 8.2,
            h = 50.06
        )

        # drittoberstes horizontales Rect
        rect14 = CollisionRect(
            pos = numpy.array([56.43, -102.47]),
            w = 31.42,
            h = 8.01
        )

        # ------------ Ende der Track-Collider-Erstellung -------------------------

        # ------------ Dash-Plate-Collider erstellen ---------------------------

        # erste Dash-Plate (in der Reihenfolge der Begegnung in einer normalen Runde)
        dash_plate1 = CollisionRect(
            pos = numpy.array([65.265, -136.89]),
            w = DASH_PLATE_WIDTH,
            h = DASH_PLATE_HEIGHT
        )

        # zweite Dash-Plate (in der Reihenfolge der Begegnung in einer normalen Runde)
        dash_plate2 = CollisionRect(
            pos = numpy.array([70.756, -166.1]),
            w = DASH_PLATE_WIDTH,
            h = DASH_PLATE_HEIGHT
        )

        # dritte Dash-Plate (in der Reihenfolge der Begegnung in einer normalen Runde)
        dash_plate3 = CollisionRect(
            pos = numpy.array([60.17, -188.88]),
            w = DASH_PLATE_WIDTH,
            h = DASH_PLATE_HEIGHT
        )

        # vierte Dash-Plate (in der Reihenfolge der Begegnung in einer normalen Runde)
        dash_plate4 = CollisionRect(
            pos = numpy.array([39.89, -194.165]),
            w = DASH_PLATE_WIDTH,
            h = DASH_PLATE_HEIGHT
        )

        # linkeste der drei Dash-Plates vor der kleinen Lücke
        dash_plate_left = CollisionRect(
            pos = numpy.array([22.6, -179.17]),
            w = DASH_PLATE_WIDTH,
            h = DASH_PLATE_HEIGHT
        )

        # mittlere der drei Dash-Plates vor der kleinen Lücke
        dash_plate_middle = CollisionRect(
            pos = numpy.array([25.235, -179.17]),
            w = DASH_PLATE_WIDTH,
            h = DASH_PLATE_HEIGHT
        )

        # rechteste der drei Dash-Plates vor der kleinen Lücke
        dash_plate_right = CollisionRect(
            pos = numpy.array([28, -179.17]),
            w = DASH_PLATE_WIDTH,
            h = DASH_PLATE_HEIGHT
        )

        # ------------ Ende der Dash-Plate-Collider-Erstellung ---------------------------

        # Ziellinien-Collider
        finish_line_coll = CollisionRect(
            pos = numpy.array([27.165, -116.6325]),
            w = 14.33,
            h = 1.145
        )

        # (die einzige) Sprungrampe
        ramp1 = CollisionRect(
            pos = numpy.array([27.165, -177.94]),
            w = 8.42,
            h = 0.12
        )

        # (die einzige) Recovery-Zone
        recovery_zone_1 = CollisionRect(
            pos = numpy.array([56.81, -141.72]),
            w = 6.8,
            h = 24.21
        )

        return Track(
            name = "track 2023 II",
            track_surface_rects = [rect1, rect2, rect3, rect4, rect5, rect7, rect8, rect9, rect10, rect11, rect12, rect13, rect14],
            key_checkpoint_rects = [rect7, rect5],
            ramp_rects = [ramp1],
            finish_line_collider = finish_line_coll,
            dash_plate_rects = [dash_plate1, dash_plate2, dash_plate3, dash_plate4, dash_plate_left, dash_plate_middle, dash_plate_right],
            recovery_rects = [recovery_zone_1],
            has_guard_rails = True
        )

    # Event Horizon I - Generiert mit Map Editor
    def create_event_horizon_track2():
        # ========== STRECKE ==========
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

        # ========== RAMPEN ==========
        ramp_1 = CollisionRect(
            pos = numpy.array([68.06, -146.00]),
            w = 8.17,
            h = 1.21
        )

        # ========== RECOVERY-ZONEN ==========
        recovery_1 = CollisionRect(
            pos = numpy.array([68.29, -75.29]),
            w = 3.18,
            h = 62.77
        )

        # ========== DASH-PLATES ==========
        dash_1 = CollisionRect(
            pos = numpy.array([32.49, -150.89]),
            w = 2.19,
            h = 2.82
        )

        # ========== ZIELLINIE ==========
        finish_1 = CollisionRect(
            pos = numpy.array([27.30, -116.43]),
            w = 13.16,
            h = 1.97
        )

        # ========== CHECKPOINTS ==========
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

        return Track(
            name = "Event Horizon I",
            track_surface_rects = [track_1, track_2, track_3, track_4, track_5, track_6, track_7],
            key_checkpoint_rects = [checkpoint_1, checkpoint_2],
            ramp_rects = [ramp_1],
            finish_line_collider = finish_1,
            dash_plate_rects = [dash_1],
            recovery_rects = [recovery_1],
            has_guard_rails = True
        )

    # Speed-Test Oval-Strecke mit Sprung-oder-umfahren Feature
    # Vereinfachte Version mit breiten, überlappenden Rechtecken
    def create_speed_oval():
        track_width = 25  # Breitere Strecke für besseres Fahrgefühl

        # -------------- Linke lange Gerade --------------
        left_straight = CollisionRect(
            pos = numpy.array([40, -200]),
            w = track_width,
            h = 320
        )

        # -------------- Untere Kurve (großes überlappenes Rechteck) --------------
        bottom_curve = CollisionRect(
            pos = numpy.array([100, -355]),
            w = 145,
            h = 30
        )

        # -------------- Rechte lange Gerade --------------
        right_straight = CollisionRect(
            pos = numpy.array([170, -200]),
            w = track_width,
            h = 320
        )

        # Sprung-Sektion auf der rechten Geraden
        jump_section = CollisionRect(
            pos = numpy.array([170, -150]),
            w = track_width,
            h = 40
        )

        # Umweg rechts daneben
        detour_section = CollisionRect(
            pos = numpy.array([205, -150]),
            w = 45,
            h = 40
        )

        # -------------- Obere Kurve (großes überlappenes Rechteck) --------------
        top_curve = CollisionRect(
            pos = numpy.array([105, -45]),
            w = 155,
            h = 30
        )

        # -------------- Ziellinie --------------
        finish_line_coll = CollisionRect(
            pos = numpy.array([40, -100]),
            w = track_width,
            h = 2
        )

        # -------------- Rampe für Sprung-Feature --------------
        jump_ramp = CollisionRect(
            pos = numpy.array([170, -165]),
            w = track_width,
            h = 0.5
        )

        # -------------- Dash-Plates --------------
        # Untere Kurve
        dash_1 = CollisionRect(
            pos = numpy.array([80, -355]),
            w = DASH_PLATE_WIDTH,
            h = DASH_PLATE_HEIGHT
        )

        dash_2 = CollisionRect(
            pos = numpy.array([120, -355]),
            w = DASH_PLATE_WIDTH,
            h = DASH_PLATE_HEIGHT
        )

        # Obere Kurve
        dash_3 = CollisionRect(
            pos = numpy.array([85, -45]),
            w = DASH_PLATE_WIDTH,
            h = DASH_PLATE_HEIGHT
        )

        dash_4 = CollisionRect(
            pos = numpy.array([125, -45]),
            w = DASH_PLATE_WIDTH,
            h = DASH_PLATE_HEIGHT
        )

        # Vor dem Sprung
        dash_5 = CollisionRect(
            pos = numpy.array([170, -180]),
            w = DASH_PLATE_WIDTH,
            h = DASH_PLATE_HEIGHT
        )

        # Linke Gerade
        dash_6 = CollisionRect(
            pos = numpy.array([40, -250]),
            w = DASH_PLATE_WIDTH,
            h = DASH_PLATE_HEIGHT
        )

        # -------------- Recovery-Zone im Umweg --------------
        recovery_zone = CollisionRect(
            pos = numpy.array([215, -150]),
            w = 20,
            h = 35
        )

        return Track(
            name = "speed_oval",
            track_surface_rects = [
                left_straight,
                bottom_curve,
                right_straight,
                jump_section,
                detour_section,
                top_curve
            ],
            key_checkpoint_rects = [top_curve, bottom_curve],
            ramp_rects = [jump_ramp],
            finish_line_collider = finish_line_coll,
            dash_plate_rects = [dash_1, dash_2, dash_3, dash_4, dash_5, dash_6],
            recovery_rects = [recovery_zone],
            has_guard_rails = True
        )

    # Funktioniert1 - Erste funktionierende selbst erstellte Strecke
    # Kollisionsdaten generiert mit Map Editor
    def create_funktioniert1():
        # ========== STRECKE ==========
        track_1 = CollisionRect(
            pos = numpy.array([71.08, -132.50]),
            w = 0.50,
            h = 0.67
        )

        track_2 = CollisionRect(
            pos = numpy.array([70.25, -110.00]),
            w = 28.17,
            h = 49.67
        )

        track_3 = CollisionRect(
            pos = numpy.array([77.92, -150.00]),
            w = 13.17,
            h = 33.33
        )

        track_4 = CollisionRect(
            pos = numpy.array([47.08, -161.92]),
            w = 73.50,
            h = 10.17
        )

        track_5 = CollisionRect(
            pos = numpy.array([14.75, -116.67]),
            w = 8.50,
            h = 100.00
        )

        track_6 = CollisionRect(
            pos = numpy.array([51.67, -70.75]),
            w = 82.67,
            h = 8.17
        )

        track_7 = CollisionRect(
            pos = numpy.array([88.75, -61.25]),
            w = 8.17,
            h = 27.17
        )

        track_8 = CollisionRect(
            pos = numpy.array([74.75, -51.75]),
            w = 35.83,
            h = 7.83
        )

        track_9 = CollisionRect(
            pos = numpy.array([67.33, -53.75]),
            w = 20.67,
            h = 10.50
        )

        # ========== RAMPE ==========
        ramp_1 = CollisionRect(
            pos = numpy.array([67.42, -58.50]),
            w = 21.83,
            h = 2.00
        )

        # ========== RECOVERY-ZONE ==========
        recovery_1 = CollisionRect(
            pos = numpy.array([70.33, -109.92]),
            w = 28.33,
            h = 49.83
        )

        # ========== DASH-PLATES ==========
        dash_1 = CollisionRect(
            pos = numpy.array([52.67, -165.17]),
            w = 2.67,
            h = 2.33
        )

        dash_2 = CollisionRect(
            pos = numpy.array([70.08, -56.50]),
            w = 14.83,
            h = 1.67
        )

        # ========== DIRT-ZONEN ==========
        dirt_1 = CollisionRect(
            pos = numpy.array([48.28, -159.48]),
            w = 11.33,
            h = 4.66
        )

        # ========== ZIELLINIE ==========
        finish_1 = CollisionRect(
            pos = numpy.array([77.50, -141.75]),
            w = 13.67,
            h = 1.83
        )

        # ========== CHECKPOINTS ==========
        checkpoint_1 = CollisionRect(
            pos = numpy.array([14.58, -114.25]),
            w = 8.50,
            h = 34.83
        )

        checkpoint_2 = CollisionRect(
            pos = numpy.array([88.58, -61.00]),
            w = 7.17,
            h = 11.00
        )

        return Track(
            name = "Funktioniert1",
            track_surface_rects = [
                track_1, track_2, track_3, track_4, track_5,
                track_6, track_7, track_8, track_9
            ],
            key_checkpoint_rects = [checkpoint_1, checkpoint_2],
            ramp_rects = [ramp_1],
            finish_line_collider = finish_1,
            dash_plate_rects = [dash_1, dash_2],
            recovery_rects = [recovery_1],
            has_guard_rails = True,
            dirt_rects = [dirt_1]
        )