# ============================================================
# CONSTANTS — colors, window size, gameplay tuning, asset paths

WINDOW_WIDTH  = 500
WINDOW_HEIGHT = 800
FPS           = 120

# ── Colors ───────────────────────────────────────────────────
WHITE      = (255, 255, 255)
BLACK      = (0,   0,   0)
RED        = (255, 0,   0)
GREEN      = (0,   255, 0)
BLUE       = (0,   100, 255)
YELLOW     = (255, 255, 0)
BG_DARK    = (8,   8,   24)
STAR_WHITE = (220, 220, 255)
GOLD       = (255, 215, 0)
BROWN      = (139, 90,  43)
GOLD_DIM   = (180, 140, 0)
CYAN       = (0,   220, 255)
CYAN_DIM   = (0,   120, 160)
GREY_LIGHT = (180, 180, 200)
ORANGE     = (255, 160, 0)

# ── Gameplay ─────────────────────────────────────────────────
INITIAL_FALL_SPEED  = 3
SPEED_INCREASE      = 0.6
SPEED_THRESHOLD     = 20
SCORE_FILE          = 'highscores.txt'

# ── Apple Frenzy ────────────── Not Functional now───────────────────
FRENZY_THRESHOLD    = 100
FRENZY_DURATION_SEC = 10
FRENZY_SPAWN_MULT   = 3.5

# ── Hearts ───────────────────────────────────────────────────
MAX_LIVES           = 3

# ── Player ───────────────────────────────────────────────────
PLAYER_SIZE         = (50, 70)

# ── Asset paths ──────────────────────────────────────────────
BGM_PATH        = "scripts/falling_game_bgm.wav"
CATCH_SFX       = "scripts/catch.wav"
PLAY_BGM        = "scripts/catch_music.wav"
GAMEOVER_SFX    = "scripts/apple_frenzy_nice_try_loop.wav"
LEVEL_SFX       = "scripts/level_up.wav"
OUCH_SFX        = "scripts/oof.wav"
H_S             = "scripts/highscore_8bit.wav"
FRENZY_BGM_PATH = "scripts/apple_frenzy_hype.wav"
FRENZY_BANNER_IMG = "scripts/Apple_Frenzy_transparent.png"

IDLE_IMG        = "scripts/idle.png"
APPLE_IMG       = "scripts/apple.png"
WORM_IMG        = "scripts/worm.png"
WALK_RIGHT_GIF  = "scripts/going_right.gif"
WALK_LEFT_GIF   = "scripts/going_left.gif"
BG_IMG          = "scripts/tree_BG.png"
MENU_BG_IMG         = "scripts/main_menu_bg.png"
BTN_START_IMG       = "scripts/btn_start.png"
BTN_START_HOVER_IMG = "scripts/btn_start_hover.png"
BTN_SHOP_IMG        = "scripts/btn_shop.png"
BTN_SHOP_HOVER_IMG  = "scripts/btn_shop_hover.png"
BTN_HTP_IMG         = "scripts/btn_htp.png"
BTN_HTP_HOVER_IMG   = "scripts/btn_htp_hover.png"
TROPHY_IMG      = "scripts/png-removebg-preview.png"
HEART_IMG           = "scripts/heart_life.png"
APPLE_SCORE_IMG     = "scripts/apple_score.png"
COIN_SCORE_IMG      = "scripts/coin_score.png"
SHIELD_ICON_IMG     = "scripts/shield_icon.png"
MAGNET_ICON_IMG     = "scripts/magnet_icon.png"
GOLDEN_APPLE_ICON   = "scripts/golden_apple_icon.png"
COIN_IMG            = "scripts/coin.png"
GOLDEN_APPLE_IMG    = "scripts/golden_apple.png"
ROTTEN_APPLE_IMG    = "scripts/rotten_apple.png"
TROPHY_HIGHSCORE_IMG = "scripts/trophy_highscore.png"
SCORE_PANEL_IMG      = "scripts/score_panel.png"