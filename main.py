import pygame
from mainlogic.constants import *
from player import Player
from enemies.asteroid import Asteroid
from environment.asteroidfield import AsteroidField

def main():
    from player.weapons.bigbomb import BigBomb
    import random
    import os, json
    pygame.init()
    FONT = pygame.font.SysFont(None, 36)
    bomb_drops = pygame.sprite.Group()
    active_bombs = []
    has_bomb = False
    bomb_icon = FONT.render("BOMB! (B)", True, (255,100,0))
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    HIGHSCORE_FILE = "highscores.json"
    score = 0
    lives = 3
    respawn_timer = 0
    highscores = []
    def load_highscores():
        nonlocal highscores
        if os.path.exists(HIGHSCORE_FILE):
            with open(HIGHSCORE_FILE, "r") as f:
                highscores = json.load(f)
        else:
            highscores = []
    def save_highscores():
        with open(HIGHSCORE_FILE, "w") as f:
            json.dump(highscores, f)
    def add_highscore(new_score):
        highscores.append(new_score)
        highscores.sort(reverse=True)
        del highscores[10:]
        save_highscores()
    load_highscores()
    show_all_highscores = False

    player = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
    updatable = [player]
    drawable = [player]

    asteroids = pygame.sprite.Group()
    Asteroid.containers = (asteroids,)
    updatable.append(asteroids)
    drawable.append(asteroids)

    from player.weapons.shot import Shot
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
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_h:
                    show_all_highscores = not show_all_highscores
                if event.key == pygame.K_b and has_bomb:
                    # Drop bomb at player position
                    active_bombs.append(BigBomb(player.position.x, player.position.y))
                    has_bomb = False
        screen.fill((0, 0, 0))
        if respawn_timer > 0:
            respawn_timer -= dt
        for obj in updatable:
            obj.update(dt)
        # Bomb drop logic
        if random.random() < 0.002 and not has_bomb and len(bomb_drops) < 1:
            # Drop a bomb somewhere random
            bx = random.randint(100, SCREEN_WIDTH-100)
            by = random.randint(100, SCREEN_HEIGHT-100)
            bomb = pygame.sprite.Sprite()
            bomb.image = bomb_icon
            bomb.rect = bomb.image.get_rect(center=(bx, by))
            bomb.position = pygame.Vector2(bx, by)
            bomb_drops.add(bomb)
        # Bomb pickup
        for bomb in list(bomb_drops):
            if player.position.distance_to(bomb.position) < PLAYER_RADIUS + 20:
                has_bomb = True
                bomb_drops.remove(bomb)
        game_over = False
        if respawn_timer <= 0:
            for asteroid in asteroids:
                if hasattr(asteroid, 'collides_with') and asteroid.collides_with(player):
                    lives -= 1
                    if lives <= 0:
                        add_highscore(score)
                        game_over = True
                    else:
                        # Respawn player in center, invulnerable for 2 seconds
                        player.rect.center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
                        player.rotation = 0
                        respawn_timer = 2.0

        if 'game_over' in locals() and game_over:
            # Show prompt and wait for user input
            prompt_font = pygame.font.SysFont(None, 48)
            prompt = prompt_font.render("Do you wish to try again?", True, (255,255,255))
            yes = prompt_font.render("Yes (Y)", True, (0,255,0))
            no = prompt_font.render("No (N)", True, (255,0,0))
            while True:
                screen.fill((0,0,0))
                screen.blit(prompt, (SCREEN_WIDTH//2 - prompt.get_width()//2, SCREEN_HEIGHT//2 - 80))
                screen.blit(yes, (SCREEN_WIDTH//2 - yes.get_width()//2, SCREEN_HEIGHT//2))
                screen.blit(no, (SCREEN_WIDTH//2 - no.get_width()//2, SCREEN_HEIGHT//2 + 60))
                pygame.display.flip()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        return
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_y:
                            # Reset game state
                            score = 0
                            lives = 3
                            player.rect.center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
                            player.rotation = 0
                            respawn_timer = 2.0
                            # Remove all asteroids and shots
                            for a in list(asteroids):
                                a.kill()
                            for s in list(shots):
                                s.kill()
                            asteroid_field = AsteroidField()
                            break
                        if event.key == pygame.K_n:
                            pygame.quit()
                            return
                else:
                    continue
                break

        for obj in drawable:
            if hasattr(obj, '__iter__') and not isinstance(obj, (str, bytes)):
                for member in obj:
                    if hasattr(member, 'draw'):
                        member.draw(screen)
            elif hasattr(obj, 'draw'):
                obj.draw(screen)
        # Draw bomb drops
        for bomb in bomb_drops:
            screen.blit(bomb.image, bomb.rect)
        # Draw active bombs
        for bomb in list(active_bombs):
            bomb.draw(screen)
            if bomb.update(dt, asteroids):
                active_bombs.remove(bomb)
        # Draw bomb icon if player has one
        if has_bomb:
            screen.blit(bomb_icon, (SCREEN_WIDTH-200, 20))

        # Draw score, lives, and highscores
        score_surf = FONT.render(f"Score: {score}", True, (255,255,255))
        screen.blit(score_surf, (20, SCREEN_HEIGHT - 40))
        lives_surf = FONT.render(f"Lives: {lives}", True, (255,255,255))
        screen.blit(lives_surf, (20, SCREEN_HEIGHT - 80))
        # Show top 3 highscores at bottom right
        highscores_sorted = sorted(highscores, reverse=True)
        for i, hs in enumerate(highscores_sorted[:3]):
            hs_surf = FONT.render(f"{i+1}. {hs}", True, (255,255,0))
            screen.blit(hs_surf, (SCREEN_WIDTH - 200, SCREEN_HEIGHT - 40 - 30*i))
        # Show all highscores if H is pressed
        if show_all_highscores:
            pygame.draw.rect(screen, (0,0,0), (SCREEN_WIDTH-300, SCREEN_HEIGHT-350, 280, 320))
            pygame.draw.rect(screen, (255,255,255), (SCREEN_WIDTH-300, SCREEN_HEIGHT-350, 280, 320), 2)
            title = FONT.render("Highscores", True, (255,255,255))
            screen.blit(title, (SCREEN_WIDTH-250, SCREEN_HEIGHT-340))
            for i, hs in enumerate(highscores_sorted[:10]):
                hs_surf = FONT.render(f"{i+1}. {hs}", True, (255,255,0))
                screen.blit(hs_surf, (SCREEN_WIDTH-280, SCREEN_HEIGHT-310 + 28*i))

        pygame.display.flip()
        dt = clock.tick(60) / 1000
        for asteroid in asteroids:
            for shot in shots:
                if hasattr(asteroid, 'collides_with') and hasattr(shot, 'collides_with') and asteroid.collides_with(shot):
                    asteroid.split()
                    shot.kill()
                    score += 1

if __name__ == "__main__":
    main()

