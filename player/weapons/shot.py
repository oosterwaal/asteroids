import pygame
from mainlogic.circleshape import CircleShape
from mainlogic.constants import SHOT_RADIUS, PLAYER_SHOOT_SPEED, PLAYER_SHOOT_COOLDOWN

class Shot(CircleShape):
    containers = []
    def __init__(self, x, y, velocity):
        super().__init__(x, y, SHOT_RADIUS)
        self.velocity = velocity
    def draw(self, screen):
        pygame.draw.circle(screen, "yellow", (int(self.position.x), int(self.position.y)), int(self.radius), 2)
    def update(self, dt):
        self.position += self.velocity * dt
