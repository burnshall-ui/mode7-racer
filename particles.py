import pygame
import random

class SparkParticle(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # Funken sind sehr klein (2x2 oder 3x3 Pixel)
        size = random.randint(2, 4)
        self.image = pygame.Surface((size, size))
        
        # Farbe: Zufallsmischung aus grellem Gelb, Orange und Weiß
        colors = [
            (255, 255, 100), # Helles Gelb
            (255, 200, 50),  # Orange
            (255, 255, 255)  # Weiß (Glutkern)
        ]
        self.image.fill(random.choice(colors))
        self.rect = self.image.get_rect(center=(x, y))

        # Physik: Explosionsartiges Wegspritzen
        # Funken fliegen eher seitlich weg
        self.vx = random.uniform(-6, 6) 
        self.vy = random.uniform(-6, 2) # Eher nach oben (in Fahrtrichtung weg) oder zufällig
        
        self.lifetime = random.randint(5, 15) # Sehr kurze Lebensdauer

    def update(self):
        self.rect.x += self.vx
        self.rect.y += self.vy
        
        # Schwerkraft simulieren (Funken fallen schnell)
        self.vy += 0.8
        
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.kill()

