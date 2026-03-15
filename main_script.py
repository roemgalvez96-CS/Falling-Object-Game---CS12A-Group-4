import pygame
import random
import sys
from PIL import Image

# ========== SETUP ============= :D
pygame.init()
pygame.mixer.init()

WINDOW_WIDTH  = 500
WINDOW_HEIGHT = 800
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
BROWN   = (139, 90, 43)
GOLD_DIM   = (180, 140, 0)
CYAN       = (0,   220, 255)
CYAN_DIM   = (0,   120, 160)
GREY_LIGHT = (180, 180, 200)
ORANGE     = (255, 160, 0)

INITIAL_FALL_SPEED = 3
SPEED_INCREASE     = 0.7
SPEED_THRESHOLD    = 20
SCORE_FILE         = 'highscores.txt'


# ==========================================================
# GAME MUSIC & ASSETS
# =========================================================
bgm          = "scripts/falling_game_bgm.wav"
points_catch = "scripts/catch.wav"
playing      = "scripts/catch_music.wav"
gameover     = "scripts/gameover_loop.wav"
level        = "scripts/level_up.wav"
ouch         = "scripts/oof.wav"
idle         = "scripts/idle.png"
apples       = "scripts/apple.png"
worms        = "scripts/worm.png"
walk_right   = "scripts/going_right.gif"
walk_left    = "scripts/going_left.gif"
BG           = "scripts/tree_BG.png"

BGS    = pygame.mixer.Sound(bgm)
PC     = pygame.mixer.Sound(points_catch)
PlayBG = pygame.mixer.Sound(playing)
G_O    = pygame.mixer.Sound(gameover)
LVL    = pygame.mixer.Sound(level)
OW     = pygame.mixer.Sound(ouch)


BGS.play(-1)

#GIF LOADER
PLAYER_SIZE = (50, 70)


def load_gif_frames(path, size=None):
    gif = Image.open(path)
    frames = []
    try:
        while True:
            frame = gif.convert("RGBA")
            surface = pygame.image.fromstring(
                frame.tobytes(), frame.size, "RGBA"
            ).convert_alpha()
            if size:
                surface = pygame.transform.scale(surface, size)
            frames.append(surface)
            gif.seek(gif.tell() + 1)
    except EOFError:
        pass
    return frames


# ============================================================
# MAIN MENU PART
# =====================================================

def get_last_score(): #This is where the score displayed from .txt file
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
        self.rect = pygame.Rect(x, y, w, h)
        self.label = label
        self.base_color = base_color
        self.hover_color = hover_color
        self.text_color = text_color
        self.hovered = False
        self.flash = 0

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
        fill = WHITE if self.flash > 0 else (self.hover_color if self.hovered else self.base_color)
        border_col = WHITE if (self.hovered or self.flash) else GREY_LIGHT
        txt_col = BLACK if (self.hovered or self.flash) else self.text_color

        pygame.draw.rect(surface, (0, 0, 0), self.rect.move(4, 4), border_radius=6)
        pygame.draw.rect(surface, fill, self.rect, border_radius=6)
        pygame.draw.rect(surface, border_col, self.rect, width=2, border_radius=6)

        ts = font.render(self.label, True, txt_col)
        surface.blit(ts, (self.rect.centerx - ts.get_width() // 2,
                          self.rect.centery - ts.get_height() // 2))


class WelcomeScreen:
    def __init__(self, screen, clock):
        self.screen = screen
        self.clock = clock
        self.state = 'menu'
        self.font_title = pygame.font.Font(None, 97)
        self.font_sub = pygame.font.Font(None, 32)
        self.font_sub2 = pygame.font.Font(None, 28)
        self.font_btn = pygame.font.Font(None, 38)
        self.font_small = pygame.font.Font(None, 28)
        bw, bh = 240, 58
        cx = WINDOW_WIDTH // 2 - bw // 2
        self.btn_start = Button(cx, 510, bw, bh, "START GAME",
                                base_color=(0, 130, 60), hover_color=(0, 200, 80))
        self.btn_quit = Button(cx, 590, bw, bh, "QUIT",
                               base_color=(120, 20, 20), hover_color=(200, 40, 40))
        self.last_score = get_last_score()
        self.bg = pygame.transform.scale(
            pygame.image.load("scripts/tree_BG.png").convert(), (WINDOW_WIDTH, WINDOW_HEIGHT)
        )

    def _draw_title(self):
        title = self.font_title.render("A FALL", True, GOLD)
        self.screen.blit(title, (WINDOW_WIDTH // 2 - title.get_width() // 2, 140))
        sub = self.font_sub2.render("CATCH ALL THE RED APPLES", True, WHITE)
        sub2 = self.font_sub2.render("AND AVOID THE ROTTEN ONE", True, WHITE)
        self.screen.blit(sub, (WINDOW_WIDTH // 2 - sub.get_width() // 2, 250))
        self.screen.blit(sub2, (WINDOW_WIDTH // 2 - sub2.get_width() // 2, 280))

        if self.last_score is not None:
            panel_w, panel_h = 200, 72
            panel_x = WINDOW_WIDTH // 2 - panel_w // 2
            pygame.draw.rect(self.screen, (101, 67, 33), (panel_x, 330, panel_w, panel_h), 0, border_radius=6)
            pygame.draw.rect(self.screen, GOLD_DIM, (panel_x, 330, panel_w, panel_h), 2, border_radius=6)
            label = self.font_small.render("PERSONAL BEST", True, WHITE)
            value = self.font_sub.render(str(self.last_score), True, GOLD)
            self.screen.blit(label, (WINDOW_WIDTH // 2 - label.get_width() // 2, 335))
            self.screen.blit(value, (WINDOW_WIDTH // 2 - value.get_width() // 2, 365))

        else:
            hint = self.font_small.render("No score yet  --  play to set a record!", True, GREY_LIGHT)
            self.screen.blit(hint, (WINDOW_WIDTH // 2 - hint.get_width() // 2, 318))

    def run(self):
        result = None
        while result is None:
            mouse_pos = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit();
                    sys.exit()
                if self.state == 'menu':
                    if self.btn_start.handle_event(event):
                        BGS.stop()
                        PlayBG.play(-1)
                        result = 'start'
                    if self.btn_quit.handle_event(event):
                        pygame.quit();
                        sys.exit()
                elif self.state == 'credits':
                    if self.btn_back.handle_event(event):
                        self.state = 'menu'
            if self.state == 'menu':
                self.btn_start.update(mouse_pos)
                self.btn_quit.update(mouse_pos)
            else:
                self.btn_back.update(mouse_pos)
            self.screen.blit(self.bg, (0, 0))
            if self.state == 'menu':
                self._draw_title()
                self.btn_start.draw(self.screen, self.font_btn)
                self.btn_quit.draw(self.screen, self.font_btn)
            else:
                self.btn_back.draw(self.screen, self.font_btn)
            pygame.display.flip()
            self.clock.tick(FPS)
        return result


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 3 — GAME ALGORITHM
# ══════════════════════════════════════════════════════════════════════════════

class Player:
    def __init__(self):
        self.speed = 5

        # ── Hitbox / position ──
        self.rect = pygame.Rect(
            WINDOW_WIDTH // 2 - PLAYER_SIZE[0] // 2, WINDOW_HEIGHT - 70, PLAYER_SIZE[0], PLAYER_SIZE[1]
        )

        # ── Load images ──
        # Idle: plain PNG scaled to player size
        self.idle_image = pygame.transform.scale(
            pygame.image.load(idle).convert_alpha(), PLAYER_SIZE
        )

        # Walk animations: extracted from animated GIFs, scaled to player size
        self.walk_frames_right = load_gif_frames(walk_right, size=PLAYER_SIZE)
        self.walk_frames_left = load_gif_frames(walk_left, size=PLAYER_SIZE)

        # ── Animation state ──
        self.current_image = self.idle_image
        self.frame_index = 0
        self.frame_timer = 0
        self.FRAME_SPEED = 8  # ticks per frame (lower = faster)

    def move(self, keys):
        moving_right1 = keys[pygame.K_RIGHT] and self.rect.right < WINDOW_WIDTH
        moving_right2 = keys[pygame.K_d] and self.rect.right < WINDOW_WIDTH
        moving_left1 = keys[pygame.K_LEFT] and self.rect.left > 0
        moving_left2 = keys[pygame.K_a] and self.rect.left > 0



        if moving_right1:
            self.rect.x += self.speed
            self.frame_timer += 1
            if self.frame_timer >= self.FRAME_SPEED:
                self.frame_timer = 0
                self.frame_index = (self.frame_index + 1) % len(self.walk_frames_right)
            self.current_image = self.walk_frames_right[self.frame_index]

        elif moving_left1:
            self.rect.x -= self.speed
            self.frame_timer += 1
            if self.frame_timer >= self.FRAME_SPEED:
                self.frame_timer = 0
                self.frame_index = (self.frame_index + 1) % len(self.walk_frames_left)
            self.current_image = self.walk_frames_left[self.frame_index]

        elif moving_right2:
            self.rect.x += self.speed
            self.frame_timer += 1
            if self.frame_timer >= self.FRAME_SPEED:
                self.frame_timer = 0
                self.frame_index = (self.frame_index + 1) % len(self.walk_frames_right)
            self.current_image = self.walk_frames_right[self.frame_index]

        elif moving_left2:
            self.rect.x -= self.speed
            self.frame_timer += 1
            if self.frame_timer >= self.FRAME_SPEED:
                self.frame_timer = 0
                self.frame_index = (self.frame_index + 1) % len(self.walk_frames_left)
            self.current_image = self.walk_frames_left[self.frame_index]

        else:
            self.frame_index = 0
            self.frame_timer = 0
            self.current_image = self.idle_image

    def draw(self, screen):
        screen.blit(self.current_image, self.rect)


class FallingObject:
    def __init__(self, obj_type, fall_speed):
        self.width = 60
        self.height = 60
        self.x = random.randint(0, WINDOW_WIDTH - self.width)
        self.y = -self.height
        self.fall_speed = fall_speed
        self.type = obj_type

        apple_img = pygame.image.load(apples).convert_alpha()
        worm_img = pygame.image.load(worms).convert_alpha()

        if self.type == 'good':
            self.image = pygame.transform.scale(apple_img, (self.width, self.height))
        else:
            self.image = pygame.transform.scale(worm_img, (self.width, self.height))

    def fall(self):
        self.y += self.fall_speed

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

    def is_off_screen(self):
        return self.y > WINDOW_HEIGHT

    def check_collision(self, player):
        #Fixed: use player.rect instead of player.x/y/width/height
        obj_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        return obj_rect.colliderect(player.rect)


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.large_font = pygame.font.Font(None, 72)
        self.small_font = pygame.font.Font(None, 28)
        self.font_btn = pygame.font.Font(None, 38)

        # Load heart image
        self.heart_img = pygame.image.load("scripts/heart_life.png").convert_alpha()
        self.heart_img = pygame.transform.scale(self.heart_img, (24, 24))

        bw, bh = 240, 58
        cx = WINDOW_WIDTH // 2 - bw // 2
        self.btn_play_again = Button(cx, 490, bw, bh, "PLAY AGAIN",
                                     base_color=(0, 130, 60), hover_color=(0, 200, 80))
        self.btn_main_menu = Button(cx, 570, bw, bh, "BACK TO MENU",
                                    base_color=CYAN_DIM, hover_color=CYAN)
        self.reset_game()

    def reset_game(self):
        self.player = Player()
        self.falling_objects = []
        self.score = 0
        self.lives = 3
        self.fall_speed = INITIAL_FALL_SPEED
        self.spawn_timer = 0
        self.spawn_delay = 60
        self.game_over = False
        self.difficulty_level = 0
        self.last_difficulty_score = 0
        self.personal_best = get_last_score()
        self.new_record = False
        self.score_saved = False
        self.gameover_music_started = False

    def spawn_object(self):
        bomb_chance = min(0.30 + (self.difficulty_level * 0.05), 0.60)
        obj_type = 'bomb' if random.random() < bomb_chance else 'good'
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
            PlayBG.stop()
            if not self.gameover_music_started:
                G_O.play(0)
                G_O.set_volume(1)
                self.gameover_music_started = True
            if not pygame.mixer.get_busy():
                BGS.play()
                BGS.set_volume(0.4)
            return

        keys = pygame.key.get_pressed()
        self.player.move(keys)  # Fixed: no tick argument needed

        self.spawn_timer += 1
        if self.spawn_timer >= self.spawn_delay:
            self.spawn_object()
            self.spawn_timer = 0

        for obj in self.falling_objects[:]:
            obj.fall()
            if obj.check_collision(self.player):
                if obj.type == 'good':
                    self.score += 1
                    PC.play()
                    PC.set_volume(0.8)
                    if self.personal_best is not None and self.score > self.personal_best:
                        self.new_record = True
                else:
                    self.lives -= 1
                    OW.play()
                    OW.set_volume(1.6)
                    if self.lives <= 0:
                        self.game_over = True
                        self._try_save_score()
                self.falling_objects.remove(obj)
            elif obj.is_off_screen():
                self.falling_objects.remove(obj)

        if self.score >= self.last_difficulty_score + SPEED_THRESHOLD and self.score > 0:
            self.difficulty_level += 1
            LVL.play()
            self.last_difficulty_score = (self.score // SPEED_THRESHOLD) * SPEED_THRESHOLD
            self.fall_speed += SPEED_INCREASE
            self.spawn_delay = max(30, self.spawn_delay - 5)
            for obj in self.falling_objects:
                obj.fall_speed = self.fall_speed

    def draw(self):
        self.screen.fill("gray")
        self.player.draw(self.screen)
        for obj in self.falling_objects:
            obj.draw(self.screen)

        # ── HUD outer frame ──
        frame_x, frame_y = 0, 0
        frame_w, frame_h = WINDOW_WIDTH, 70
        pygame.draw.rect(self.screen, GOLD_DIM, (frame_x, frame_y, frame_w, frame_h), 0, border_radius=6)
        pygame.draw.rect(self.screen, (30, 20, 10), (frame_x + 2, frame_y + 2, frame_w - 4, frame_h - 4), 0, border_radius=5)
        pygame.draw.rect(self.screen, GOLD_DIM, (frame_x, frame_y, frame_w, frame_h), 2, border_radius=6)

        # ── Text row with divider line ──
        row_h = 36
        pygame.draw.rect(self.screen, GOLD_DIM, (frame_x, frame_y, frame_w, row_h), 0, border_radius=6)
        pygame.draw.rect(self.screen, (30, 20, 10), (frame_x + 2, frame_y + 2, frame_w - 4, row_h - 2), 0)
        pygame.draw.line(self.screen, GOLD_DIM, (frame_x, frame_y + row_h), (frame_x + frame_w, frame_y + row_h), 2)

        col_w = frame_w // 3
        level_txt = self.small_font.render(f"Level: {self.difficulty_level + 1}", True, WHITE)
        score_txt = self.small_font.render(f"Score: {self.score}", True, WHITE)

        if self.personal_best is not None:
            if self.new_record:
                best_txt = self.small_font.render("Best: NEW!", True, ORANGE)
            else:
                best_txt = self.small_font.render(f"Best: {self.personal_best}", True, GREY_LIGHT)
        else:
            best_txt = self.small_font.render("Best: --", True, GREY_LIGHT)

        text_y = frame_y + (row_h - level_txt.get_height()) // 2
        self.screen.blit(level_txt, (frame_x + 10, text_y))
        self.screen.blit(score_txt, (frame_x + col_w + (col_w - score_txt.get_width()) // 2, text_y))
        self.screen.blit(best_txt, (frame_x + frame_w - best_txt.get_width() - 10, text_y))

        # ── Hearts bottom-right inside frame ──
        hearts_y = frame_y + row_h + (frame_h - row_h - self.heart_img.get_height()) // 2
        hearts_x = frame_x + frame_w - (3 * self.heart_img.get_width() + 2 * 4) - 10
        for i in range(self.lives):
            self.screen.blit(self.heart_img, (hearts_x + i * (self.heart_img.get_width() + 4), hearts_y))

        if self.difficulty_level > 0 and self.score - self.last_difficulty_score < 5:
            lv = self.small_font.render(f"WAVE {self.difficulty_level + 1}!", True, GOLD)
            self.screen.blit(lv, (frame_x + 10, hearts_y))

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

        # ── Border around the entire game window ──
        pygame.draw.rect(self.screen, GOLD_DIM, (0, 0, WINDOW_WIDTH, WINDOW_HEIGHT), 4)

        pygame.display.flip()

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit();
                    sys.exit()
                if event.type == pygame.KEYDOWN and self.game_over:
                    if event.key == pygame.K_r:
                        return 'restart'
                    elif event.key == pygame.K_q:
                        pygame.quit();
                        sys.exit()
                if self.game_over:
                    if self.btn_play_again.handle_event(event):
                        G_O.stop()
                        BGS.stop()
                        PlayBG.play(-1)
                        return 'restart'
                    if self.btn_main_menu.handle_event(event):
                        PlayBG.stop()
                        G_O.stop()
                        BGS.stop()
                        BGS.play(-1)
                        BGS.set_volume(1)
                        return 'menu'
            self.update()
            self.draw()
            self.clock.tick(FPS)


# ── ENTRY POINT ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("A Fall - v1.3 (Beta)") #Game Caption Part
    clock = pygame.time.Clock()

    while True:
        welcome = WelcomeScreen(screen, clock)
        result = welcome.run()

        if result == 'start':
            while True:
                game = Game()
                outcome = game.run()
                if outcome == 'restart':
                    continue
                else:
                    break
