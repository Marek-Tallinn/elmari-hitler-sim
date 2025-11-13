import pygame
import random

class Terrorist(pygame.sprite.Sprite):
    
    def __init__(self, screen, game_settings, stats):
        super(Terrorist, self).__init__()
        self.screen = screen
        self.screen_rect = screen.get_rect()
        self.terrorist = pygame.image.load('terrorist.png').convert_alpha()
        self.rect = self.terrorist.get_rect(
            midright=(
                game_settings.screen_width + 20,
                random.randint(0, game_settings.screen_height),
            )
        )
        self.speed = random.randint(stats.min_speed, stats.max_speed)
        
    def blit_me(self):
        self.screen.blit(self.terrorist, self.rect)
        
    def update(self):
        self.rect.move_ip(-self.speed, 0)
        if self.rect.right < 0:
            self.kill()