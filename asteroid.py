import pygame
from circleshape import CircleShape

class Asteroid(CircleShape):

    def split(self):
        import random
        from constants import ASTEROID_MIN_RADIUS
        self.kill()
        if self.radius <= ASTEROID_MIN_RADIUS:
            return
        random_angle = random.uniform(20, 50)
        v1 = self.velocity.rotate(random_angle) * 1.2
        v2 = self.velocity.rotate(-random_angle) * 1.2
        new_radius = self.radius - ASTEROID_MIN_RADIUS
        from asteroid import Asteroid
        Asteroid(self.position.x, self.position.y, new_radius).velocity = v1
        Asteroid(self.position.x, self.position.y, new_radius).velocity = v2
    containers = []

    def __init__(self, x, y, radius):
        super().__init__(x, y, radius)

    def draw(self, screen):
        pygame.draw.circle(screen, "white", (int(self.position.x), int(self.position.y)), int(self.radius), 2)

    def update(self, dt):
        self.position += self.velocity * dt
