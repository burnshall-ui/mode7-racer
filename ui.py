from settings.ui_settings import SPEED_DISPLAY_MULTIPLIER, NUMBER_IMAGES

# Verwaltet Aktualisierungen der UI in jedem Frame.
# Das Zeichnen der UI wird im Hauptmodul (App-Klasse) durchgeführt.
class UI:
    # Parameter:
    # player: Spieler-Instanz, die mit dieser UI-Instanz verfolgt werden soll
    # speed_meter_sprites: Array der Sprites, die den Geschwindigkeitsmesser bilden
    # timer_sprites: Array der Sprites, die den Timer bilden
    def __init__(self, player, speed_meter_sprites, timer_sprites):
        self.player = player
        self.speed_meter_sprites = speed_meter_sprites
        self.timer_sprites = timer_sprites

    # Aktualisiert (Bildkomponenten der) UI-Sprites.
    def update(self, elapsed_milliseconds):
        # Geschwindigkeitsmesser-Sprite-Bilder aktualisieren.
        # Die am wenigsten signifikante Ziffer ist bei Index 0,
        # die am meisten signifikante Ziffer ist beim maximalen Index.
        display_speed = int(abs(self.player.current_speed * SPEED_DISPLAY_MULTIPLIER))
        for i in range(0, 4):
            self.speed_meter_sprites[i].image = NUMBER_IMAGES[
                (display_speed // (10 ** i)) % 10
            ]

        # Timer-UI aktualisieren
        self.timer_sprites[0].image = NUMBER_IMAGES[
            int(elapsed_milliseconds) % 10
        ]
        self.timer_sprites[1].image = NUMBER_IMAGES[
            (int(elapsed_milliseconds) // 10) % 10
        ]
        self.timer_sprites[2].image = NUMBER_IMAGES[
            (int(elapsed_milliseconds) // 100) % 10
        ]
        self.timer_sprites[3].image = NUMBER_IMAGES[
            (int(elapsed_milliseconds) // 1000) % 10
        ]
        self.timer_sprites[4].image = NUMBER_IMAGES[
            (int(elapsed_milliseconds) // 10000) % 6
        ]
        self.timer_sprites[5].image = NUMBER_IMAGES[
            (int(elapsed_milliseconds) // 60000) % 10
        ]
        self.timer_sprites[6].image = NUMBER_IMAGES[
            (int(elapsed_milliseconds) // 600000) % 10
        ]

        # Energiebalken zeichnen