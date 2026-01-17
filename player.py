import numpy
import pygame
from pygame import mixer

from settings.debug_settings import IN_DEV_MODE, COLLISION_DETECTION_OFF # Debug-Konfiguration
from settings.key_settings import STD_ACCEL_KEY, STD_LEFT_KEY, STD_RIGHT_KEY, STD_BRAKE_KEY, STD_BOOST_KEY # Tastenbelegungs-Konfiguration
from settings.gamepad_settings import (
    GAMEPAD_STEER_AXIS, GAMEPAD_DEADZONE, GAMEPAD_STEER_SENSITIVITY,
    GAMEPAD_GAS_BUTTON, GAMEPAD_BRAKE_BUTTON, GAMEPAD_BOOST_BUTTON,
    USE_TRIGGER_FOR_GAS, GAMEPAD_GAS_TRIGGER_AXIS, GAMEPAD_BRAKE_TRIGGER_AXIS,
    GAMEPAD_DEBUG, USE_DPAD_FOR_STEERING
) # Gamepad-Konfiguration
from settings.renderer_settings import NORMAL_ON_SCREEN_PLAYER_POSITION_X, NORMAL_ON_SCREEN_PLAYER_POSITION_Y, RENDER_SCALE # Rendering-Konfiguration
from settings.machine_settings import PLAYER_COLLISION_RECT_WIDTH, PLAYER_COLLISION_RECT_HEIGHT # Spieler-Kollisionsrechteck-Konfiguration
from settings.machine_settings import HEIGHT_DURING_JUMP, HIT_COST_SPEED_FACTOR, MIN_BOUNCE_BACK_FORCE
from settings.machine_settings import OBSTACLE_HIT_SPEED_RETENTION
from settings.machine_settings import MIN_JUMP_SPEED, DIRT_DAMPING, DIRT_MAX_SPEED_FACTOR, BOB_SPEED, BOB_AMPLITUDE 

from collision import CollisionRect

from animation import AnimatedMachine

class Player(pygame.sprite.Sprite, AnimatedMachine):
    # Konstruktor.
    # machine: die Maschine, die von diesem Spieler gesteuert wird
    # current_race: das Rennen, das der Spieler gerade fährt
    # gamepad: optionale Referenz zum Gamepad/Controller (None wenn kein Controller)
    def __init__(self, machine, current_race, gamepad=None):
        # Gamepad-Referenz speichern
        self.gamepad = gamepad

        # Renn-Daten-Referenz,
        # um auf die Umgebung reagieren zu können
        # und die Spielerposition zu initialisieren
        self.current_race = current_race
        
        # Position und Rotation initialisieren (gemäß dem aktuell gefahrenen Rennen)
        self.reinitialize_position_angle()
        
        # Physik-Variablen
        self.machine = machine # enthält alle relevanten Daten zu den physikalischen Eigenschaften der Spielermaschine
        self.current_speed = 0 # wie schnell sich der Spieler im aktuellen Frame bewegt
        self.centri = 0 # wie stark die im aktuellen Frame angewendete Zentrifugalkraft ist

        # Aktuelle Energiemenge, die der Maschine noch verbleibt
        self.current_energy = self.machine.max_energy

        # Animationsvariablen initialisieren durch Aufruf des entsprechenden Superklassen-Konstruktors
        AnimatedMachine.__init__(self,
            idle_anim = self.machine.idle_anim,
            driving_anim = self.machine.driving_anim,
            jumping_anim = self.machine.jumping_anim
        )
        
        # Animation auf die initiale umschalten
        self.switch_animation("driving")

        # Rendering-Variablen (für Maschine ohne Schatten).
        # Die x-Koordinate des Spielers ist immer fest,
        # die y-Koordinate normalerweise auch fest,
        # wird während eines Sprungs gemäß einer konfigurierten quadratischen Funktion geändert.
        pygame.sprite.Sprite.__init__(self) # Aufruf des Konstruktors der pygame Sprite-Klasse (verantwortlich für Rendering)
        self.image = self.current_frame()
        self.rect = self.image.get_rect()
        self.rect.topleft = [NORMAL_ON_SCREEN_PLAYER_POSITION_X, NORMAL_ON_SCREEN_PLAYER_POSITION_Y]

        # Neues Sprite-Objekt für den Maschinenschatten erstellen,
        # der die ganze Zeit über fest bleibt.
        self.shadow_sprite = pygame.sprite.Sprite()
        shadow_img = pygame.image.load(self.machine.shadow_image_path)
        # Schatten skalieren entsprechend RENDER_SCALE
        if RENDER_SCALE != 1.0:
            new_width = int(shadow_img.get_width() * RENDER_SCALE)
            new_height = int(shadow_img.get_height() * RENDER_SCALE)
            shadow_img = pygame.transform.scale(shadow_img, (new_width, new_height))
        self.shadow_sprite.image = shadow_img
        self.shadow_sprite.rect = self.shadow_sprite.image.get_rect()
        # Schatten-Sprite wird so erstellt, dass es in Ordnung ist, wenn Spieler + Schatten dieselben Bildschirmkoordinaten haben
        self.shadow_sprite.rect.topleft = [NORMAL_ON_SCREEN_PLAYER_POSITION_X, NORMAL_ON_SCREEN_PLAYER_POSITION_Y]

        # Spieler-Status-Flags/Variablen
        self.steering_left = False
        self.steering_right = False
        self.jumping = False
        self.jumped_off_timestamp = None # Zeitstempel, wann der Spieler zuletzt von einer Rampe gesprungen ist
        # Beim Springen: Dies ist die Dauer des Sprungs vom Start bis zur Landung.
        # Wird benötigt, um die y-Koordinate des Spielers auf dem Bildschirm während des Sprungs zu berechnen.
        self.current_jump_duration = 0
        self.finished = False # ob der Spieler das aktuelle Rennen beendet hat
        self.destroyed = False # ob die Spielermaschine zerstört wurde aufgrund von Absturz außerhalb der Grenzen oder keine Energie mehr
        self.boosted = False
        self.last_boost_started_timestamp = None # Zeitstempel, wann der Spieler zuletzt einen Boost gestartet hat
        self.has_boost_power = False # ob der Spieler seinen Booster verwenden darf (während der ersten Runde auf False gesetzt, wechselt nach Abschluss der ersten Runde auf True)

        # Bobbing-Effekt: Leichtes Auf-und-Ab beim Fahren (wie in F-Zero)
        self.bob_phase = 0.0  # Aktuelle Phase der Bobbing-Animation

        # Kurvenneigung: Schiff kippt beim Lenken (wie in F-Zero)
        self.tilt_angle = 0.0  # Aktueller Neigungswinkel in Grad

        # Letzte Inputs (für Sound-Logik, wird in racing_mode_movement gesetzt)
        self.last_input_gas = False
        self.last_input_left = False
        self.last_input_right = False

        # Engine-Sounds laden
        try:
            self.engine_sounds = {
                "idle": mixer.Sound("sounds/leerlauf.wav"),
                "normal": mixer.Sound("sounds/gas_normal.wav"),
                "boost": mixer.Sound("sounds/gas_boost.wav"),
                "steering": mixer.Sound("sounds/gas_lenken.wav")
            }
            # Lautstärke anpassen
            for sound in self.engine_sounds.values():
                sound.set_volume(0.4)

            self.current_engine_sound = None  # Aktuell abgespielter Sound
            self.current_engine_state = None  # idle, normal, boost

            # NEU: Status für den separaten Kurvensound
            self.steering_sound_playing = False
            
            # Zusätzliche SFX
            self.collision_sound = mixer.Sound("sounds/kollision.wav")
            self.collision_sound.set_volume(0.6)
            
            self.regen_sound = mixer.Sound("sounds/regeneration.wav")
            self.regen_sound.set_volume(0.5)
            self.regen_sound_playing = False
            
        except Exception as e:
            print(f"Engine-Sounds konnten nicht geladen werden: {e}")
            self.engine_sounds = None

        # Flag für Lande-Effekt (Partikel)
        self.just_landed = False

    # Aktualisiert Spielerdaten und Position.
    # 
    # Parameter:
    # time: Anzahl der Frames seit Spielstart
    def update(self, time, delta):
        # Spieler gemäß Lenkeingaben und aktueller Geschwindigkeit bewegen
        if IN_DEV_MODE:
            self.dev_mode_movement()
        elif not self.destroyed:
            self.racing_mode_movement(time, delta)

        # Aktuelles rechteckiges Kollisionsrechteck des Spielers speichern
        # zur Verwendung in mehreren Umgebungsprüfungen und Aktualisierungen.
        current_collision_rect = CollisionRect(
            pos = self.position,
            w = PLAYER_COLLISION_RECT_WIDTH,
            h = PLAYER_COLLISION_RECT_HEIGHT
        )

        # Rundenzähler aktualisieren.
        # Dafür benötigt das Streckenobjekt die aktuelle Position des Spielers.
        self.current_race.update_lap_count(current_collision_rect, time)

        # Spieler boosten lassen, wenn auf Dash-Plate.
        # Über eine Dash-Plate springen führt natürlich nicht zu einem Boost.
        if self.current_race.is_on_dash_plate(current_collision_rect) and not self.jumping and not self.boosted:
            self.boosted = True
            self.last_boost_started_timestamp = time # Zeitstempel zur Bestimmung, wann der Boost enden soll
        if self.boosted:
            self.continue_boost(time)

        # Spieler springen lassen, wenn auf Rampe.
        # Nur springen wenn Geschwindigkeit positiv und über Minimum (verhindert Rückwärts-Sprünge)
        if self.current_race.is_on_ramp(current_collision_rect) and not self.jumping and self.current_speed >= MIN_JUMP_SPEED:
            self.jumping = True # Status-Flag setzen
            self.current_jump_duration = self.machine.jump_duration_multiplier * self.current_speed # Sprungdauer basierend auf Geschwindigkeit berechnen
            self.jumped_off_timestamp = time # Zeitstempel zur Berechnung der Höhe in späteren Frames
        if self.jumping:
            self.continue_jump(time)

        # Spieler Energie wiederherstellen lassen, wenn in Wiederherstellungszone.
        # Über eine Wiederherstellungszone springen zählt natürlich nicht.
        is_recovering = self.current_race.is_on_recovery_zone(current_collision_rect) and not self.jumping
        
        if is_recovering:
            self.current_energy += self.machine.recover_speed * delta
            if self.current_energy > self.machine.max_energy:
                self.current_energy = self.machine.max_energy
            
            # Sound abspielen wenn nicht schon läuft
            if self.engine_sounds and not self.regen_sound_playing and not self.finished and not self.destroyed:
                self.regen_sound.play(loops=-1)
                self.regen_sound_playing = True
        else:
            # Sound stoppen wenn wir den Bereich verlassen
            if self.engine_sounds and self.regen_sound_playing:
                self.regen_sound.stop()
                self.regen_sound_playing = False

        # Spieler verlangsamen, wenn auf Dirt-Zone.
        # Über Dirt springen hat keinen Effekt.
        if self.current_race.is_on_dirt(current_collision_rect) and not self.jumping:
            # Damping-Effekt: Geschwindigkeit wird pro Frame reduziert
            self.current_speed *= DIRT_DAMPING

            # Zusätzlich: Höchstgeschwindigkeit auf Dirt begrenzen
            dirt_max_speed = self.machine.max_speed * DIRT_MAX_SPEED_FACTOR
            if self.current_speed > dirt_max_speed:
                self.current_speed = dirt_max_speed

        # Aktuelle Animation des Spielers vorrücken und Bild des Spieler-Sprites aktualisieren
        # Beim Springen: Jump-Animation verwenden
        if self.jumping:
            self.switch_to_jumping_animation()

        self.advance_current_animation(delta)
        self.image = self.current_frame()

        # TODO: Kurvenneigung mit echten Sprites einbauen
        # Benötigt: violet_machine_left0001-0004.png und violet_machine_right0001-0004.png

        # Bobbing-Effekt: Leichtes Auf-und-Ab beim Fahren (wie in F-Zero)
        # Nur wenn nicht springend, Geschwindigkeit > 0 und NICHT am Lenken
        # (beim Lenken neigt sich das Schiff stattdessen)
        is_steering = self.steering_left or self.steering_right
        if not self.jumping and self.current_speed > 0 and not is_steering:
            # Phase voranschreiten (schneller bei höherer Geschwindigkeit)
            speed_factor = min(1.0, self.current_speed / self.machine.max_speed)
            self.bob_phase += BOB_SPEED * delta * speed_factor

            # Sinusförmige Bewegung berechnen
            bob_amplitude_scaled = BOB_AMPLITUDE * RENDER_SCALE
            bob_offset = numpy.sin(self.bob_phase) * bob_amplitude_scaled * speed_factor

            # Y-Position anpassen
            self.rect.topleft = [
                NORMAL_ON_SCREEN_PLAYER_POSITION_X,
                NORMAL_ON_SCREEN_PLAYER_POSITION_Y + bob_offset
            ]
        elif not self.jumping:
            # Wenn nicht springend und keine Geschwindigkeit oder am Lenken: normale Position
            # (später hier: Neigung beim Kurvenfahren einbauen)
            self.rect.topleft = [
                NORMAL_ON_SCREEN_PLAYER_POSITION_X,
                NORMAL_ON_SCREEN_PLAYER_POSITION_Y
            ]

        # Engine-Sound-Verwaltung
        if self.engine_sounds and not self.destroyed and not IN_DEV_MODE:
            # Wenn das Rennen vorbei ist, alle Sounds stoppen
            if self.finished:
                if self.current_engine_sound:
                    self.current_engine_sound.stop()
                    self.current_engine_sound = None
                    self.current_engine_state = None
                if self.steering_sound_playing:
                    self.engine_sounds["steering"].stop()
                    self.steering_sound_playing = False
                if self.regen_sound_playing:
                    self.regen_sound.stop()
                    self.regen_sound_playing = False
                return

            # Inputs aus racing_mode_movement verwenden (kombiniert Tastatur + Gamepad)
            is_pressing_gas = self.last_input_gas
            is_pressing_left = self.last_input_left
            is_pressing_right = self.last_input_right

            # ---------------------------------------------------------
            # Teil 1: Basis-Motorsound (Idle, Normal, Boost)
            # ---------------------------------------------------------
            # Bestimme den Ziel-Zustand des Motors
            target_engine_state = "idle"

            # Priorität 1: Boosting
            if self.boosted and is_pressing_gas:
                target_engine_state = "boost"
            # Priorität 2: Normal Gas
            elif is_pressing_gas:
                target_engine_state = "normal"
            # Sonst: Leerlauf (Idle) bleibt gesetzt

            # Sound wechseln, wenn sich der Motor-Status geändert hat
            if target_engine_state != self.current_engine_state:
                # Alten Motorsound stoppen
                if self.current_engine_sound:
                    self.current_engine_sound.stop()

                # Neuen Sound starten (als Loop)
                self.current_engine_sound = self.engine_sounds[target_engine_state]
                self.current_engine_sound.play(loops=-1)
                self.current_engine_state = target_engine_state

            # ---------------------------------------------------------
            # Teil 2: Kurvensound (Overlay / Zusätzlich)
            # ---------------------------------------------------------
            is_steering = is_pressing_left or is_pressing_right

            if is_steering:
                # Wenn wir lenken, aber der Sound noch nicht läuft -> starten
                if not self.steering_sound_playing:
                    self.engine_sounds["steering"].play(loops=-1)
                    self.steering_sound_playing = True
            else:
                # Wenn wir nicht mehr lenken, aber Sound noch läuft -> stoppen
                if self.steering_sound_playing:
                    self.engine_sounds["steering"].stop()
                    self.steering_sound_playing = False


    # Bewegt und rotiert die Kamera frei basierend auf Spielereingaben.
    def dev_mode_movement(self):
        # Sinus und Kosinus des aktuellen Winkels berechnen,
        # um die Spielerposition basierend auf ihrer Rotation aktualisieren zu können.
        sin_a = numpy.sin(self.angle)
        cos_a = numpy.cos(self.angle)

        # Skalierte Versionen dieser beiden Werte für Bequemlichkeit speichern.
        # Spieler bewegt sich im Dev-Modus immer mit maximaler Geschwindigkeit.
        speed_sin, speed_cos = self.machine.max_speed * sin_a, self.machine.max_speed * cos_a

        # Variablen initialisieren, die die Änderung der Spielerposition halten,
        # die während der Methode akkumuliert werden.
        dx, dy = 0, 0

        # Tastenereignisse sammeln
        keys = pygame.key.get_pressed()

        # Änderung der Spielerposition basierend auf gedrückten Tasten akkumulieren.
        if keys[pygame.K_w]:
            dx += speed_cos
            dy += speed_sin
        if keys[pygame.K_s]:
            dx += -speed_cos
            dy += -speed_sin
        if keys[pygame.K_a]:
            dx += -speed_sin
            dy += speed_cos
        if keys[pygame.K_d]:
            dx += speed_sin
            dy += -speed_cos

        # Spielerposition ändern
        self.position[0] += dx
        self.position[1] += dy

        # Spielerrotation ändern
        if keys[pygame.K_LEFT]:
            self.angle += self.rotation_speed
        if keys[pygame.K_RIGHT]:
            self.angle -= self.rotation_speed

        print("x: " + str(self.position[0]) + " y: " + str(self.position[1]) + " a: " + str(self.angle))

    # Bewegt die Maschine des Spielers wie in einem Rennen (Beschleunigen, Bremsen und Lenken).
    #
    # Parameter:
    # time - der Zeitstempel des Frame-Updates, in dem dieser Aufruf gemacht wurde
    # delta - die Zeit zwischen diesem Frame und dem vorherigen Frame
    def racing_mode_movement(self, time, delta):
        # Tastenereignisse sammeln
        keys = pygame.key.get_pressed()

        # ==================== GAMEPAD INPUT SAMMELN ====================
        # Gamepad-Inputs werden mit Tastatur-Inputs kombiniert (OR-Verknüpfung)
        gamepad_gas = False
        gamepad_brake = False
        gamepad_boost = False
        gamepad_steer = 0.0  # -1.0 = voll links, +1.0 = voll rechts

        if self.gamepad:
            try:
                # Gas-Button oder Trigger
                if USE_TRIGGER_FOR_GAS:
                    # Trigger-Wert: -1.0 bis 1.0 (manche Controller: 0.0 bis 1.0)
                    trigger_val = self.gamepad.get_axis(GAMEPAD_GAS_TRIGGER_AXIS)
                    gamepad_gas = trigger_val > 0.3  # 30% gedrückt = Gas
                    brake_val = self.gamepad.get_axis(GAMEPAD_BRAKE_TRIGGER_AXIS)
                    gamepad_brake = brake_val > 0.3
                else:
                    gamepad_gas = self.gamepad.get_button(GAMEPAD_GAS_BUTTON)
                    gamepad_brake = self.gamepad.get_button(GAMEPAD_BRAKE_BUTTON)

                # Boost-Button
                gamepad_boost = self.gamepad.get_button(GAMEPAD_BOOST_BUTTON)

                # Lenkung - D-Pad (Hat) oder Analog-Stick
                if USE_DPAD_FOR_STEERING:
                    # D-Pad ist bei den meisten Controllern ein "Hat"
                    if self.gamepad.get_numhats() > 0:
                        hat = self.gamepad.get_hat(0)  # (x, y) Tuple
                        gamepad_steer = float(hat[0])  # -1 = links, 0 = neutral, 1 = rechts
                    else:
                        # Fallback: Stick verwenden wenn kein Hat vorhanden
                        raw_steer = self.gamepad.get_axis(GAMEPAD_STEER_AXIS)
                        if abs(raw_steer) > GAMEPAD_DEADZONE:
                            gamepad_steer = raw_steer * GAMEPAD_STEER_SENSITIVITY
                else:
                    # Analog-Stick für Lenkung
                    raw_steer = self.gamepad.get_axis(GAMEPAD_STEER_AXIS)
                    if abs(raw_steer) > GAMEPAD_DEADZONE:
                        gamepad_steer = raw_steer * GAMEPAD_STEER_SENSITIVITY

                # Debug-Ausgabe
                if GAMEPAD_DEBUG:
                    # Alle gedrückten Buttons anzeigen
                    for i in range(self.gamepad.get_numbuttons()):
                        if self.gamepad.get_button(i):
                            print(f"Gamepad Button {i} gedrückt")
                    # Achsen nur bei signifikanter Bewegung
                    for i in range(self.gamepad.get_numaxes()):
                        axis_val = self.gamepad.get_axis(i)
                        if abs(axis_val) > 0.5:
                            print(f"Gamepad Achse {i}: {axis_val:.2f}")
            except Exception as e:
                # Falls was mit dem Gamepad schiefgeht, einfach ignorieren
                if GAMEPAD_DEBUG:
                    print(f"Gamepad Fehler: {e}")

        # ==================== KOMBINIERTE INPUTS ====================
        # Tastatur ODER Gamepad löst die Aktion aus
        input_gas = keys[STD_ACCEL_KEY] or gamepad_gas
        input_brake = keys[STD_BRAKE_KEY] or gamepad_brake
        input_boost = keys[STD_BOOST_KEY] or gamepad_boost
        input_left = keys[STD_LEFT_KEY] or gamepad_steer < -GAMEPAD_DEADZONE
        input_right = keys[STD_RIGHT_KEY] or gamepad_steer > GAMEPAD_DEADZONE

        # Inputs als Instanzvariablen speichern (für Sound-Logik in update())
        self.last_input_gas = input_gas
        self.last_input_left = input_left
        self.last_input_right = input_right

        # Bestimmen, ob der Spieler in diesem Frame einen Boost starten möchte
        if input_boost and self.can_boost():
            self.last_boost_started_timestamp = time # Zeitstempel nehmen
            self.current_energy -= self.machine.boost_cost # Boosten kostet etwas Energie
            self.boosted = True # Status-Flag aktualisieren

        # Lenken.
        if input_left and not self.finished:
            # Flags aktualisieren
            self.steering_left = True
            self.steering_right = False

            # Spieler rotieren - bei Gamepad proportional zum Stick-Ausschlag
            steer_factor = abs(gamepad_steer) if gamepad_steer < 0 else 1.0
            self.angle += self.machine.rotation_speed * delta * steer_factor

        if input_right and not self.finished:
            # Flags aktualisieren
            self.steering_left = False
            self.steering_right = True

            # Spieler rotieren - bei Gamepad proportional zum Stick-Ausschlag
            steer_factor = gamepad_steer if gamepad_steer > 0 else 1.0
            self.angle -= self.machine.rotation_speed * delta * steer_factor

        # ------------ Aktualisierung der Spielergeschwindigkeit ------------------

        # Geschwindigkeit erhöhen, wenn Beschleunigungstaste gedrückt wird.
        # Beschleunigungseingabe sollte ignoriert werden, wenn die Geschwindigkeit derzeit über der aktuellen Maximalgeschwindigkeit der Maschine liegt.
        current_max_speed = self.machine.boosted_max_speed if self.boosted else self.machine.max_speed
        if input_gas and not self.finished and not self.current_speed > current_max_speed:
            # Auf Fahranimation umschalten
            self.switch_to_driving_animation()

            # Geschwindigkeit erhöhen
            self.current_speed += (
                self.machine.boosted_acceleration if self.boosted else self.machine.acceleration
            ) * delta
        # Geschwindigkeit stark verringern, wenn Bremstaste gedrückt wird.
        # Der Spieler kann nicht bremsen, wenn er in der Luft ist.
        elif input_brake and not self.finished and not self.jumping:
            # Egal ob Spieler sich vorwärts oder rückwärts bewegt:
            # Auf Leerlauf-Animation umschalten, wenn Spieler bremst
            self.switch_to_idle_animation()

            # Fall 1: Spieler bewegt sich derzeit vorwärts
            if self.current_speed > 0:
                self.current_speed -= self.machine.brake * delta 
                # Geschwindigkeit auf null begrenzen, da der Spieler
                # nicht rückwärts fahren können sollte.
                if self.current_speed < 0:
                    self.current_speed = 0
            # Fall 2: Spieler bewegt sich derzeit rückwärts (z.B. wegen Zurückprallens)
            elif self.current_speed < 0:
                self.current_speed += self.machine.brake * delta
                # Geschwindigkeit auf null begrenzen, da der Spieler
                # nicht wieder vorwärts gehen sollte
                if self.current_speed > 0:
                    self.current_speed = 0
        # Geschwindigkeit leicht verringern, wenn weder Beschleunigungs- noch Bremstaste gedrückt wird.
        # Verringern bedeutet hierbei Annäherung an null
        # (ansonsten würde sich der Spieler rückwärts mit zunehmender Geschwindigkeit bewegen,
        # wenn keine Taste gedrückt wird).
        else: 
            # Auf Leerlauf-Animation umschalten
            self.switch_to_idle_animation()

            # In diesem Spiel verliert der Spieler keine Geschwindigkeit während des Sprungs.
            if not self.jumping:
                # Geschwindigkeitsverlust berechnen und anwenden
                current_speed_loss = (self.machine.boosted_speed_loss 
                    if self.boosted or self.current_speed > self.machine.max_speed # stärkerer Geschwindigkeitsverlust, wenn Maschine über ihrer regulären Höchstgeschwindigkeit ist
                    else self.machine.speed_loss) * delta
                if self.current_speed > 0:
                    self.current_speed -= current_speed_loss
                    # Geschwindigkeit auf null begrenzen (von unten), um Zittern zu verhindern.
                    if self.current_speed < 0:
                        self.current_speed = 0
                elif self.current_speed < 0:
                    self.current_speed += current_speed_loss
                    # Geschwindigkeit auf null begrenzen (von oben), um Zittern zu verhindern.
                    if self.current_speed > 0:
                        self.current_speed = 0




        # -------- end of updating player's speed -----------------------



        # -------- Berechnung der Zentrifugalkraftstärke -----------------



        # Wenn der Spieler in diesem Frame eine der Lenktasten drückt,
        # erhöht sich die Zentrifugalkraft (wird bei einem bestimmten Limit begrenzt).
        # Die Erhöhung der Zentrifugalkräfte ist proportional zur aktuellen Geschwindigkeit des Spielers.
        if input_left or input_right:
            self.centri += self.machine.centri_increase * self.current_speed * delta
            if self.centri > self.machine.max_centri:
                self.centri = self.machine.max_centri
        # Andernfalls: Die angewendete Zentrifugalkraft verringert sich
        # (kann nicht unter 0 fallen)
        else:
            self.centri -= self.machine.centri_decrease * delta 
            if self.centri < 0:
                self.centri = 0
                
                # Wenn die Zentrifugalkräfte abgeklungen sind,
                # ist die Kurve beendet und die Flags können zurückgesetzt werden.
                self.steering_left = False
                self.steering_right = False 



        # --------- Ende der Berechnung der Zentrifugalkraftstärke ----------



        # ---------- tatsächliche Bewegung des Spielers ---------------



        # Bewegungsrichtung aus den Spielereingaben berechnen
        # sowie aus Speed + Stärke der Zentrifugalkraft.



        # Sinus und Kosinus des aktuellen Winkels berechnen,
        # um die Spielerposition basierend auf der Rotation aktualisieren zu können.
        sin_a = numpy.sin(self.angle)
        cos_a = numpy.cos(self.angle)

        # Für die Übersicht: skalierte Varianten der Speed- und Zentrifugalkraft-Richtungen speichern.
        # Richtungen mit dem Speed skalieren
        # und mit dem aktuellen Delta (Zeit zwischen aktuellem und letztem Frame).
        # Der letzte Skalierungsfaktor ist nötig, damit der Player-Speed unabhängig von der Game-Framerate ist
        speed_sin, speed_cos = self.current_speed * delta * sin_a, self.current_speed * delta * cos_a # speed
        cf_sin, cf_cos = self.centri * speed_sin * -1 * delta, self.centri * speed_cos * -1 * delta # centrifugal forces

        # Nächste Frame-Position des Spielers berechnen, inkl. verschobenem Collision-Rect.
        next_frame_position_x = self.position[0] + speed_cos
        next_frame_position_y = self.position[1] + speed_sin
        frame_lookahead_collision_rect = CollisionRect(
            pos = numpy.array([next_frame_position_x, next_frame_position_y]), 
            w = PLAYER_COLLISION_RECT_WIDTH,
            h = PLAYER_COLLISION_RECT_HEIGHT
        )

        # Prüfen, ob der Spieler beim Move wie oben berechnet auf dem Track bleibt.
        # Wenn ja (oder wenn der Spieler springt): bewegen.
        # Wenn nein: zurückprallen lassen.
        #
        # Nur-Debug-Feature: Wenn Collision-Detection ausgeschaltet ist, wird der Spieler immer bewegt und nie zurückgeprallt.
        if self.current_race.is_on_track(frame_lookahead_collision_rect) or self.jumping or COLLISION_DETECTION_OFF:
            self.position[0] = next_frame_position_x
            self.position[1] = next_frame_position_y
        else:
            # Wenn Guard Rails aktiv sind:
            # Spieler verliert etwas Energie und prallt zurück
            if self.current_race.guard_rails_active():
                # Spieler prallt zurück, weil sein Move-Speed umgedreht wird.
                # Der Spieler behält dabei nicht seinen kompletten Speed.
                # Es gibt eine minimale Kraft, die immer angewendet wird,
                # um zu verhindern, dass der Spieler außerhalb der Track-Grenzen festhängt.
                self.current_speed = -(self.current_speed * OBSTACLE_HIT_SPEED_RETENTION + MIN_BOUNCE_BACK_FORCE)

                # Soundeffekt bei Kollision (nur wenn Sound geladen und nicht zerstört/finished)
                if self.engine_sounds and not self.finished and not self.destroyed:
                    self.collision_sound.play()

                # Zentrifugalkraft zurücksetzen um zu verhindern dass Spieler in Wand stecken bleibt
                self.centri = 0
                self.steering_left = False
                self.steering_right = False

                # Spieler verliert Energie.
                self.lose_energy(self.current_speed)

                # Player-Maschine wird zerstört, wenn sie mehr Schaden genommen hat, als sie aushält
                if self.current_energy < 0:
                    self.destroy()
            # Wenn keine Guard Rails aktiv sind:
            # Player-Maschine wird zerstört
            else:
                self.destroy()



        # ----------------- Anwenden der Zentrifugalkräfte



        # Spielerposition im nächsten Frame berechnen
        if self.steering_left:
            next_frame_position_x = self.position[0] - cf_sin
            next_frame_position_y = self.position[1] + cf_cos
        if self.steering_right:
            next_frame_position_x = self.position[0] + cf_sin
            next_frame_position_y = self.position[1] - cf_cos

        # -------------- Entscheiden, ob Zentrifugalkräfte angewendet werden sollen -------------------
        
        

        # Spielerposition im nächsten Frame berechnen
        frame_lookahead_collision_rect = CollisionRect(
            pos = numpy.array([next_frame_position_x, next_frame_position_y]),
            w = PLAYER_COLLISION_RECT_WIDTH,
            h = PLAYER_COLLISION_RECT_HEIGHT
        )

        # Prüfen, ob der Spieler auf dem Track bleibt, wenn er wie oben bewegt wird.
        # Wenn ja (oder wenn der Spieler springt oder Collision-Detection im Debug-Modus aus ist): bewegen.
        # Sonst: Spieler verliert Energie oder die Player-Maschine wird zerstört
        # (abhängig davon, ob der Track aktive Guard Rails hat).
        if self.current_race.is_on_track(frame_lookahead_collision_rect) or self.jumping or COLLISION_DETECTION_OFF:
            self.position[0] = next_frame_position_x
            self.position[1] = next_frame_position_y
        else:
            if self.current_race.guard_rails_active():
                # Zentrifugalkraft wird zurückgesetzt
                self.centri = 0

                # Spieler bekommt Schaden proportional zur aktuell angewendeten Kraft
                self.lose_energy(self.centri)

                # Player-Maschine wird zerstört, wenn keine Energie mehr da ist
                if self.current_energy < 0:
                    self.destroy()
            else: 
                # Player-Maschine wird sofort zerstört, wenn der Track keine aktiven Guard Rails hat
                self.destroy()



        # ------------------ Ende des Anwendens der Zentrifugalkräfte ------------ 



        # ------ Ende der tatsächlichen Bewegung des Spielers -----------------------
    
    # Aktualisiert Spieler-Status-Flags und bewegt den Spieler
    # zu seiner aktuellen Bildschirm-Y-Position
    # abhängig von der Zeit, seit der Spieler von der Strecke gesprungen ist.
    def continue_jump(self, time):
        # Zeit seit Sprungstart berechnen
        elapsed_time = time - self.jumped_off_timestamp

        # Nach oben auf dem Bildschirm bewegen = y-Koordinate verringern
        self.rect.topleft = [
            NORMAL_ON_SCREEN_PLAYER_POSITION_X, 
            NORMAL_ON_SCREEN_PLAYER_POSITION_Y - HEIGHT_DURING_JUMP(elapsed_time, self.current_jump_duration)
        ]

        # Sprung beenden (Status-Flag zurücksetzen), wenn Sprungdauer erreicht
        # Um visuelle Artefakte zu verhindern, wird das Spieler-Rechteck auf seine normale y-Position auf dem Bildschirm zurückgesetzt.
        if elapsed_time >= self.current_jump_duration:
            self.jumping = False
            self.just_landed = True # Signal für Landung setzen

            self.rect.topleft = [
                NORMAL_ON_SCREEN_PLAYER_POSITION_X, NORMAL_ON_SCREEN_PLAYER_POSITION_Y
            ]

            # wenn der Spieler außerhalb der Streckengrenzen landet, hat er den Lauf nicht geschafft
            current_collision_rect = CollisionRect(
                self.position,
                PLAYER_COLLISION_RECT_WIDTH,
                PLAYER_COLLISION_RECT_HEIGHT
            )
            if not self.current_race.is_on_track(current_collision_rect):
                print("Spieler außerhalb der Grenzen!")
                self.destroy()

    # Wird einmal pro Frame aufgerufen, wenn der Spieler derzeit einen Booster aktiv hat.
    # Prüft, ob der Booster enden sollte, da seine Dauer überschritten wurde.
    def continue_boost(self, time):
        # Zeit seit Booststart berechnen
        elapsed_time = time - self.last_boost_started_timestamp

        # prüfen, ob Boost enden sollte
        if elapsed_time > self.machine.boost_duration:
            self.boosted = False

    # Bestimmt, ob der Spieler derzeit seine Boost-Kraft verwenden kann.
    # (i)   Spieler muss Booster freigeschaltet haben (d.h. erste Runde abgeschlossen, normalerweise)
    # (ii)  Spieler kann keinen aktiven Boost im Moment haben
    # (iii) Spieler muss genug Energie haben
    def can_boost(self):
        return self.has_boost_power and not self.boosted and self.current_energy >= self.machine.boost_cost

    # (Neu-)Setzt das Spielerobjekt auf die initiale Position
    # für die aktuelle Rennstrecke.
    # Setzt auch alle Kräfte zurück, die derzeit auf den Spieler angewendet werden.
    # Beispielverwendung: Spieler zur Startposition am Anfang eines Rennens bringen
    def reinitialize(self):
        # Position und Rotation zurücksetzen
        self.reinitialize_position_angle()

        # Kräfte zurücksetzen
        self.current_speed = 0
        self.centri = 0

        # Energie auf Maximum zurücksetzen
        self.current_energy = self.machine.max_energy

        # Status-Flags zurücksetzen
        self.jumping = False
        self.finished = False
        self.destroyed = False
        self.boosted = False
        self.has_boost_power = False
        self.steering_left = False
        self.steering_right = False
        self.bob_phase = 0.0  # Bobbing-Phase zurücksetzen
        self.tilt_angle = 0.0  # Neigungswinkel zurücksetzen

        # Engine-Sound zurücksetzen
        if self.engine_sounds:
            # Motor stoppen
            if self.current_engine_sound:
                self.current_engine_sound.stop()
            # Lenkung stoppen (NEU)
            if self.steering_sound_playing:
                self.engine_sounds["steering"].stop()
            # Regen stoppen
            if self.regen_sound_playing:
                self.regen_sound.stop()

            self.current_engine_sound = None
            self.current_engine_state = None
            self.steering_sound_playing = False
            self.regen_sound_playing = False

        # Bildschirmposition zurücksetzen
        self.rect.topleft = [
            NORMAL_ON_SCREEN_PLAYER_POSITION_X,
            NORMAL_ON_SCREEN_PLAYER_POSITION_Y
        ]

    # Setzt die Position und Rotation des Spielers auf die initialen zurück, die vom aktuellen Rennen vorgeschrieben sind.
    def reinitialize_position_angle(self):
        self.position = numpy.array([self.current_race.init_player_pos_x, self.current_race.init_player_pos_y])
        self.angle = self.current_race.init_player_angle

    # Zerstört die Spielermaschine durch Aktualisierung eines Status-Flags
    # und Abspielen der Explosionsanimation.
    def destroy(self):
        self.destroyed = True
        # Engine-Sound stoppen
        if self.engine_sounds:
            if self.current_engine_sound:
                self.current_engine_sound.stop()
            # Lenkung stoppen (NEU)
            if self.steering_sound_playing:
                self.engine_sounds["steering"].stop()
            # Regen stoppen
            if self.regen_sound_playing:
                self.regen_sound.stop()

            self.current_engine_sound = None
            self.current_engine_state = None
            self.steering_sound_playing = False
            self.regen_sound_playing = False
        print("Spielermaschine zerstört!")

    # Lässt die Spielermaschine Energie proportional zur übergebenen Kraft verlieren.
    # Beispiele für Kräfte sind die aktuelle Geschwindigkeit der Maschine, die derzeit angewendete Zentrifugalkraft, ...
    def lose_energy(self, force):
        # Verwendet einen konstanten Faktor (siehe Settings-Modul), um die aktuelle Geschwindigkeit auf Energieverlust zu skalieren.
        # Schließlich wird die individuelle Körperstärke der Maschine berücksichtigt.
        lost_energy = (abs(force) * HIT_COST_SPEED_FACTOR) * self.machine.hit_cost
        
        self.current_energy -= lost_energy