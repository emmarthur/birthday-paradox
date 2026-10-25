# Book directions — Birthday Paradox

**Catalog #437** · Al Sweigart, *The Big Book of Small Python Projects*, **Project #2**

- Online chapter: [inventwithpython.com/bigbookpython/project2.html](https://inventwithpython.com/bigbookpython/project2.html)
- Upstream: [birthdayparadox.py](https://github.com/asweigart/the-big-book-of-small-python-projects/blob/main/birthdayparadox.py)
- Local reference: [`reference/birthdayparadox.py`](./reference/birthdayparadox.py)
- Shared logic: [`birthday_core.py`](./birthday_core.py)

## What the book asks you to build

Monte Carlo exploration of the [birthday problem](https://en.wikipedia.org/wiki/Birthday_problem): random birthdays for **N** people (1–100), check for a duplicate, then run **100,000** trials and report how often a match occurred.

## Core functions

| Function | Role |
|----------|------|
| `getBirthdays(n)` | `n` random `datetime.date` values in year 2001, day offset 0–364 |
| `getMatch(birthdays)` | First duplicate date, or `None` |

## Step order (terminal program)

1. Print intro text.
2. Ask *How many birthdays shall I generate? (Max 100)* until valid `numBDays`.
3. Print comma-separated `Mon D` list for one sample group.
4. Print whether a match exists in that sample.
5. Prompt *Press Enter to begin...* then run **100,000** loops with progress every **10,000**.
6. Print match count and `probability = round(simMatch / 100_000 * 100, 2)`.

## Web version (`web/` — FastAPI, port **3006**)

| Book step | Web equivalent |
|-----------|----------------|
| Input `numBDays` | Number input (1–100) |
| One sample + match message | **Generate one sample** → `POST /api/sample` |
| 100,000 simulations + progress | **Run 100,000 simulations** → SSE `GET /stream/monte-carlo?n=` |
| `getBirthdays` / `getMatch` | [`birthday_core.py`](./birthday_core.py) |
