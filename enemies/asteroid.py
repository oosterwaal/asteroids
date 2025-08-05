import pygame
from mainlogic.circleshape import CircleShape

class Asteroid(CircleShape):

    def split(self):
        import random
        from mainlogic.constants import ASTEROID_MIN_RADIUS
        self.kill()
        if self.radius <= ASTEROID_MIN_RADIUS:
            return
        random_angle = random.uniform(20, 50)
        v1 = self.velocity.rotate(random_angle) * 1.2
        v2 = self.velocity.rotate(-random_angle) * 1.2
        new_radius = self.radius - ASTEROID_MIN_RADIUS
        Asteroid(self.position.x, self.position.y, new_radius).velocity = v1
        Asteroid(self.position.x, self.position.y, new_radius).velocity = v2
    containers = []

    def __init__(self, x, y, radius):
        super().__init__(x, y, radius)
        import math, random
        self._num_points = random.randint(12, 18)
        angle_step = 2 * math.pi / self._num_points
        self._shape = []
        for i in range(self._num_points):
            angle = i * angle_step
            lump = random.uniform(0.75, 1.25)
            r = self.radius * lump
            self._shape.append((r, angle))

    def draw(self, screen):
        import math
        points = []
        for r, angle in self._shape:
            x = self.position.x + r * math.cos(angle)
            y = self.position.y + r * math.sin(angle)
            points.append((x, y))
        pygame.draw.polygon(screen, "white", points, 2)

    def update(self, dt):
        self.position += self.velocity * dt
