# ============================================================
# BUTTON — reusable clickable button widget
# ============================================================

import pygame
from constants import WHITE, BLACK, GREY_LIGHT, CYAN, CYAN_DIM


class Button:
    def __init__(self, x, y, w, h, label,
                 base_color=CYAN_DIM, hover_color=CYAN, text_color=WHITE, hover_text_color=BLACK):
        self.rect            = pygame.Rect(x, y, w, h)
        self.label           = label
        self.base_color      = base_color
        self.hover_color     = hover_color
        self.text_color      = text_color
        self.hover_text_color = hover_text_color
        self.hovered         = False
        self.flash           = 0

    def handle_event(self, event):
        """Return True on left-click inside the button."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.flash = 8
                return True
        return False

    def update(self, mouse_pos):
        self.hovered = self.rect.collidepoint(mouse_pos)
        if self.flash > 0:
            self.flash -= 1

    def draw(self, surface, font):
        fill       = WHITE if self.flash > 0 else (self.hover_color if self.hovered else self.base_color)
        border_col = WHITE if (self.hovered or self.flash) else GREY_LIGHT
        txt_col    = self.hover_text_color if (self.hovered or self.flash) else self.text_color

        pygame.draw.rect(surface, BLACK,      self.rect.move(4, 4), border_radius=6)
        pygame.draw.rect(surface, fill,       self.rect,            border_radius=6)
        pygame.draw.rect(surface, border_col, self.rect, width=2,   border_radius=6)

        ts = font.render(self.label, True, txt_col)
        surface.blit(ts, (self.rect.centerx - ts.get_width()  // 2,
                          self.rect.centery - ts.get_height() // 2))