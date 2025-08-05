import pygame

# Base class for game objects
class CircleShape(pygame.sprite.Sprite):
    def collides_with(self, other):
        # Returns True if this circle collides with another circle
        return self.position.distance_to(other.position) < (self.radius + other.radius)
    def __init__(self, x, y, radius):
        # Only pass pygame.sprite.Group containers to Sprite.__init__
        groups = []
        if hasattr(self, "containers"):
            for c in self.containers:
                if isinstance(c, pygame.sprite.Group):
                    groups.append(c)
        super().__init__(*groups)

        self.position = pygame.Vector2(x, y)
        self.velocity = pygame.Vector2(0, 0)
        self.radius = radius

    def draw(self, screen):
        # sub-classes must override
        pass

    def update(self, dt):
        # sub-classes must override
        pass
