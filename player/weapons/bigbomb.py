import pygame
from mainlogic.constants import PLAYER_RADIUS

class Mine(pygame.sprite.Sprite):
    def __init__(self, x, y, radius=80):
        super().__init__()
        self.position = pygame.Vector2(x, y)
        self.radius = radius
        self.armed = False
        self.timer = 0.5  # seconds until armed
        self.exploded = False

    def update(self, dt, asteroids):
        if not self.armed:
            self.timer -= dt
            if self.timer <= 0:
                self.armed = True
        if self.armed and not self.exploded:
            for asteroid in list(asteroids):
                if self.position.distance_to(asteroid.position) < self.radius:
                    self.exploded = True
                    asteroid.split()
                    asteroid.kill()
            if self.exploded:
                return True  # signal to remove mine
        return False

    def draw(self, screen):
        color = (255, 255, 0) if self.armed else (150, 150, 150)
        x, y = int(self.position.x), int(self.position.y)
        # Draw asterisk
        pygame.draw.line(screen, color, (x-10, y), (x+10, y), 2)
        pygame.draw.line(screen, color, (x, y-10), (x, y+10), 2)
        pygame.draw.line(screen, color, (x-7, y-7), (x+7, y+7), 2)
        pygame.draw.line(screen, color, (x-7, y+7), (x+7, y-7), 2)
