import pygame
import random


class RageCoin(pygame.sprite.Sprite):
    """Special pickup that activates rage mode."""

    def __init__(self, screen, game_settings, stats):
        super().__init__()
        self.screen = screen
        self.screen_rect = screen.get_rect()
        self.image = pygame.image.load('rage.png').convert_alpha()
        self.rect = self.image.get_rect(
            midright=(
                game_settings.screen_width + 30,
                random.randint(30, game_settings.screen_height - 30),
            )
        )
        self.speed = random.randint(stats.min_speed, stats.max_speed)

    def blit_me(self):
        self.screen.blit(self.image, self.rect)

    def update(self):
        self.rect.move_ip(-self.speed, 0)
        if self.rect.right < 0:
            self.kill()
