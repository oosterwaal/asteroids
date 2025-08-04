import pygame
from constants import *
from player import Player
from asteroid import Asteroid
from asteroidfield import AsteroidField

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    player = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
    updatable = [player]
    drawable = [player]

    asteroids = pygame.sprite.Group()
    Asteroid.containers = (asteroids,)
    updatable.append(asteroids)
    drawable.append(asteroids)

    from shot import Shot
    shots = pygame.sprite.Group()
    Shot.containers = (shots,)
    updatable.append(shots)
    drawable.append(shots)
    AsteroidField.containers = [updatable]
    asteroid_field = AsteroidField()

    print("Starting Asteroids!")
    print("Screen width: 1280")
    print("Screen height: 720")
    
    clock = pygame.time.Clock()
    dt = 0

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
        screen.fill((0, 0, 0))
        for obj in updatable:
            obj.update(dt)
        for asteroid in asteroids:
            if hasattr(asteroid, 'collides_with') and asteroid.collides_with(player):
                print("Game over!")
                pygame.quit()
                return

        for obj in drawable:
            if hasattr(obj, '__iter__') and not isinstance(obj, (str, bytes)):
                for member in obj:
                    if hasattr(member, 'draw'):
                        member.draw(screen)
            elif hasattr(obj, 'draw'):
                obj.draw(screen)
        pygame.display.flip()
        dt = clock.tick(60) / 1000
        for asteroid in asteroids:
            for shot in shots:
                if hasattr(asteroid, 'collides_with') and hasattr(shot, 'collides_with') and asteroid.collides_with(shot):
                    asteroid.split()
                    shot.kill()

if __name__ == "__main__":
    main()

