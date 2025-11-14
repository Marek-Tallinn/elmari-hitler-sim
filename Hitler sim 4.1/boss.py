import pygame


class Boss(pygame.sprite.Sprite):
    """Stationary boss that hovers near the right side and spawns terrorists."""

    def __init__(self, screen, game_settings):
        super().__init__()
        self.screen = screen
        self.screen_rect = screen.get_rect()
        self.target_x = int(game_settings.screen_width * 0.92)
        self.image = self._load_image()
        self.rect = self.image.get_rect(
            midright=(
                game_settings.screen_width + self.image.get_width(),
                self.screen_rect.centery,
            )
        )
        self.speed = 4
        self.throw_cooldown = 900
        self.last_throw = 0

    def _load_image(self):
        try:
            return pygame.image.load('boss.png').convert_alpha()
        except pygame.error:
            size = (160, 180)
            surf = pygame.Surface(size, pygame.SRCALPHA)
            pygame.draw.rect(surf, (150, 0, 0), surf.get_rect(), border_radius=20)
            pygame.draw.rect(surf, (255, 215, 0), surf.get_rect(), width=4, border_radius=20)
            pygame.draw.circle(surf, (255, 255, 255), (size[0] // 2, size[1] // 3), 25)
            pygame.draw.circle(surf, (0, 0, 0), (size[0] // 2 - 12, size[1] // 3), 8)
            pygame.draw.circle(surf, (0, 0, 0), (size[0] // 2 + 12, size[1] // 3), 8)
            pygame.draw.rect(surf, (0, 0, 0), (size[0] // 2 - 25, size[1] // 3 + 30, 50, 10))
            return surf

    def update(self, terrorists, game_settings, stats):
        if self.rect.right > self.target_x:
            self.rect.move_ip(-self.speed, 0)
            if self.rect.right < self.target_x:
                self.rect.right = self.target_x
        current_time = pygame.time.get_ticks()
        if current_time - self.last_throw >= self.throw_cooldown:
            self.spawn_terrorist(terrorists, game_settings, stats)
            self.last_throw = current_time

    def spawn_terrorist(self, terrorists, game_settings, stats):
        from terrorist import Terrorist

        new_terrorist = Terrorist(self.screen, game_settings, stats)
        new_terrorist.rect.midright = self.rect.midleft
        terrorists.add(new_terrorist)

    def blit_me(self):
        self.screen.blit(self.image, self.rect)
