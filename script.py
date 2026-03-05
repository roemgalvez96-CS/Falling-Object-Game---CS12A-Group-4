import pygame
import random
import sys
import os

from pygame.mixer_music import stop

# ── SETUP ──────────────────────────────────────────────────────────────────────
pygame.init()
pygame.mixer.init()

WINDOW_WIDTH  = 500
WINDOW_HEIGHT = 900
FPS           = 120

WHITE      = (255, 255, 255)
BLACK      = (0,   0,   0)
RED        = (255, 0,   0)
GREEN      = (0,   255, 0)
BLUE       = (0,   100, 255)
YELLOW     = (255, 255, 0)
BG_DARK    = (8,   8,   24)
STAR_WHITE = (220, 220, 255)
GOLD       = (255, 215, 0)
GOLD_DIM   = (180, 140, 0)
CYAN       = (0,   220, 255)
CYAN_DIM   = (0,   120, 160)
GREY_LIGHT = (180, 180, 200)
ORANGE     = (255, 160, 0)

INITIAL_FALL_SPEED = 3
SPEED_INCREASE     = 1.5
SPEED_THRESHOLD    = 20
SCORE_FILE         = 'warmup.txt'

BASE_DIR = os.path.dirname(__file__)


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 1 — GAME MUSIC
# ══════════════════════════════════════════════════════════════════════════════
# Loads all audio assets and starts the background music on launch.
# bgm        – looping background track for the main menu
# points_catch – short sound played when a good apple is caught
# playing    – in-game background music while a round is active
# gameover   – looping audio shown on the game-over screen
# level      – jingle that fires each time the difficulty level increases
# ──────────────────────────────────────────────────────────────────────────────

bgm          = pygame.mixer.Sound("falling_game_bgm.wav")
points_catch = pygame.mixer.Sound("catch.wav")
playing      = pygame.mixer.Sound("catch_music.wav")
gameover     = pygame.mixer.Sound("gameover_loop.wav")
level        = pygame.mixer.Sound("level_up.wav")

bgm.play(-1)   # start menu music immediately


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 2 — MAIN MENU
# ══════════════════════════════════════════════════════════════════════════════
# Helpers for reading / writing the personal-best score file, the reusable
# Button widget, and the WelcomeScreen class that drives the title screen and
# the credits screen.
# ──────────────────────────────────────────────────────────────────────────────

def get_last_score():
    try:
        with open(SCORE_FILE, 'r') as f:
            lines = [ln.strip() for ln in f.readlines() if ln.strip()]
        if not lines:
            return None
        return int(lines[-1])
    except (FileNotFoundError, ValueError):
        return None


def save_score(score):
    with open(SCORE_FILE, 'a') as f:
        f.write(str(score) + '\n')


class Button:
    def __init__(self, x, y, w, h, label,
                 base_color=CYAN_DIM, hover_color=CYAN, text_color=WHITE):
        self.rect        = pygame.Rect(x, y, w, h)
        self.label       = label
        self.base_color  = base_color
        self.hover_color = hover_color
        self.text_color  = text_color
        self.hovered     = False
        self.flash       = 0

    def handle_event(self, event):
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
        txt_col    = BLACK if (self.hovered or self.flash) else self.text_color
        pygame.draw.rect(surface, (0, 0, 0), self.rect.move(4, 4), border_radius=6)
        pygame.draw.rect(surface, fill,       self.rect,            border_radius=6)
        pygame.draw.rect(surface, border_col, self.rect, width=2,   border_radius=6)
        ts = font.render(self.label, True, txt_col)
        surface.blit(ts, (self.rect.centerx - ts.get_width() // 2,
                          self.rect.centery - ts.get_height() // 2))


class WelcomeScreen:
    def __init__(self, screen, clock):
        self.screen = screen
        self.clock  = clock
        self.state  = 'menu'
        self.font_title = pygame.font.Font(None, 97)
        self.font_sub   = pygame.font.Font(None, 32)
        self.font_sub2  = pygame.font.Font(None, 28)
        self.font_btn   = pygame.font.Font(None, 38)
        self.font_small = pygame.font.Font(None, 28)
        bw, bh = 240, 58
        cx = WINDOW_WIDTH // 2 - bw // 2
        self.btn_start   = Button(cx, 510, bw, bh, "START GAME",
                                  base_color=(0, 130, 60), hover_color=(0, 200, 80))
        self.btn_credits = Button(cx, 590, bw, bh, "CREDITS",
                                  base_color=CYAN_DIM, hover_color=CYAN)
        self.btn_quit    = Button(cx, 670, bw, bh, "QUIT",
                                  base_color=(120, 20, 20), hover_color=(200, 40, 40))
        self.btn_back    = Button(WINDOW_WIDTH // 2 - 100, 780, 200, 50, "BACK",
                                  base_color=CYAN_DIM, hover_color=CYAN)
        self.last_score = get_last_score()

    def _draw_title(self):
        title = self.font_title.render("A FALL", True, GOLD)
        self.screen.blit(title, (WINDOW_WIDTH // 2 - title.get_width() // 2, 140))
        sub  = self.font_sub2.render("CATCH ALL THE RED APPLES", True, GREY_LIGHT)
        sub2 = self.font_sub2.render("AND AVOID THE ROTTEN ONE", True, GREY_LIGHT)
        self.screen.blit(sub,  (WINDOW_WIDTH // 2 - sub.get_width()  // 2, 250))
        self.screen.blit(sub2, (WINDOW_WIDTH // 2 - sub2.get_width() // 2, 280))

        if self.last_score is not None:
            panel_w, panel_h = 200, 72
            panel_x = WINDOW_WIDTH // 2 - panel_w // 2
            panel_surf = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
            panel_surf.fill((255, 215, 0, 18))
            self.screen.blit(panel_surf, (panel_x, 330))
            pygame.draw.rect(self.screen, GOLD_DIM, (panel_x, 330, panel_w, panel_h), 1, border_radius=6)
            label = self.font_small.render("PERSONAL BEST", True, GOLD_DIM)
            value = self.font_sub.render(str(self.last_score), True, GOLD)
            self.screen.blit(label, (WINDOW_WIDTH // 2 - label.get_width() // 2, 335))
            self.screen.blit(value, (WINDOW_WIDTH // 2 - value.get_width() // 2, 365))
        else:
            hint = self.font_small.render("No score yet  --  play to set a record!", True, GREY_LIGHT)
            self.screen.blit(hint, (WINDOW_WIDTH // 2 - hint.get_width() // 2, 318))

    def _draw_credits(self):
        lines = [
            ("A FALL",                    self.font_title, GOLD,       160),
            ("A Pygame Mini-Game",        self.font_sub,   GREY_LIGHT, 265),
            ("Game Design & Code",        self.font_sub,   CYAN,       360),
            ("Basta namin",               self.font_sub,   WHITE,      400),
            ("Built with",                self.font_sub,   GREY_LIGHT, 470),
            ("Python  &  Pygame",         self.font_sub,   WHITE,      510),
            ("Controls: A / D to move",   self.font_small, GREY_LIGHT, 590),
            ("R = Restart  |  Q = Quit",  self.font_small, GREY_LIGHT, 620),
        ]
        for text, font, color, y in lines:
            s = font.render(text, True, color)
            self.screen.blit(s, (WINDOW_WIDTH // 2 - s.get_width() // 2, y))

    def run(self):
        result = None
        while result is None:
            mouse_pos = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                if self.state == 'menu':
                    if self.btn_start.handle_event(event):
                        bgm.stop()
                        playing.play(-1)
                        result = 'start'
                    if self.btn_credits.handle_event(event): self.state = 'credits'
                    if self.btn_quit.handle_event(event):    pygame.quit(); sys.exit()
                elif self.state == 'credits':
                    if self.btn_back.handle_event(event):    self.state = 'menu'
            if self.state == 'menu':
                self.btn_start.update(mouse_pos)
                self.btn_credits.update(mouse_pos)
                self.btn_quit.update(mouse_pos)
            else:
                self.btn_back.update(mouse_pos)
            self.screen.fill(BG_DARK)
            if self.state == 'menu':
                self._draw_title()
                self.btn_start.draw(self.screen, self.font_btn)
                self.btn_credits.draw(self.screen, self.font_btn)
                self.btn_quit.draw(self.screen, self.font_btn)
            else:
                self._draw_credits()
                self.btn_back.draw(self.screen, self.font_btn)
            pygame.display.flip()
            self.clock.tick(FPS)
        return result


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 3 — GAME ALGORITHM
# ══════════════════════════════════════════════════════════════════════════════
# Contains the core gameplay logic: the Player basket, the FallingObject
# (apples / bombs), and the Game controller that ties spawning, collision,
# difficulty scaling, drawing, and the game-loop together.
# ──────────────────────────────────────────────────────────────────────────────

class Player:
    def __init__(self):
        self.width  = 60
        self.height = 60
        self.x      = WINDOW_WIDTH // 2 - self.width // 2
        self.y      = WINDOW_HEIGHT - self.height - 10
        self.speed  = 7
        self.color  = BLUE

    def move(self, keys):
        if keys[pygame.K_a] and self.x > 0:
            self.x -= self.speed
        if keys[pygame.K_d] and self.x < WINDOW_WIDTH - self.width:
            self.x += self.speed

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(screen, WHITE, (self.x + 5, self.y + 5, self.width - 10, self.height - 10), 3)


class FallingObject:
    def __init__(self, obj_type, fall_speed):
        self.width      = 40
        self.height     = 40
        self.x          = random.randint(0, WINDOW_WIDTH - self.width)
        self.y          = -self.height
        self.fall_speed = fall_speed
        self.type       = obj_type
        self.color      = GREEN if self.type == 'good' else RED

    def fall(self):
        self.y += self.fall_speed

    def draw(self, screen):
        cx = self.x + self.width  // 2
        cy = self.y + self.height // 2
        r  = self.width // 2
        if self.type == 'good':
            pygame.draw.circle(screen, self.color, (cx, cy), r)
            pygame.draw.circle(screen, YELLOW,     (cx, cy), self.width // 3)
        else:
            pygame.draw.circle(screen, self.color, (cx, cy), r)
            pygame.draw.line(screen, BLACK, (cx, self.y), (cx - 5, self.y - 10), 3)

    def is_off_screen(self):
        return self.y > WINDOW_HEIGHT

    def check_collision(self, player):
        return (self.x < player.x + player.width  and
                self.x + self.width  > player.x   and
                self.y < player.y + player.height  and
                self.y + self.height > player.y)


class Game:
    def __init__(self):
        self.screen     = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Game")
        self.clock      = pygame.time.Clock()
        self.font       = pygame.font.Font(None, 36)
        self.large_font = pygame.font.Font(None, 72)
        self.small_font = pygame.font.Font(None, 28)
        self.font_btn   = pygame.font.Font(None, 38)

        # Game-over buttons
        bw, bh = 240, 58
        cx = WINDOW_WIDTH // 2 - bw // 2
        self.btn_play_again = Button(cx, 490, bw, bh, "PLAY AGAIN",
                                     base_color=(0, 130, 60), hover_color=(0, 200, 80))
        self.btn_main_menu  = Button(cx, 570, bw, bh, "BACK TO MENU",
                                     base_color=CYAN_DIM, hover_color=CYAN)
        self.reset_game()

    def reset_game(self):
        self.player                = Player()
        self.falling_objects       = []
        self.score                 = 0
        self.lives                 = 3
        self.fall_speed            = INITIAL_FALL_SPEED
        self.spawn_timer           = 0
        self.spawn_delay           = 60
        self.game_over             = False
        self.difficulty_level      = 0
        self.last_difficulty_score = 0
        self.personal_best         = get_last_score()
        self.new_record            = False
        self.score_saved           = False
        sound_played               = False

    def spawn_object(self):
        bomb_chance = min(0.30 + (self.difficulty_level * 0.05), 0.60)
        obj_type    = 'bomb' if random.random() < bomb_chance else 'good'
        self.falling_objects.append(FallingObject(obj_type, self.fall_speed))

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

    def update(self):
        if self.game_over:
            playing.stop()
            gameover.play(-0)
            return
        keys = pygame.key.get_pressed()
        self.player.move(keys)
        self.spawn_timer += 1
        if self.spawn_timer >= self.spawn_delay:
            self.spawn_object()
            self.spawn_timer = 0
        for obj in self.falling_objects[:]:
            obj.fall()
            if obj.check_collision(self.player):
                if obj.type == 'good':
                    self.score += 1
                    points_catch.play()
                    points_catch.set_volume(0.8)
                    if self.personal_best is not None and self.score > self.personal_best:
                        self.new_record = True
                else:
                    self.lives -= 1
                    if self.lives <= 0:
                        self.game_over = True
                        self._try_save_score()
                self.falling_objects.remove(obj)
            elif obj.is_off_screen():
                self.falling_objects.remove(obj)
        if self.score >= self.last_difficulty_score + SPEED_THRESHOLD and self.score > 0:
            self.difficulty_level      += 1
            level.play()
            self.last_difficulty_score  = (self.score // SPEED_THRESHOLD) * SPEED_THRESHOLD
            self.fall_speed            += SPEED_INCREASE
            self.spawn_delay            = max(30, self.spawn_delay - 5)
            for obj in self.falling_objects:
                obj.fall_speed = self.fall_speed

    def draw(self):
        self.screen.fill("gray")
        self.player.draw(self.screen)
        for obj in self.falling_objects:
            obj.draw(self.screen)

        self.screen.blit(self.font.render(f"Score: {self.score}",              True, BLACK), (10, 10))
        self.screen.blit(self.font.render(f"Lives: {self.lives}",              True, BLACK), (10, 50))
        self.screen.blit(self.font.render(f"Level: {self.difficulty_level+1}", True, BLACK), (10, 90))

        if self.personal_best is not None:
            if self.new_record:
                pb_label, pb_color = "NEW RECORD!", ORANGE
            else:
                pb_label, pb_color = f"Best: {self.personal_best}", (150, 150, 150)
            pb_surf = self.small_font.render(pb_label, True, pb_color)
            self.screen.blit(pb_surf, (WINDOW_WIDTH - pb_surf.get_width() - 10, 10))
            if not self.new_record:
                gap = self.personal_best - self.score
                if gap > 0:
                    gap_surf = self.small_font.render(f"({gap} to beat)", True, (180, 180, 180))
                    self.screen.blit(gap_surf, (WINDOW_WIDTH - gap_surf.get_width() - 10, 36))

        if self.difficulty_level > 0 and self.score - self.last_difficulty_score < 5:
            lv = self.font.render(f"LEVEL {self.difficulty_level + 1}!", True, RED)
            self.screen.blit(lv, (WINDOW_WIDTH // 2 - lv.get_width() // 2, 10))

        if self.game_over:
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
            overlay.set_alpha(128)
            overlay.fill(BLACK)
            self.screen.blit(overlay, (0, 0))

            go = self.large_font.render("GAME OVER", True, RED)
            fs = self.font.render(f"Final Score: {self.score}", True, WHITE)
            self.screen.blit(go, (WINDOW_WIDTH // 2 - go.get_width() // 2, 200))
            self.screen.blit(fs, (WINDOW_WIDTH // 2 - fs.get_width() // 2, 300))

            if self.new_record:
                nr = self.font.render("NEW PERSONAL BEST!", True, GOLD)
                self.screen.blit(nr, (WINDOW_WIDTH // 2 - nr.get_width() // 2, 380))
            elif self.personal_best is not None:
                nb = self.small_font.render(f"Personal best: {self.personal_best}", True, GREY_LIGHT)
                self.screen.blit(nb, (WINDOW_WIDTH // 2 - nb.get_width() // 2, 380))

            mouse_pos = pygame.mouse.get_pos()
            self.btn_play_again.update(mouse_pos)
            self.btn_main_menu.update(mouse_pos)
            self.btn_play_again.draw(self.screen, self.font_btn)
            self.btn_main_menu.draw(self.screen, self.font_btn)

        pygame.display.flip()

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                if event.type == pygame.KEYDOWN and self.game_over:
                    if event.key == pygame.K_r:
                        return 'restart'
                    elif event.key == pygame.K_q:
                        pygame.quit(); sys.exit()
                if self.game_over:
                    if self.btn_play_again.handle_event(event):
                        gameover.stop()
                        bgm.stop()
                        playing.play(-1)
                        return 'restart'
                    if self.btn_main_menu.handle_event(event):
                        playing.stop()
                        gameover.stop()
                        bgm.play(-1)
                        return 'menu'
            self.update()
            self.draw()
            self.clock.tick(FPS)


# ── ENTRY POINT ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Space & Rocks")
    clock = pygame.time.Clock()

    while True:
        welcome = WelcomeScreen(screen, clock)
        result  = welcome.run()

        if result == 'start':
            while True:
                game    = Game()
                outcome = game.run()
                if outcome == 'restart':
                    continue   # play again immediately
                else:          # 'menu'
                    break      # back to welcome screen