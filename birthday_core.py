"""
Birthday paradox simulation — shared logic for reference script and FastAPI web app.

Flow:
  1. get_birthdays(n)     — random dates in one leap-agnostic year (2001 + 0–364 days).
  2. get_match(birthdays) — first duplicate date, or None.
  3. monte_carlo_stream   — repeat step 1–2 SIMULATION_COUNT times; count matches.

The web app calls these functions; reference/birthdayparadox.py is the interactive terminal version.
"""

from __future__ import annotations

import datetime
import random
from collections.abc import Iterator
from typing import Any

# Book uses 100_000 trials; progress prints every 10_000.
SIMULATION_COUNT = 100_000
PROGRESS_EVERY = 10_000
MAX_GROUP_SIZE = 100
MIN_GROUP_SIZE = 1

MONTHS = (
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec",
)


def get_birthdays(number_of_birthdays: int) -> list[datetime.date]:
    """Return `number_of_birthdays` random dates (same year — only month/day matter)."""
    birthdays: list[datetime.date] = []
    start_of_year = datetime.date(2001, 1, 1)
    for _ in range(number_of_birthdays):
        random_days = datetime.timedelta(random.randint(0, 364))
        birthdays.append(start_of_year + random_days)
    return birthdays


def get_match(birthdays: list[datetime.date]) -> datetime.date | None:
    """Return one date that appears twice, or None if all unique."""
    if len(birthdays) == len(set(birthdays)):
        return None
    for index_a, birthday_a in enumerate(birthdays):
        for birthday_b in birthdays[index_a + 1 :]:
            if birthday_a == birthday_b:
                return birthday_a
    return None


def format_birthday(birthday: datetime.date) -> str:
    """Book-style label, e.g. 'Jul 29'."""
    month_name = MONTHS[birthday.month - 1]
    return f"{month_name} {birthday.day}"


def format_birthday_list(birthdays: list[datetime.date]) -> str:
    """Comma-separated list like the book's sample output."""
    return ", ".join(format_birthday(b) for b in birthdays)


def validate_group_size(num_bdays: int) -> None:
    if not (MIN_GROUP_SIZE <= num_bdays <= MAX_GROUP_SIZE):
        raise ValueError(
            f"Group size must be between {MIN_GROUP_SIZE} and {MAX_GROUP_SIZE}.",
        )


def run_sample(num_bdays: int) -> dict[str, Any]:
    """
    One random group: generate birthdays, detect match, return JSON-friendly dict.
    """
    validate_group_size(num_bdays)
    birthdays = get_birthdays(num_bdays)
    match = get_match(birthdays)
    return {
        "num_bdays": num_bdays,
        "birthdays_text": format_birthday_list(birthdays),
        "birthdays": [format_birthday(b) for b in birthdays],
        "has_match": match is not None,
        "match_text": format_birthday(match) if match else None,
    }


def monte_carlo_stream(num_bdays: int) -> Iterator[dict[str, Any]]:
    """
    Yield progress events, then a final summary (same math as the book's second half).

    Yields:
        {"type": "progress", "completed": int}  every PROGRESS_EVERY iterations
        {"type": "done", "sim_match", "probability", "num_bdays", "simulation_count"}
    """
    validate_group_size(num_bdays)
    sim_match = 0
    for i in range(SIMULATION_COUNT):
        if i % PROGRESS_EVERY == 0:
            yield {"type": "progress", "completed": i}
        if get_match(get_birthdays(num_bdays)) is not None:
            sim_match += 1
    probability = round(sim_match / SIMULATION_COUNT * 100, 2)
    yield {
        "type": "done",
        "num_bdays": num_bdays,
        "sim_match": sim_match,
        "simulation_count": SIMULATION_COUNT,
        "probability": probability,
    }
