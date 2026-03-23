# ============================================================
# FALLING OBJECT — apple, bomb (worm), heart power-up, coin
# ============================================================

import pygame
import random
from constants import WINDOW_WIDTH, WINDOW_HEIGHT, APPLE_IMG, WORM_IMG, HEART_IMG, COIN_IMG, GOLDEN_APPLE_IMG, ROTTEN_APPLE_IMG

# Minimum horizontal gap between any two objects at spawn time
MIN_SPAWN_GAP = 10
# Max attempts to find a non-overlapping x position before giving up
MAX_SPAWN_ATTEMPTS = 10


class FallingObject:
    # Cached images — loaded once at class level
    _apple_surface = None
    _worm_surface  = None
    _heart_surface = None
    _coin_surface         = None
    _golden_apple_surface = None
    _rotten_apple_surface = None

    @classmethod
    def _get_surface(cls, obj_type, size):
        if obj_type == 'good':
            if cls._apple_surface is None or cls._apple_surface.get_size() != size:
                cls._apple_surface = pygame.transform.scale(
                    pygame.image.load(APPLE_IMG).convert_alpha(), size
                )
            return cls._apple_surface
        elif obj_type == 'bomb':
            if cls._worm_surface is None or cls._worm_surface.get_size() != size:
                cls._worm_surface = pygame.transform.scale(
                    pygame.image.load(WORM_IMG).convert_alpha(), size
                )
            return cls._worm_surface
        elif obj_type == 'heart':
            if cls._heart_surface is None or cls._heart_surface.get_size() != size:
                cls._heart_surface = pygame.transform.scale(
                    pygame.image.load(HEART_IMG).convert_alpha(), size
                )
            return cls._heart_surface
        elif obj_type == 'coin':
            if cls._coin_surface is None or cls._coin_surface.get_size() != size:
                cls._coin_surface = pygame.transform.scale(
                    pygame.image.load(COIN_IMG).convert_alpha(), size
                )
            return cls._coin_surface
        elif obj_type == 'golden_apple':
            if cls._golden_apple_surface is None or cls._golden_apple_surface.get_size() != size:
                cls._golden_apple_surface = pygame.transform.scale(
                    pygame.image.load(GOLDEN_APPLE_IMG).convert_alpha(), size
                )
            return cls._golden_apple_surface
        else:  # rotten_apple
            if cls._rotten_apple_surface is None or cls._rotten_apple_surface.get_size() != size:
                cls._rotten_apple_surface = pygame.transform.scale(
                    pygame.image.load(ROTTEN_APPLE_IMG).convert_alpha(), size
                )
            return cls._rotten_apple_surface

    def __init__(self, obj_type, fall_speed, existing_objects=None):
        self.type = obj_type

        if self.type in ('heart', 'coin', 'golden_apple', 'rotten_apple'):
            self.width  = 55
            self.height = 55
        else:
            self.width  = 60
            self.height = 60

        self.x          = self._pick_x(existing_objects or [])
        self.y          = -self.height - random.randint(0, 120)
        self.fall_speed = fall_speed
        self.image      = FallingObject._get_surface(obj_type, (self.width, self.height))

    def _pick_x(self, existing_objects):
        """Return an x position that doesn't overlap objects near the top."""
        for _ in range(MAX_SPAWN_ATTEMPTS):
            x = random.randint(0, WINDOW_WIDTH - self.width)
            if not self._overlaps(x, existing_objects):
                return x
        return x

    def _overlaps(self, x, existing_objects):
        """True if candidate x overlaps any nearby object at a similar Y."""
        for obj in existing_objects:
            if obj.y > 200:
                continue
            if abs(obj.y - (-self.height)) > 100:
                continue
            gap       = MIN_SPAWN_GAP
            obj_left  = obj.x - gap
            obj_right = obj.x + obj.width + gap
            if x < obj_right and x + self.width > obj_left:
                return True
        return False

    def fall(self):
        self.y += self.fall_speed

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

    def is_off_screen(self):
        return self.y > WINDOW_HEIGHT

    def check_collision(self, player):
        return pygame.Rect(self.x, self.y, self.width, self.height).colliderect(player.hitbox)