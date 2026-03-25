# ============================================================
# SCORES — read / write the high-score file
# ============================================================

from constants import SCORE_FILE


def get_last_score():
    """Return the last saved score (int) or None if no file / empty."""
    try:
        with open(SCORE_FILE, 'r') as f:
            lines = [ln.strip() for ln in f.readlines() if ln.strip()]
        if not lines:
            return None
        return int(lines[-1])
    except (FileNotFoundError, ValueError):
        return None


def save_score(score):
    """Append score to the score file."""
    with open(SCORE_FILE, 'a') as f:
        f.write(str(score) + '\n')
