# 💭 Reflection: Game Glitch Investigator

Answer each question in 3 to 5 sentences. Be specific and honest about what actually happened while you worked. This is about your process, not trying to sound perfect.

## 1. What was broken when you started?

- What did the game look like the first time you ran it?
- List at least two concrete bugs you noticed at the start  
  (for example: "the hints were backwards").

When I first ran the game, the page looked normal but it was impossible to win. The hints pointed me in the wrong direction, and on some attempts a correct guess was still marked wrong. The difficulty settings also felt backwards, since "Normal" had a wider range than "Hard."

**Bug Reproduction Log**

Document at least 3 bugs you found. Add rows as needed.

| Input | Expected Behavior | Actual Behavior | Console Output / Error |
|-------|-------------------|-----------------|------------------------|
| Guess higher than the secret | Hint says "Go LOWER" | Hint says "Go HIGHER" | No error |
| Correct guess on an even attempt | "Correct! You win" | Marked wrong, no win | `TypeError: '>' not supported between 'int' and 'str'` |
| Select "Hard" difficulty | Widest range, fewest attempts | Range 1–50, smaller than Normal (1–100) | No error |
| Click "New Game" after losing | Fresh, playable game | Still "Game over", old score kept | No error |

---

## 2. How did you use AI as a teammate?

- Which AI tools did you use on this project (for example: ChatGPT, Gemini, Copilot)?
- Give one example of an AI suggestion that was correct (including what the AI suggested and how you verified the result).
- Give one example of an AI suggestion that was incorrect or misleading (including what the AI suggested and how you verified the result).

I worked with Claude (Claude Code) as my main AI teammate. One suggestion that was correct involved the "impossible to win" bug: the AI noticed that on even attempts the secret number was being cast to a string, so comparing an integer guess to a string always failed. I verified this by removing the cast and then winning the game several times in a row. One suggestion that was misleading came during testing. The AI first ran the tests with `python -m pytest` and reported that everything passed, which made me think the suite was fine. However, when I ran `pytest tests/` myself, I got a `ModuleNotFoundError`. I verified the real problem by reproducing the command, and I discovered the project root was not on the import path. This taught me to test using the exact command I plan to use.

---

## 3. Debugging and testing your fixes

- How did you decide whether a bug was really fixed?
- Describe at least one test you ran (manual or using pytest)  
  and what it showed you about your code.
- Did AI help you design or understand any tests? How?

I decided a bug was really fixed in two ways. First, I played the game manually and opened the Developer Debug Info panel to compare my guess against the real secret number. Second, I relied on automated tests so the fixes could not silently break again. One test I ran was `test_too_high_always_penalizes`, which checks that a "Too High" guess always loses five points. This mattered because the original scoring rewarded the player on even attempts, which made no sense. When the test passed, it confirmed the scoring was now consistent. The AI helped me design tests by suggesting edge cases I had not considered, such as flooring the win score at ten points and truncating a float guess like "3.9" into an integer. Writing these tests also helped me understand exactly what behavior each function was supposed to guarantee.

---

## 4. What did you learn about Streamlit and state?

- How would you explain Streamlit "reruns" and session state to a friend who has never used Streamlit?

I would tell my friend that Streamlit re-runs the entire script from top to bottom every time you interact with the page, such as clicking a button or typing in a box. This means normal variables do not survive between clicks, because the script starts fresh each time and forgets everything. To keep information alive, like the secret number or the score, you have to store it in `st.session_state`, which is a special dictionary that persists across reruns. The tricky part is that you also have to reset that state yourself when needed. For example, the "New Game" button only reset some values and left the old status and score behind, so the game stayed stuck on "Game over." Once I understood that reruns wipe everything except session state, the strange behavior finally made sense, and I knew exactly which values I had to initialize and reset.

---

## 5. Looking ahead: your developer habits

- What is one habit or strategy from this project that you want to reuse in future labs or projects?
  - This could be a testing habit, a prompting strategy, or a way you used Git.
- What is one thing you would do differently next time you work with AI on a coding task?
- In one or two sentences, describe how this project changed the way you think about AI generated code.

A habit I want to reuse is fixing one bug at a time and testing each fix. Next time I will verify commands myself. I now treat AI code as a fast draft.
