import pygame
from mainlogic.constants import *
from player import Player
from enemies.asteroid import Asteroid
from environment.asteroidfield import AsteroidField

def main():
    # Power-up state
    shield_active = False
    # shield lasts until hit
    speed_active = False
    speed_timer = 0
    powerup_drops = pygame.sprite.Group()
    from player.weapons.bigbomb import Mine
    import random
    import os, json
    import math
    pygame.init()
    FONT = pygame.font.SysFont(None, 36)
    bomb_drops = pygame.sprite.Group()
    active_bombs = []
    has_bomb = False
    bomb_icon = FONT.render("MINE (M)", True, (255,255,0))
    shield_icon = FONT.render("SHIELD", True, (0,200,255))
    speed_icon = FONT.render("SPEED", True, (0,255,0))
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    score = 0
    lives = 3
    respawn_timer = 0
    # Multi-level system
    level = 1
    level_cleared = False
    max_level = 10  # You can adjust this as needed
    HIGHSCORE_FILE = "highscores.json"
    highscores = []
    show_all_highscores = False

    def add_highscore(new_score):
        # Prompt for name if new_score qualifies for highscore
        highscores_sorted = sorted(highscores, key=lambda x: x['score'], reverse=True)
        if len(highscores_sorted) < 10 or new_score > highscores_sorted[-1]['score']:
            name = show_name_popup()
            highscores.append({'name': name, 'score': new_score})
            highscores.sort(key=lambda x: x['score'], reverse=True)
            del highscores[10:]
            save_highscores()
        else:
            highscores.append({'name': '', 'score': new_score})
            highscores.sort(key=lambda x: x['score'], reverse=True)
            del highscores[10:]
            save_highscores()

    def show_name_popup():
        input_box = pygame.Rect(SCREEN_WIDTH//2-100, SCREEN_HEIGHT//2, 200, 40)
        color_inactive = pygame.Color('lightskyblue3')
        color_active = pygame.Color('dodgerblue2')
        color = color_inactive
        active = True
        text = ''
        font = pygame.font.Font(None, 48)
        prompt = font.render("New Highscore! Enter your name:", True, (255,255,255))
        clock = pygame.time.Clock()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if input_box.collidepoint(event.pos):
                        active = True
                    else:
                        active = False
                    color = color_active if active else color_inactive
                if event.type == pygame.KEYDOWN:
                    if active:
                        if event.key == pygame.K_RETURN:
                            return text if text else "Player"
                        elif event.key == pygame.K_BACKSPACE:
                            text = text[:-1]
                        else:
                            if len(text) < 12 and event.unicode.isprintable():
                                text += event.unicode
            # Draw popup over game
            popup_rect = pygame.Rect(SCREEN_WIDTH//2-220, SCREEN_HEIGHT//2-120, 440, 180)
            pygame.draw.rect(screen, (30,30,30), popup_rect)
            pygame.draw.rect(screen, (255,255,255), popup_rect, 3)
            screen.blit(prompt, (SCREEN_WIDTH//2 - prompt.get_width()//2, SCREEN_HEIGHT//2 - 80))
            txt_surface = font.render(text, True, color)
            width = max(200, txt_surface.get_width()+10)
            input_box.w = width
            screen.blit(txt_surface, (input_box.x+5, input_box.y+5))
            pygame.draw.rect(screen, color, input_box, 2)
            pygame.display.flip()
            clock.tick(30)

    def prompt_for_name():
        input_box = pygame.Rect(SCREEN_WIDTH//2-100, SCREEN_HEIGHT//2, 200, 40)
        color_inactive = pygame.Color('lightskyblue3')
        color_active = pygame.Color('dodgerblue2')
        color = color_inactive
        active = False
        text = ''
        font = pygame.font.Font(None, 48)
        prompt = font.render("New Highscore! Enter your name:", True, (255,255,255))
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if input_box.collidepoint(event.pos):
                        active = not active
                    else:
                        active = False
                    color = color_active if active else color_inactive
                if event.type == pygame.KEYDOWN:
                    if active:
                        if event.key == pygame.K_RETURN:
                            return text if text else "Player"
                        elif event.key == pygame.K_BACKSPACE:
                            text = text[:-1]
                        else:
                            if len(text) < 12 and event.unicode.isprintable():
                                text += event.unicode
            screen.fill((0,0,0))
            screen.blit(prompt, (SCREEN_WIDTH//2 - prompt.get_width()//2, SCREEN_HEIGHT//2 - 80))
            txt_surface = font.render(text, True, color)
            width = max(200, txt_surface.get_width()+10)
            input_box.w = width
            screen.blit(txt_surface, (input_box.x+5, input_box.y+5))
            pygame.draw.rect(screen, color, input_box, 2)
            pygame.display.flip()
    respawn_timer = 0
    HIGHSCORE_FILE = "highscores.json"
    highscores = []
    def load_highscores():
        nonlocal highscores
        if os.path.exists(HIGHSCORE_FILE):
            with open(HIGHSCORE_FILE, "r") as f:
                loaded = json.load(f)
                # Ensure loaded is a list of dicts with 'name' and 'score'
                if isinstance(loaded, list):
                    highscores = [hs if isinstance(hs, dict) and 'score' in hs else {'name': '', 'score': hs} for hs in loaded]
                else:
                    highscores = []
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

    def get_environment_for_level(lvl):
        """
        Load environment settings for a given level from the environments folder.
        You can expand this to load different modules or configs per level.
        """
        # Example: Use asteroidfield for all levels, but you can add more files later
        from environment.asteroidfield import get_level_config
        # get_level_config should return a dict with settings for the level
        return get_level_config(lvl)

    def start_level(lvl):
        # Clear asteroids and shots
        for a in list(asteroids):
            a.kill()
        for s in list(shots):
            s.kill()
        # Load environment settings for this level
        env = get_environment_for_level(lvl)
        num_asteroids = env.get('num_asteroids', min(3 + lvl * 2, 30))
        asteroid_sizes = env.get('asteroid_sizes', [2, 3])
        # Spawn asteroids based on environment config
        for _ in range(num_asteroids):
            ax = random.randint(50, SCREEN_WIDTH-50)
            ay = random.randint(50, SCREEN_HEIGHT-50)
            Asteroid(ax, ay, size=random.choice(asteroid_sizes))
        # Optionally adjust asteroid speed/difficulty here using env
        # Reset player position
        player.rect.center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        player.rotation = 0
        # Reset power-ups, bombs, etc. if needed
        # ...
        return

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
                if event.key == pygame.K_m and has_bomb:
                    # Drop mine at player position
                    active_bombs.append(Mine(player.position.x, player.position.y))
                    has_bomb = False
        # Power-up timers
        # Shield lasts until hit, no timer
        if speed_active:
            speed_timer -= dt
            if speed_timer <= 0:
                speed_active = False
        screen.fill((0, 0, 0))
        if respawn_timer > 0:
            respawn_timer -= dt
        for obj in updatable:
            obj.update(dt)

        # Multi-level system: check if level cleared
        if not asteroids and not level_cleared:
            level_cleared = True
            # Show level complete message
            level_font = pygame.font.SysFont(None, 64)
            msg = level_font.render(f"Level {level} Complete!", True, (0,255,0))
            screen.blit(msg, (SCREEN_WIDTH//2 - msg.get_width()//2, SCREEN_HEIGHT//2 - 100))
            pygame.display.flip()
            pygame.time.wait(1500)
            level += 1
            if level > max_level:
                # Game completed
                win_font = pygame.font.SysFont(None, 64)
                win_msg = win_font.render("You Win!", True, (255,255,0))
                screen.blit(win_msg, (SCREEN_WIDTH//2 - win_msg.get_width()//2, SCREEN_HEIGHT//2))
                pygame.display.flip()
                pygame.time.wait(2500)
                pygame.quit()
                return
            start_level(level)
            level_cleared = False
        # Power-up and bomb drop logic
        # Drop bomb
        if random.random() < 0.002 and not has_bomb and len(bomb_drops) < 1:
            bx = random.randint(100, SCREEN_WIDTH-100)
            by = random.randint(100, SCREEN_HEIGHT-100)
            bomb = pygame.sprite.Sprite()
            bomb.image = bomb_icon
            bomb.rect = bomb.image.get_rect(center=(bx, by))
            bomb.position = pygame.Vector2(bx, by)
            bomb.type = 'bomb'
            bomb_drops.add(bomb)
        # Drop shield power-up
        if random.random() < 0.001 and not shield_active and not any(getattr(p, 'type', '') == 'shield' for p in powerup_drops):
            bx = random.randint(100, SCREEN_WIDTH-100)
            by = random.randint(100, SCREEN_HEIGHT-100)
            shield = pygame.sprite.Sprite()
            shield.image = shield_icon
            shield.rect = shield.image.get_rect(center=(bx, by))
            shield.position = pygame.Vector2(bx, by)
            shield.type = 'shield'
            powerup_drops.add(shield)
        # Drop speed power-up
        if random.random() < 0.001 and not speed_active and not any(getattr(p, 'type', '') == 'speed' for p in powerup_drops):
            bx = random.randint(100, SCREEN_WIDTH-100)
            by = random.randint(100, SCREEN_HEIGHT-100)
            speed = pygame.sprite.Sprite()
            speed.image = speed_icon
            speed.rect = speed.image.get_rect(center=(bx, by))
            speed.position = pygame.Vector2(bx, by)
            speed.type = 'speed'
            powerup_drops.add(speed)
        # Bomb pickup
        for bomb in list(bomb_drops):
            if player.position.distance_to(bomb.position) < PLAYER_RADIUS + 20:
                has_bomb = True
                bomb_drops.remove(bomb)
        # Power-up pickup
        for p in list(powerup_drops):
            if player.position.distance_to(p.position) < PLAYER_RADIUS + 20:
                if p.type == 'shield':
                    shield_active = True
                elif p.type == 'speed':
                    speed_active = True
                    speed_timer = 10
                powerup_drops.remove(p)
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
            for asteroid in list(asteroids):
                if hasattr(asteroid, 'collides_with') and asteroid.collides_with(player):
                    if shield_active:
                        # Shield absorbs hit, asteroid bounces and splits/destroys
                        # Bounce asteroid away from player
                        direction = asteroid.position - player.position
                        if direction.length() == 0:
                            direction = pygame.Vector2(1, 0)
                        direction = direction.normalize()
                        asteroid.position += direction * 40
                        # Split or destroy asteroid
                        if hasattr(asteroid, 'split'):
                            asteroid.split()
                        asteroid.kill()
                        shield_active = False
                        continue
                    lives -= 1
                    if lives <= 0:
                        add_highscore(score)
                        game_over = True
                    else:
                        # Respawn player in center, invulnerable for 2 seconds
                        player.rect.center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
                        player.rotation = 0
                        respawn_timer = 2.0
        # Apply speed power-up
        if speed_active:
            player.speed_boost = 2.0
        else:
            if hasattr(player, 'speed_boost'):
                del player.speed_boost

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
        # Draw power-up drops
        for p in powerup_drops:
            screen.blit(p.image, p.rect)
        # Draw active bombs
        for bomb in list(active_bombs):
            bomb.draw(screen)
            if bomb.update(dt, asteroids):
                active_bombs.remove(bomb)
        # Draw bomb icon if player has one
        if has_bomb:
            screen.blit(bomb_icon, (SCREEN_WIDTH-200, 20))
        # Draw shield effect (blue circle) around player
        if shield_active:
            pygame.draw.circle(screen, (0,200,255), (int(player.position.x), int(player.position.y)), PLAYER_RADIUS+12, 3)
        # Draw speed effect (red tail) behind player
        if speed_active:
            tail_length = 40
            # Pygame rotation 0 is upward, so subtract 90 degrees to get forward
            angle_rad = math.radians(player.rotation - 270)
            forward_dx = math.cos(angle_rad)
            forward_dy = math.sin(angle_rad)
            start_pos = (int(player.position.x), int(player.position.y))
            end_pos = (int(player.position.x - forward_dx * tail_length), int(player.position.y - forward_dy * tail_length))
            pygame.draw.line(screen, (255,0,0), start_pos, end_pos, 6)

        # Draw score, lives, level, and highscores
        score_surf = FONT.render(f"Score: {score}", True, (255,255,255))
        screen.blit(score_surf, (20, SCREEN_HEIGHT - 40))
        lives_surf = FONT.render(f"Lives: {lives}", True, (255,255,255))
        screen.blit(lives_surf, (20, SCREEN_HEIGHT - 80))
        level_surf = FONT.render(f"Level: {level}", True, (0,255,255))
        screen.blit(level_surf, (SCREEN_WIDTH//2 - 60, 20))
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

