import pygame.font

class Scoreboard():
    def __init__(self, game_settings, screen, stats):
        self.screen = screen
        self.screen_rect = screen.get_rect()
        self.game_settings = game_settings
        self.stats = stats
        self.text_color = (0, 0, 0)
        self.font = pygame.font.SysFont(None, 46)
        self.heart_size = 28
        self.heart_spacing = 8
        self.filled_heart = self._build_heart_surface((220, 30, 70))
        self.empty_heart = self._build_heart_surface((110, 110, 110))
        self.small_font = pygame.font.SysFont(None, 32)
        self.prepare_score()
        self.prepare_level()
        self.prepare_record()
        
    def prepare_score(self):
        score_str = str(self.stats.score)
        temp_surface = self.font.render(score_str, True, self.text_color)
        self.score_image = pygame.Surface(temp_surface.get_size(), pygame.SRCALPHA)
        self.score_image.fill((255, 255, 255, 0))
        self.score_image.blit(temp_surface, (0, 0))
        self.score_coin = pygame.image.load('coin_parem_kui_varem.png').convert_alpha()
        self.score_image_rect = self.score_image.get_rect()
        self.score_image_rect.left = self.screen_rect.left + 70
        self.score_image_rect.top = 20
        self.score_coin_rect = self.score_coin.get_rect()
        self.score_coin_rect.left = self.screen_rect.left + 10
        self.score_coin_rect.top = 10
        
    def prepare_level(self):
        level_str = str(self.stats.level)
        temp_surface = self.font.render('LEVEL: ' + level_str, True, self.text_color)
        self.level_image = pygame.Surface(temp_surface.get_size(), pygame.SRCALPHA)
        self.level_image.fill((255, 255, 255, 0))
        self.level_image.blit(temp_surface, (0, 0)) 
        self.level_rect = self.level_image.get_rect()
        self.level_rect.left = self.screen_rect.left + 10
        self.level_rect.top = 60
        self.prepare_multiplier()
    
    def prepare_record(self):
        record_str = str(self.stats.record)
        temp_surface = self.font.render('HI-SCORE: ' + record_str, True, self.text_color)
        self.record_image = pygame.Surface(temp_surface.get_size(), pygame.SRCALPHA)
        self.record_image.fill((255, 255, 255, 0))
        self.record_image.blit(temp_surface, (0, 0))
        self.record_rect = self.record_image.get_rect()
        self.record_rect.right = self.screen_rect.right - 10
        self.record_rect.top = 20
        
    def draw_score(self):
        self.screen.blit(self.score_image, self.score_image_rect)
        self.screen.blit(self.score_coin, self.score_coin_rect)
        self.screen.blit(self.level_image, self.level_rect)
        self.screen.blit(self.record_image, self.record_rect)
        self.screen.blit(self.multiplier_image, self.multiplier_rect)
        self._draw_hearts()

    def prepare_multiplier(self):
        mult_str = f"MULT: {self.stats.score_multiplier:.1f}x"
        self.multiplier_image = self.small_font.render(mult_str, True, self.text_color)
        self.multiplier_rect = self.multiplier_image.get_rect()
        self.multiplier_rect.left = self.screen_rect.left + 10
        self.multiplier_rect.top = self.level_rect.bottom + 10

    def _build_heart_surface(self, color):
        size = self.heart_size
        heart_surface = pygame.Surface((size, size), pygame.SRCALPHA)
        left_center = (int(size * 0.35), int(size * 0.35))
        right_center = (int(size * 0.65), int(size * 0.35))
        radius = int(size * 0.25)
        pygame.draw.circle(heart_surface, color, left_center, radius)
        pygame.draw.circle(heart_surface, color, right_center, radius)
        points = [
            (int(size * 0.15), int(size * 0.45)),
            (int(size * 0.5), int(size * 0.9)),
            (int(size * 0.85), int(size * 0.45)),
        ]
        pygame.draw.polygon(heart_surface, color, points)
        return heart_surface

    def _draw_hearts(self):
        total_width = self.stats.max_health * self.heart_size + (self.stats.max_health - 1) * self.heart_spacing
        start_x = self.screen_rect.right - total_width - 10
        y = self.record_rect.bottom + 10
        for i in range(self.stats.max_health):
            heart = self.filled_heart if i < self.stats.health else self.empty_heart
            rect = heart.get_rect()
            rect.topleft = (start_x + i * (self.heart_size + self.heart_spacing), y)
            self.screen.blit(heart, rect)
