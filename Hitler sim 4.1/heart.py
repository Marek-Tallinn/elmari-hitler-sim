import pygame
import random


class Heart(pygame.sprite.Sprite):
    """Floating heart collectible that restores player health."""

    def __init__(self, screen, game_settings, stats):
        super().__init__()
        self.screen = screen
        self.screen_rect = screen.get_rect()
        self.image = self._build_heart_surface()
        self.rect = self.image.get_rect(
            midright=(
                game_settings.screen_width + 20,
                random.randint(40, game_settings.screen_height - 40),
            )
        )
        self.speed = random.randint(stats.min_speed, stats.max_speed)

    def _build_heart_surface(self):
        size = 36
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        color = (220, 30, 70)
        left_center = (int(size * 0.3), int(size * 0.3))
        right_center = (int(size * 0.7), int(size * 0.3))
        radius = int(size * 0.22)
        pygame.draw.circle(surface, color, left_center, radius)
        pygame.draw.circle(surface, color, right_center, radius)
        points = [
            (int(size * 0.1), int(size * 0.35)),
            (int(size * 0.5), int(size * 0.9)),
            (int(size * 0.9), int(size * 0.35)),
        ]
        pygame.draw.polygon(surface, color, points)
        # Soft highlight instead of a harsh black outline to avoid visual seams.
        highlight_color = (255, 120, 150)
        pygame.draw.lines(surface, highlight_color, False, points, 1)
        return surface

    def blit_me(self):
        self.screen.blit(self.image, self.rect)

    def update(self):
        self.rect.move_ip(-self.speed, 0)
        if self.rect.right < 0:
            self.kill()
