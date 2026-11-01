import random

import altair as alt
import pandas as pd
import streamlit as st

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
    save_high_scores,
    update_high_scores,
    update_score,
    update_stats,
)

# Maps each outcome to the hint shown to the player.
HINT_MESSAGES = {
    "Win": "🎉 Correct!",
    "Too High": "📉 Go LOWER!",
    "Too Low": "📈 Go HIGHER!",
}

# Personal-best scores persist here across restarts (gitignored).
HIGH_SCORE_FILE = "high_scores.json"

st.set_page_config(page_title="Glitchy Guesser", page_icon="🎮")

st.title("🎮 Game Glitch Investigator")
st.caption("An AI-generated guessing game. Something is off.")

st.sidebar.header("Settings")

difficulty = st.sidebar.selectbox(
    "Difficulty",
    ["Easy", "Normal", "Hard"],
    index=1,
)

attempt_limit_map = {
    "Easy": 8,
    "Normal": 6,
    "Hard": 5,
}
attempt_limit = attempt_limit_map[difficulty]

low, high = get_range_for_difficulty(difficulty)

st.sidebar.caption(f"Range: {low} to {high}")
st.sidebar.caption(f"Attempts allowed: {attempt_limit}")

if "secret" not in st.session_state:
    st.session_state.secret = random.randint(low, high)

if "attempts" not in st.session_state:
    st.session_state.attempts = 0

if "score" not in st.session_state:
    st.session_state.score = 0

if "status" not in st.session_state:
    st.session_state.status = "playing"

if "history" not in st.session_state:
    st.session_state.history = []

# Session stats accumulate across New Games (reset only on app restart).
if "stats" not in st.session_state:
    st.session_state.stats = {
        "games_played": 0,
        "games_won": 0,
        "attempts_in_wins": 0,
    }

# Load persisted personal bests once; they survive New Game and restarts.
if "high_scores" not in st.session_state:
    st.session_state.high_scores = load_high_scores(HIGH_SCORE_FILE)

best_for_difficulty = st.session_state.high_scores.get(difficulty)
st.sidebar.caption(
    f"🥇 Best ({difficulty}): "
    f"{best_for_difficulty if best_for_difficulty is not None else '—'}"
)

tab_play, tab_history, tab_stats = st.tabs(["Play", "History", "Stats"])

with tab_play:
    st.subheader("Make a guess")

    st.info(
        f"Guess a number between {low} and {high}. "
        f"Attempts left: {attempt_limit - st.session_state.attempts}"
    )

    st.progress(attempts_progress(st.session_state.attempts, attempt_limit))
    st.caption(f"Attempt {st.session_state.attempts} of {attempt_limit}")

    with st.expander("Developer Debug Info"):
        st.write("Secret:", st.session_state.secret)
        st.write("Attempts:", st.session_state.attempts)
        st.write("Score:", st.session_state.score)
        st.write("Difficulty:", difficulty)
        st.write("History:", st.session_state.history)

    raw_guess = st.text_input(
        "Enter your guess:",
        key=f"guess_input_{difficulty}"
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        submit = st.button("Submit Guess 🚀")
    with col2:
        new_game = st.button("New Game 🔁")
    with col3:
        show_hint = st.checkbox("Show hint", value=True)

    if new_game:
        # New Game resets the current round only; stats and high scores persist.
        st.session_state.attempts = 0
        st.session_state.secret = random.randint(low, high)
        st.session_state.score = 0
        st.session_state.status = "playing"
        st.session_state.history = []
        st.success("New game started.")
        st.rerun()

    if st.session_state.status != "playing":
        if st.session_state.status == "won":
            st.success("You already won. Start a new game to play again.")
        else:
            st.error("Game over. Start a new game to try again.")
    elif submit:
        st.session_state.attempts += 1

        ok, guess_int, err = parse_guess(raw_guess)

        if not ok:
            st.session_state.history.append(
                {"attempt": st.session_state.attempts, "guess": raw_guess}
            )
            st.error(err)
        else:
            secret = st.session_state.secret

            outcome = check_guess(guess_int, secret)
            message = HINT_MESSAGES[outcome]
            proximity = proximity_label(guess_int, secret, low, high)
            meter = proximity_meter(guess_int, secret, low, high)

            if show_hint:
                hint_text = f"{message}  ·  {proximity}\n\n{meter}"
                style = hint_style(outcome, proximity)
                if style == "success":
                    st.success(hint_text)
                elif style == "warning":
                    st.warning(hint_text)
                else:
                    st.error(hint_text)

            previous_score = st.session_state.score
            st.session_state.score = update_score(
                current_score=previous_score,
                outcome=outcome,
                attempt_number=st.session_state.attempts,
            )
            points_this_turn = st.session_state.score - previous_score

            st.metric(
                "Score",
                st.session_state.score,
                delta=points_this_turn,
            )

            st.session_state.history.append(
                {
                    "attempt": st.session_state.attempts,
                    "guess": guess_int,
                    "outcome": outcome,
                    "proximity": proximity,
                    "score_after": st.session_state.score,
                }
            )

            if outcome == "Win":
                st.balloons()
                st.session_state.status = "won"
                st.session_state.stats = update_stats(
                    st.session_state.stats,
                    won=True,
                    attempts=st.session_state.attempts,
                )
                st.success(
                    f"You won! The secret was {st.session_state.secret}. "
                    f"Final score: {st.session_state.score}"
                )

                st.session_state.high_scores, is_new_record = update_high_scores(
                    st.session_state.high_scores,
                    difficulty,
                    st.session_state.score,
                )
                save_high_scores(HIGH_SCORE_FILE, st.session_state.high_scores)
                if is_new_record:
                    st.success(f"🏆 New personal best for {difficulty}!")
            elif st.session_state.attempts >= attempt_limit:
                st.snow()
                st.session_state.status = "lost"
                st.session_state.stats = update_stats(
                    st.session_state.stats,
                    won=False,
                    attempts=st.session_state.attempts,
                )
                st.error(
                    f"Out of attempts! "
                    f"The secret was {st.session_state.secret}. "
                    f"Score: {st.session_state.score}"
                )

with tab_history:
    st.subheader("Guess History")

    valid_guesses = [
        r for r in st.session_state.history if isinstance(r.get("guess"), int)
    ]

    if not valid_guesses:
        st.caption("No guesses yet. Make a guess to see your history here.")
    else:
        chart_df = pd.DataFrame(
            [{"Attempt": r["attempt"], "Guess": r["guess"]} for r in valid_guesses]
        )
        guess_line = (
            alt.Chart(chart_df)
            .mark_line(point=True)
            .encode(
                x=alt.X("Attempt:O", title="Attempt"),
                y=alt.Y(
                    "Guess:Q",
                    title="Guess",
                    scale=alt.Scale(domain=[low, high]),
                ),
            )
        )

        # Only reveal the secret reference line once the game is over,
        # so the chart never spoils an in-progress game.
        if st.session_state.status != "playing":
            secret_df = pd.DataFrame({"Secret": [st.session_state.secret]})
            secret_line = (
                alt.Chart(secret_df)
                .mark_rule(color="red", strokeDash=[6, 4])
                .encode(y="Secret:Q")
            )
            chart = guess_line + secret_line
        else:
            chart = guess_line

        st.altair_chart(chart, width="stretch")

        st.markdown("**Session summary**")
        st.table(build_summary_rows(st.session_state.history))

with tab_stats:
    st.subheader("Session Stats")

    stats = st.session_state.stats
    games_won = stats.get("games_won", 0)
    win_rate = compute_win_rate(stats)
    avg_attempts = (
        stats.get("attempts_in_wins", 0) / games_won if games_won else None
    )

    c1, c2, c3 = st.columns(3)
    c1.metric("Games played", stats.get("games_played", 0))
    c2.metric("Games won", games_won)
    c3.metric("Win rate", f"{win_rate * 100:.0f}%")

    st.metric(
        "Avg attempts per win",
        f"{avg_attempts:.1f}" if avg_attempts is not None else "—",
    )
    st.caption(
        "Stats accumulate across New Games and reset when the app restarts."
    )

st.divider()
st.caption("Built by an AI that claims this code is production-ready.")
