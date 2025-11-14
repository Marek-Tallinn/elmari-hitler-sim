import os
import pygame
from settings import Settings
from game_stats import GameStats
from scoreboard import Scoreboard
from player import Player
from coin import Coin
from robber import Robber
from terrorist import Terrorist
from star import Star
from button import Button
import functions as func
from timestop_coin import TimeStopCoin


BACKGROUND_VARIANTS = {
    (1920, 1080): 'background_1080p.png',
    (2560, 1440): 'background_1440p.png',
    (3840, 2160): 'background_4k.png',
}


def _select_background_image(width, height, default_path='hitler.png'):
    candidate = BACKGROUND_VARIANTS.get((width, height))
    if candidate and os.path.exists(candidate):
        return candidate

    resolution_named = f'background_{width}x{height}.png'
    if os.path.exists(resolution_named):
        return resolution_named

    return default_path

def run_game():
    pygame.init()
    gm_settings = Settings()

    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    gm_settings.screen_width, gm_settings.screen_height = screen.get_size()
    pygame.display.set_caption(gm_settings.caption)

    window_icon = pygame.image.load('supermario.png')

    pygame.display.set_icon(window_icon)
    
    background_path = _select_background_image(gm_settings.screen_width, gm_settings.screen_height)
    background_image = pygame.image.load(background_path)
    rage_background_image = pygame.image.load('rage_backround.png')
    
    play_button = Button(gm_settings, screen, 'PLAY')
    resume_button = Button(gm_settings, screen, 'RESUME')
    skill_button = Button(gm_settings, screen, 'SKILL TREE')
    exit_button = Button(gm_settings, screen, 'EXIT GAME')

    center_x = gm_settings.screen_width // 2
    center_y = gm_settings.screen_height // 2
    spacing = 80
    ordered_buttons = [resume_button, skill_button, exit_button]
    for idx, btn in enumerate(ordered_buttons):
        btn.rect.center = (center_x, center_y + (idx - 1) * spacing)
        btn.msg_image_rect.center = btn.rect.center

    menu_buttons = {
        'resume': resume_button,
        'skills': skill_button,
        'exit': exit_button,
    }
    
    clock = pygame.time.Clock()
    
    stats = GameStats()
    func.ensure_infinite_bombs_if_enabled(stats, gm_settings)
    
    sb = Scoreboard(gm_settings, screen, stats)
    
    player = Player(screen)
    
    coins = pygame.sprite.Group()
    
    robbers = pygame.sprite.Group()
    
    terrorists = pygame.sprite.Group()
    
    stars = pygame.sprite.Group()

    hearts = pygame.sprite.Group()

    powerups = pygame.sprite.Group()
    
    timestop_coins = pygame.sprite.Group()
    rage_coins = pygame.sprite.Group()

    bosses = pygame.sprite.Group()
    gas_missiles = pygame.sprite.Group()

    func.check_music(stats)
    stats.wave_start_time = pygame.time.get_ticks()
    
    while True:
        func.update_rage_status(stats)
        func.check_events(gm_settings, screen, player, coins, robbers, terrorists, stars, powerups, hearts, timestop_coins, rage_coins, bosses, gas_missiles, stats, sb, play_button, menu_buttons)
        if stats.game_active and not stats.upgrade_menu_open and not stats.pause_menu_open:
            player.update()
            coins.update()
            timestop_coins.update()
            rage_coins.update()
            stars.update()
            hearts.update()
            powerups.update()
            func.update_gas_missiles(gas_missiles, stats, sb, gm_settings, coins, stars, robbers, terrorists, bosses, player)
            func.update_coins(player, coins, stats, sb, gm_settings)
            func.update_timestop_coins(player, timestop_coins, stats, sb, gm_settings)
            func.update_rage_coins(player, rage_coins, stats)
            func.update_stars(player, stars, stats, sb, gm_settings)
            func.update_hearts(player, hearts, stats)
            func.update_powerups(player, powerups, coins, stars, robbers, terrorists, stats, sb, gm_settings)
            if stats.time_stopped:
                if pygame.time.get_ticks() - stats.time_stop_start > stats.time_stop_duration:
                    stats.time_stopped = False
            if stats.gas_bomb_active:
                if pygame.time.get_ticks() - stats.gas_bomb_start > stats.gas_bomb_duration:
                    stats.gas_bomb_active = False
                    stats.gas_bomb_zone = None
                
            if not stats.time_stopped:
                robbers.update()
                terrorists.update()
                bosses.update(terrorists, gm_settings, stats)
                func.update_robbers(player, robbers, stats, sb, gm_settings)
                func.update_terrorists(player, terrorists, stats, sb, gm_settings)

        func.update_waves(stats, player, bosses, gm_settings, screen)
        active_background = rage_background_image if stats.rage_active else background_image
        screen.blit(active_background, (0, 0))
        func.update_screen(gm_settings, screen, player, coins, timestop_coins, rage_coins, robbers, terrorists, stars, powerups, hearts, bosses, gas_missiles, clock, sb, play_button, menu_buttons, stats)




run_game()
