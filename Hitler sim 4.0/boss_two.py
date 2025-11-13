import pygame

from boss import Boss


class BossTwo(Boss):
    """More durable boss variant that spawns paired terrorists."""

    def __init__(self, screen, game_settings):
        super().__init__(screen, game_settings)
        self.speed = 3
        self.throw_cooldown = 700
        margin = 80
        self.target_x = self.screen_rect.right - margin
        self.rect.midright = (
            self.screen_rect.right + self.rect.width,
            self.screen_rect.centery,
        )

    def _load_image(self):
        try:
            return pygame.image.load('boss_2.png').convert_alpha()
        except pygame.error:
            return super()._load_image()

    def spawn_terrorist(self, terrorists, game_settings, stats):
        super().spawn_terrorist(terrorists, game_settings, stats)
        from terrorist import Terrorist

        extra = Terrorist(self.screen, game_settings, stats)
        extra.rect.midright = self.rect.midleft
        extra.rect.y += 60
        terrorists.add(extra)
