# Klasse, die eine Maschine repräsentiert,
# einschließlich aller Physik-Engine-bezogenen Daten (Beschleunigungskraft, Höchstgeschwindigkeit, ...)
# und Grafik
class Machine:
    def __init__(self, max_speed, boosted_max_speed, acceleration, boosted_acceleration, brake, speed_loss, 
            boosted_speed_loss, max_centri, centri_increase, centri_decrease, jump_duration_multiplier, boost_duration, max_energy, 
            boost_cost, hit_cost, recover_speed,
            rotation_speed, idle_anim, driving_anim, shadow_image_path):
        # ----------- Initialisierung der Physik-Variablen ----------------------



        # Höchstgeschwindigkeit
        self.max_speed = max_speed
        self.boosted_max_speed = boosted_max_speed # Höchstgeschwindigkeit, wenn ein Boost aktiv ist

        # Beschleunigungskraft:
        # Menge an Geschwindigkeit, die pro Frame hinzugefügt wird, in dem der Spieler den Beschleuniger gedrückt hält
        self.acceleration = acceleration
        self.boosted_acceleration = boosted_acceleration # Beschleunigungskraft ist unterschiedlich (normalerweise stärker), wenn der Booster verwendet wird

        # Bremskraft:
        # Menge an Geschwindigkeit, die pro Frame subtrahiert wird, in dem der Spieler die Bremsen gedrückt hält
        self.brake = brake

        # Geschwindigkeitsverlust:
        # beschreibt, wie gut die Maschine Geschwindigkeit behält, wenn der Spieler nicht beschleunigt
        # genauer gesagt, dies ist die Menge an Geschwindigkeit, die in jedem Frame subtrahiert wird,
        # in dem der Spieler nicht beschleunigt
        # (aber auch nicht die Bremsen drückt)
        self.speed_loss = speed_loss
        self.boosted_speed_loss = boosted_speed_loss # Geschwindigkeitsverlust ist unterschiedlich, wenn ein Boost aktiv ist

        # -------------------- Zentrifugalkraft-Variablen ------------------------------------------

        # Zentrifugalkraft:
        # Bestimmt, wie stark die Maschine nach außen gedrückt wird, wenn gelenkt wird.
        # Genauer gesagt quantifizieren die Zentrifugalkraft-Variablen den Prozentsatz der Höchstgeschwindigkeit der Maschine,
        # der als Zentrifugalkraft angewendet wird.

        # wie viel die Zentrifugalkraft in jedem Frame zunimmt, in dem die Maschine lenkt
        self.centri_increase = centri_increase 

        # die Obergrenze für die maximale Zentrifugalkraft, die in einem einzigen Frame angewendet werden soll
        self.max_centri = max_centri

        # wie viel die Zentrifugalkraft in jedem Frame abnimmt, in dem die Maschine nicht lenkt
        self.centri_decrease = centri_decrease

        # ---------------------- Ende der Zentrifugalkraft-Variablen -----------------------------------

        # in Sekunden,
        # multipliziert mit der aktuellen Geschwindigkeit, um die Dauer eines Sprungs zu bestimmen
        self.jump_duration_multiplier = jump_duration_multiplier

        # Dauer eines Boosts in Sekunden
        self.boost_duration = boost_duration

        # maximale Energiemenge, die diese Maschine haben kann
        self.max_energy = max_energy

        # wie viel Energie die Maschine verliert, wenn der Booster verwendet wird
        self.boost_cost = boost_cost

        # verwendet, um die Energiemenge zu bestimmen, die die Maschine beim Aufprall auf Hindernisse verliert
        self.hit_cost = hit_cost

        # wie schnell die Maschine Energie wiederherstellt, wenn sie sich in einer Erholungszone befindet
        self.recover_speed = recover_speed

        # wie schnell der Spieler rotieren kann, wenn er lenkt
        self.rotation_speed = rotation_speed



        # ----------- Ende der Initialisierung der Physik-Variablen ----------------------



        # ----------- Initialisierung der Grafik-Variablen ----------------------



        # Bilder der Animation, die abgespielt wird, wenn die Maschine im Leerlauf ist
        self.idle_anim = idle_anim

        # Bilder der Animation, die abgespielt wird, wenn der Beschleuniger der Maschine aktiviert ist
        self.driving_anim = driving_anim

        # Bild des Schattens, den die Maschine auf die Strecke wirft
        # (sollte unter der Maschine gezeichnet werden)
        self.shadow_image_path = shadow_image_path



        # ----------- Ende der Initialisierung der Grafik-Variablen ----------------------