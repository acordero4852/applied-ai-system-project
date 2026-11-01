# 🎮 Game Glitch Investigator: The Impossible Guesser

## 🚨 The Situation

You asked an AI to build a simple "Number Guessing Game" using Streamlit.
It wrote the code, ran away, and now the game is unplayable. 

- You can't win.
- The hints lie to you.
- The secret number seems to have commitment issues.

## 🛠️ Setup

1. Install dependencies: `pip install -r requirements.txt`
2. Run the broken app: `python -m streamlit run app.py`

## 🕵️‍♂️ Your Mission

1. **Play the game.** Open the "Developer Debug Info" tab in the app to see the secret number. Try to win.
2. **Find the State Bug.** Why does the secret number change every time you click "Submit"? Ask ChatGPT: *"How do I keep a variable from resetting in Streamlit when I click a button?"*
3. **Fix the Logic.** The hints ("Higher/Lower") are wrong. Fix them.
4. **Refactor & Test.** - Move the logic into `logic_utils.py`.
   - Run `pytest` in your terminal.
   - Keep fixing until all tests pass!

## 📝 Document Your Experience

- [x] Describe the game's purpose.
- [x] Detail which bugs you found.
- [x] Explain what fixes you applied.

## 📸 Demo Walkthrough

Describe your fixed game in numbered steps so a reader can follow along without watching a video:

1. Open the app and choose a difficulty, which sets the number range and attempts allowed.
2. Read the blue banner, which now shows the correct range and remaining attempts for that difficulty.
3. Type a guess and click "Submit Guess" to see an accurate higher or lower hint.
4. Follow the corrected hints toward the secret number until you guess it and win points.
5. Click "New Game" to fully reset the score, attempts, status, and pick a fresh secret.

**Screenshot** *(optional)*: <!-- Insert a screenshot of your fixed, winning game here -->

## 🧪 Test Results

```
# Paste your pytest output here, e.g.:
$ pytest tests/
============================================ test session starts ============================================
platform darwin -- Python 3.10.4, pytest-9.0.3, pluggy-1.6.0
rootdir: ~/game-glitch-investigator
plugins: anyio-4.7.0
collected 16 items                                                                                          

tests/test_game_logic.py ................                                                             [100%]

============================================ 16 passed in 0.01s =============================================
```

## 🚀 Stretch Features

- [x] **High Score / Personal Best tracker.** The game now saves your best score per difficulty (Easy / Normal / Hard) to a local `high_scores.json` file. Your best for the current difficulty shows in the sidebar (`🥇 Best`), and beating it triggers a `🏆 New personal best!` banner. The record survives "New Game" and app restarts. Persistence logic lives in `update_high_scores` / `load_high_scores` / `save_high_scores` in `logic_utils.py` and is covered by tests. Core game logic was not modified.
- [x] **Guess History visualization.** The app is now organized into **Play / History / Stats** tabs. The History tab shows an Altair chart of your guesses per attempt so you can watch them converge; the secret's reference line only appears once the game ends, so the chart never spoils an in-progress round.
- [x] **Hot / Cold proximity feedback.** Every guess shows a 🔥 Blazing / 🌡️ Warm / ❄️ Cold label alongside the Higher/Lower hint, based on how close you are as a fraction of the range (`proximity_label` in `logic_utils.py`).
- [x] **Session summary table.** The History tab lists every guess this round — attempt #, guess, hint, proximity, and running score (`build_summary_rows`).
- [x] **Session stats counter.** The Stats tab tracks games played, games won, win rate, and average attempts per win. Stats accumulate across New Games and reset on app restart (`update_stats` / `compute_win_rate`).

**Enhanced Game UI:**

- [x] **Tabbed layout.** The game is organized into Play / History / Stats tabs (see above).
- [x] **Color-coded hints.** The hint box changes color with how close you are: green when you're 🔥 Blazing or win, yellow when 🌡️ Warm, red when ❄️ Cold (`hint_style`).
- [x] **Attempts progress meter.** A progress bar and "Attempt X of Y" caption show how many guesses you have left (`attempts_progress`).
- [x] **Emoji thermometer bar.** Each guess shows a 10-segment 🔥/⬜ bar that fills as you get hotter (`proximity_meter`).
- [x] **Win / lose polish.** Balloons on a win, snow on a loss, and a live `Score` metric that shows the point change (e.g. `+80` or `−5`) on every guess.

All stretch features add only new pure helpers plus display/state code — `check_guess`, `update_score`, `get_range_for_difficulty`, and `parse_guess` were left unchanged, and all tests pass.
