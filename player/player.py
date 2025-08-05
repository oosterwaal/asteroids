import pygame
from mainlogic.constants import PLAYER_RADIUS, PLAYER_TURN_SPEED, PLAYER_SPEED, PLAYER_SHOOT_SPEED, PLAYER_SHOOT_COOLDOWN

class Player(pygame.sprite.Sprite):
    def collides_with(self, other):
        # Triangular hitbox: check if any triangle vertex is inside the other, or if any edge intersects the other's circle
        triangle = self.triangle()
        # Check if any vertex is inside the other's circle
        for pt in triangle:
            if pt.distance_to(other.position) < other.radius:
                return True
        # Check if any edge intersects the other's circle
        for i in range(3):
            a = triangle[i]
            b = triangle[(i+1)%3]
            ab = b - a
            ap = other.position - a
            t = max(0, min(1, ap.dot(ab) / ab.length_squared() if ab.length_squared() else 0))
            closest = a + ab * t
            if closest.distance_to(other.position) < other.radius:
                return True
        return False

    def shoot(self):
        if self.shoot_timer > 0:
            return
        from player.weapons.shot import Shot
        direction = pygame.Vector2(0, 1).rotate(self.rotation)
        velocity = direction * PLAYER_SHOOT_SPEED
        Shot(self.position.x, self.position.y, velocity)
        self.shoot_timer = PLAYER_SHOOT_COOLDOWN
    @property
    def radius(self):
        return PLAYER_RADIUS
    @property
    def position(self):
        return pygame.Vector2(self.rect.center)
    def move(self, dt):
        direction = pygame.Vector2(0, 1).rotate(self.rotation)
        speed = PLAYER_SPEED * getattr(self, 'speed_boost', 1.0)
        movement = direction * speed * dt
        center = pygame.Vector2(self.rect.center)
        center += movement
        self.rect.center = (center.x, center.y)

    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((PLAYER_RADIUS * 2, PLAYER_RADIUS * 2), pygame.SRCALPHA)
        pygame.draw.polygon(self.image, "white", [(PLAYER_RADIUS, 0), (0, PLAYER_RADIUS), (PLAYER_RADIUS, PLAYER_RADIUS * 2)], 2)
        self.rect = self.image.get_rect(center=(x, y))
        self.rotation = 0
        self.shoot_timer = 0
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
        if self.shoot_timer > 0:
            self.shoot_timer -= dt
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            self.rotate(-dt)
        if keys[pygame.K_d]:
            self.rotate(dt)
        if keys[pygame.K_w]:
            self.move(dt)
        if keys[pygame.K_s]:
            self.move(-dt)
        if keys[pygame.K_SPACE]:
            self.shoot()
