"""
Wave generation, enemy spawn schedules, difficulty ramping, and wave state management.
"""

from src.enemy import Enemy


class WaveManager:
    def __init__(self, map_waypoints):
        self.waypoints = map_waypoints
        self.current_wave = 0
        self.max_waves = 15

        self.is_spawning = False
        self.wave_in_progress = False

        self.spawn_queue = []
        self.spawn_timer = 0.0
        self.spawn_interval = 1.0

        self.between_wave_timer = 5.0
        self.auto_start_next = False

    def start_next_wave(self):
        if self.wave_in_progress:
            return False

        self.current_wave += 1
        self.wave_in_progress = True
        self.is_spawning = True
        self.spawn_queue = self._build_wave_schedule(self.current_wave)
        self.spawn_timer = 0.2
        return True

    def _build_wave_schedule(self, wave_num):
        """Generates a thematic military convoy for the wave."""
        schedule = []
        wave_scale = 1.0 + (wave_num - 1) * 0.22

        if wave_num == 1:
            # Recon Scouts
            for _ in range(8):
                schedule.append(("scout", 0.9, wave_scale))
        elif wave_num == 2:
            # Scouts + Technicals
            for _ in range(6):
                schedule.append(("scout", 0.7, wave_scale))
            for _ in range(4):
                schedule.append(("technical", 1.1, wave_scale))
        elif wave_num == 3:
            # Technical motorized patrol
            for _ in range(10):
                schedule.append(("technical", 0.85, wave_scale))
        elif wave_num == 4:
            # First Armored APCs with scout vanguard
            for _ in range(5):
                schedule.append(("scout", 0.5, wave_scale))
            for _ in range(4):
                schedule.append(("apc", 1.5, wave_scale))
        elif wave_num == 5:
            # Mini-Boss / Tank column
            for _ in range(6):
                schedule.append(("technical", 0.7, wave_scale))
            schedule.append(("tank", 2.0, wave_scale * 1.1))
            for _ in range(4):
                schedule.append(("apc", 1.2, wave_scale))
        elif wave_num <= 9:
            # Combined arms assaults
            num_scouts = 6 + wave_num
            num_techs = 6 + wave_num
            num_apcs = 3 + wave_num // 2
            num_tanks = 1 + wave_num // 3
            for _ in range(num_scouts):
                schedule.append(("scout", 0.45, wave_scale))
            for _ in range(num_techs):
                schedule.append(("technical", 0.65, wave_scale))
            for _ in range(num_apcs):
                schedule.append(("apc", 1.2, wave_scale))
            for _ in range(num_tanks):
                schedule.append(("tank", 1.8, wave_scale))
        elif wave_num == 10:
            # Wave 10 Boss: First Mobile Dreadnought
            for _ in range(8):
                schedule.append(("technical", 0.5, wave_scale))
            schedule.append(("boss", 2.5, wave_scale * 1.2))
            for _ in range(4):
                schedule.append(("tank", 1.5, wave_scale))
        elif wave_num < 15:
            # Intense endgame armored blitz
            for _ in range(12):
                schedule.append(("scout", 0.35, wave_scale))
            for _ in range(8):
                schedule.append(("apc", 0.9, wave_scale))
            for _ in range(6):
                schedule.append(("tank", 1.4, wave_scale))
        else: # Wave 15 Final Showdown
            for _ in range(10):
                schedule.append(("tank", 1.0, wave_scale))
            schedule.append(("boss", 2.0, wave_scale * 1.4))
            schedule.append(("boss", 3.0, wave_scale * 1.4))

        return schedule

    def update(self, dt, active_enemies):
        if not self.wave_in_progress:
            return

        if self.is_spawning:
            self.spawn_timer -= dt
            if self.spawn_timer <= 0:
                if len(self.spawn_queue) > 0:
                    enemy_type, delay_next, scale = self.spawn_queue.pop(0)
                    active_enemies.append(Enemy(enemy_type, self.waypoints, scale))
                    self.spawn_timer = delay_next
                else:
                    self.is_spawning = False

        # If finished spawning and all enemies eliminated
        if not self.is_spawning and len(active_enemies) == 0:
            self.wave_in_progress = False
