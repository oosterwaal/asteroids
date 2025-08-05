import pygame
from mainlogic.constants import PLAYER_RADIUS

class BigBomb(pygame.sprite.Sprite):
    def __init__(self, x, y, radius=80):
        super().__init__()
        self.position = pygame.Vector2(x, y)
        self.radius = radius
        self.timer = 0.5  # seconds until detonation
        self.exploded = False
    def update(self, dt, asteroids):
        self.timer -= dt
        if self.timer <= 0 and not self.exploded:
            self.exploded = True
            destroyed = []
            for asteroid in list(asteroids):
                if self.position.distance_to(asteroid.position) < self.radius:
                    destroyed.append(asteroid)
            for asteroid in destroyed:
                asteroid.split()
                asteroid.kill()
            return True  # signal to remove bomb
        return False
    def draw(self, screen):
        color = (255, 100, 0) if not self.exploded else (255, 255, 0)
        pygame.draw.circle(screen, color, (int(self.position.x), int(self.position.y)), int(self.radius), 2)
