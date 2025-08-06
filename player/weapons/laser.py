import pygame
import math
from mainlogic.constants import *

class Laser:
    def __init__(self, player):
        self.player = player
        self.active = True
        self.timer = 10.0  # seconds
        self.width = 8
        self.color = (255, 0, 0)

    def update(self, dt, asteroids):
        if not self.active:
            return False
        self.timer -= dt
        if self.timer <= 0:
            self.active = False
            return True  # signal to remove
        # Calculate laser direction
        angle_rad = math.radians(self.player.rotation - 270)
        start_pos = pygame.Vector2(self.player.position.x, self.player.position.y)
        # Limit laser length to twice the ship's size
        if hasattr(self.player.rect, 'width'):
            max_length = 2 * self.player.rect.width
        else:
            max_length = 2 * getattr(self.player, 'radius', 40)
        end_pos = pygame.Vector2(
            self.player.position.x + math.cos(angle_rad) * max_length,
            self.player.position.y + math.sin(angle_rad) * max_length
        )
        # Destroy asteroids in path
        for asteroid in list(asteroids):
            # Simple collision: check if asteroid center is close to laser line
            ap = pygame.Vector2(asteroid.position.x, asteroid.position.y)
            laser_vec = end_pos - start_pos
            point_vec = ap - start_pos
            proj = point_vec.dot(laser_vec) / laser_vec.length_squared() if laser_vec.length_squared() > 0 else 0
            closest = start_pos + laser_vec * proj
            dist = ap.distance_to(closest)
            if 0 <= proj <= 1 and dist < asteroid.radius + self.width:
                asteroid.kill()
        return False

    def draw(self, screen):
        if not self.active:
            return
        angle_rad = math.radians(self.player.rotation - 270)
        start_pos = (int(self.player.position.x), int(self.player.position.y))
        # Limit laser length to twice the ship's size
        if hasattr(self.player.rect, 'width'):
            max_length = 2 * self.player.rect.width
        else:
            max_length = 2 * getattr(self.player, 'radius', 40)
        end_pos = (
            int(self.player.position.x + math.cos(angle_rad) * max_length),
            int(self.player.position.y + math.sin(angle_rad) * max_length)
        )
        pygame.draw.line(screen, self.color, start_pos, end_pos, self.width)
