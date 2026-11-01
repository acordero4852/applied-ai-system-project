import json


def get_range_for_difficulty(difficulty: str):
    """Return (low, high) inclusive range for a given difficulty."""
    if difficulty == "Easy":
        return 1, 20
    if difficulty == "Normal":
        return 1, 50
    if difficulty == "Hard":
        return 1, 100
    return 1, 100


def parse_guess(raw: str):
    """
    Parse user input into an int guess.

    Returns: (ok: bool, guess_int: int | None, error_message: str | None)
    """
    if raw is None or raw == "":
        return False, None, "Enter a guess."

    try:
        if "." in raw:
            value = int(float(raw))
        else:
            value = int(raw)
    except Exception:
        return False, None, "That is not a number."

    return True, value, None


def check_guess(guess, secret):
    """
    Compare guess to secret and return the outcome.

    outcome is one of: "Win", "Too High", "Too Low"
    """
    if guess == secret:
        return "Win"
    if guess > secret:
        return "Too High"
    return "Too Low"


def update_score(current_score: int, outcome: str, attempt_number: int):
    """Update score based on outcome and attempt number."""
    if outcome == "Win":
        points = 100 - 10 * (attempt_number - 1)
        if points < 10:
            points = 10
        return current_score + points

    if outcome in ("Too High", "Too Low"):
        return current_score - 5

    return current_score


def update_high_scores(scores: dict, difficulty: str, score: int):
    """
    Record a new personal best for a difficulty if it beats the old one.

    Pure function: does not mutate `scores` and does no file I/O.

    Returns: (new_scores: dict, is_new_record: bool)
    A new record is set only when the difficulty has no score yet or the
    new score is strictly greater than the existing best (ties do not count).
    """
    new_scores = dict(scores)
    best = new_scores.get(difficulty)

    if best is None or score > best:
        new_scores[difficulty] = score
        return new_scores, True

    return new_scores, False


def load_high_scores(path: str):
    """
    Load the high-score table from a JSON file.

    Tolerant by design: returns {} if the file is missing, unreadable, or
    contains invalid JSON, so a corrupt file never crashes the game.
    """
    try:
        with open(path, "r") as f:
            data = json.load(f)
    except (OSError, ValueError):
        return {}

    if not isinstance(data, dict):
        return {}

    return data


def save_high_scores(path: str, scores: dict) -> None:
    """Write the high-score table to a JSON file."""
    with open(path, "w") as f:
        json.dump(scores, f)


def proximity_label(guess, secret, low, high):
    """
    Describe how close a guess is to the secret as a Hot/Cold label.

    Distance is measured as a fraction of the full range width, so the same
    label means the same relative closeness on every difficulty. A guess
    above or below the secret by the same amount gets the same label.

    Returns one of: "🔥 Blazing", "🌡️ Warm", "❄️ Cold".
    """
    if guess == secret:
        return "🔥 Blazing"

    span = high - low
    if span <= 0:
        return "🔥 Blazing"

    distance_fraction = abs(guess - secret) / span

    if distance_fraction <= 0.10:
        return "🔥 Blazing"
    if distance_fraction <= 0.30:
        return "🌡️ Warm"
    return "❄️ Cold"


def build_summary_rows(history):
    """
    Shape enriched history records into display rows for a summary table.

    Each history record is a dict like:
        {"attempt": 1, "guess": 42, "outcome": "Too High",
         "proximity": "❄️ Cold", "score_after": -5}
    Invalid-guess records may omit some fields; missing values render as "—".
    """
    rows = []
    for record in history:
        rows.append(
            {
                "Attempt": record.get("attempt", "—"),
                "Guess": record.get("guess", "—"),
                "Hint": record.get("outcome", "—"),
                "Proximity": record.get("proximity", "—"),
                "Score": record.get("score_after", "—"),
            }
        )
    return rows


def update_stats(stats: dict, won: bool, attempts: int):
    """
    Record the result of a finished game into a session stats dict.

    Pure function: returns a new dict and does not mutate the input.
    Tracks total games, games won, and total attempts across won games
    (used to compute the average attempts per win).
    """
    new_stats = {
        "games_played": stats.get("games_played", 0) + 1,
        "games_won": stats.get("games_won", 0),
        "attempts_in_wins": stats.get("attempts_in_wins", 0),
    }

    if won:
        new_stats["games_won"] += 1
        new_stats["attempts_in_wins"] += attempts

    return new_stats


def compute_win_rate(stats: dict):
    """Return the win rate (0.0-1.0). Zero games played means 0.0."""
    played = stats.get("games_played", 0)
    if played == 0:
        return 0.0
    return stats.get("games_won", 0) / played


def hint_style(outcome, proximity):
    """
    Pick the Streamlit message style for a hint based on how hot the guess is.

    Returns one of: "success", "warning", "error".
    A win or a "🔥 Blazing" guess is success (green), "🌡️ Warm" is warning
    (yellow), and anything colder is error (red).
    """
    if outcome == "Win" or "Blazing" in proximity:
        return "success"
    if "Warm" in proximity:
        return "warning"
    return "error"


def attempts_progress(attempts, limit):
    """
    Fraction of allowed attempts used, clamped to 0.0-1.0.

    Safe when limit is 0 (returns 0.0) so the progress bar never divides
    by zero or overflows past the end.
    """
    if limit <= 0:
        return 0.0

    fraction = attempts / limit
    if fraction < 0:
        return 0.0
    if fraction > 1:
        return 1.0
    return fraction


def proximity_meter(guess, secret, low, high, segments: int = 10):
    """
    Build a filling thermometer bar showing how close a guess is.

    Closer guesses fill more 🔥 segments; far guesses stay mostly ⬜.
    An exact match fills every segment. Returns a string of length `segments`.
    """
    span = high - low
    if span <= 0 or guess == secret:
        return "🔥" * segments

    distance_fraction = abs(guess - secret) / span
    if distance_fraction > 1:
        distance_fraction = 1.0

    # Closeness: 1.0 when exact, 0.0 when a full range-width away.
    closeness = 1.0 - distance_fraction
    filled = round(closeness * segments)

    return "🔥" * filled + "⬜" * (segments - filled)
