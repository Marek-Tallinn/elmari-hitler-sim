import pygame
import random

POWERUP_IMAGE_PATH = 'collector_powerup.png'


class CollectorPowerUp(pygame.sprite.Sprite):
    """Sweeps loot and wipes enemies when the player collects it."""

    def __init__(self, screen, game_settings, stats):
        super().__init__()
        self.screen = screen
        self.screen_rect = screen.get_rect()
        self.image = self._load_image()
        self.rect = self.image.get_rect(
            midright=(
                game_settings.screen_width + 20,
                random.randint(40, game_settings.screen_height - 40),
            )
        )
        self.speed = random.randint(stats.min_speed, stats.max_speed)

    def _load_image(self):
        try:
            return pygame.image.load(POWERUP_IMAGE_PATH).convert_alpha()
        except pygame.error:
            size = 48
            placeholder = pygame.Surface((size, size), pygame.SRCALPHA)
            pygame.draw.circle(placeholder, (255, 215, 0), (size // 2, size // 2), size // 2)
            pygame.draw.circle(placeholder, (255, 69, 0), (size // 2, size // 2), size // 3, 3)
            pygame.draw.line(placeholder, (0, 191, 255), (12, size // 2), (size - 12, size // 2), 4)
            return placeholder

    def blit_me(self):
        self.screen.blit(self.image, self.rect)

    def update(self):
        self.rect.move_ip(-self.speed, 0)
        if self.rect.right < 0:
            self.kill()
