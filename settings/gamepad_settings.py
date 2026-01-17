# Gamepad/Controller-Einstellungen
# Funktioniert mit den meisten USB-Controllern (Logitech, Xbox, PlayStation, etc.)

# ==================== ACHSEN-KONFIGURATION ====================
# Achsen-Index für Lenkung (normalerweise linker Stick horizontal)
GAMEPAD_STEER_AXIS = 0

# Deadzone - Werte unter diesem Schwellwert werden ignoriert
# Verhindert ungewollte Bewegung wenn der Stick nicht ganz zentriert ist
GAMEPAD_DEADZONE = 0.2

# Empfindlichkeit der Lenkung (1.0 = normal, höher = empfindlicher)
GAMEPAD_STEER_SENSITIVITY = 1.0


# ==================== BUTTON-KONFIGURATION ====================
# PS3-Style Controller (Logitech F310/F710, Dual Action, etc.):
#
#        [L1/4]                              [R1/5]
#        [L2/6]                              [R2/7]
#
#           ^                            (3) Dreieck
#       < D-Pad >     [Select] [Start]   (2) Quadrat  (1) Kreis
#           v            [8]     [9]         (0) X / Kreuz
#
#       [Linker Stick]              [Rechter Stick]
#
# Tipp: Setze GAMEPAD_DEBUG = True und starte das Spiel,
#       dann siehst du in der Konsole welcher Button welche Nummer hat!

GAMEPAD_GAS_BUTTON = 0       # X / Kreuz (Gas geben)
GAMEPAD_BRAKE_BUTTON = 3     # Dreieck (Bremsen)
GAMEPAD_BOOST_BUTTON = 1     # Kreis (Boost)
GAMEPAD_CONFIRM_BUTTON = 0   # X / Kreuz (Bestätigen in Menüs)
GAMEPAD_PAUSE_BUTTON = 9     # Start (Pause-Menü) - manchmal auch 7

# ==================== D-PAD FÜR STEUERUNG ====================
# Bei PS3-Style Controllern ist das D-Pad oft ein "Hat" (POV-Switch)
# Setze auf True um D-Pad statt Stick für Lenkung zu verwenden
USE_DPAD_FOR_STEERING = True


# ==================== ALTERNATIVE: TRIGGER-GAS ====================
# Bei Controllern mit Analog-Triggern (Xbox, PlayStation)
# Setze auf True um rechten Trigger als Gas zu verwenden
USE_TRIGGER_FOR_GAS = False
GAMEPAD_GAS_TRIGGER_AXIS = 5    # Rechter Trigger (Xbox: 5, manche: 4)
GAMEPAD_BRAKE_TRIGGER_AXIS = 2  # Linker Trigger


# ==================== D-PAD ====================
# D-Pad für Menü-Navigation (falls der Controller einen hat)
# Bei manchen Controllern ist D-Pad als Achsen (Axis), bei anderen als Buttons
GAMEPAD_DPAD_IS_AXIS = True      # True = D-Pad sind Achsen, False = D-Pad sind Buttons
GAMEPAD_DPAD_X_AXIS = 4          # Horizontale D-Pad Achse
GAMEPAD_DPAD_Y_AXIS = 5          # Vertikale D-Pad Achse
# Falls D-Pad Buttons sind:
GAMEPAD_DPAD_UP_BUTTON = 11
GAMEPAD_DPAD_DOWN_BUTTON = 12
GAMEPAD_DPAD_LEFT_BUTTON = 13
GAMEPAD_DPAD_RIGHT_BUTTON = 14


# ==================== DEBUG ====================
# Auf True setzen um Button/Achsen-Nummern in der Konsole anzuzeigen
# WICHTIG: Zum Testen auf True setzen, dann Buttons drücken und Nummern notieren!
GAMEPAD_DEBUG = False
