# ============================================================
# MAIN — entry point, wires everything together
# ============================================================

import pygame
import sys

from constants import WINDOW_WIDTH, WINDOW_HEIGHT, FPS
from assets import BGS          # starts BGM on import
from welcome_screen import WelcomeScreen
from game import Game


def main():
    pygame.init()
    pygame.mixer.init()

    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Worminator - v1.6 (Beta)")
    clock = pygame.time.Clock()

    BGS.play(-1)   # menu background music

    while True:
        # ── Welcome / title screen ────────────────────────────────────────────
        welcome = WelcomeScreen(screen, clock)
        result  = welcome.run()

        if result == 'start':
            # ── Game loop (supports restart without re-showing menu) ──────────
            while True:
                game    = Game()
                outcome = game.run()
                if outcome == 'restart':
                    continue
                else:
                    break
        elif result == 'shop':
            pass  # shop screen — implement later
        elif result == 'how_to_play':
            # ── How To Play screen — plug in your image here later ────────────
            pass  # will be implemented when image is provided


if __name__ == "__main__":
    main()