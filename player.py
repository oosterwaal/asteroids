import pygame
from constants import PLAYER_RADIUS, PLAYER_TURN_SPEED, PLAYER_SPEED

class Player(pygame.sprite.Sprite):
    def move(self, dt):
        direction = pygame.Vector2(0, 1).rotate(self.rotation)
        movement = direction * PLAYER_SPEED * dt
        center = pygame.Vector2(self.rect.center)
        center += movement
        self.rect.center = (center.x, center.y)

    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((PLAYER_RADIUS * 2, PLAYER_RADIUS * 2), pygame.SRCALPHA)
        pygame.draw.polygon(self.image, "white", [(PLAYER_RADIUS, 0), (0, PLAYER_RADIUS), (PLAYER_RADIUS, PLAYER_RADIUS * 2)], 2)
        self.rect = self.image.get_rect(center=(x, y))
        self.rotation = 0
    def triangle(self):
        forward = pygame.Vector2(0, 1).rotate(self.rotation)
        right = pygame.Vector2(0, 1).rotate(self.rotation + 90) * PLAYER_RADIUS / 1.5
        center = pygame.Vector2(self.rect.center)
        a = center + forward * PLAYER_RADIUS
        b = center - forward * PLAYER_RADIUS - right
        c = center - forward * PLAYER_RADIUS + right
        return [a, b, c]
    def draw(self, screen):
        pygame.draw.polygon(screen, "white", self.triangle(), 2)

    def rotate(self, dt):
        self.rotation += PLAYER_TURN_SPEED * dt

    def update(self, dt):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            self.rotate(-dt)
        if keys[pygame.K_d]:
            self.rotate(dt)
        if keys[pygame.K_w]:
            self.move(dt)
        if keys[pygame.K_s]:
            self.move(-dt)
