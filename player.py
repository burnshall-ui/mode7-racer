import numpy
import pygame

from settings.debug_settings import IN_DEV_MODE, COLLISION_DETECTION_OFF # Debug-Konfiguration
from settings.key_settings import STD_ACCEL_KEY, STD_LEFT_KEY, STD_RIGHT_KEY, STD_BRAKE_KEY, STD_BOOST_KEY # Tastenbelegungs-Konfiguration
from settings.renderer_settings import NORMAL_ON_SCREEN_PLAYER_POSITION_X, NORMAL_ON_SCREEN_PLAYER_POSITION_Y, RENDER_SCALE # Render-Konfiguration
from settings.machine_settings import PLAYER_COLLISION_RECT_WIDTH, PLAYER_COLLISION_RECT_HEIGHT # Spieler-Kollisions-Rechteck-Konfiguration
from settings.machine_settings import HEIGHT_DURING_JUMP, HIT_COST_SPEED_FACTOR, MIN_BOUNCE_BACK_FORCE
from settings.machine_settings import OBSTACLE_HIT_SPEED_RETENTION 

from collision import CollisionRect

from animation import AnimatedMachine

class Player(pygame.sprite.Sprite, AnimatedMachine):
    # Konstruktor.
    # machine: die Maschine, die von diesem Spieler gesteuert wird
    # current_race: das Rennen, das der Spieler gerade fährt
    def __init__(self, machine, current_race):
        # Referenz auf Renn-Daten
        # um auf die Umgebung reagieren zu können
        # und die Spieler-Position initialisieren zu können
        self.current_race = current_race
        
        # Position und Rotation initialisieren (gemäß dem aktuell gefahrenen Rennen)
        self.reinitialize_position_angle()
        
        # Physik-Variablen
        self.machine = machine # enthält alle relevanten Daten zu physikalischen Eigenschaften der Spieler-Maschine
        self.current_speed = 0 # wie schnell sich der Spieler im aktuellen Frame bewegt
        self.centri = 0 # wie stark die Zentrifugalkraft ist, die im aktuellen Frame angewendet wird

        # Aktuelle Menge an Energie, die der Maschine noch bleibt
        self.current_energy = self.machine.max_energy

        # Animations-Variablen initialisieren durch Aufruf des entsprechenden Super-Klassen-Konstruktors
        AnimatedMachine.__init__(self, 
            idle_anim = self.machine.idle_anim,
            driving_anim = self.machine.driving_anim
        )
        
        # Animation auf die initiale umschalten
        self.switch_animation("driving")

        # Rendering-Variablen (für Maschine ohne Schatten).
        # Die x-Koordinate des Spielers ist immer fest,
        # die y-Koordinate normalerweise auch,
        # wird während eines Sprungs gemäß einer konfigurierten quadratischen Funktion geändert.
        pygame.sprite.Sprite.__init__(self) # Konstruktor der pygame Sprite-Klasse aufrufen (verantwortlich für Rendering)
        self.image = self.current_frame()
        self.rect = self.image.get_rect()
        self.rect.topleft = [NORMAL_ON_SCREEN_PLAYER_POSITION_X, NORMAL_ON_SCREEN_PLAYER_POSITION_Y]

        # Erstellt ein neues Sprite-Objekt für den Maschinen-Schatten,
        # der die ganze Zeit über fixiert bleibt.
        self.shadow_sprite = pygame.sprite.Sprite()
        shadow_img = pygame.image.load(self.machine.shadow_image_path)
        # Schatten skalieren entsprechend RENDER_SCALE
        if RENDER_SCALE != 1.0:
            new_width = int(shadow_img.get_width() * RENDER_SCALE)
            new_height = int(shadow_img.get_height() * RENDER_SCALE)
            shadow_img = pygame.transform.scale(shadow_img, (new_width, new_height))
        self.shadow_sprite.image = shadow_img
        self.shadow_sprite.rect = self.shadow_sprite.image.get_rect()
        # Schatten-Sprite wird so erstellt, dass es in Ordnung ist, wenn Spieler + Schatten an denselben Bildschirmkoordinaten sind
        self.shadow_sprite.rect.topleft = [NORMAL_ON_SCREEN_PLAYER_POSITION_X, NORMAL_ON_SCREEN_PLAYER_POSITION_Y]

        # Spieler Status-Flags/Variablen
        self.steering_left = False
        self.steering_right = False
        self.jumping = False
        self.jumped_off_timestamp = None # Zeitstempel, wann der Spieler zuletzt von einer Rampe gesprungen ist
        # Beim Springen: Dies ist die Dauer des Sprungs vom Start bis zur Landung.
        # Benötigt, um die y-Koordinate des Spielers auf dem Bildschirm während des Sprungs zu berechnen.
        self.current_jump_duration = 0
        self.finished = False # ob der Spieler das aktuelle Rennen beendet hat
        self.destroyed = False # ob die Spieler-Maschine zerstört wurde aufgrund eines Absturzes außerhalb der Grenzen oder keiner Energie mehr
        self.boosted = False
        self.last_boost_started_timestamp = None # Zeitstempel, wann der Spieler zuletzt einen Boost gestartet hat
        self.has_boost_power = False # ob der Spieler seinen Booster verwenden darf (wird auf False gesetzt während der ersten Runde, wechselt zu True nach Abschluss der ersten Runde)

    # Aktualisiert Spielerdaten und Position.
    # 
    # Parameter:
    # time: Anzahl der Frames seit Spielstart
    def update(self, time, delta):
        # Spieler entsprechend Steuereingaben und aktueller Geschwindigkeit bewegen
        if IN_DEV_MODE:
            self.dev_mode_movement()
        elif not self.destroyed:
            self.racing_mode_movement(time, delta)

        # Aktuelles rechteckiges Kollisions-Rechteck des Spielers speichern
        # für die Verwendung in mehreren Umgebungsprüfungen und Aktualisierungen.
        current_collision_rect = CollisionRect(
            pos = self.position,
            w = PLAYER_COLLISION_RECT_WIDTH,
            h = PLAYER_COLLISION_RECT_HEIGHT
        )

        # Rundenzählung aktualisieren.
        # Dafür benötigt das Strecken-Objekt die aktuelle Position des Spielers.
        self.current_race.update_lap_count(current_collision_rect)

        # Spieler boosten lassen, wenn auf Dash-Platte.
        # Über eine Dash-Platte springen führt natürlich nicht zu einem Boost.
        if self.current_race.is_on_dash_plate(current_collision_rect) and not self.jumping and not self.boosted:
            self.boosted = True
            self.last_boost_started_timestamp = time # Zeitstempel zur Bestimmung, wann der Boost enden soll
        if self.boosted:
            self.continue_boost(time)

        # Spieler springen lassen, wenn auf Rampe.
        # Nur springen, wenn Geschwindigkeit positiv und über Minimum (verhindert Rückwärts-Sprünge)
        MIN_JUMP_SPEED = 2.0  # Mindestgeschwindigkeit für Sprung
        if self.current_race.is_on_ramp(current_collision_rect) and not self.jumping and self.current_speed >= MIN_JUMP_SPEED:
            self.jumping = True # Status-Flag setzen
            self.current_jump_duration = self.machine.jump_duration_multiplier * self.current_speed # Dauer des Sprungs basierend auf Geschwindigkeit berechnen
            self.jumped_off_timestamp = time # Zeitstempel zur Berechnung der Höhe in späteren Frames
        if self.jumping:
            self.continue_jump(time)

        # Spieler Energie wiederherstellen lassen, wenn in Erholungszone.
        # Über eine Erholungszone springen zählt natürlich nicht.
        if self.current_race.is_on_recovery_zone(current_collision_rect) and not self.jumping:
            self.current_energy += self.machine.recover_speed * delta
            if self.current_energy > self.machine.max_energy:
                self.current_energy = self.machine.max_energy

        # Aktuelle Animation des Spielers fortführen und das Bild des Spieler-Sprites aktualisieren
        self.advance_current_animation(delta)
        self.image = self.current_frame()


    # Moves and rotates the camera freely based on player input. 
    def dev_mode_movement(self):
        # Compute sine and cosine of current angle 
        # to be able to update player position
        # based on their rotation.
        sin_a = numpy.sin(self.angle)
        cos_a = numpy.cos(self.angle)

        # Store the scaled versions of those two values for convenience.
        # Player always moves at maximum speed when in dev mode.
        speed_sin, speed_cos = self.machine.max_speed * sin_a, self.machine.max_speed * cos_a

        # Initialize the variables holding the change in player position
        # which are accumulated throughout the method.
        dx, dy = 0, 0

        # collect key events
        keys = pygame.key.get_pressed()

        # accumulate the change in player position based on the pressed keys.
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

        # Change player position
        self.position[0] += dx
        self.position[1] += dy

        # Change player rotation
        if keys[pygame.K_LEFT]:
            self.angle += self.rotation_speed
        if keys[pygame.K_RIGHT]:
            self.angle -= self.rotation_speed

        print("x: " + str(self.position[0]) + " y: " + str(self.position[1]) + " a: " + str(self.angle))

    # Moves the player's machine as in a race (accelerating, braking and steering).
    #
    # Parameters:
    # time - the timestamp of the frame update in which this call was made
    # delta - the time between this frame and the previous frame
    def racing_mode_movement(self, time, delta):
        # collect key events
        keys = pygame.key.get_pressed()

        # determine whether the player intends to start a boost in this frame
        if keys[STD_BOOST_KEY] and self.can_boost():
            self.last_boost_started_timestamp = time # take timestamp
            self.current_energy -= self.machine.boost_cost # boosting costs a bit of energy
            self.boosted = True # status flag update

        # Steering.
        if keys[STD_LEFT_KEY] and not self.finished:
            # update flags
            self.steering_left = True
            self.steering_right = False
            
            # rotate player
            self.angle += self.machine.rotation_speed * delta
            
        if keys[STD_RIGHT_KEY] and not self.finished:
            # update flags
            self.steering_left = False
            self.steering_right = True
            
            # rotate player
            self.angle -= self.machine.rotation_speed * delta

        # ------------ updating player's speed ------------------
        
        # Increase speed when acceleration button pressed.
        # Acceleration input should be ignored when the speed currently is above the machine's current max speed.
        current_max_speed = self.machine.boosted_max_speed if self.boosted else self.machine.max_speed
        if keys[STD_ACCEL_KEY] and not self.finished and not self.current_speed > current_max_speed:
            # switch to driving animation
            self.switch_to_driving_animation()

            # Increase speed
            self.current_speed += (
                self.machine.boosted_acceleration if self.boosted else self.machine.acceleration
            ) * delta
        # Decrease speed heavily when brake button pressed.
        # The player cannot brake when mid-air.
        elif keys[STD_BRAKE_KEY] and not self.finished and not self.jumping:
            # no matter whether player moves forwards or backwards:
            # transition to idle animation when player brakes
            self.switch_to_idle_animation()

            # case 1: player currently moves forwards
            if self.current_speed > 0:
                self.current_speed -= self.machine.brake * delta 
                # Clamp speed to zero since the player
                # should not be able to drive backwards.
                if self.current_speed < 0:
                    self.current_speed = 0
            # case 2: player currently moves backwards (e.g. because of bouncing back)
            elif self.current_speed < 0:
                self.current_speed += self.machine.brake * delta
                # Clamp speed to zero since the player 
                # should not go forward again
                if self.current_speed > 0:
                    self.current_speed = 0
        # Decrease speed slightly when neither acceleration nor brake button pressed.
        # Decreasing hereby means approaching zero
        # (otherwise the player would move backwards at increasing speed
        # if no button is pressed).
        else: 
            # switch to idle animation
            self.switch_to_idle_animation()

            # In this game, the player does not lose speed while jumping.
            if not self.jumping:
                # Compute and apply speed loss
                current_speed_loss = (self.machine.boosted_speed_loss 
                    if self.boosted or self.current_speed > self.machine.max_speed # stronger speed loss when machine is above its regular top speed
                    else self.machine.speed_loss) * delta
                if self.current_speed > 0:
                    self.current_speed -= current_speed_loss
                    # Clamp speed to zero (from below) to prevent jitter.
                    if self.current_speed < 0:
                        self.current_speed = 0
                elif self.current_speed < 0:
                    self.current_speed += current_speed_loss
                    # Clamp speed to zero (from above) to prevent jitter.
                    if self.current_speed > 0:
                        self.current_speed = 0




        # -------- end of updating player's speed -----------------------



        # -------- computing centrifugal force strength -----------------



        # If the player presses one of the turn buttons in the current frame,
        # the centrifugal force increases (is capped at a certain limit)
        # The increase in centrifugal forces is proportional to the player's current speed.
        if keys[STD_LEFT_KEY] or keys[STD_RIGHT_KEY]:
            self.centri += self.machine.centri_increase * self.current_speed * delta
            if self.centri > self.machine.max_centri:
                self.centri = self.machine.max_centri
        # otherwise: the applied centrifugal force decreases
        # (cannot fall below 0)
        else:
            self.centri -= self.machine.centri_decrease * delta 
            if self.centri < 0:
                self.centri = 0
                
                # When the centrifugal forces are done wearing off,
                # the turn is finished and the flags can be reset.
                self.steering_left = False
                self.steering_right = False 



        # --------- end of computing centrifugal force strength ----------



        # ---------- actual movement of the player ---------------



        # Compute movement direction from player inputs 
        # and speed + centrifugal force strength.



        # Compute sine and cosine of current angle 
        # to be able to update player position
        # based on their rotation.
        sin_a = numpy.sin(self.angle)
        cos_a = numpy.cos(self.angle)

        # Store the scaled versions of the speed and centrifugal forces directions for convenience.
        # Scale the directions with the speed 
        # and the current delta (time between current and last frame).
        # The latter scale factor must be applied to make the player speed independent of the games framerate
        speed_sin, speed_cos = self.current_speed * delta * sin_a, self.current_speed * delta * cos_a # speed
        cf_sin, cf_cos = self.centri * speed_sin * -1 * delta, self.centri * speed_cos * -1 * delta # centrifugal forces

        # Compute player's position in the next frame including the moved collision rect.
        next_frame_position_x = self.position[0] + speed_cos
        next_frame_position_y = self.position[1] + speed_sin
        frame_lookahead_collision_rect = CollisionRect(
            pos = numpy.array([next_frame_position_x, next_frame_position_y]), 
            w = PLAYER_COLLISION_RECT_WIDTH,
            h = PLAYER_COLLISION_RECT_HEIGHT
        )

        # Check if player would stay on track when moved as computed above.
        # If yes or if the player is jumping, move them.
        # If no, make them bounce back.
        #
        # Debug-only feature: if collision detection is turned off, the player is always moved, never bounced back.
        if self.current_race.is_on_track(frame_lookahead_collision_rect) or self.jumping or COLLISION_DETECTION_OFF:
            self.position[0] = next_frame_position_x
            self.position[1] = next_frame_position_y
        else:
            # If guard rails are active:
            # Player loses some energy and bounces back
            if self.current_race.guard_rails_active():
                # Player bounces back since their move speed is flipped.
                # Player does not retain all of its speed.
                # There is a minimal force that is always applied
                # to prevent the player getting stuck outside the track boundaries.
                self.current_speed = -(self.current_speed * OBSTACLE_HIT_SPEED_RETENTION + MIN_BOUNCE_BACK_FORCE)

                # Player loses energy.
                self.lose_energy(self.current_speed)

                # player machine is destroyed if it has taken more damage than it can sustain
                if self.current_energy < 0:
                    self.destroy()
            # If no guard rails are active:
            # player machine is destroyed
            else:
                self.destroy()



        # ----------------- application of centrifugal forces



        # compute player position in next frame
        if self.steering_left:
            next_frame_position_x = self.position[0] - cf_sin
            next_frame_position_y = self.position[1] + cf_cos
        if self.steering_right:
            next_frame_position_x = self.position[0] + cf_sin
            next_frame_position_y = self.position[1] - cf_cos

        # -------------- determining whether centrifugal forces should be applied -------------------
        
        

        # compute position of player in next frame
        frame_lookahead_collision_rect = CollisionRect(
            pos = numpy.array([next_frame_position_x, next_frame_position_y]),
            w = PLAYER_COLLISION_RECT_WIDTH,
            h = PLAYER_COLLISION_RECT_HEIGHT
        )

        # Check if the player would stay on the track when moved as above.
        # If so (or the player is jumping or the collision detection is turned off in debug mode), move them.
        # Else, make the player lose some energy or destroy the player machine
        # (depending on whether the track has active guard rails).
        if self.current_race.is_on_track(frame_lookahead_collision_rect) or self.jumping or COLLISION_DETECTION_OFF:
            self.position[0] = next_frame_position_x
            self.position[1] = next_frame_position_y
        else:
            if self.current_race.guard_rails_active():
                # centrifugal force is reset
                self.centri = 0

                # player gets damaged proportional to force currently applied
                self.lose_energy(self.centri)

                # player machine destroyed if out of energy
                if self.current_energy < 0:
                    self.destroy()
            else: 
                # player machine immediately destroyed if track has no guard rails active
                self.destroy()



        # ------------------ end of application of centrifugal forces ------------ 



        # ------ end of actual movement of the player -----------------------
    
    # Updates player status flags and moves the player
    # to its current screen Y position
    # depending on the time since the player jumped off the track.
    def continue_jump(self, time):
        # compute time since jump started
        elapsed_time = time - self.jumped_off_timestamp

        # moving up on screen = decreasing the y coordinate
        self.rect.topleft = [
            NORMAL_ON_SCREEN_PLAYER_POSITION_X, 
            NORMAL_ON_SCREEN_PLAYER_POSITION_Y - HEIGHT_DURING_JUMP(elapsed_time, self.current_jump_duration)
        ]

        # End jump (reset status flag) if jump duration reached
        # To prevent any visual artifacts, the player rect is reset to its normal y position on screen.
        if elapsed_time >= self.current_jump_duration:
            self.jumping = False

            self.rect.topleft = [
                NORMAL_ON_SCREEN_PLAYER_POSITION_X, NORMAL_ON_SCREEN_PLAYER_POSITION_Y
            ]

            # if the player lands out of the track bounds, they have failed the run
            current_collision_rect = CollisionRect(
                self.position,
                PLAYER_COLLISION_RECT_WIDTH,
                PLAYER_COLLISION_RECT_HEIGHT
            )
            if not self.current_race.is_on_track(current_collision_rect):
                print("player out of bounds!")
                self.destroy()

    # Called once per frame if the player currently has a booster active.
    # Checks whether the booster should end since its duration has exceeded.
    def continue_boost(self, time):
        # compute time since boost started
        elapsed_time = time - self.last_boost_started_timestamp

        # check whether boost should end
        if elapsed_time > self.machine.boost_duration:
            self.boosted = False

    # Determines whether the player is currently able to use their boost power.
    # (i)   player must have booster unlocked (i.e. completed first lap, usually)
    # (ii)  player cannot have a boost active at the moment
    # (iii) player has to have enough energy
    def can_boost(self):
        return self.has_boost_power and not self.boosted and self.current_energy >= self.machine.boost_cost

    # (Re-)sets the player object to the initial position
    # for the current race track.
    # Also resets all forces that are currently applied to the player.
    # Example usage: get the player to the start position at the start of a race
    def reinitialize(self):
        # reset position and rotation
        self.reinitialize_position_angle()

        # reset forces
        self.current_speed = 0
        self.centri = 0

        # reset energy to max
        self.current_energy = self.machine.max_energy

        # reset status flags
        self.jumping = False
        self.finished = False
        self.destroyed = False
        self.boosted = False
        self.has_boost_power = False
        self.steering_left = False
        self.steering_right = False

        # reset screen position
        self.rect.topleft = [
            NORMAL_ON_SCREEN_PLAYER_POSITION_X,
            NORMAL_ON_SCREEN_PLAYER_POSITION_Y
        ]

    # Resets the position and rotation of the player to the initial ones prescribed by the current race. 
    def reinitialize_position_angle(self):
        self.position = numpy.array([self.current_race.init_player_pos_x, self.current_race.init_player_pos_y])
        self.angle = self.current_race.init_player_angle

    # Destroys the player machine by updating a status flag
    # and playing the explosion animation.
    def destroy(self):
        self.destroyed = True
        print("player machine destroyed!")

    # Makes the player machine lose energy proportional to the passed force.
    # Examples for forces are the machines current speed, the currently applied centrifugal force, ...
    def lose_energy(self, force):
        # Uses a constant factor (see settings module) to scale current speed to energy loss.
        # Lastly, the individual body strength of the machine is taken into account.
        lost_energy = (abs(force) * HIT_COST_SPEED_FACTOR) * self.machine.hit_cost
        
        self.current_energy -= lost_energy