class GameStats():
    
    
    def __init__(self):
        self.base_max_health = 3
        self.base_max_health_cap = 5
        self.max_health_cap = self.base_max_health_cap
        self.base_time_stop_duration = 3000
        self.base_gas_bomb_duration = 2500
        self.gas_bomb_duration = self.base_gas_bomb_duration
        self.base_max_time_stops = 2
        self.max_time_stops = self.base_max_time_stops
        self.base_max_bombs = 2
        self.max_bombs = self.base_max_bombs
        self.wave_duration = 30000
        self.max_timestop_upgrades = 3
        self.max_heart_upgrades = self.max_health_cap - self.base_max_health
        self.max_multiplier_upgrades = 10
        self.skill_points_per_boss = 1

        self.game_active = False
        self.music_on = True
        self.game_fresh = True
        self.time_stopped = False
        self.time_stop_start = 0
        self.gas_bomb_active = False
        self.gas_bomb_start = 0
        self.gas_bomb_zone = None
        self.gas_bomb_radius_scale = 1.0
        self.gas_bomb_global = False
        self.upgrade_menu_open = False
        self.skill_menu_open = False
        self.upgrade_menu_page = 'shop'
        self.pause_menu_open = False
        self.pause_started_at = 0
        self.menu_open_via_user = False
        self.boss_active = False
        self.boss_hp = 0
        self.boss_max_hp = 5
        self.boss_spawned_for_wave = False

        self.reset_stats()

    def reset_stats(self):
        self.score = 0
        self.level = 1
        self.bonus = 0
        self.record = self.record_loader()
        self.min_speed = 1
        self.max_speed = 5
        self.time_stopped = False
        self.time_stop_start = 0
        self.waves_completed = 0
        self.wave_number = 1
        self.wave_start_time = 0
        self.upgrade_menu_open = False
        self.skill_menu_open = False
        self.upgrade_menu_page = 'shop'
        self.pause_menu_open = False
        self.pause_started_at = 0
        self.menu_open_via_user = False

        self.max_time_stops = self.base_max_time_stops
        self.max_bombs = self.base_max_bombs
        self.max_health_cap = self.base_max_health_cap
        self.gas_bomb_duration = self.base_gas_bomb_duration

        self.timestop_upgrade_level = 0
        self.heart_upgrade_level = 0
        self.multiplier_upgrade_level = 0
        self.skill_multiplier_bonus = 0.0
        self.flat_score_bonus = 0
        self.skill_points = 0
        self.unlocked_skills = set()

        self.time_stop_duration = self.base_time_stop_duration
        self.max_health = self.base_max_health
        self.health = 1
        self.speed_progress = 0.0

        self.time_stops_available = 0
        self.bombs_available = 0
        self.gas_bomb_active = False
        self.gas_bomb_start = 0
        self.gas_bomb_zone = None
        self.gas_bomb_radius_scale = 1.0
        self.gas_bomb_global = False
        self.boss_active = False
        self.boss_hp = 0
        self.boss_max_hp = 5
        self.boss_spawned_for_wave = False
        self.recalc_multiplier()
    
    def record_loader(self):
        with open ("record.txt", "r") as file:
            record = int(file.read())
        return record
    
    def record_saver(self, new_record):
        if new_record > self.record:
            self.record = new_record
            with open ("record.txt", "w") as file:
                file.write(str(new_record))

    def recalc_multiplier(self):
        base_multiplier = 1.0 + self.multiplier_upgrade_level * 0.1
        self.score_multiplier = base_multiplier + self.skill_multiplier_bonus
