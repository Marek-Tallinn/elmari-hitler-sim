import sys
import math
import pygame
from player import Player
from coin import Coin
from robber import Robber
from terrorist import Terrorist
from star import Star
from timestop_coin import TimeStopCoin
from powerup import CollectorPowerUp
from heart import Heart
from boss import Boss
from boss_two import BossTwo
from video_intro import play_intro, play_boss_intro
from gas_missile import GasMissile
from rage_coin import RageCoin

pygame.init()
pygame.mixer.init(44100, -16, 2, 2048)
pygame.mixer.music.load('music.mp3')
pygame.mixer.music.set_volume(0.3)
ADDCOIN = pygame.USEREVENT + 1
pygame.time.set_timer(ADDCOIN, 500)
ADDROBBER = pygame.USEREVENT + 2
pygame.time.set_timer(ADDROBBER, 1500)
ADDTERRORIST = pygame.USEREVENT + 3
pygame.time.set_timer(ADDTERRORIST, 2000)
ADDSTAR = pygame.USEREVENT + 4
pygame.time.set_timer(ADDSTAR, 2500)
ADDTIMESTOPCOIN = pygame.USEREVENT + 5
pygame.time.set_timer(ADDTIMESTOPCOIN, 8000)
ADDPOWERUP = pygame.USEREVENT + 6
pygame.time.set_timer(ADDPOWERUP, 12000)
ADDHEART = pygame.USEREVENT + 7
pygame.time.set_timer(ADDHEART, 6500)
ADDRAGECOIN = pygame.USEREVENT + 8
pygame.time.set_timer(ADDRAGECOIN, 1000)


coin_sfx = pygame.mixer.Sound('coin.mp3')
robber_sfx = pygame.mixer.Sound('robber_parem.mp3')
star_sfx = pygame.mixer.Sound('star.mp3')
game_over_sfx = pygame.mixer.Sound('gameover.mp3')
timestop_sfx = pygame.mixer.Sound('timestop.mp3')
try:
    gas_bomb_sfx = pygame.mixer.Sound('gas_bomb_placeholder.mp3')
except (pygame.error, FileNotFoundError):
    gas_bomb_sfx = pygame.mixer.Sound('star.mp3')

def _build_heart_surface(size, color):
    surface = pygame.Surface((size, size), pygame.SRCALPHA)
    left_center = (int(size * 0.35), int(size * 0.35))
    right_center = (int(size * 0.65), int(size * 0.35))
    radius = int(size * 0.25)
    pygame.draw.circle(surface, color, left_center, radius)
    pygame.draw.circle(surface, color, right_center, radius)
    points = [
        (int(size * 0.15), int(size * 0.45)),
        (int(size * 0.5), int(size * 0.9)),
        (int(size * 0.85), int(size * 0.45)),
    ]
    pygame.draw.polygon(surface, color, points)
    return surface

BOSS_HEART_SIZE = 24
boss_full_heart = _build_heart_surface(BOSS_HEART_SIZE, (220, 30, 70))
boss_empty_heart = _build_heart_surface(BOSS_HEART_SIZE, (90, 90, 90))

def _stop_player(player):
    if player is None:
        return
    player.moving_up = False
    player.moving_down = False
    player.moving_left = False
    player.moving_right = False

def open_pause_menu(stats, player=None, user_initiated=False):
    if stats.pause_menu_open:
        stats.menu_open_via_user = stats.menu_open_via_user or user_initiated
        return
    stats.pause_menu_open = True
    stats.menu_open_via_user = user_initiated
    stats.pause_started_at = pygame.time.get_ticks()
    _stop_player(player)

def close_pause_menu(stats, adjust_wave_timer=True):
    if not stats.pause_menu_open:
        return
    if adjust_wave_timer and stats.pause_started_at and stats.wave_start_time:
        paused_duration = pygame.time.get_ticks() - stats.pause_started_at
        stats.wave_start_time += paused_duration
    stats.pause_menu_open = False
    stats.pause_started_at = 0
    stats.menu_open_via_user = False
    stats.skill_menu_open = False

def _has_infinite_bombs(game_settings):
    return bool(getattr(game_settings, 'infinite_gas_bombs', False))

def ensure_infinite_bombs_if_enabled(stats, game_settings):
    if not _has_infinite_bombs(game_settings):
        return
    if stats.max_bombs <= 0:
        stats.max_bombs = 1
    stats.bombs_available = stats.max_bombs

def check_events(game_settings, screen, player, coins, robbers, terrorists, stars, powerups, hearts, timestop_coins, rage_coins, bosses, gas_missiles, stats, sb, play_button, menu_buttons):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            update_record_and_quit(stats)
        elif event.type == pygame.KEYDOWN:
            if stats.upgrade_menu_open:
                handle_upgrade_keypress(event.key, stats, sb)
                continue
            if stats.skill_menu_open:
                handle_skill_menu_keypress(event.key, stats)
                continue
            if event.key == pygame.K_ESCAPE:
                if stats.pause_menu_open:
                    close_pause_menu(stats)
                else:
                    open_pause_menu(stats, player, user_initiated=True)
                continue
            if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                player.moving_right = True
            if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                player.moving_left = True
            if event.key == pygame.K_UP or event.key == pygame.K_w:
                player.moving_up = True
            if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                player.moving_down = True
            if event.key == pygame.K_m:
                stats.music_on = not stats.music_on
                check_music(stats)
            if event.key == pygame.K_r:
                activate_gas_bomb(screen, stats, sb, game_settings, gas_missiles, bosses, player)
            if event.key == pygame.K_t:
                activate_time_stop(stats)
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                player.moving_right = False
            if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                player.moving_left = False
            if event.key == pygame.K_UP or event.key == pygame.K_w:
                player.moving_up = False
            if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                player.moving_down = False
        elif event.type == ADDCOIN and stats.game_active and not stats.upgrade_menu_open and not stats.pause_menu_open:
            add_coin(game_settings, screen, coins, stats)
        elif event.type == ADDROBBER and stats.game_active and not stats.upgrade_menu_open and not stats.pause_menu_open:
            add_robber(game_settings, screen, robbers, stats)
        elif event.type == ADDTERRORIST and stats.game_active and not stats.upgrade_menu_open and not stats.pause_menu_open:
            add_terrorist(game_settings, screen, terrorists, stats)
        elif event.type == ADDSTAR and stats.game_active and not stats.upgrade_menu_open and not stats.pause_menu_open:
            add_star(game_settings, screen, stars, stats)
        elif event.type == ADDPOWERUP and stats.game_active and not stats.upgrade_menu_open and not stats.pause_menu_open:
            add_powerup(game_settings, screen, powerups, stats)
        elif event.type == ADDHEART and stats.game_active and not stats.upgrade_menu_open and not stats.pause_menu_open:
            add_heart(game_settings, screen, hearts, stats)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            groups = [coins, robbers, terrorists, stars, powerups, hearts, timestop_coins, rage_coins, bosses, gas_missiles]
            if stats.pause_menu_open and handle_pause_menu_click(stats, player, menu_buttons, mouse_x, mouse_y):
                continue
            if stats.pause_menu_open:
                continue
            check_play_button(game_settings, screen, stats, sb, play_button, mouse_x, mouse_y, groups)
        elif event.type == ADDTIMESTOPCOIN and stats.game_active and not stats.upgrade_menu_open and not stats.pause_menu_open:
            add_timestop_coin(game_settings, screen, timestop_coins, stats)
        elif event.type == ADDRAGECOIN and stats.game_active and not stats.upgrade_menu_open and not stats.pause_menu_open:
            add_rage_coin(game_settings, screen, rage_coins, stats)
   
def check_play_button(game_settings, screen, stats, sb, play_button, mouse_x, mouse_y, sprite_groups):
    if play_button.rect.collidepoint(mouse_x, mouse_y):
        music_was_playing = pygame.mixer.music.get_busy()
        if music_was_playing:
            pygame.mixer.music.pause()
        try:
            play_intro(screen, game_settings)
        finally:
            if music_was_playing:
                pygame.mixer.music.unpause()
        stats.reset_stats()
        _set_music_track('music.mp3', stats, volume=0.3)
        ensure_infinite_bombs_if_enabled(stats, game_settings)
        stats.game_active = True
        stats.game_fresh = False
        for group in sprite_groups:
            group.empty()
        sb.prepare_score()
        sb.prepare_level()
        sb.prepare_record()
        sb.prepare_multiplier()
        stats.wave_start_time = pygame.time.get_ticks()

def handle_pause_menu_click(stats, player, menu_buttons, mouse_x, mouse_y):
    resume_button = menu_buttons.get('resume')
    skill_button = menu_buttons.get('skills')
    exit_button = menu_buttons.get('exit')

    if resume_button and resume_button.rect.collidepoint(mouse_x, mouse_y):
        if stats.upgrade_menu_open:
            close_upgrade_menu(stats, resume_play=True)
        elif stats.skill_menu_open:
            close_skill_menu(stats, resume_play=True)
        else:
            close_pause_menu(stats)
        return True

    if skill_button and skill_button.rect.collidepoint(mouse_x, mouse_y):
        if not stats.skill_menu_open:
            open_skill_menu(stats, player, ensure_pause=False)
        return True

    if exit_button and exit_button.rect.collidepoint(mouse_x, mouse_y):
        update_record_and_quit(stats)
        return True

    return False

def update_timestop_coins(player, timestop_coins, stats, sb, game_settings):
    hit_coin = pygame.sprite.spritecollideany(player, timestop_coins)
    if hit_coin:
        hit_coin.kill()
        if stats.time_stops_available < stats.max_time_stops:
            stats.time_stops_available += 1
        else:
            coin_sfx.play()

def add_timestop_coin(game_settings, screen, timestop_coins, stats):
    new_timestop_coin = TimeStopCoin(screen, game_settings, stats)
    timestop_coins.add(new_timestop_coin)

def update_rage_coins(player, rage_coins, stats):
    if stats.rage_active:
        rage_coins.empty()
        return
    hit_coin = pygame.sprite.spritecollideany(player, rage_coins)
    if not hit_coin:
        return
    hit_coin.kill()
    coin_sfx.play()
    activate_rage_mode(stats)

def add_rage_coin(game_settings, screen, rage_coins, stats):
    if stats.rage_active or len(rage_coins) > 0:
        return
    now = pygame.time.get_ticks()
    if getattr(stats, 'rage_next_available_time', 0) > now:
        return
    rage_coin = RageCoin(screen, game_settings, stats)
    rage_coins.add(rage_coin)

def update_screen(game_settings, screen, player, coins, timestop_coins, rage_coins, robbers, terrorists, stars, powerups, hearts, bosses, gas_missiles, clock, sb, play_button, menu_buttons, stats):
    player.blit_me()

    sprite_groups = [coins, timestop_coins, rage_coins, robbers, terrorists, stars, powerups, hearts, bosses, gas_missiles]
    for sprite_group in sprite_groups:
        for sprite in sprite_group:
            sprite.blit_me()

    if stats.time_stopped:
        overlay = pygame.Surface((game_settings.screen_width, game_settings.screen_height), pygame.SRCALPHA)
        overlay.fill((100, 100, 255, 100))
        screen.blit(overlay, (0, 0))
    if stats.gas_bomb_active and stats.gas_bomb_zone:
        overlay = pygame.Surface((game_settings.screen_width, game_settings.screen_height), pygame.SRCALPHA)
        center, radius = stats.gas_bomb_zone
        pygame.draw.circle(overlay, (0, 255, 0, 90), center, radius)
        screen.blit(overlay, (0, 0))

    draw_boss_health(screen, bosses, stats)
    draw_bomb_inventory(screen, game_settings, stats)
    draw_timestop_inventory(screen, game_settings, stats)
    draw_powerup_guides(screen, game_settings)
    draw_wave_status(screen, game_settings, stats)
    draw_rage_status(screen, game_settings, stats)
    if stats.pause_menu_open:
        draw_pause_menu(screen, game_settings, stats, menu_buttons)
    if stats.upgrade_menu_open:
        draw_upgrade_menu(screen, game_settings, stats)
    if stats.skill_menu_open:
        draw_skill_menu(screen, game_settings, stats)

    if not stats.game_active:
        play_button.draw_button()
    if not stats.game_fresh:
        sb.draw_score()

    clock.tick(120)
    pygame.display.flip()

    
def add_coin(game_settings, screen, coins, stats):
    new_coin = Coin(screen, game_settings, stats)
    coins.add(new_coin)
    
def add_robber(game_settings, screen, robbers, stats):
    new_robber = Robber(screen, game_settings, stats)
    robbers.add(new_robber)

def add_terrorist(game_settings, screen, terrorists, stats):
    new_terrorist = Terrorist(screen, game_settings, stats)
    terrorists.add(new_terrorist)

def add_star(game_settings, screen, stars, stats):
    new_star = Star(screen, game_settings, stats)
    stars.add(new_star)
    
def add_powerup(game_settings, screen, powerups, stats):
    new_powerup = CollectorPowerUp(screen, game_settings, stats)
    powerups.add(new_powerup)

def add_heart(game_settings, screen, hearts, stats):
    new_heart = Heart(screen, game_settings, stats)
    hearts.add(new_heart)

def handle_level_up(stats, sb, game_settings):
    if (int(stats.score / game_settings.bonus_score)) > stats.bonus:
        stats.level += 1
        sb.prepare_level()
        stats.bonus += 1
        stats.speed_progress += 0.5
        if stats.speed_progress >= 1.0:
            increment = int(stats.speed_progress)
            stats.min_speed += increment
            stats.max_speed += increment
            stats.speed_progress -= increment

def apply_score_gain(stats, sb, game_settings, base_points):
    if base_points <= 0:
        return
    scaled_gain = max(1, int(round(base_points * stats.score_multiplier)))
    actual_gain = max(1, scaled_gain + stats.flat_score_bonus)
    stats.score += actual_gain
    handle_level_up(stats, sb, game_settings)
    sb.prepare_score()

def handle_sprite_collision(player, sprite_group, sound, score_change, stats, sb, game_settings):
    hit_sprite = pygame.sprite.spritecollideany(player, sprite_group)
    if hit_sprite == None:
        return False
    sound.play()
    if score_change is not None:
        apply_score_gain(stats, sb, game_settings, score_change)
    hit_sprite.kill()
    return True

def update_coins(player, coins, stats, sb, game_settings):
    handle_sprite_collision(player, coins, coin_sfx, 1, stats, sb, game_settings)

def update_robbers(player, robbers, stats, sb, game_settings):
    hitted_robber = pygame.sprite.spritecollideany(player, robbers)
    if hitted_robber is not None and getattr(stats, 'rage_active', False):
        hitted_robber.kill()
        apply_score_gain(stats, sb, game_settings, 1)
        player.is_penalised = False
        return
    if hitted_robber != None and not player.is_penalised:
        robber_sfx.play()
        if stats.score > 5:
            stats.score -= 5
            player.is_penalised = True
        else:
            stats.score = 0
            player.is_penalised = True
    elif hitted_robber == None:
        player.is_penalised = False
    sb.prepare_score()
    
def update_terrorists(player, terrorists, stats, sb, game_settings):
    hitted_terrorist = pygame.sprite.spritecollideany(player, terrorists)
    if hitted_terrorist is not None and getattr(stats, 'rage_active', False):
        hitted_terrorist.kill()
        apply_score_gain(stats, sb, game_settings, 1)
        return
    if hitted_terrorist != None:
        hitted_terrorist.kill()
        if stats.health > 0:
            stats.health -= 1
        if stats.health <= 0:
            game_over_sfx.play()
            update_record(stats)
            stats.min_speed = 1
            stats.max_speed = 5
            stats.game_active = False
        else:
            robber_sfx.play()
    sb.prepare_score()
    sb.prepare_level()
    sb.prepare_record()

def update_stars(player, stars, stats, sb, game_settings):
    handle_sprite_collision(player, stars, star_sfx, 5, stats, sb, game_settings)

def update_hearts(player, hearts, stats):
    hit_heart = pygame.sprite.spritecollideany(player, hearts)
    if hit_heart == None:
        return
    hit_heart.kill()
    if stats.health < stats.max_health:
        stats.health += 1
        star_sfx.play()
    else:
        coin_sfx.play()

def update_powerups(player, powerups, coins, stars, robbers, terrorists, stats, sb, game_settings):
    hit_powerup = pygame.sprite.spritecollideany(player, powerups)
    if hit_powerup == None:
        return
    hit_powerup.kill()
    if stats.bombs_available < stats.max_bombs:
        stats.bombs_available += 1
        star_sfx.play()
    else:
        coin_sfx.play()

def activate_gas_bomb(screen, stats, sb, game_settings, gas_missiles, bosses, player):
    infinite_bombs = _has_infinite_bombs(game_settings)
    if not infinite_bombs:
        if stats.bombs_available <= 0:
            return
        stats.bombs_available -= 1
    else:
        stats.bombs_available = stats.max_bombs
    if stats.boss_active and bosses:
        target = bosses.sprites()[0].rect.center
    else:
        target = pygame.mouse.get_pos()
    direction = (target[0] - player.rect.centerx, target[1] - player.rect.centery)
    missile = GasMissile(screen, player.rect.center, direction, game_settings)
    gas_missiles.add(missile)

def activate_time_stop(stats):
    if stats.time_stops_available <= 0 or stats.time_stopped:
        return
    stats.time_stops_available -= 1
    timestop_sfx.play()
    stats.time_stopped = True
    stats.time_stop_start = pygame.time.get_ticks()

def activate_rage_mode(stats):
    if stats.rage_active:
        return
    stats.rage_active = True
    stats.rage_start_time = pygame.time.get_ticks()
    stats.rage_next_available_time = stats.rage_start_time + getattr(stats, 'rage_cooldown_ms', 45000)
    _set_music_track('rage.mp3', stats, volume=1.0)

def update_rage_status(stats):
    if not getattr(stats, 'rage_active', False):
        return
    if stats.rage_start_time == 0:
        stats.rage_active = False
        return
    elapsed = pygame.time.get_ticks() - stats.rage_start_time
    if elapsed >= getattr(stats, 'rage_duration_ms', 15000):
        stats.rage_active = False
        stats.rage_start_time = 0
        _set_music_track('music.mp3', stats, volume=0.3)

def update_gas_missiles(gas_missiles, stats, sb, game_settings, coins, stars, robbers, terrorists, bosses, player):
    if len(gas_missiles) == 0:
        return

    explosions = []
    for missile in gas_missiles.sprites():
        missile.update()
        if missile.ready_to_explode():
            explosions.append(missile.consume_explosion_center())
            continue

        explosion_needed = False

        hits = pygame.sprite.spritecollide(missile, robbers, True)
        if hits:
            apply_score_gain(stats, sb, game_settings, len(hits) * 5)
            explosion_needed = True

        hits = pygame.sprite.spritecollide(missile, terrorists, True)
        if hits:
            apply_score_gain(stats, sb, game_settings, len(hits) * 5)
            explosion_needed = True

        if stats.boss_active and bosses:
            boss = bosses.sprites()[0]
            if boss.rect.colliderect(missile.rect):
                stats.boss_hp -= 1
                explosion_needed = True
                if stats.boss_hp <= 0:
                    finish_boss_fight(stats, sb, bosses, player)

        if explosion_needed:
            missile.trigger_explosion()
            explosions.append(missile.consume_explosion_center())

    for center in explosions:
        handle_gas_explosion(center, stats, sb, game_settings, coins, stars, robbers, terrorists, bosses, player)


def handle_gas_explosion(center, stats, sb, game_settings, coins, stars, robbers, terrorists, bosses, player):
    gas_bomb_sfx.play()
    stats.gas_bomb_active = True
    stats.gas_bomb_start = pygame.time.get_ticks()
    base = min(game_settings.screen_width, game_settings.screen_height) * 0.4
    radius = int(base * stats.gas_bomb_radius_scale)
    if stats.gas_bomb_global:
        radius = int(math.hypot(game_settings.screen_width, game_settings.screen_height))
    stats.gas_bomb_zone = (center, radius)

    def remove_in_radius(group):
        removed = 0
        for sprite in list(group.sprites()):
            if _distance_sq(sprite.rect.center, center) <= radius * radius:
                sprite.kill()
                removed += 1
        return removed

    kills = remove_in_radius(robbers) + remove_in_radius(terrorists)
    if kills > 0:
        apply_score_gain(stats, sb, game_settings, kills * 5)

    coins_collected = remove_in_radius(coins)
    stars_collected = remove_in_radius(stars)
    score_from_pickups = coins_collected + stars_collected * 5
    if score_from_pickups > 0:
        apply_score_gain(stats, sb, game_settings, score_from_pickups)

    if stats.boss_active and bosses:
        boss = bosses.sprites()[0]
        if _circle_rect_overlap(center, radius, boss.rect):
            stats.boss_hp -= 1
            if stats.boss_hp <= 0:
                finish_boss_fight(stats, sb, bosses, player)


def _distance_sq(a, b):
    dx = a[0] - b[0]
    dy = a[1] - b[1]
    return dx * dx + dy * dy


def _circle_rect_overlap(center, radius, rect):
    cx, cy = center
    rx, ry = rect.center
    dx = max(abs(cx - rx) - rect.width / 2, 0)
    dy = max(abs(cy - ry) - rect.height / 2, 0)
    return dx * dx + dy * dy <= radius * radius

def draw_bomb_inventory(screen, game_settings, stats):
    icon_size = 34
    spacing = 10
    base_x = 10
    base_y = game_settings.screen_height - icon_size - 10
    infinite_bombs = _has_infinite_bombs(game_settings)
    for i in range(stats.max_bombs):
        rect = pygame.Rect(
            base_x + i * (icon_size + spacing),
            base_y,
            icon_size,
            icon_size,
        )
        filled = infinite_bombs or i < stats.bombs_available
        bg_color = (40, 150, 60) if filled else (70, 70, 70)
        border_color = (15, 50, 20) if filled else (40, 40, 40)
        pygame.draw.rect(screen, border_color, rect, border_radius=6)
        inner = rect.inflate(-4, -4)
        pygame.draw.rect(screen, bg_color, inner, border_radius=4)
        pygame.draw.circle(screen, (230, 255, 230), inner.center, icon_size // 3, 3)

def draw_timestop_inventory(screen, game_settings, stats):
    icon_size = 34
    spacing = 10
    total_width = stats.max_time_stops * icon_size + max(0, stats.max_time_stops - 1) * spacing
    base_x = game_settings.screen_width - total_width - 10
    base_y = game_settings.screen_height - icon_size - 10
    for i in range(stats.max_time_stops):
        rect = pygame.Rect(
            base_x + i * (icon_size + spacing),
            base_y,
            icon_size,
            icon_size,
        )
        filled = i < stats.time_stops_available
        bg_color = (70, 130, 180) if filled else (70, 70, 70)
        border_color = (30, 60, 90) if filled else (40, 40, 40)
        pygame.draw.rect(screen, border_color, rect, border_radius=6)
        inner = rect.inflate(-4, -4)
        pygame.draw.rect(screen, bg_color, inner, border_radius=4)
        pygame.draw.line(screen, (240, 240, 255), inner.midtop, inner.midbottom, 3)

def draw_wave_status(screen, game_settings, stats):
    font = pygame.font.SysFont(None, 32)
    if stats.boss_active:
        title = f"WAVE {stats.wave_number} - BOSS"
        timer_text = f"HP: {stats.boss_hp}"
    else:
        title = f"WAVE {stats.wave_number}"
        if stats.upgrade_menu_open:
            timer_text = "UPGRADE READY"
        elif not stats.game_active:
            timer_text = "PAUSED"
        else:
            elapsed = pygame.time.get_ticks() - stats.wave_start_time if stats.wave_start_time else 0
            remaining = max(0, stats.wave_duration - elapsed)
            timer_text = f"{remaining // 1000:02d}s"
    text_surface = font.render(f"{title} - {timer_text}", True, (255, 255, 255))
    rect = text_surface.get_rect()
    rect.midtop = (game_settings.screen_width // 2, 10)
    bg = pygame.Surface((rect.width + 20, rect.height + 10), pygame.SRCALPHA)
    bg.fill((0, 0, 0, 120))
    bg_rect = bg.get_rect(center=rect.center)
    screen.blit(bg, bg_rect)
    screen.blit(text_surface, rect)

def draw_rage_status(screen, game_settings, stats):
    font = pygame.font.SysFont(None, 30)
    padding = 12
    base_pos = (padding, 140)
    now = pygame.time.get_ticks()
    if getattr(stats, 'rage_active', False):
        remaining = max(0, (stats.rage_duration_ms + stats.rage_start_time) - now)
        seconds = remaining / 1000
        label = f"RAGE: {seconds:0.1f}s"
        color = (255, 100, 80)
    else:
        cooldown = max(0, getattr(stats, 'rage_next_available_time', 0) - now)
        if cooldown <= 0:
            label = "RAGE READY"
            color = (255, 220, 120)
        else:
            label = f"RAGE CD: {cooldown // 1000}s"
            color = (200, 200, 200)
    text_surface = font.render(label, True, color)
    rect = text_surface.get_rect(topleft=base_pos)
    bg = pygame.Surface((rect.width + padding, rect.height + padding), pygame.SRCALPHA)
    bg.fill((0, 0, 0, 140))
    bg_rect = bg.get_rect()
    bg_rect.topleft = (rect.left - padding // 2, rect.top - padding // 2)
    screen.blit(bg, bg_rect)
    screen.blit(text_surface, rect)

def draw_boss_health(screen, bosses, stats):
    if not stats.boss_active or not bosses:
        return
    boss = bosses.sprites()[0]
    total = stats.boss_max_hp
    spacing = 6
    total_width = total * BOSS_HEART_SIZE + (total - 1) * spacing
    start_x = boss.rect.centerx - total_width // 2
    y = boss.rect.top - BOSS_HEART_SIZE - 10
    for i in range(total):
        heart = boss_full_heart if i < stats.boss_hp else boss_empty_heart
        rect = heart.get_rect()
        rect.topleft = (start_x + i * (BOSS_HEART_SIZE + spacing), y)
        screen.blit(heart, rect)
    
def update_waves(stats, player, bosses, game_settings, screen):
    if not stats.game_active:
        return
    if stats.pause_menu_open:
        return
    if stats.boss_active:
        return
    if stats.wave_number % 5 == 0:
        if not stats.boss_spawned_for_wave and not stats.upgrade_menu_open:
            spawn_boss(game_settings, screen, bosses, stats)
        return
    if stats.upgrade_menu_open:
        return
    if stats.wave_start_time == 0:
        stats.wave_start_time = pygame.time.get_ticks()
    elapsed = pygame.time.get_ticks() - stats.wave_start_time
    if elapsed < stats.wave_duration:
        return
    advance_wave(stats, player)

def advance_wave(stats, player):
    stats.waves_completed += 1
    stats.wave_number += 1
    stats.wave_start_time = 0
    stats.boss_spawned_for_wave = False
    if stats.waves_completed % 2 == 0:
        open_upgrade_menu(stats, player)
    else:
        stats.wave_start_time = pygame.time.get_ticks()

def _select_boss_variant(stats):
    """Return the boss class and HP for the upcoming encounter."""
    if stats.wave_number <= 0:
        boss_round = 1
    else:
        boss_round = max(1, stats.wave_number // 5)
    if boss_round % 2 == 0:
        return BossTwo, 8
    return Boss, 5

def spawn_boss(game_settings, screen, bosses, stats):
    bosses.empty()
    boss_cls, boss_hp = _select_boss_variant(stats)
    if boss_cls is BossTwo:
        music_was_playing = pygame.mixer.music.get_busy() if stats.music_on else False
        if music_was_playing:
            pygame.mixer.music.pause()
        try:
            play_boss_intro(screen, game_settings)
        finally:
            if music_was_playing and stats.music_on:
                pygame.mixer.music.unpause()
    new_boss = boss_cls(screen, game_settings)
    bosses.add(new_boss)
    stats.boss_active = True
    stats.boss_max_hp = boss_hp
    stats.boss_hp = boss_hp
    stats.boss_spawned_for_wave = True
    stats.wave_start_time = 0

def finish_boss_fight(stats, sb, bosses, player):
    bosses.empty()
    stats.boss_active = False
    stats.boss_hp = 0
    stats.skill_points += stats.skill_points_per_boss
    advance_wave(stats, player)
    sb.prepare_score()
    sb.prepare_level()

def open_upgrade_menu(stats, player=None, ensure_pause=True, user_initiated=False):
    if ensure_pause:
        open_pause_menu(stats, player, user_initiated=user_initiated)
    else:
        _stop_player(player)
    stats.upgrade_menu_open = True
    stats.skill_menu_open = False
    stats.upgrade_menu_page = 'shop'

def close_upgrade_menu(stats, resume_play=True):
    stats.upgrade_menu_open = False
    if resume_play and stats.wave_start_time == 0 and stats.wave_number % 5 != 0:
        stats.wave_start_time = pygame.time.get_ticks()
    if resume_play:
        close_pause_menu(stats, adjust_wave_timer=stats.menu_open_via_user)

def open_skill_menu(stats, player=None, ensure_pause=True, user_initiated=False):
    if ensure_pause:
        open_pause_menu(stats, player, user_initiated=user_initiated)
    else:
        _stop_player(player)
    stats.skill_menu_open = True
    stats.upgrade_menu_open = False

def close_skill_menu(stats, resume_play=True):
    stats.skill_menu_open = False
    if resume_play and stats.wave_start_time == 0 and stats.wave_number % 5 != 0:
        stats.wave_start_time = pygame.time.get_ticks()
    if resume_play:
        close_pause_menu(stats, adjust_wave_timer=stats.menu_open_via_user)

def _key_to_option_index(key):
    if pygame.K_1 <= key <= pygame.K_9:
        return key - pygame.K_1
    if key == pygame.K_0:
        return 9
    return None

def _toggle_upgrade_menu_page(stats):
    stats.upgrade_menu_page = 'skills' if stats.upgrade_menu_page == 'shop' else 'shop'

def get_purchase_options_for_page(stats):
    if stats.upgrade_menu_page == 'skills':
        return get_skill_options(stats)
    return get_upgrade_options(stats)

def handle_upgrade_keypress(key, stats, sb):
    if key == pygame.K_TAB:
        _toggle_upgrade_menu_page(stats)
        return
    if key == pygame.K_ESCAPE:
        close_upgrade_menu(stats, resume_play=not stats.menu_open_via_user)
        return
    idx = _key_to_option_index(key)
    if idx is None:
        return
    options = get_purchase_options_for_page(stats)
    if idx >= len(options):
        return
    option = options[idx]
    if not option['enabled']:
        return
    if option['type'] == 'skill':
        success = apply_skill(option['id'], stats, sb)
    else:
        success = apply_upgrade(option['id'], stats, sb)
    if success:
        close_upgrade_menu(stats, resume_play=not stats.menu_open_via_user)

def handle_skill_menu_keypress(key, stats):
    if key == pygame.K_ESCAPE:
        close_skill_menu(stats, resume_play=not stats.menu_open_via_user)

def get_upgrade_options(stats):
    options = []

    timestop_cost = 75 + stats.timestop_upgrade_level * 25
    timestop_available = stats.timestop_upgrade_level < stats.max_timestop_upgrades
    options.append({
        'type': 'upgrade',
        'id': 'timestop',
        'label': 'Extend Time Stop (+1s)',
        'cost': timestop_cost,
        'available': timestop_available,
        'enabled': timestop_available and stats.score >= timestop_cost,
        'description': 'Freeze enemies longer when you press T.'
    })

    heart_cost = 120 + stats.heart_upgrade_level * 60
    heart_available = stats.max_health < stats.max_health_cap
    options.append({
        'type': 'upgrade',
        'id': 'heart',
        'label': 'Increase Heart Capacity (+1)',
        'cost': heart_cost,
        'available': heart_available,
        'enabled': heart_available and stats.score >= heart_cost,
        'description': 'Raise the life cap (max 5 hearts).'
    })

    mult_cost = 90 + stats.multiplier_upgrade_level * 45
    mult_available = stats.multiplier_upgrade_level < stats.max_multiplier_upgrades
    options.append({
        'type': 'upgrade',
        'id': 'multiplier',
        'label': 'Boost Score Multiplier (+0.1x)',
        'cost': mult_cost,
        'available': mult_available,
        'enabled': mult_available and stats.score >= mult_cost,
        'description': 'Earn more points from every pickup.'
    })

    return options

def apply_upgrade(option_id, stats, sb):
    if option_id == 'timestop' and stats.timestop_upgrade_level < stats.max_timestop_upgrades:
        cost = 75 + stats.timestop_upgrade_level * 25
        if stats.score < cost:
            return False
        stats.score -= cost
        stats.timestop_upgrade_level += 1
        stats.time_stop_duration += 1000
    elif option_id == 'heart' and stats.max_health < stats.max_health_cap:
        cost = 120 + stats.heart_upgrade_level * 60
        if stats.score < cost:
            return False
        stats.score -= cost
        stats.heart_upgrade_level += 1
        stats.max_health = min(stats.max_health + 1, stats.max_health_cap)
        stats.health = stats.max_health
    elif option_id == 'multiplier' and stats.multiplier_upgrade_level < stats.max_multiplier_upgrades:
        cost = 90 + stats.multiplier_upgrade_level * 45
        if stats.score < cost:
            return False
        stats.score -= cost
        stats.multiplier_upgrade_level += 1
        stats.recalc_multiplier()
        sb.prepare_multiplier()
    else:
        return False
    sb.prepare_score()
    return True

SKILL_TREE_NODES = [
    {
        'id': 'skill_extra_time_stop',
        'label': 'Reserve Battery',
        'branch': 'Chrono',
        'description': '+1 max Time Stop charge and fully refills them.',
        'cost': 1,
        'requires': None,
    },
    {
        'id': 'skill_time_freeze_mastery',
        'label': 'Frozen Reality',
        'branch': 'Chrono',
        'description': '+1.5s Time Stop duration.',
        'cost': 2,
        'requires': 'skill_extra_time_stop',
    },
    {
        'id': 'skill_extra_bomb',
        'label': 'Spare Canister',
        'branch': 'Arsenal',
        'description': '+1 max Gas Bomb and grants one immediately.',
        'cost': 1,
        'requires': None,
    },
    {
        'id': 'skill_bomb_radiation',
        'label': 'Pressurised Payload',
        'branch': 'Arsenal',
        'description': 'Gas Bomb explosion radius increases greatly.',
        'cost': 2,
        'requires': 'skill_extra_bomb',
    },
    {
        'id': 'skill_bomb_cataclysm',
        'label': 'Total Saturation',
        'branch': 'Arsenal',
        'description': 'Gas Bombs engulf the entire arena.',
        'cost': 3,
        'requires': 'skill_bomb_radiation',
    },
    {
        'id': 'skill_combo_instinct',
        'label': 'Combo Sense',
        'branch': 'Economy',
        'description': '+0.2x score multiplier.',
        'cost': 1,
        'requires': None,
    },
    {
        'id': 'skill_coin_alchemy',
        'label': 'Coin Alchemy',
        'branch': 'Economy',
        'description': 'Each pickup grants +1 bonus score.',
        'cost': 2,
        'requires': 'skill_combo_instinct',
    },
]

SKILL_TREE_LOOKUP = {node['id']: node for node in SKILL_TREE_NODES}

def get_skill_options(stats):
    options = []
    for node in SKILL_TREE_NODES:
        unlocked = node['id'] in stats.unlocked_skills
        requires = node.get('requires')
        prereq_met = requires is None or requires in stats.unlocked_skills
        available = (not unlocked) and prereq_met
        requires_label = SKILL_TREE_LOOKUP[requires]['label'] if requires else None
        options.append({
            'type': 'skill',
            'id': node['id'],
            'label': node['label'],
            'branch': node['branch'],
            'cost': node['cost'],
            'currency': 'SP',
            'description': node['description'],
            'available': available,
            'enabled': available and stats.skill_points >= node['cost'],
            'unlocked': unlocked,
            'prereq_met': prereq_met,
            'requires': requires,
            'requires_label': requires_label,
        })
    return options

def apply_skill(skill_id, stats, sb):
    node = SKILL_TREE_LOOKUP.get(skill_id)
    if node is None:
        return False
    if skill_id in stats.unlocked_skills:
        return False
    requires = node.get('requires')
    if requires and requires not in stats.unlocked_skills:
        return False
    cost = node['cost']
    if stats.skill_points < cost:
        return False
    stats.skill_points -= cost
    stats.unlocked_skills.add(skill_id)

    if skill_id == 'skill_extra_time_stop':
        stats.max_time_stops += 1
        stats.time_stops_available = stats.max_time_stops
    elif skill_id == 'skill_time_freeze_mastery':
        stats.time_stop_duration += 1500
    elif skill_id == 'skill_extra_bomb':
        stats.max_bombs += 1
        stats.bombs_available = stats.max_bombs
    elif skill_id == 'skill_bomb_radiation':
        stats.gas_bomb_radius_scale += 0.5
    elif skill_id == 'skill_bomb_cataclysm':
        stats.gas_bomb_global = True
    elif skill_id == 'skill_combo_instinct':
        stats.skill_multiplier_bonus += 0.2
        stats.recalc_multiplier()
        sb.prepare_multiplier()
    elif skill_id == 'skill_coin_alchemy':
        stats.flat_score_bonus += 1
    else:
        stats.unlocked_skills.remove(skill_id)
        stats.skill_points += cost
        return False

    return True

def draw_pause_menu(screen, game_settings, stats, menu_buttons):
    overlay = pygame.Surface((game_settings.screen_width, game_settings.screen_height), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))
    screen.blit(overlay, (0, 0))

    title_font = pygame.font.SysFont(None, 72)
    title = 'PAUSED' if stats.game_active else 'MENU'
    title_surface = title_font.render(title, True, (255, 255, 255))
    title_rect = title_surface.get_rect()
    title_rect.center = (game_settings.screen_width // 2, game_settings.screen_height // 2 - 160)
    screen.blit(title_surface, title_rect)

    if not stats.upgrade_menu_open and not stats.skill_menu_open:
        for button in menu_buttons.values():
            button.draw_button()
    else:
        hint_font = pygame.font.SysFont(None, 32)
        hint_surface = hint_font.render('Press ESC to return to the menu', True, (255, 255, 255))
        hint_rect = hint_surface.get_rect()
        hint_rect.midtop = (game_settings.screen_width // 2, title_rect.bottom + 20)
        screen.blit(hint_surface, hint_rect)

def _render_shop_options(panel, font, options, start_y, start_x=20, line_height=70):
    """Draws the score-based upgrades list and returns the final y offset."""
    for idx, option in enumerate(options):
        enabled = option['enabled']
        color = (255, 255, 255) if enabled else (150, 150, 150)
        y = start_y + idx * line_height
        label = f"{idx + 1}. {option['label']} - Cost: {option['cost']} Score"
        label_surface = font.render(label, True, color)
        panel.blit(label_surface, (start_x, y))
        desc_surface = font.render(option['description'], True, color)
        panel.blit(desc_surface, (start_x + 20, y + 30))
    return start_y + len(options) * line_height

def _render_skill_options(panel, font, skill_options, start_y, start_x=20, line_height=85):
    """Draws the skill tree list and returns the final y offset."""
    for idx, option in enumerate(skill_options):
        number = idx + 1
        y = start_y + idx * line_height
        if option['unlocked']:
            color = (120, 220, 140)
            status_text = "UNLOCKED"
        elif not option['prereq_met']:
            color = (140, 140, 140)
            req_name = option['requires_label'] or "previous skill"
            status_text = f"Requires {req_name}"
        elif option['enabled']:
            color = (255, 255, 255)
            status_text = "Ready to learn"
        else:
            color = (240, 200, 120)
            status_text = "Need more Skill Points"
        label = f"{number}. [{option['branch']}] {option['label']} - Cost: {option['cost']} SP"
        label_surface = font.render(label, True, color)
        panel.blit(label_surface, (start_x, y))
        desc_surface = font.render(option['description'], True, color)
        panel.blit(desc_surface, (start_x + 20, y + 25))
        status_surface = font.render(status_text, True, color)
        panel.blit(status_surface, (start_x + 20, y + 50))
    return start_y + len(skill_options) * line_height

def draw_upgrade_menu(screen, game_settings, stats):
    overlay = pygame.Surface((game_settings.screen_width, game_settings.screen_height), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))

    panel_width = int(game_settings.screen_width * 0.85)
    panel_height = int(game_settings.screen_height * 0.9)
    panel = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
    pygame.draw.rect(panel, (20, 20, 20, 235), panel.get_rect(), border_radius=12)
    pygame.draw.rect(panel, (80, 200, 120), panel.get_rect(), width=3, border_radius=12)

    title_font = pygame.font.SysFont(None, 52)
    body_font = pygame.font.SysFont(None, 32)
    title = title_font.render("UPGRADE MENU", True, (255, 255, 255))
    panel.blit(title, (20, 15))

    instructions = body_font.render("Press 1-9 (0 for slot 10) to buy, TAB switches pages, ESC to skip", True, (200, 200, 200))
    panel.blit(instructions, (20, 60))

    score_text = body_font.render(f"Score: {stats.score}", True, (255, 215, 0))
    score_rect = score_text.get_rect()
    score_rect.topright = (panel_width - 20, 20)
    panel.blit(score_text, score_rect)

    skill_points_text = body_font.render(f"Skill Points: {stats.skill_points}", True, (140, 200, 255))
    skill_rect = skill_points_text.get_rect()
    skill_rect.topright = (panel_width - 20, score_rect.bottom + 5)
    panel.blit(skill_points_text, skill_rect)

    upgrade_options = get_upgrade_options(stats)
    skill_options = get_skill_options(stats)

    tab_font = pygame.font.SysFont(None, 32)
    tabs = [('shop', 'Shop Upgrades'), ('skills', 'Skill Tree')]
    tab_width = 220
    tab_height = 42
    tab_spacing = 15
    tab_y = 110
    for idx, (page, label) in enumerate(tabs):
        rect = pygame.Rect(20 + idx * (tab_width + tab_spacing), tab_y, tab_width, tab_height)
        is_active = stats.upgrade_menu_page == page
        bg_color = (60, 120, 90) if is_active and page == 'shop' else (60, 90, 150) if is_active else (35, 35, 35)
        pygame.draw.rect(panel, bg_color, rect, border_radius=8)
        pygame.draw.rect(panel, (120, 120, 120), rect, width=1, border_radius=8)
        label_surface = tab_font.render(label, True, (255, 255, 255))
        label_rect = label_surface.get_rect(center=rect.center)
        panel.blit(label_surface, label_rect)

    content_top = tab_y + tab_height + 25
    message = None

    if stats.upgrade_menu_page == 'shop':
        header = body_font.render("SHOP UPGRADES (cost: Score)", True, (180, 255, 200))
        panel.blit(header, (20, content_top))
        list_start = content_top + 35
        _render_shop_options(panel, body_font, upgrade_options, list_start)
        available = any(option['available'] for option in upgrade_options)
        affordable = any(option['enabled'] for option in upgrade_options)
        if not available:
            message = "All shop upgrades unlocked! Press TAB to view the Skill Tree."
        elif not affordable:
            message = "Earn more score to afford the next upgrade."
    else:
        header = body_font.render("SKILL TREE (cost: Skill Points)", True, (140, 200, 255))
        panel.blit(header, (20, content_top))
        list_start = content_top + 35
        _render_skill_options(panel, body_font, skill_options, list_start)
        all_unlocked = all(option['unlocked'] for option in skill_options)
        available = any(option['available'] for option in skill_options)
        affordable = any(option['enabled'] for option in skill_options)
        if all_unlocked:
            message = "All skills unlocked! Press TAB to return to the shop."
        elif not available:
            message = "Unlock prerequisite skills to progress further."
        elif not affordable:
            message = "Defeat bosses to earn more Skill Points."

    if message:
        msg = body_font.render(message, True, (255, 180, 120))
        panel.blit(msg, (20, panel_height - 60))

    panel_rect = panel.get_rect(center=(game_settings.screen_width // 2, game_settings.screen_height // 2))
    screen.blit(panel, panel_rect)

def draw_skill_menu(screen, game_settings, stats):
    overlay = pygame.Surface((game_settings.screen_width, game_settings.screen_height), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 190))
    screen.blit(overlay, (0, 0))

    panel_width = int(game_settings.screen_width * 0.7)
    panel_height = int(game_settings.screen_height * 0.6)
    panel = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
    pygame.draw.rect(panel, (18, 18, 18, 235), panel.get_rect(), border_radius=16)
    pygame.draw.rect(panel, (100, 160, 255), panel.get_rect(), width=3, border_radius=16)

    title_font = pygame.font.SysFont(None, 58)
    body_font = pygame.font.SysFont(None, 32)
    title = title_font.render("SKILL TREE", True, (255, 255, 255))
    title_rect = title.get_rect(midtop=(panel_width // 2, 20))
    panel.blit(title, title_rect)

    subtext = body_font.render("Spend Skill Points between waves or after bosses.", True, (200, 200, 200))
    subtext_rect = subtext.get_rect(midtop=(panel_width // 2, title_rect.bottom + 15))
    panel.blit(subtext, subtext_rect)

    points_text = body_font.render(f"Skill Points available: {stats.skill_points}", True, (140, 200, 255))
    points_rect = points_text.get_rect(midtop=(panel_width // 2, subtext_rect.bottom + 20))
    panel.blit(points_text, points_rect)

    skill_options = get_skill_options(stats)
    list_start = points_rect.bottom + 30
    _render_skill_options(panel, body_font, skill_options, list_start, start_x=40)

    panel_rect = panel.get_rect(center=(game_settings.screen_width // 2, game_settings.screen_height // 2))
    screen.blit(panel, panel_rect)
def draw_powerup_guides(screen, game_settings):
    font = pygame.font.SysFont(None, 28)
    guide_text = "R - Gas Bomb    T - Time Stop"
    text_surface = font.render(guide_text, True, (255, 255, 255))
    padding = 8
    bg_rect = text_surface.get_rect()
    bg_rect.midbottom = (
        game_settings.screen_width // 2,
        game_settings.screen_height - 5,
    )
    bg_rect.inflate_ip(padding * 2, padding * 2)
    pygame.draw.rect(screen, (0, 0, 0, 150), bg_rect)
    text_rect = text_surface.get_rect(center=bg_rect.center)
    screen.blit(text_surface, text_rect)
    
def _set_music_track(track, stats, volume=None):
    if getattr(stats, 'active_music', None) == track:
        if volume is not None:
            stats.music_volume = volume
            pygame.mixer.music.set_volume(volume)
        return
    try:
        pygame.mixer.music.load(track)
    except pygame.error:
        return
    stats.active_music = track
    if volume is not None:
        stats.music_volume = volume
    pygame.mixer.music.set_volume(stats.music_volume)
    if stats.music_on:
        pygame.mixer.music.play(-1)

def check_music(stats):
    if stats.music_on == True:
        pygame.mixer.music.set_volume(getattr(stats, 'music_volume', 0.3))
        pygame.mixer.music.play(-1)
    else:
        pygame.mixer.music.stop()

def update_record(stats):
    stats.record_saver(stats.score)

def update_record_and_quit(stats):
    stats.record_saver(stats.score)
    sys.exit()
