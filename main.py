import pygame
from constants import *

def main():
    print("Starting Asteroids!")
    print("Screen width: 1280")
    print("Screen height: 720")

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    main()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
        screen.fill((0, 0, 0))
        pygame.display.flip()           
