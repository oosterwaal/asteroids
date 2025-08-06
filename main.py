
import pygame
from mainlogic.constants import *
from player import Player
from enemies.asteroid import Asteroid
from environment.asteroidfield import AsteroidField

def main():

    # Key bindings dictionary
    key_bindings = {
        'laser': pygame.K_l,
        'mine': pygame.K_m,
        'settings': pygame.K_s,
        'highscores': pygame.K_h
    }

    def show_settings_menu():
        menu_font = pygame.font.SysFont(None, 48)
        info_font = pygame.font.SysFont(None, 32)
        selected = None
        running = True
        while running:
            screen.fill((20, 20, 40))
            title = menu_font.render("Settings: Change Key Bindings", True, (255,255,255))
            screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 100))
            y = 200
            for action, key in key_bindings.items():
                key_name = pygame.key.name(key)
                txt = info_font.render(f"{action.capitalize()}: {key_name}", True, (200,200,200) if selected != action else (255,255,0))
                screen.blit(txt, (SCREEN_WIDTH//2 - 200, y))
                y += 50
            prompt = info_font.render("Press UP/DOWN to select, ENTER to change, ESC to exit", True, (180,180,255))
            screen.blit(prompt, (SCREEN_WIDTH//2 - prompt.get_width()//2, y+30))
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                        break
                    actions = list(key_bindings.keys())
                    if selected is None:
                        selected = actions[0]
                    elif event.key == pygame.K_DOWN:
                        idx = actions.index(selected)
                        selected = actions[(idx+1)%len(actions)]
                    elif event.key == pygame.K_UP:
                        idx = actions.index(selected)
                        selected = actions[(idx-1)%len(actions)]
                    elif event.key == pygame.K_RETURN:
                        # Wait for next key press
                        waiting = True
                        while waiting:
                            for e in pygame.event.get():
                                if e.type == pygame.KEYDOWN and e.key != pygame.K_RETURN:
                                    key_bindings[selected] = e.key
                                    waiting = False
                                elif e.type == pygame.QUIT:
                                    pygame.quit()
                                    exit()
        return
    # Laser feature removed
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
    # Load background images for each level
    background_images = []
    for i in range(1, 11):
        try:
            img = pygame.image.load(f"backgrounds/background{i}.png").convert()
            img = pygame.transform.scale(img, (SCREEN_WIDTH, SCREEN_HEIGHT))
            background_images.append(img)
        except Exception:
            # If image not found, use a solid color
            bg = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            bg.fill((10 + i*10, 10 + i*10, 30 + i*10))
            background_images.append(bg)
    score = 0
    lives = 3
    respawn_timer = 0
    # Multi-level system
    level = 1
    level_cleared = False  # Ensure level does not start as complete
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
    # Only keep the correct add_highscore function (already defined above)
    # ...existing code...
    def destroy_asteroid(asteroid):
        """
        Handles splitting and removal of asteroids, and increments score.
        """
        # Only increment score if asteroid was alive before
        was_alive = asteroid.alive()
        r = getattr(asteroid, 'radius', 0)
        small_limit = max(PLAYER_RADIUS, player.rect.width // 2) * 1.5
        if r <= small_limit:
            asteroid.kill()
        else:
            if hasattr(asteroid, 'split'):
                asteroid.split()
            asteroid.kill()
        if was_alive and not asteroid.alive():
            nonlocal score
            score += 1

    def show_start_screen():
        start_font = pygame.font.SysFont(None, 72)
        info_font = pygame.font.SysFont(None, 36)
        waiting = True
        while waiting:
            screen.fill((10, 10, 30))
            title = start_font.render("ASTEROIDS", True, (255,255,255))
            prompt = info_font.render("Press ENTER to Start", True, (0,255,0))
            screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, SCREEN_HEIGHT//2 - 120))
            screen.blit(prompt, (SCREEN_WIDTH//2 - prompt.get_width()//2, SCREEN_HEIGHT//2))
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        waiting = False
                        break
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
        # Asteroid count: Level 1 = 100, each next level +25, max 10 levels
        total_asteroids = min(100 + (lvl - 1) * 25, 325)
        # Wave size logic
        if lvl == 1:
            wave_size = 5
        elif lvl < 5:
            wave_size = 10
        elif lvl < 10:
            wave_size = 15
        else:
            wave_size = 20
        # Ensure minimum asteroid size is at least the player's visual size
        min_size = max(PLAYER_RADIUS, player.rect.width // 2)
        asteroid_sizes = env.get('asteroid_sizes', [min_size, int(min_size * 1.5), int(min_size * 2)])
        asteroid_sizes = [size for size in asteroid_sizes if size >= min_size]
        if not asteroid_sizes:
            asteroid_sizes = [int(min_size * 2)]
        # Wave spawning state
        nonlocal wave_spawned, wave_timer, asteroids_spawned, current_wave_size, total_asteroids_to_spawn
        wave_spawned = 0
        wave_timer = 0.0
        asteroids_spawned = 0
        current_wave_size = wave_size
        total_asteroids_to_spawn = total_asteroids
        # Reset player position
        player.rect.center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        player.rotation = 0
        # Reset power-ups, bombs, etc. if needed
        # ...
        # Do NOT spawn any asteroids here; let the wave logic handle it
        return
    # Wave spawning state variables
    wave_spawned = 0
    wave_timer = 0.0
    asteroids_spawned = 0
    current_wave_size = 5
    total_asteroids_to_spawn = 100
    level_started = False  # New flag to track if asteroids have spawned

    show_start_screen()
    print("Starting Asteroids!")
    # Start the first level so asteroids are present
    start_level(level)
    level_cleared = False  # Ensure level does not start as complete
    clock = pygame.time.Clock()
    dt = 0

    while True:
        game_over = False
        # --- MOVEMENT LOGIC BLOCK ---
        # Handle input and movement
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN:
                if event.key == key_bindings['highscores']:
                    show_all_highscores = not show_all_highscores
                if event.key == pygame.K_q:
                    show_settings_menu()
        # Power-up timers
        if speed_active:
            speed_timer -= dt
            if speed_timer <= 0:
                speed_active = False
        # Draw background for current level
        bg_idx = min(level-1, len(background_images)-1)
        screen.blit(background_images[bg_idx], (0, 0))
        if respawn_timer > 0:
            respawn_timer -= dt
        # Asteroid wave spawning logic
        # For level 1, max asteroids on screen is 5
        if level == 1:
            max_asteroids_on_screen = 5
            current_wave_size = 5  # Ensure only 5 spawn per wave
        else:
            max_asteroids_on_screen = current_wave_size * 2
        wave_delay = 2.5  # seconds between waves
        # Only spawn if we haven't reached the total for the level
        if asteroids_spawned < total_asteroids_to_spawn:
            wave_timer += dt
            # Strict cap: never allow more than 5 asteroids in level 1
            if wave_timer >= wave_delay and ((level != 1 and len(asteroids) < max_asteroids_on_screen) or (level == 1 and len(asteroids) < 5)):
                available_slots = 5 - len(asteroids) if level == 1 else max_asteroids_on_screen - len(asteroids)
                remaining_to_spawn = total_asteroids_to_spawn - asteroids_spawned
                spawn_count = min(current_wave_size, available_slots, remaining_to_spawn)
                if spawn_count > 0:
                    min_size = max(PLAYER_RADIUS, player.rect.width // 2)
                    asteroid_sizes = [min_size, int(min_size * 1.5), int(min_size * 2)]
                    for _ in range(spawn_count):
                        # Spawn asteroids offscreen
                        edge = random.randint(0, 3)
                        if edge == 0:
                            ax = -60
                            ay = random.randint(0, SCREEN_HEIGHT)
                        elif edge == 1:
                            ax = SCREEN_WIDTH + 60
                            ay = random.randint(0, SCREEN_HEIGHT)
                        elif edge == 2:
                            ax = random.randint(0, SCREEN_WIDTH)
                            ay = -60
                        else:
                            ax = random.randint(0, SCREEN_WIDTH)
                            ay = SCREEN_HEIGHT + 60
                        radius = random.choice(asteroid_sizes)
                        asteroid = Asteroid(ax, ay, radius)
                        angle = random.uniform(0, 2 * math.pi)
                        speed = random.uniform(80, 180)
                        asteroid.velocity = pygame.Vector2(math.cos(angle), math.sin(angle)) * speed
                    asteroids_spawned += spawn_count
                    wave_timer = 0.0
                    level_started = True
        for obj in updatable:
            obj.update(dt)

        # --- WEAPON LOGIC BLOCK ---
        # Handle weapon input and update
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == key_bindings['mine'] and has_bomb:
                    active_bombs.append(Mine(player.position.x, player.position.y))
                    has_bomb = False

        # Laser feature removed

        # Shot collision logic
        for asteroid in asteroids:
            for shot in shots:
                if hasattr(asteroid, 'collides_with') and hasattr(shot, 'collides_with') and asteroid.collides_with(shot):
                    destroy_asteroid(asteroid)
                    shot.kill()

        # Multi-level system: check if level cleared
        if level_started and not asteroids and not level_cleared:
            level_cleared = True
            level_font = pygame.font.SysFont(None, 64)
            msg = level_font.render(f"Level {level} Complete!", True, (0,255,0))
            screen.blit(msg, (SCREEN_WIDTH//2 - msg.get_width()//2, SCREEN_HEIGHT//2 - 100))
            pygame.display.flip()
            pygame.time.wait(1500)
            level += 1
            if level > max_level:
                win_font = pygame.font.SysFont(None, 64)
                win_msg = win_font.render("You Are Victorious!", True, (255,255,0))
                screen.blit(win_msg, (SCREEN_WIDTH//2 - win_msg.get_width()//2, SCREEN_HEIGHT//2))
                pygame.display.flip()
                pygame.time.wait(2500)
                pygame.quit()
                return
            start_level(level)
            level_cleared = False
            level_started = False  # Reset for next level
        # Power-up and bomb drop logic (consolidated, only during active gameplay)
        if not level_cleared and not game_over:
            # Drop bomb (relax condition: allow more frequent drops if none present)
            if random.random() < 0.01 and not has_bomb and len(bomb_drops) < 1:
                bx = random.randint(100, SCREEN_WIDTH-100)
                by = random.randint(100, SCREEN_HEIGHT-100)
                bomb = pygame.sprite.Sprite()
                bomb.image = bomb_icon
                bomb.rect = bomb.image.get_rect(center=(bx, by))
                bomb.position = pygame.Vector2(bx, by)
                bomb.type = 'bomb'
                bomb_drops.add(bomb)
            # Drop shield power-up (relax condition: allow more frequent drops if none present)
            if random.random() < 0.005 and not shield_active and not any(getattr(p, 'type', '') == 'shield' for p in powerup_drops):
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
                            # Fully reset game state
                            score = 0
                            lives = 3
                            level = 1
                            level_cleared = False
                            respawn_timer = 0
                            shield_active = False
                            speed_active = False
                            speed_timer = 0
                            has_bomb = False
                            active_bombs.clear()
                            bomb_drops.empty()
                            powerup_drops.empty()
                            player.rect.center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
                            player.rotation = 0
                            # Remove all asteroids and shots
                            for a in list(asteroids):
                                a.kill()
                            for s in list(shots):
                                s.kill()
                            asteroid_field = AsteroidField()
                            start_level(level)
                            level_started = False
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
        # Laser feature removed

        # Draw score, lives, level, and highscores
        score_surf = FONT.render(f"Score: {score}", True, (255,255,255))
        screen.blit(score_surf, (20, SCREEN_HEIGHT - 40))
        lives_surf = FONT.render(f"Lives: {lives}", True, (255,255,255))
        screen.blit(lives_surf, (20, SCREEN_HEIGHT - 80))
        level_surf = FONT.render(f"Level: {level}", True, (0,255,255))
        screen.blit(level_surf, (SCREEN_WIDTH//2 - 60, 20))
        # Show top 3 highscores at bottom right
        highscores_sorted = sorted(highscores, key=lambda x: x['score'], reverse=True)
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
                    destroy_asteroid(asteroid)
                    shot.kill()

if __name__ == "__main__":
    main()

