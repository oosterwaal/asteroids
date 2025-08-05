import pygame
import random

class Explosion:
    def __init__(self, x, y, radius):
        self.position = pygame.Vector2(x, y)
        self.radius = radius
        self.particles = []
        for _ in range(20):
            angle = random.uniform(0, 2 * 3.14159)
            speed = random.uniform(80, 200)
            color = random.choice([(255, 80, 0), (255, 180, 0), (255, 0, 0)])
            self.particles.append({
                'pos': pygame.Vector2(x, y),
                'vel': pygame.Vector2(speed, 0).rotate_rad(angle),
                'color': color,
                'life': random.uniform(0.3, 0.7)
            })
        self.alive = True
    def update(self, dt):
        for p in self.particles:
            p['pos'] += p['vel'] * dt
            p['life'] -= dt
        self.particles = [p for p in self.particles if p['life'] > 0]
        if not self.particles:
            self.alive = False
    def draw(self, screen):
        for p in self.particles:
            pygame.draw.circle(screen, p['color'], (int(p['pos'].x), int(p['pos'].y)), 4)
