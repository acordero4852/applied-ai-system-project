# AI Interactions Log

> **Stretch features only.** Only fill in the sections that apply to stretch features you attempted. If you did not attempt a stretch feature, leave its section blank or delete it. This file is not required for the core project.

---

## Agent Workflow (SF8)

> Document your experience using an AI agent (e.g., Cursor Agent, Claude, Copilot) to make multi-step changes autonomously.

**What task did you give the agent?**

<!-- Describe the goal you asked the agent to accomplish -->

**What did the agent do?**

<!-- List the steps the agent took (files edited, commands run, etc.) -->

**What did you have to verify or fix manually?**

<!-- Describe anything the agent got wrong or that required human review -->

---

## Test Generation (SF7)

> Document how you used AI to help generate or improve tests.

| Edge Case | Prompt Used | AI-Suggested Test | Did It Pass? | Your Reasoning |
|-----------|-------------|-------------------|--------------|----------------|
| First score for a difficulty | "Write a test for saving a high score when none exists yet" | `test_high_score_new_difficulty_is_record` — expects `(True, {"Easy": 90})` | ✅ Yes | Confirms a brand-new difficulty always counts as a record. |
| A tie with the current best | "What edge case am I missing for a personal-best tracker?" | `test_high_score_tie_is_not_record` — equal score is NOT a new record | ✅ Yes | Prevents "new best!" spam when you merely match your old score. |
| Lower score should not overwrite | "Test that a worse score does not replace the saved best" | `test_high_score_below_previous_is_not_record` — dict unchanged | ✅ Yes | Guarantees the saved value only ever moves up. |
| Function must not mutate caller's dict | "Make sure the update is pure and doesn't mutate its input" | `test_high_score_does_not_mutate_input` | ✅ Yes | Pure function is safer to reuse and reason about. |
| Missing high-score file | "What should load do if the file doesn't exist?" | `test_load_high_scores_missing_file_returns_empty` → `{}` | ✅ Yes | The game must start cleanly on a fresh machine with no saved file. |
| Exact guess = hottest | "Test the Hot/Cold label when the guess equals the secret" | `test_proximity_exact_match_is_blazing` → 🔥 | ✅ Yes | An exact hit should always read as the hottest label. |
| Proximity is symmetric | "Same distance above or below the secret should feel equally close" | `test_proximity_symmetric_above_and_below` | ✅ Yes | Direction (too high vs too low) shouldn't change how 'hot' you are. |
| Empty history table | "What should the summary table show before any guesses?" | `test_build_summary_rows_empty` → `[]` | ✅ Yes | Avoids rendering a broken/empty table on a fresh game. |
| Invalid-guess row | "Handle a history record that has no hint or score" | `test_build_summary_rows_handles_invalid_record` → missing fields show `—` | ✅ Yes | Invalid guesses shouldn't crash the summary table. |
| Win rate with no games | "What is the win rate before any game is played?" | `test_compute_win_rate_zero_games` → `0.0` | ✅ Yes | Prevents a divide-by-zero on the Stats tab at startup. |
| Stats stay pure | "Make sure recording a game result doesn't mutate the old stats dict" | `test_update_stats_does_not_mutate_input` | ✅ Yes | Pure updates are safer to store in session state. |
| Cold hint should look "cold" | "Which color box for a cold guess?" | `test_hint_style_cold_is_error` → `"error"` (red) | ✅ Yes | Confirms the color mapping matches the temperature label. |
| Progress bar over the limit | "What if attempts somehow exceed the limit?" | `test_attempts_progress_over_limit_clamps` → `1.0` | ✅ Yes | A progress value above 1.0 would break `st.progress`. |
| Progress bar with 0 limit | "Guard the meter against a zero attempt limit" | `test_attempts_progress_zero_limit_is_safe` → `0.0` | ✅ Yes | Prevents a divide-by-zero when building the bar. |
| Thermometer fixed width | "The emoji bar should always be the same length" | `test_proximity_meter_has_fixed_length` → 10 segments | ✅ Yes | Keeps the bar from jumping around between guesses. |
| Thermometer fills as you warm up | "Closer guesses should show more fire" | `test_proximity_meter_closer_fills_more` | ✅ Yes | Verifies the bar actually reflects closeness. |

---

## Linting & Style (SF9)

> Document your use of AI for linting or code style improvements.

**Prompt used:**

```
<!-- Paste the prompt you gave the AI -->
```

**Linting output before:**

```
<!-- Paste relevant linter warnings/errors -->
```

**Changes applied:**

<!-- Describe what you changed based on the AI's suggestions -->

---

## Model Comparison (SF11)

> Compare two AI models on the same task.

**Task given to both models:**

<!-- Describe what you asked each model to do -->

| | Model A | Model B |
|-|---------|---------|
| **Model name** | | |
| **Response summary** | | |
| **More Pythonic?** | | |
| **Clearer explanation?** | | |

**Which did you prefer and why?**

<!-- Your conclusion -->
