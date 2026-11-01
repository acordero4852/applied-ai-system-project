from logic_utils import (
    attempts_progress,
    build_summary_rows,
    check_guess,
    compute_win_rate,
    get_range_for_difficulty,
    hint_style,
    load_high_scores,
    parse_guess,
    proximity_label,
    proximity_meter,
    update_high_scores,
    update_score,
    update_stats,
)


# ---------------------------------------------------------------------------
# check_guess
# ---------------------------------------------------------------------------
def test_winning_guess():
    # If the secret is 50 and guess is 50, it should be a win
    result = check_guess(50, 50)
    assert result == "Win"


def test_guess_too_high():
    # If secret is 50 and guess is 60, hint should be "Too High"
    result = check_guess(60, 50)
    assert result == "Too High"


def test_guess_too_low():
    # If secret is 50 and guess is 40, hint should be "Too Low"
    result = check_guess(40, 50)
    assert result == "Too Low"


# ---------------------------------------------------------------------------
# get_range_for_difficulty  (Glitch #1: Normal/Hard ranges were swapped)
# ---------------------------------------------------------------------------
def test_range_easy():
    assert get_range_for_difficulty("Easy") == (1, 20)


def test_range_normal():
    assert get_range_for_difficulty("Normal") == (1, 50)


def test_range_hard():
    assert get_range_for_difficulty("Hard") == (1, 100)


def test_range_escalates():
    # Difficulty should get harder: Hard's range must be wider than Normal's,
    # which must be wider than Easy's.
    _, easy_high = get_range_for_difficulty("Easy")
    _, normal_high = get_range_for_difficulty("Normal")
    _, hard_high = get_range_for_difficulty("Hard")
    assert easy_high < normal_high < hard_high


# ---------------------------------------------------------------------------
# parse_guess
# ---------------------------------------------------------------------------
def test_parse_valid_integer():
    assert parse_guess("42") == (True, 42, None)


def test_parse_float_is_truncated():
    ok, value, err = parse_guess("3.9")
    assert ok is True
    assert value == 3
    assert err is None


def test_parse_empty_input():
    ok, value, err = parse_guess("")
    assert ok is False
    assert value is None
    assert err == "Enter a guess."


def test_parse_non_number():
    ok, value, err = parse_guess("abc")
    assert ok is False
    assert err == "That is not a number."


# ---------------------------------------------------------------------------
# update_score  (Glitch #8: win off-by-one + Too High sometimes rewarded)
# ---------------------------------------------------------------------------
def test_win_on_first_attempt_is_full_points():
    assert update_score(0, "Win", 1) == 100


def test_win_loses_ten_points_per_attempt():
    assert update_score(0, "Win", 3) == 80


def test_win_points_floored_at_ten():
    # Even a very late win should never drop below 10 points.
    assert update_score(0, "Win", 50) == 10


def test_too_high_always_penalizes():
    # Used to reward +5 on even attempts; now it must always be -5.
    assert update_score(0, "Too High", 2) == -5
    assert update_score(0, "Too High", 3) == -5


def test_too_low_penalizes():
    assert update_score(0, "Too Low", 4) == -5


# ---------------------------------------------------------------------------
# update_high_scores  (Stretch: per-difficulty personal best)
# ---------------------------------------------------------------------------
def test_high_score_new_difficulty_is_record():
    scores, is_record = update_high_scores({}, "Easy", 90)
    assert is_record is True
    assert scores == {"Easy": 90}


def test_high_score_beats_previous_best():
    scores, is_record = update_high_scores({"Hard": 70}, "Hard", 100)
    assert is_record is True
    assert scores == {"Hard": 100}


def test_high_score_below_previous_is_not_record():
    scores, is_record = update_high_scores({"Normal": 80}, "Normal", 50)
    assert is_record is False
    assert scores == {"Normal": 80}


def test_high_score_tie_is_not_record():
    scores, is_record = update_high_scores({"Easy": 90}, "Easy", 90)
    assert is_record is False
    assert scores == {"Easy": 90}


def test_high_score_does_not_mutate_input():
    original = {"Easy": 50}
    update_high_scores(original, "Easy", 100)
    assert original == {"Easy": 50}


def test_load_high_scores_missing_file_returns_empty():
    assert load_high_scores("definitely_not_a_real_file_123.json") == {}


# ---------------------------------------------------------------------------
# proximity_label  (Stretch: Hot/Cold feedback)
# ---------------------------------------------------------------------------
def test_proximity_exact_match_is_blazing():
    assert proximity_label(50, 50, 1, 100) == "🔥 Blazing"


def test_proximity_close_is_blazing():
    # Within 10% of a range of ~100 (distance 5 of 99).
    assert proximity_label(55, 50, 1, 100) == "🔥 Blazing"


def test_proximity_medium_is_warm():
    # ~20% of the range away.
    assert proximity_label(70, 50, 1, 100) == "🌡️ Warm"


def test_proximity_far_is_cold():
    assert proximity_label(95, 50, 1, 100) == "❄️ Cold"


def test_proximity_symmetric_above_and_below():
    # Same distance above or below the secret gives the same label.
    assert proximity_label(30, 50, 1, 100) == proximity_label(70, 50, 1, 100)


# ---------------------------------------------------------------------------
# build_summary_rows  (Stretch: session summary table)
# ---------------------------------------------------------------------------
def test_build_summary_rows_empty():
    assert build_summary_rows([]) == []


def test_build_summary_rows_maps_fields():
    history = [
        {
            "attempt": 1,
            "guess": 42,
            "outcome": "Too High",
            "proximity": "❄️ Cold",
            "score_after": -5,
        }
    ]
    rows = build_summary_rows(history)
    assert rows == [
        {
            "Attempt": 1,
            "Guess": 42,
            "Hint": "Too High",
            "Proximity": "❄️ Cold",
            "Score": -5,
        }
    ]


def test_build_summary_rows_handles_invalid_record():
    # An invalid-guess record only has attempt + guess; missing fields show "—".
    rows = build_summary_rows([{"attempt": 2, "guess": "abc"}])
    assert rows[0]["Hint"] == "—"
    assert rows[0]["Proximity"] == "—"
    assert rows[0]["Score"] == "—"


# ---------------------------------------------------------------------------
# update_stats / compute_win_rate  (Stretch: session stats)
# ---------------------------------------------------------------------------
def test_update_stats_first_win():
    stats = update_stats({}, won=True, attempts=3)
    assert stats == {
        "games_played": 1,
        "games_won": 1,
        "attempts_in_wins": 3,
    }


def test_update_stats_first_loss():
    stats = update_stats({}, won=False, attempts=5)
    assert stats == {
        "games_played": 1,
        "games_won": 0,
        "attempts_in_wins": 0,
    }


def test_update_stats_does_not_mutate_input():
    original = {"games_played": 1, "games_won": 1, "attempts_in_wins": 2}
    update_stats(original, won=True, attempts=4)
    assert original == {"games_played": 1, "games_won": 1, "attempts_in_wins": 2}


def test_compute_win_rate_zero_games():
    assert compute_win_rate({}) == 0.0


def test_compute_win_rate_half():
    stats = {"games_played": 4, "games_won": 2}
    assert compute_win_rate(stats) == 0.5


# ---------------------------------------------------------------------------
# hint_style  (Enhanced UI: color-coded hints)
# ---------------------------------------------------------------------------
def test_hint_style_win_is_success():
    assert hint_style("Win", "🔥 Blazing") == "success"


def test_hint_style_blazing_is_success():
    assert hint_style("Too High", "🔥 Blazing") == "success"


def test_hint_style_warm_is_warning():
    assert hint_style("Too Low", "🌡️ Warm") == "warning"


def test_hint_style_cold_is_error():
    assert hint_style("Too High", "❄️ Cold") == "error"


# ---------------------------------------------------------------------------
# attempts_progress  (Enhanced UI: progress meter)
# ---------------------------------------------------------------------------
def test_attempts_progress_none_used():
    assert attempts_progress(0, 6) == 0.0


def test_attempts_progress_half():
    assert attempts_progress(3, 6) == 0.5


def test_attempts_progress_full():
    assert attempts_progress(6, 6) == 1.0


def test_attempts_progress_over_limit_clamps():
    assert attempts_progress(9, 6) == 1.0


def test_attempts_progress_zero_limit_is_safe():
    # No divide-by-zero when the limit is 0.
    assert attempts_progress(0, 0) == 0.0


# ---------------------------------------------------------------------------
# proximity_meter  (Enhanced UI: emoji thermometer bar)
# ---------------------------------------------------------------------------
def test_proximity_meter_exact_is_full():
    assert proximity_meter(50, 50, 1, 100, segments=10) == "🔥" * 10


def test_proximity_meter_far_is_nearly_empty():
    # A guess a full range-width away has zero closeness.
    meter = proximity_meter(1, 100, 1, 100, segments=10)
    assert meter == "⬜" * 10


def test_proximity_meter_has_fixed_length():
    meter = proximity_meter(70, 50, 1, 100, segments=10)
    assert len(meter) == 10


def test_proximity_meter_closer_fills_more():
    near = proximity_meter(55, 50, 1, 100, segments=10).count("🔥")
    far = proximity_meter(90, 50, 1, 100, segments=10).count("🔥")
    assert near > far
