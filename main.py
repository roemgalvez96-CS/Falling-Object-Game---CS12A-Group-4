# ============================================================
# MAIN — entry point, wires everything together
# ============================================================

import pygame
import sys

from constants import WINDOW_WIDTH, WINDOW_HEIGHT, FPS
from assets import BGS
from welcome_screen import WelcomeScreen
from game import Game


def main():
    pygame.init()
    pygame.mixer.init()

    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Worminator")
    clock = pygame.time.Clock()

    BGS.play(-1)

    while True:
        # ── Welcome / title screen ────────────────────────────────────────────
        welcome = WelcomeScreen(screen, clock)
        result  = welcome.run()

        if result == 'start':
            # ── Game loop ────────────────────────────────────────────────────
            while True:
                game    = Game()
                outcome = game.run()
                if outcome == 'restart':
                    continue
                else:
                    break   # 'menu' → back to welcome screen


if __name__ == "__main__":
    main()
