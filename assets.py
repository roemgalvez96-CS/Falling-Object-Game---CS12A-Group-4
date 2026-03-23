# ============================================================
# ASSETS — loads all sounds and provides the GIF frame loader
# ============================================================

import pygame
from PIL import Image
from constants import (
    BGM_PATH, CATCH_SFX, PLAY_BGM, GAMEOVER_SFX,
    LEVEL_SFX, OUCH_SFX, FRENZY_BGM_PATH,
)

pygame.mixer.init()
# ── Sounds ───────────────────────────────────────────────────
BGS        = pygame.mixer.Sound(BGM_PATH)
PC         = pygame.mixer.Sound(CATCH_SFX)
PlayBG     = pygame.mixer.Sound(PLAY_BGM)
G_O        = pygame.mixer.Sound(GAMEOVER_SFX)
LVL        = pygame.mixer.Sound(LEVEL_SFX)
OW         = pygame.mixer.Sound(OUCH_SFX)
FRENZY_BGM = pygame.mixer.Sound(FRENZY_BGM_PATH)


# ── GIF loader ───────────────────────────────────────────────
def load_gif_frames(path, size=None):
    """Return a list of pygame Surfaces from an animated GIF."""
    gif    = Image.open(path)
    frames = []
    try:
        while True:
            frame   = gif.convert("RGBA")
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
