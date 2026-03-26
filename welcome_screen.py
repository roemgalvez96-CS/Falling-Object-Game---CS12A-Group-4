# ============================================================
# WELCOME SCREEN — image-based buttons, HTP overlay
# ============================================================

import pygame
import sys
import os
from constants import (
    WINDOW_WIDTH, WINDOW_HEIGHT, FPS,
    WHITE, GREY_LIGHT, GOLD, GOLD_DIM,
    MENU_BG_IMG,
    BTN_START_IMG, BTN_START_HOVER_IMG,
    BTN_HTP_IMG, BTN_HTP_HOVER_IMG,
)
from scores import get_last_score
from assets import BGS, PlayBG


class ImageButton:
    """A button that uses two images: normal and hovered."""
    def __init__(self, x, y, w, h, normal_img, hover_img):
        self.rect       = pygame.Rect(x, y, w, h)
        self.normal_img = pygame.transform.scale(normal_img, (w, h))
        self.hover_img  = pygame.transform.scale(hover_img,  (w, h))
        self.hovered    = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True
        return False

    def update(self, mouse_pos):
        self.hovered = self.rect.collidepoint(mouse_pos)

    def draw(self, surface):
        img = self.hover_img if self.hovered else self.normal_img
        surface.blit(img, self.rect)


class WelcomeScreen:
    def __init__(self, screen, clock):
        self.screen     = screen
        self.clock      = clock
        self.font_sub   = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 28)

        base = os.path.dirname(os.path.abspath(__file__))

        # Background
        self.bg = pygame.transform.scale(
            pygame.image.load(MENU_BG_IMG).convert(), (WINDOW_WIDTH, WINDOW_HEIGHT)
        )

        # Load button images
        def load(path): return pygame.image.load(path).convert_alpha()

        start_n = load(BTN_START_IMG);  start_h = load(BTN_START_HOVER_IMG)
        htp_n   = load(BTN_HTP_IMG);    htp_h   = load(BTN_HTP_HOVER_IMG)

        BTN_W, BTN_H = 190, 70
        cx = WINDOW_WIDTH // 2 - BTN_W // 2

        START_Y = 420
        HTP_Y   = 510

        self.btn_start = ImageButton(cx, START_Y, BTN_W, BTN_H, start_n, start_h)
        self.btn_htp   = ImageButton(cx, HTP_Y,   BTN_W, BTN_H, htp_n,   htp_h)

        self.last_score = get_last_score()

        # ── HTP overlay assets ────────────────────────────────────────────────
        htp_raw = pygame.image.load(
            os.path.join(base, "scripts", "how_to_play.png")
        ).convert_alpha()
        self.htp_img = pygame.transform.scale(htp_raw, (WINDOW_WIDTH, WINDOW_HEIGHT))

        x_raw = pygame.image.load(
            os.path.join(base, "scripts", "x_button.png")
        ).convert_alpha()
        X_SIZE       = (48, 48)   # ← resize X button here
        self.x_img   = pygame.transform.scale(x_raw, X_SIZE)
        self.x_hover = self.x_img.copy()
        self.x_hover.fill((255, 80, 80, 100), special_flags=pygame.BLEND_RGBA_ADD)

        X_MARGIN   = 50           # ← margin from top-right edge
        self.x_rect = self.x_img.get_rect(
            topright=(WINDOW_WIDTH - X_MARGIN, X_MARGIN)
        )

        # Dim overlay behind HTP image
        self.dim = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        self.dim.fill((0, 0, 0, 160))

        self.show_htp = False     # toggle for HTP overlay

    # ── draw ──────────────────────────────────────────────────────────────────
    def _draw(self, mouse_pos):
        # Always draw the menu background
        self.screen.blit(self.bg, (0, 0))

        # Personal best
        PB_Y = 310
        if self.last_score is not None:
            pb_value = self.font_sub.render(str(self.last_score), True, WHITE)
        else:
            pb_value = self.font_small.render("--", True, GREY_LIGHT)
        self.screen.blit(pb_value, (WINDOW_WIDTH // 2 - pb_value.get_width() // 2, PB_Y))

        # Buttons (only interactive when HTP is not open)
        if not self.show_htp:
            self.btn_start.draw(self.screen)
            self.btn_htp.draw(self.screen)

        # ── HTP overlay on top ────────────────────────────────────────────────
        if self.show_htp:
            self.screen.blit(self.dim,     (0, 0))          # dim the menu
            self.screen.blit(self.htp_img, (0, 0))          # HTP image

            x_hovered = self.x_rect.collidepoint(mouse_pos)
            self.screen.blit(
                self.x_hover if x_hovered else self.x_img,
                self.x_rect
            )

    # ── main loop ─────────────────────────────────────────────────────────────
    def run(self):
        result = None
        while result is None:
            mouse_pos = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()

                if self.show_htp:
                    # Close HTP on X click or ESC
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                        self.show_htp = False
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        if self.x_rect.collidepoint(event.pos):
                            self.show_htp = False
                else:
                    # Normal menu interactions
                    if self.btn_start.handle_event(event):
                        BGS.stop()
                        PlayBG.play(-1)
                        result = 'start'
                    if self.btn_htp.handle_event(event):
                        self.show_htp = True   # open overlay

            if not self.show_htp:
                self.btn_start.update(mouse_pos)
                self.btn_htp.update(mouse_pos)

            self._draw(mouse_pos)
            pygame.display.flip()
            self.clock.tick(FPS)

        return result
