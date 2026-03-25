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
    pygame.display.set_caption("Worminator - v1.6 (Beta)")
    clock = pygame.time.Clock()

    BGS.play(-1)

    while True:
        # ── Welcome / title screen ────────────────────────────────────────────
        welcome = WelcomeScreen(screen, clock)
        result = welcome.run()

        if result == 'start':
            # ── Pet selection screen ──────────────────────────────────────────

            # ── Game loop ────────────────────────────────────────────────────
            while True:
                game = Game()  # Create an instance of Game
                result = game.run()  # Call run() on the instance
                if result == 'restart':
                    continue
                else:
                    break  # 'menu' → back to welcome screen

        elif result == 'how_to_play':
            _show_how_to_play(screen, clock)


def _show_how_to_play(screen, clock):
    font_title = pygame.font.Font(None, 52)
    font_body = pygame.font.Font(None, 28)
    font_small = pygame.font.Font(None, 24)

    # Create Back button
    from button import Button
    back_btn = Button(
        WINDOW_WIDTH // 2 - 100,
        WINDOW_HEIGHT - 80,
        200, 50,
        "BACK",
        base_color=(100, 100, 100),
        hover_color=(150, 150, 150)
    )

    lines = [
        ("HOW TO PLAY", True),
        ("", False),
        ("← → or A D  —  Move your character", False),
        ("", False),
        ("Catch apples to score points.", False),
        ("Miss an apple = lose a life.", False),
        ("Lose all 3 lives = Game Over.", False),
        ("", False),
        ("Apple        — +1 point (catch it!)", False),
        ("Worm         — avoid! Lose a life.", False),
        ("Golden Apple — collect 5 → Frenzy Mode!", False),
        ("Rotten Apple — cursed! Worms chase you.", False),
        ("Heart        — restores 1 life.", False),
        ("", False),
        ("W —  Activate Magnet", False),
        ("S —  Activate Shield", False),
        ("", False),
        ("APPLE FRENZY MODE", True),
        ("Collect 5 golden apples to trigger Frenzy!", False),
        ("Apples rain down — catch as many as you can!", False),
        ("Missed apples won't cost lives for 3 seconds", False),
        ("after Frenzy ends.", False),
        ("", False),
        ("Press ESC or click BACK to return.", False),
    ]

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Handle Back button click
            if back_btn.handle_event(event):
                running = False

            # Handle ESC key press
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

            # Handle mouse click anywhere (but not on the button)
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                if not back_btn.rect.collidepoint(mx, my):
                    running = False

        screen.fill((15, 10, 30))

        # Draw a soft panel
        panel = pygame.Surface((WINDOW_WIDTH - 40, WINDOW_HEIGHT - 100), pygame.SRCALPHA)
        panel.fill((0, 0, 0, 160))
        screen.blit(panel, (20, 30))

        y = 44
        for text, is_title in lines:
            if is_title:
                surf = font_title.render(text, True, (255, 215, 0))
            else:
                surf = font_body.render(text, True, (220, 220, 255))
            screen.blit(surf, (WINDOW_WIDTH // 2 - surf.get_width() // 2, y))
            y += surf.get_height() + (8 if is_title else 4)

        # Draw Back button
        mouse_pos = pygame.mouse.get_pos()
        back_btn.update(mouse_pos)
        back_btn.draw(screen, font_body)

        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    main()