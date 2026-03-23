# ============================================================
# WELCOME SCREEN — image-based buttons, personal best sign
# ============================================================

import pygame
import sys
from constants import (
    WINDOW_WIDTH, WINDOW_HEIGHT, FPS,
    WHITE, GREY_LIGHT, GOLD, GOLD_DIM,
    MENU_BG_IMG,
    BTN_START_IMG, BTN_START_HOVER_IMG,
    BTN_SHOP_IMG, BTN_SHOP_HOVER_IMG,
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

        # Background
        self.bg = pygame.transform.scale(
            pygame.image.load(MENU_BG_IMG).convert(), (WINDOW_WIDTH, WINDOW_HEIGHT)
        )



        # Load button images
        def load(path): return pygame.image.load(path).convert_alpha()

        start_n  = load(BTN_START_IMG);       start_h  = load(BTN_START_HOVER_IMG)
        shop_n   = load(BTN_SHOP_IMG);        shop_h   = load(BTN_SHOP_HOVER_IMG)
        htp_n    = load(BTN_HTP_IMG);         htp_h    = load(BTN_HTP_HOVER_IMG)

        # Button sizes  ← change (w, h) to resize buttons
        BTN_W, BTN_H = 190, 70
        cx = WINDOW_WIDTH // 2 - BTN_W // 2

        # Button Y positions  ← change these to reposition buttons
        START_Y  = 390
        SHOP_Y   = 475
        HTP_Y    = 555

        self.btn_start = ImageButton(cx, START_Y,  BTN_W, BTN_H, start_n, start_h)
        self.btn_shop  = ImageButton(cx, SHOP_Y,   BTN_W, BTN_H, shop_n,  shop_h)
        self.btn_htp   = ImageButton(cx, HTP_Y,    BTN_W, BTN_H, htp_n,   htp_h)

        self.last_score = get_last_score()

    # ── draw ──────────────────────────────────────────────────────────────────
    def _draw(self):
        self.screen.blit(self.bg, (0, 0))

        # ── Personal best display ─────────────────────────────────────────────
        # PB_Y: vertical position of the personal best text ← change to reposition
        PB_Y = 290
        pb_label = self.font_small.render("", True, GOLD)
        self.screen.blit(pb_label, (WINDOW_WIDTH // 2 - pb_label.get_width() // 2, PB_Y))

        if self.last_score is not None:
            pb_value = self.font_sub.render(str(self.last_score), True, WHITE)
        else:
            pb_value = self.font_small.render("No score yet", True, GREY_LIGHT)
        self.screen.blit(pb_value, (WINDOW_WIDTH // 2 - pb_value.get_width() // 2, PB_Y + pb_label.get_height() + 4))

        # Buttons
        self.btn_start.draw(self.screen)
        self.btn_shop.draw(self.screen)
        self.btn_htp.draw(self.screen)

    # ── main loop ─────────────────────────────────────────────────────────────
    def run(self):
        result = None
        while result is None:
            mouse_pos = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                if self.btn_start.handle_event(event):
                    BGS.stop()
                    PlayBG.play(-1)
                    result = 'start'
                if self.btn_shop.handle_event(event):
                    result = 'shop'
                if self.btn_htp.handle_event(event):
                    result = 'how_to_play'

            self.btn_start.update(mouse_pos)
            self.btn_shop.update(mouse_pos)
            self.btn_htp.update(mouse_pos)

            self._draw()
            pygame.display.flip()
            self.clock.tick(FPS)

        return result