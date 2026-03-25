# ============================================================
# PLAYER — movement, animation, drawing
# ============================================================

import pygame
from constants import WINDOW_WIDTH, WINDOW_HEIGHT, PLAYER_SIZE, IDLE_IMG, WALK_RIGHT_GIF, WALK_LEFT_GIF
from assets import load_gif_frames


class Player:
    def __init__(self):
        self.speed = 6.2
        self.rect  = pygame.Rect(
            WINDOW_WIDTH  // 2 - PLAYER_SIZE[0] // 2,
            WINDOW_HEIGHT - 95,          #value to move the player up/down
            PLAYER_SIZE[0], PLAYER_SIZE[1]
        )

        self.idle_image        = pygame.transform.scale(
            pygame.image.load(IDLE_IMG).convert_alpha(), PLAYER_SIZE
        )
        self.walk_frames_right = load_gif_frames(WALK_RIGHT_GIF, size=PLAYER_SIZE)
        self.walk_frames_left  = load_gif_frames(WALK_LEFT_GIF,  size=PLAYER_SIZE)

        self.current_image = self.idle_image
        self.frame_index   = 0
        self.frame_timer   = 0
        self.FRAME_SPEED   = 8

        # Hitbox is 40% smaller than the sprite, centered on it
        hb_w = int(PLAYER_SIZE[0] * 0.5)
        hb_h = int(PLAYER_SIZE[1] * 0.5)
        self.hitbox = pygame.Rect(
            self.rect.centerx - hb_w // 2,
            self.rect.centery - hb_h // 2,
            hb_w, hb_h
        )

    def _sync_hitbox(self):
        """Keep hitbox centered on the sprite rect."""
        self.hitbox.centerx = self.rect.centerx
        self.hitbox.centery = self.rect.centery

    def move(self, keys):
        moving_right = (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and self.rect.right < WINDOW_WIDTH
        moving_left  = (keys[pygame.K_LEFT]  or keys[pygame.K_a]) and self.rect.left  > 0

        if moving_right:
            self.rect.x     += self.speed
            self.frame_timer += 1
            if self.frame_timer >= self.FRAME_SPEED:
                self.frame_timer = 0
                self.frame_index = (self.frame_index + 1) % len(self.walk_frames_right)
            self.current_image = self.walk_frames_right[self.frame_index]

        elif moving_left:
            self.rect.x     -= self.speed
            self.frame_timer += 1
            if self.frame_timer >= self.FRAME_SPEED:
                self.frame_timer = 0
                self.frame_index = (self.frame_index + 1) % len(self.walk_frames_left)
            self.current_image = self.walk_frames_left[self.frame_index]

        else:
            self.frame_index   = 0
            self.frame_timer   = 0
            self.current_image = self.idle_image

        self._sync_hitbox()

    def draw(self, screen):
        screen.blit(self.current_image, self.rect)