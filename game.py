# ============================================================
# GAME — core update / draw loop, frenzy, HUD, game-over screen
# ============================================================

import pygame
import random
import sys
import math
from constants import (
    WINDOW_WIDTH, WINDOW_HEIGHT, FPS,
    WHITE, BLACK, RED, GOLD, GOLD_DIM, CYAN, CYAN_DIM,
    INITIAL_FALL_SPEED, SPEED_INCREASE, SPEED_THRESHOLD,
    FRENZY_DURATION_SEC, FRENZY_SPAWN_MULT,
    MAX_LIVES,
    BG_IMG, HEART_IMG, FRENZY_BANNER_IMG,
    SHIELD_ICON_IMG, MAGNET_ICON_IMG, GOLDEN_APPLE_ICON,
    TROPHY_HIGHSCORE_IMG, SCORE_PANEL_IMG
)
from assets import PC, PlayBG, G_O, LVL, OW, FRENZY_BGM, H_S
from button import Button
from player import Player
from falling_object import FallingObject
from scores import get_last_score, save_score


class Game:
    def __init__(self, pet_id=None):
        self.screen     = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock      = pygame.time.Clock()
        self.font       = pygame.font.Font(None, 36)
        self.large_font = pygame.font.Font(None, 72)
        self.small_font = pygame.font.Font(None, 28)
        self.tiny_font = pygame.font.Font(None, 20)
        self.font_btn   = pygame.font.Font(None, 38)

        self.bg = pygame.transform.scale(
            pygame.image.load(BG_IMG).convert(), (WINDOW_WIDTH, WINDOW_HEIGHT)
        )

        self.frenzy_tint = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.frenzy_tint.fill((255, 200, 0))
        self.frenzy_tint.set_alpha(40)

        raw_banner = pygame.image.load(FRENZY_BANNER_IMG).convert_alpha()
        banner_w = WINDOW_WIDTH - 40
        ratio    = banner_w / raw_banner.get_width()
        banner_h = int(raw_banner.get_height() * ratio)
        self.frenzy_banner_img = pygame.transform.scale(raw_banner, (banner_w, banner_h))

        TROPHY_HIGHSCORE_SIZE = (320, 314)
        SCORE_PANEL_SIZE      = (340, 195)

        self.trophy_highscore_img = pygame.transform.scale(
            pygame.image.load(TROPHY_HIGHSCORE_IMG).convert_alpha(), TROPHY_HIGHSCORE_SIZE
        )
        self.score_panel_img = pygame.transform.scale(
            pygame.image.load(SCORE_PANEL_IMG).convert_alpha(), SCORE_PANEL_SIZE
        )

        PANEL_Y   = 160
        BTN_H     = 58
        GAP       = 12
        tallest   = max(TROPHY_HIGHSCORE_SIZE[1], SCORE_PANEL_SIZE[1])
        btn1_y    = PANEL_Y + tallest + 50
        btn2_y    = btn1_y + BTN_H + GAP
        bw, cx    = 240, WINDOW_WIDTH // 2 - 120

        self.btn_play_again = Button(cx, btn1_y, bw, BTN_H, "PLAY AGAIN",
                                     base_color=(0, 130, 60), hover_color=(0, 200, 80))
        self.btn_main_menu  = Button(cx, btn2_y, bw, BTN_H, "BACK TO MENU",
                                     base_color=CYAN_DIM, hover_color=CYAN)

        self.heart_img = pygame.transform.scale(
            pygame.image.load(HEART_IMG).convert_alpha(), (24, 24)
        )

        ICON_SIZE = (52, 52)
        self.shield_icon_img = pygame.transform.scale(
            pygame.image.load(SHIELD_ICON_IMG).convert_alpha(), ICON_SIZE
        )
        self.magnet_icon_img = pygame.transform.scale(
            pygame.image.load(MAGNET_ICON_IMG).convert_alpha(), ICON_SIZE
        )
        self.golden_apple_icon_img = pygame.transform.scale(
            pygame.image.load(GOLDEN_APPLE_ICON).convert_alpha(), (28, 28)
        )

        # ── Top HUD bar ────────────────────────────────────────────────────────
        HUD_BAR_HEIGHT = 52   # ← adjust bar height here
        raw_hud = pygame.image.load("scripts/hud.png").convert_alpha()
        self.hud_bar_img    = pygame.transform.scale(raw_hud, (WINDOW_WIDTH, HUD_BAR_HEIGHT))
        self.hud_bar_height = HUD_BAR_HEIGHT

        self.reset_game()

    # ── reset ──────────────────────────────────────────────────────────────────
    def reset_game(self):
        self.player             = Player()
        self.falling_objects    = []
        self.score              = 0
        self.lives              = MAX_LIVES
        self.fall_speed         = INITIAL_FALL_SPEED
        self.spawn_timer        = 0
        self.spawn_delay        = 120
        self.pending_spawns     = []
        self.game_over          = False
        self.difficulty_level       = 0
        self.last_difficulty_score  = 0
        self.personal_best          = get_last_score()
        self.new_record             = False
        self.score_saved            = False
        self.gameover_music_started = False
        self.heart_flash_timer      = 0
        self.golden_apples_caught   = 0
        self.golden_apple_flash_timer = 0
        self.rotten_magnet_active   = False
        self.rotten_magnet_timer    = 0
        self.rotten_magnet_duration = 5 * FPS

        COOLDOWN = 120 * FPS
        DURATION = 5   * FPS

        self.shield_active       = False
        self.shield_timer        = 0
        self.shield_cooldown     = 0
        self.shield_duration     = DURATION
        self.shield_cooldown_max = COOLDOWN

        self.magnet_active       = False
        self.magnet_timer        = 0
        self.magnet_cooldown     = 0
        self.magnet_duration     = DURATION
        self.magnet_cooldown_max = COOLDOWN

        self.apple_pts_mult          = 1.0
        self.golden_apple_spawn_mult = 1.0

        self.worm_chance_increase = 0.05
        self.frenzy_active        = False
        self.frenzy_timer         = 0
        self.frenzy_ticks_total   = FRENZY_DURATION_SEC * FPS
        self.last_frenzy_trigger  = 0
        self.frenzy_flash_timer   = 0
        self.post_frenzy_grace    = 0

    # ── frenzy helpers ─────────────────────────────────────────────────────────
    def _start_frenzy(self):
        self.frenzy_active      = True
        self.frenzy_timer       = self.frenzy_ticks_total
        self.frenzy_flash_timer = 90
        self.falling_objects    = [o for o in self.falling_objects if o.type != 'bomb']
        PlayBG.stop()
        FRENZY_BGM.play(-1)

    def _end_frenzy(self):
        self.frenzy_active     = False
        self.frenzy_timer      = 0
        self.post_frenzy_grace = 2.5 * FPS
        FRENZY_BGM.stop()
        PlayBG.play(-1)

    def _effective_spawn_delay(self):
        if self.frenzy_active:
            return max(15, self.spawn_delay // FRENZY_SPAWN_MULT)
        return self.spawn_delay

    # ── spawning ───────────────────────────────────────────────────────────────
    def _spawn_one(self, obj_type):
        obj = FallingObject(obj_type, self.fall_speed, self.falling_objects)
        self.falling_objects.append(obj)

    def spawn_object(self):
        if self.frenzy_active:
            self._spawn_one('good')
            return

        heart_on_screen = any(o.type == 'heart' for o in self.falling_objects)
        if self.lives < MAX_LIVES and not heart_on_screen and random.random() < 0.15:
            self._spawn_one('heart')
            return

        golden_on_screen = any(o.type == 'golden_apple' for o in self.falling_objects)
        if not golden_on_screen and random.random() < 0.08 * self.golden_apple_spawn_mult:
            self._spawn_one('golden_apple')
            return

        WORM_CHANCE         = 0.30 + (self.worm_chance_increase * self.difficulty_level)
        WORM_CHANCE         = min(WORM_CHANCE, 0.65)
        ROTTEN_APPLE_CHANCE = 0.15

        roll = random.random()
        if roll < WORM_CHANCE:
            self._spawn_one('bomb')
            self.pending_spawns.append(('bomb', random.randint(20, 60)))
        elif roll < WORM_CHANCE + ROTTEN_APPLE_CHANCE:
            self._spawn_one('rotten_apple')
            self.pending_spawns.append(('rotten_apple', random.randint(20, 60)))
        else:
            self._spawn_one('good')
            self.pending_spawns.append(('good', random.randint(20, 60)))

    # ── score saving ───────────────────────────────────────────────────────────
    def _try_save_score(self):
        if self.score_saved:
            return
        if self.personal_best is None:
            if self.score > 0:
                save_score(self.score)
                self.score_saved = True
        elif self.score > self.personal_best:
            save_score(self.score)
            self.score_saved = True

    # ── update ─────────────────────────────────────────────────────────────────
    def update(self):
        if self.game_over:
            PlayBG.stop()
            FRENZY_BGM.stop()
            if not self.gameover_music_started:
                G_O.play(-1)
                G_O.set_volume(1)
                self.gameover_music_started = True
            return

        keys = pygame.key.get_pressed()
        self.player.move(keys)

        if self.heart_flash_timer > 0:
            self.heart_flash_timer -= 1
        if self.golden_apple_flash_timer > 0:
            self.golden_apple_flash_timer -= 1
        if self.rotten_magnet_active:
            self.rotten_magnet_timer -= 1
            if self.rotten_magnet_timer <= 0:
                self.rotten_magnet_active = False

        if self.post_frenzy_grace > 0:
            self.post_frenzy_grace -= 1

        if self.shield_active:
            self.shield_timer -= 1
            if self.shield_timer <= 0:
                self.shield_active   = False
                self.shield_cooldown = self.shield_cooldown_max
        elif self.shield_cooldown > 0:
            self.shield_cooldown -= 1

        if self.magnet_active:
            self.magnet_timer -= 1
            if self.magnet_timer <= 0:
                self.magnet_active   = False
                self.magnet_cooldown = self.magnet_cooldown_max
        elif self.magnet_cooldown > 0:
            self.magnet_cooldown -= 1

        if self.magnet_active:
            target_x = self.player.rect.centerx
            target_y = self.player.rect.centery
            for obj in self.falling_objects[:]:
                if obj.type in ('good', 'golden_apple', 'heart'):
                    ox = obj.x + obj.width // 2
                    oy = obj.y + obj.height // 2
                    if ox < target_x: obj.x += 3
                    elif ox > target_x: obj.x -= 3
                    if oy > target_y: obj.y -= 3
                    if abs(ox - target_x) < 20 and abs(oy - target_y) < 20:
                        if obj.type == 'good':
                            self.score += int(1 * self.apple_pts_mult)
                            PC.play(); PC.set_volume(0.8)
                            if self.personal_best is not None and self.score > self.personal_best:
                                self.new_record = True
                        elif obj.type == 'golden_apple':
                            self.golden_apples_caught += 1
                            self.golden_apple_flash_timer = 90
                            PC.play(); PC.set_volume(1.0)
                        elif obj.type == 'heart':
                            if self.lives < MAX_LIVES:
                                self.lives += 1
                            PC.play(); PC.set_volume(1.0)
                            self.heart_flash_timer = 90
                        if obj in self.falling_objects:
                            self.falling_objects.remove(obj)

        if self.rotten_magnet_active:
            target_x = self.player.rect.centerx
            target_y = self.player.rect.centery
            for obj in self.falling_objects[:]:
                if obj.type == 'bomb':
                    ox = obj.x + obj.width // 2
                    oy = obj.y + obj.height // 2
                    if ox < target_x: obj.x += 4
                    elif ox > target_x: obj.x -= 4
                    if obj.y > target_y: obj.y -= 4
                    if abs(ox - target_x) < 20 and abs(oy - target_y) < 20:
                        if not self.shield_active:
                            self.lives -= 1
                            OW.play(); OW.set_volume(1.6)
                            if self.lives <= 0:
                                self.game_over = True
                                self._try_save_score()
                        if obj in self.falling_objects:
                            self.falling_objects.remove(obj)

        if self.frenzy_active:
            self.frenzy_timer -= 1
            if self.frenzy_flash_timer > 0:
                self.frenzy_flash_timer -= 1
            if self.frenzy_timer <= 0:
                self._end_frenzy()

        if self.golden_apples_caught >= 5 and not self.frenzy_active:
            self.golden_apples_caught = 0
            self._start_frenzy()

        still_pending = []
        for obj_type, delay in self.pending_spawns:
            delay -= 1
            if delay <= 0:
                self._spawn_one(obj_type)
            else:
                still_pending.append((obj_type, delay))
        self.pending_spawns = still_pending

        self.spawn_timer += 1
        if self.spawn_timer >= self._effective_spawn_delay():
            self.spawn_object()
            self.spawn_timer = 0

        for obj in self.falling_objects[:]:
            obj.fall()
            if obj.check_collision(self.player):
                if obj.type == 'good':
                    self.score += int(1 * self.apple_pts_mult)
                    PC.play(); PC.set_volume(0.8)
                    if self.personal_best is not None and self.score > self.personal_best:
                        self.new_record = True
                elif obj.type == 'bomb':
                    if not self.shield_active:
                        self.lives -= 1
                        OW.play(); OW.set_volume(1.6)
                        if self.lives <= 0:
                            self.game_over = True
                            self._try_save_score()
                elif obj.type == 'heart':
                    if self.lives < MAX_LIVES:
                        self.lives += 1
                    PC.play(); PC.set_volume(1.0)
                    self.heart_flash_timer = 90
                elif obj.type == 'rotten_apple':
                    if not self.shield_active:
                        self.lives -= 1
                        OW.play(); OW.set_volume(1.6)
                        if self.lives <= 0:
                            self.game_over = True
                            self._try_save_score()
                    self.rotten_magnet_active = True
                    self.rotten_magnet_timer  = self.rotten_magnet_duration
                elif obj.type == 'golden_apple':
                    self.golden_apples_caught += 1
                    self.golden_apple_flash_timer = 90
                    PC.play(); PC.set_volume(1.0)
                self.falling_objects.remove(obj)

            elif obj.is_off_screen():
                if obj.type == 'good' and not self.frenzy_active \
                        and not self.shield_active \
                        and self.post_frenzy_grace <= 0:
                    self.lives -= 1
                    OW.play(); OW.set_volume(1.0)
                    if self.lives <= 0:
                        self.game_over = True
                        self._try_save_score()
                self.falling_objects.remove(obj)

        if not self.frenzy_active:
            if self.score >= self.last_difficulty_score + SPEED_THRESHOLD and self.score > 0:
                self.difficulty_level      += 1
                LVL.play()
                self.last_difficulty_score  = (self.score // SPEED_THRESHOLD) * SPEED_THRESHOLD
                self.fall_speed  += SPEED_INCREASE
                self.fall_speed   = min(self.fall_speed, 15)
                self.spawn_delay  = max(30, self.spawn_delay - 3)
                for obj in self.falling_objects:
                    obj.fall_speed = self.fall_speed
                self.worm_chance_increase += 0.01
                self.worm_chance_increase  = min(self.worm_chance_increase, 0.13)

    # ── draw ───────────────────────────────────────────────────────────────────
    def draw(self):
        self.screen.blit(self.bg, (0, 0))

        if self.frenzy_active:
            self.screen.blit(self.frenzy_tint, (0, 0))

        self.player.draw(self.screen)

        if self.shield_active:
            pulse       = abs((self.shield_timer % 30) - 15) / 15
            radius      = int(self.player.rect.width * 0.75 + 6 * pulse)
            alpha       = int(180 + 60 * pulse)
            shield_surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(shield_surf, (80, 180, 255, alpha // 3), (radius, radius), radius)
            pygame.draw.circle(shield_surf, (100, 200, 255, alpha),     (radius, radius), radius, 3)
            pygame.draw.circle(shield_surf, (200, 240, 255, alpha // 2),(radius, radius), max(1, radius - 6), 1)
            self.screen.blit(shield_surf, (
                self.player.rect.centerx - radius,
                self.player.rect.centery - radius
            ))
            secs = max(0, self.shield_timer // FPS)
            t = self.small_font.render(f"{secs}s", True, (100, 200, 255))
            self.screen.blit(t, (
                self.player.rect.centerx - t.get_width() // 2,
                self.player.rect.top - t.get_height() - 4
            ))

        for obj in self.falling_objects:
            obj.draw(self.screen)

        self._draw_hud()

        if self.heart_flash_timer > 0:
            self._draw_heart_banner()
        if self.golden_apple_flash_timer > 0:
            self._draw_golden_apple_banner()
        if self.rotten_magnet_active:
            self._draw_rotten_magnet_effect()
        if self.frenzy_active:
            self._draw_frenzy_ui()
        if self.game_over:
            self._draw_game_over()

        pygame.draw.rect(self.screen, GOLD_DIM, (0, 0, WINDOW_WIDTH, WINDOW_HEIGHT), 4)
        pygame.display.flip()

    # ── HUD ────────────────────────────────────────────────────────────────────
    def _draw_hud(self):
        ICON_SIZE = 40
        HUD_X     = 8
        HUD_Y     = 0   # ← shift entire bar up/down

        # ── HUD bar ───────────────────────────────────────────────────────────
        self.screen.blit(self.hud_bar_img, (0, HUD_Y))
        BAR_H = self.hud_bar_height

        # ── Score text ────────────────────────────────────────────────────────
        SCORE_X   = HUD_X + 50   # ← move score LEFT/RIGHT
        score_txt = self.small_font.render(str(self.score), True, BLACK)
        SCORE_Y   = HUD_Y + (BAR_H - score_txt.get_height()) // 2  # vertically centred
        self.screen.blit(score_txt, (SCORE_X, SCORE_Y))

        # ── Magnet & Shield icons — inside HUD bar, right of apple pill ───────
        ICON_X1 = 100   # ← magnet X position (pixels from left) — move LEFT/RIGHT
        ICON_X2 = 150   # ← shield X position (pixels from left) — move LEFT/RIGHT
        ICON_Y  = HUD_Y + (BAR_H - ICON_SIZE) // 2   # vertically centred in bar

        magnet_img = pygame.transform.scale(self.magnet_icon_img, (ICON_SIZE, ICON_SIZE))
        shield_img = pygame.transform.scale(self.shield_icon_img, (ICON_SIZE, ICON_SIZE))

        if not self.magnet_active and self.magnet_cooldown > 0:
            magnet_img.set_alpha(100)
        if not self.shield_active and self.shield_cooldown > 0:
            shield_img.set_alpha(100)

        self._magnet_rect = pygame.Rect(ICON_X1, ICON_Y, ICON_SIZE, ICON_SIZE)
        self._shield_rect = pygame.Rect(ICON_X2, ICON_Y, ICON_SIZE, ICON_SIZE)

        self.screen.blit(magnet_img, (ICON_X1, ICON_Y))
        self.screen.blit(shield_img, (ICON_X2, ICON_Y))

        # ── Cooldown rings ────────────────────────────────────────────────────
        for active, timer, cooldown, cd_max, duration, ix in [
            (self.magnet_active, self.magnet_timer, self.magnet_cooldown,
             self.magnet_cooldown_max, self.magnet_duration, ICON_X1),
            (self.shield_active, self.shield_timer, self.shield_cooldown,
             self.shield_cooldown_max, self.shield_duration, ICON_X2),
        ]:
            cx_ = ix     + ICON_SIZE // 2
            cy_ = ICON_Y + ICON_SIZE // 2
            r   = ICON_SIZE // 2
            if active:
                progress  = timer / duration
                end_angle = -math.pi / 2 + 2 * math.pi * progress
                pygame.draw.arc(self.screen, (0, 255, 100),
                    (cx_ - r, cy_ - r, ICON_SIZE, ICON_SIZE),
                    -math.pi / 2, max(end_angle, -math.pi / 2 + 0.01), 4)
                secs = max(0, timer // FPS)
                t = self.small_font.render(str(secs), True, WHITE)
                self.screen.blit(t, (cx_ - t.get_width()//2, cy_ - t.get_height()//2))
            elif cooldown > 0:
                progress  = cooldown / cd_max
                end_angle = -math.pi / 2 + 2 * math.pi * progress
                pygame.draw.arc(self.screen, (255, 60, 60),
                    (cx_ - r, cy_ - r, ICON_SIZE, ICON_SIZE),
                    -math.pi / 2, max(end_angle, -math.pi / 2 + 0.01), 4)
                secs = max(0, cooldown // FPS)
                t = self.small_font.render(str(secs), True, WHITE)
                self.screen.blit(t, (cx_ - t.get_width()//2, cy_ - t.get_height()//2))

        # ── Level text ────────────────────────────────────────────────────────
        level_txt = self.small_font.render(f"LEVEL {self.difficulty_level + 1}", True, WHITE)
        self.screen.blit(level_txt, (
            WINDOW_WIDTH // 2 - level_txt.get_width() // 2, HUD_Y + 18
        ))
        if not self.frenzy_active and self.difficulty_level > 0 \
                and self.score - self.last_difficulty_score < 5:
            wave_txt = self.tiny_font.render("LEVEL UP!", True, GOLD)  # ← changed to tiny_font (size 18)
            self.screen.blit(wave_txt, (
                320 - 20, HUD_Y + 20
            ))

        # ── Hearts ────────────────────────────────────────────────────────────
        HEART_SIZE = 30
        heart_img  = pygame.transform.scale(self.heart_img, (HEART_SIZE, HEART_SIZE))
        hx = WINDOW_WIDTH - 8 - (MAX_LIVES * HEART_SIZE + (MAX_LIVES - 1) * 4)
        hy = HUD_Y + 10
        for i in range(MAX_LIVES):
            x = hx + i * (HEART_SIZE + 4)
            if i < self.lives:
                self.screen.blit(heart_img, (x, hy))
            else:
                dim = heart_img.copy(); dim.set_alpha(50)
                self.screen.blit(dim, (x, hy))

    def _draw_heart_banner(self):
        alpha  = int(255 * min(self.heart_flash_timer / 30, 1.0))
        pulse  = abs((self.heart_flash_timer % 30) - 15) / 15
        hf     = pygame.font.Font(None, int(44 + 6 * pulse))
        banner = hf.render("+1 Life!", True, RED)
        shadow = hf.render("+1 Life!", True, BLACK)
        banner.set_alpha(alpha); shadow.set_alpha(alpha)
        bx = WINDOW_WIDTH // 2 - banner.get_width() // 2
        by = WINDOW_HEIGHT // 2 - 40
        self.screen.blit(shadow, (bx + 2, by + 2))
        self.screen.blit(banner, (bx, by))

    def _draw_golden_apple_banner(self):
        alpha     = int(255 * min(self.golden_apple_flash_timer / 30, 1.0))
        pulse     = abs((self.golden_apple_flash_timer % 30) - 15) / 15
        hf        = pygame.font.Font(None, int(44 + 6 * pulse))
        remaining = 5 - self.golden_apples_caught
        text      = f"FRENZY IN {remaining}!" if remaining > 0 else "FRENZY!"
        banner    = hf.render(text, True, GOLD)
        shadow    = hf.render(text, True, BLACK)
        banner.set_alpha(alpha); shadow.set_alpha(alpha)
        bx = WINDOW_WIDTH // 2 - banner.get_width() // 2
        by = WINDOW_HEIGHT // 2 - 80
        self.screen.blit(shadow, (bx + 2, by + 2))
        self.screen.blit(banner, (bx, by))

    def _draw_rotten_magnet_effect(self):
        pulse  = abs((self.rotten_magnet_timer % 30) - 15) / 15
        radius = int(self.player.rect.width * 0.80 + 8 * pulse)
        alpha  = int(160 + 80 * pulse)
        surf   = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(surf, (180, 0, 80, alpha // 3), (radius, radius), radius)
        pygame.draw.circle(surf, (220, 50, 120, alpha),    (radius, radius), radius, 3)
        self.screen.blit(surf, (
            self.player.rect.centerx - radius,
            self.player.rect.centery - radius
        ))
        secs = max(0, self.rotten_magnet_timer // FPS)
        t = self.small_font.render(f"CURSED {secs}s", True, (220, 50, 120))
        self.screen.blit(t, (
            self.player.rect.centerx - t.get_width() // 2,
            self.player.rect.top - t.get_height() - 20
        ))

    def _draw_frenzy_ui(self):
        if self.frenzy_flash_timer > 0:
            alpha  = int(255 * (self.frenzy_flash_timer / 90))
            pulse  = abs((self.frenzy_flash_timer % 30) - 15) / 15
            scale  = 1.0 + 0.04 * pulse
            pw     = int(self.frenzy_banner_img.get_width()  * scale)
            ph     = int(self.frenzy_banner_img.get_height() * scale)
            pulsed = pygame.transform.scale(self.frenzy_banner_img, (pw, ph))
            pulsed.set_alpha(alpha)
            bx = WINDOW_WIDTH  // 2 - pw // 2
            by = WINDOW_HEIGHT // 2 - ph // 2 - 30
            self.screen.blit(pulsed, (bx, by))

    def _draw_game_over(self):
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))

        SCORE_PANEL_Y        = 260
        SCORE_BOX_TOP_RATIO  = 0.20
        TROPHY_PANEL_Y       = 140
        TROPHY_BOX_TOP_RATIO = 0.60

        if self.new_record:
            panel     = self.trophy_highscore_img
            PANEL_Y   = TROPHY_PANEL_Y
            BOX_RATIO = TROPHY_BOX_TOP_RATIO
            G_O.stop(); H_S.play(-1); H_S.set_volume(0.4)
        else:
            panel     = self.score_panel_img
            PANEL_Y   = SCORE_PANEL_Y
            BOX_RATIO = SCORE_BOX_TOP_RATIO

        panel_x = WINDOW_WIDTH // 2 - panel.get_width() // 2
        self.screen.blit(panel, (panel_x, PANEL_Y))

        box_top    = PANEL_Y + int(panel.get_height() * BOX_RATIO)
        box_bottom = PANEL_Y + panel.get_height()
        box_center = (box_top + box_bottom) // 2

        fs_value = self.large_font.render(str(self.score), True, (80, 40, 0))

        if self.personal_best is not None and not self.new_record:
            pb_surf = self.small_font.render(f"Personal best: {self.personal_best}", True, (80, 40, 0))
        else:
            pb_surf = None

        score_h    = fs_value.get_height() + 2
        pb_h       = pb_surf.get_height() + 2 if pb_surf else 0
        total_h    = score_h + pb_h
        text_start = box_center - total_h // 2

        self.screen.blit(fs_value, (WINDOW_WIDTH//2 - fs_value.get_width()//2, text_start))
        if pb_surf:
            self.screen.blit(pb_surf, (WINDOW_WIDTH//2 - pb_surf.get_width()//2, text_start + score_h))

        btn_y = PANEL_Y + panel.get_height() + 14
        self.btn_play_again.rect.centerx = WINDOW_WIDTH // 2
        self.btn_main_menu.rect.centerx  = WINDOW_WIDTH // 2
        self.btn_play_again.rect.y = btn_y
        self.btn_main_menu.rect.y  = btn_y + 58 + 12

        mouse_pos = pygame.mouse.get_pos()
        self.btn_play_again.update(mouse_pos)
        self.btn_main_menu.update(mouse_pos)
        self.btn_play_again.draw(self.screen, self.font_btn)
        self.btn_main_menu.draw(self.screen, self.font_btn)

    # ── run loop ───────────────────────────────────────────────────────────────
    def run(self):
        from assets import BGS
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not self.game_over:
                    mx, my = event.pos
                    if hasattr(self, '_shield_rect') and self._shield_rect.collidepoint(mx, my):
                        if not self.shield_active and self.shield_cooldown == 0:
                            self.shield_active = True
                            self.shield_timer  = self.shield_duration
                    if hasattr(self, '_magnet_rect') and self._magnet_rect.collidepoint(mx, my):
                        if not self.magnet_active and self.magnet_cooldown == 0:
                            self.magnet_active = True
                            self.magnet_timer  = self.magnet_duration

                if event.type == pygame.KEYDOWN and not self.game_over:
                    if event.key == pygame.K_w:
                        if not self.magnet_active and self.magnet_cooldown == 0:
                            self.magnet_active = True
                            self.magnet_timer  = self.magnet_duration
                    if event.key == pygame.K_s:
                        if not self.shield_active and self.shield_cooldown == 0:
                            self.shield_active = True
                            self.shield_timer  = self.shield_duration

                if event.type == pygame.KEYDOWN and self.game_over:
                    if event.key == pygame.K_r:
                        return 'restart'
                    elif event.key == pygame.K_q:
                        pygame.quit(); sys.exit()

                if self.game_over:
                    if self.btn_play_again.handle_event(event):
                        G_O.stop(); BGS.stop(); PlayBG.play(-1)
                        return 'restart'
                    if self.btn_main_menu.handle_event(event):
                        PlayBG.stop(); G_O.stop(); FRENZY_BGM.stop(); H_S.stop()
                        BGS.stop(); BGS.play(-1); BGS.set_volume(1)
                        return 'menu'

            self.update()
            self.draw()
            self.clock.tick(FPS)
