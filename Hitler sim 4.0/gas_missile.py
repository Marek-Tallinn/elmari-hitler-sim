import pygame


class GasMissile(pygame.sprite.Sprite):
    """Projectile that travels in a straight line before triggering an explosion."""

    def __init__(self, screen, start_pos, direction, game_settings, speed=18):
        super().__init__()
        self.screen = screen
        self.image = pygame.Surface((48, 14), pygame.SRCALPHA)
        pygame.draw.rect(self.image, (30, 200, 120), self.image.get_rect(), border_radius=6)
        pygame.draw.rect(self.image, (240, 255, 240), self.image.get_rect(), width=2, border_radius=6)
        self.rect = self.image.get_rect(center=start_pos)

        vec = pygame.math.Vector2(direction)
        if vec.length_squared() == 0:
            vec = pygame.math.Vector2(1, 0)
        self.direction = vec.normalize()
        self.speed = speed
        self.distance_travelled = 0
        self.max_distance = game_settings.screen_width * 0.5
        self.bounds = pygame.Rect(0, 0, game_settings.screen_width, game_settings.screen_height)

        self._pending_explosion = False

    def update(self):
        if self._pending_explosion:
            return
        movement = self.direction * self.speed
        self.rect.centerx += movement.x
        self.rect.centery += movement.y
        self.distance_travelled += movement.length()

        if not self.bounds.collidepoint(self.rect.center):
            self._pending_explosion = True
            return

        if self.distance_travelled >= self.max_distance:
            self._pending_explosion = True

    def trigger_explosion(self):
        """Mark the missile for immediate explosion."""
        self._pending_explosion = True

    def ready_to_explode(self):
        return self._pending_explosion

    def consume_explosion_center(self):
        """Return the explosion center and remove the missile."""
        center = self.rect.center
        self.kill()
        return center

    def blit_me(self):
        self.screen.blit(self.image, self.rect)
