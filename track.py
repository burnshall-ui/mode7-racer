# Eine Klasse, die (die Kollisionskarte für) eine Rennstrecke modelliert.
# Objekte der Klasse enthalten einen Namen und mehrere Listen von Kollisionsrechtecken,
# die die Streckenoberfläche, Rampen, verschiedene Arten von Gimmicks und Hindernissen modellieren, ...
#
# Parameter floor_texture_path und bg_texture_path sind die Pfade zu den Texturen für die Strecke und den Planeten
# sowie für den Skybox-ähnlichen Hintergrund.
class Track:
    def __init__(self, name, track_surface_rects, key_checkpoint_rects, ramp_rects, finish_line_collider, 
            dash_plate_rects, recovery_rects, has_guard_rails):
        self.name = name

        self.track_surface_rects = track_surface_rects
        
        self.key_checkpoints = [KeyCheckpoint(kc_rect) for kc_rect in key_checkpoint_rects]

        self.ramp_rects = ramp_rects

        self.finish_line_collider = finish_line_collider

        self.dash_plate_rects = dash_plate_rects

        self.recovery_zone_rects = recovery_rects

        # Flag, das bestimmt, ob die Strecke feste Grenzen hat oder nicht
        # (im letzteren Fall fällt der Spieler einfach von der Strecke)
        self.has_guard_rails = has_guard_rails


    
    # ------------------ Methoden für Kollisionserkennung ---------------------------



    # Diese Methoden prüfen, ob ein übergebenes rechteckiges Kollisionsrechteck
    # mit etwas auf der Strecke kollidiert.  



    # Bestimmt, ob das übergebene rechteckige Kollisionsrechteck auf der Streckenoberfläche ist oder nicht.
    # 
    # Parameter:
    # other (CollisionRect)
    def is_on_track(self, other):
        return collides_with_list(self.track_surface_rects, other)

    # Bestimmt, ob das übergebene rechteckige Kollisionsrechteck eine Dash-Plate auf der Strecke trifft oder nicht.
    #
    # Parameter:
    # other (CollisionRect)
    def is_on_dash_plate(self, other):
        return collides_with_list(self.dash_plate_rects, other)

    # Bestimmt, ob das übergebene rechteckige Kollisionsrechteck eine Wiederherstellungszone auf der Strecke trifft.
    #
    # Parameter:
    # other (CollisionRect)
    def is_on_recovery_zone(self, other):
        return collides_with_list(self.recovery_zone_rects, other)

    # Bestimmt, ob das übergebene rechteckige Kollisionsrechteck auf einer Rampe ist oder nicht.
    #
    # Parameter:
    # other (CollisionRect)
    def is_on_ramp(self, other):
        return collides_with_list(self.ramp_rects, other)

    # Bestimmt, ob das übergebene rechteckige Kollisionsrechteck auf der Ziellinie ist oder nicht.
    #
    # Parameter:
    # other (CollisionRect)
    def is_on_finish_line(self, other):
        return self.finish_line_collider.overlap(other)



    # --------------------- Ende der Methoden für Kollisionserkennung ---------------------------



    # --------------------- Methoden für die Behandlung der Schlüssel-Checkpoints auf der Strecke ------------------



    # Prüft für jeden Schlüssel-Checkpoint, ob das übergebene Spieler-Kollisionsrechteck
    # über einem (oder mehreren) Schlüssel-Checkpoint liegt.
    # Wenn ja, werden diese Schlüssel-Checkpoints als passiert markiert.
    def update_key_checkpoints(self, player_coll):
        for key_checkpoint in self.key_checkpoints:
            if key_checkpoint.collider.overlap(player_coll):
                key_checkpoint.passed = True

    # Gibt genau dann true zurück,
    # wenn der Spieler alle Schlüssel-Checkpoints auf der Strecke passiert hat.
    def all_key_checkpoints_passed(self):
        for key_checkpoint in self.key_checkpoints:
            if not key_checkpoint.passed:
                return False
        return True

    # Setzt die Passiert-Flags aller Schlüssel-Checkpoints auf false.
    def reset_key_checkpoints(self):
        for key_checkpoint in self.key_checkpoints:
            key_checkpoint.passed = False



    # ----------------- Ende der Methoden für die Behandlung der Schlüssel-Checkpoints auf der Strecke



    # Kapselt die Prüfung, ob die Leitplanken auf dieser Strecke
    # in einem bestimmten Frame aktiv sind.
    # Beachte, dass dies nicht nur davon abhängen könnte, ob die Strecke Leitplanken hat,
    # sondern auch Fallen auf der Strecke könnten die Leitplanken der Strecke vorübergehend deaktivieren können.
    def guard_rails_active(self):
        return self.has_guard_rails



# Ein Schlüssel-Checkpoint für das Rundenzählsystem.
# Besteht aus einem CollisionRect und einem Passiert-Flag.
#
# Wenn der Spieler alle Schlüssel-Checkpoints passiert und dann die Ziellinie,
# zählt dies als abgeschlossene Runde.
# In jedem Fall wird die Liste der passierten Schlüssel-Checkpoints zurückgesetzt.
class KeyCheckpoint:
    # Erstellt eine neue Schlüssel-Checkpoint-Instanz mit dem übergebenen Kollisionsrechteck.
    # Anfangs ist der Checkpoint als nicht vom Spieler passiert markiert.
    def __init__(self, collider):
        self.collider = collider
        self.passed = False

# Prüft, ob das übergebene rechteckige Kollisionsrechteck
# mit einem der Kollisionsrechtecke in der übergebenen Liste kollidiert.
#
# Parameter:
# list      - Liste von CollisionRect
# other     - CollisionRect
def collides_with_list(coll_list, other):
    for rect_coll in coll_list:
        if rect_coll.overlap(other):
            return True
    return False

