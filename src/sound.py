"""
Procedural sound generator for game audio effects without requiring external .wav files.
Gracefully operates in dummy mode if audio device is unavailable.
"""

import math
import struct
import pygame


class SoundManager:
    def __init__(self):
        self.enabled = False
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
            self.enabled = True
            self.sounds = self._generate_sounds()
        except Exception as e:
            print(f"[SoundManager] Audio initialization skipped ({e}). Running silently.")
            self.sounds = {}

    def _generate_sine_wave(self, freq_start, freq_end, duration_sec, volume=0.3):
        sample_rate = 22050
        num_samples = int(duration_sec * sample_rate)
        buf = bytearray()

        for i in range(num_samples):
            t = i / num_samples
            freq = freq_start + (freq_end - freq_start) * t
            envelope = (1.0 - t) * volume
            sample = int(32767 * envelope * math.sin(2.0 * math.pi * freq * (i / sample_rate)))
            # Clamp 16-bit
            sample = max(-32768, min(32767, sample))
            packed = struct.pack("<h", sample)
            buf += packed + packed  # Stereo (L + R)

        return pygame.mixer.Sound(buffer=bytes(buf))

    def _generate_noise_explosion(self, duration_sec=0.4, volume=0.4):
        import random
        sample_rate = 22050
        num_samples = int(duration_sec * sample_rate)
        buf = bytearray()

        last_sample = 0
        for i in range(num_samples):
            t = i / num_samples
            envelope = ((1.0 - t) ** 1.8) * volume
            # Low-pass noise for explosion rumble
            white = random.uniform(-1.0, 1.0)
            sample_val = last_sample * 0.85 + white * 0.15
            last_sample = sample_val

            sample = int(32767 * envelope * sample_val)
            sample = max(-32768, min(32767, sample))
            packed = struct.pack("<h", sample)
            buf += packed + packed

        return pygame.mixer.Sound(buffer=bytes(buf))

    def _generate_sounds(self):
        sounds = {}
        try:
            sounds["gatling"] = self._generate_sine_wave(850, 200, 0.06, volume=0.22)
            sounds["missile_launch"] = self._generate_sine_wave(300, 750, 0.18, volume=0.28)
            sounds["sniper"] = self._generate_sine_wave(1200, 140, 0.22, volume=0.35)
            sounds["tesla"] = self._generate_sine_wave(400, 1100, 0.14, volume=0.25)
            sounds["explosion"] = self._generate_noise_explosion(0.42, volume=0.35)
            sounds["build"] = self._generate_sine_wave(440, 880, 0.12, volume=0.25)
            sounds["sell"] = self._generate_sine_wave(880, 440, 0.12, volume=0.25)
            sounds["hit"] = self._generate_sine_wave(280, 120, 0.04, volume=0.18)
            sounds["game_over"] = self._generate_sine_wave(400, 80, 1.0, volume=0.4)
            sounds["victory"] = self._generate_sine_wave(350, 950, 0.8, volume=0.4)
        except Exception as e:
            print(f"[SoundManager] Error generating procedural sound buffers: {e}")
        return sounds

    def play(self, sound_name):
        if not self.enabled:
            return
        snd = self.sounds.get(sound_name)
        if snd:
            try:
                snd.play()
            except Exception:
                pass
