import pygame
import random

class Star(pygame.sprite.Sprite):
    
    def __init__(self, screen, game_settings, stats):
        super(Star, self).__init__()
        self.screen = screen
        self.screen_rect = screen.get_rect()
        self.star = pygame.image.load('star.png').convert_alpha()
        self.rect = self.star.get_rect(
            midright=(
                game_settings.screen_width + 20,
                random.randint(0, game_settings.screen_height),
            )
        )
        self.speed = random.randint(stats.min_speed, stats.max_speed)
        
    def blit_me(self):
        self.screen.blit(self.star, self.rect)
        
    def update(self):
        self.rect.move_ip(-self.speed, 0)
        if self.rect.right < 0:
            self.kill()