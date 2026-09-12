"""
Custom tools for the Deadline Agent.

Each function decorated with @tool becomes something the agent can call
on its own when it decides it's relevant - this is what makes it an
*agent* rather than a script that always does the same thing.
"""

import json
import os
from datetime import datetime, timedelta, timezone
from strands import tool

DATA_FILE = os.path.join(os.path.dirname(__file__), "data", "deadlines.json")

# Default to IST (UTC+5:30) if a deadline is added without a timezone offset
DEFAULT_TZ = timezone(timedelta(hours=5, minutes=30))


def _parse_due_date(due_date_str: str) -> datetime:
    """Parse an ISO date string, assuming IST if no timezone is given."""
    dt = datetime.fromisoformat(due_date_str)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=DEFAULT_TZ)
    return dt


def _load_deadlines() -> list:
    with open(DATA_FILE, "r") as f:
        return json.load(f)


def _save_deadlines(deadlines: list) -> None:
    with open(DATA_FILE, "w") as f:
        json.dump(deadlines, f, indent=2)


@tool
def get_upcoming_deadlines(days_ahead: int = 7) -> str:
    """
    Get all deadlines due within the next N days, sorted by urgency.

    Args:
        days_ahead: How many days into the future to look (default 7).

    Returns:
        A formatted string listing upcoming deadlines with how much time is left.
    """
    now = datetime.now(timezone.utc)
    cutoff = now + timedelta(days=days_ahead)
    deadlines = _load_deadlines()

    upcoming = []
    for d in deadlines:
        due = _parse_due_date(d["due_date"])
        if now <= due <= cutoff:
            hours_left = (due - now).total_seconds() / 3600
            upcoming.append((hours_left, d))

    upcoming.sort(key=lambda x: x[0])

    if not upcoming:
        return "No deadlines in the next {} days.".format(days_ahead)

    lines = []
    for hours_left, d in upcoming:
        days_left = hours_left / 24
        lines.append(
            f"- [{d['priority'].upper()}] {d['title']} — due in {days_left:.1f} days "
            f"({d['notes']})"
        )
    return "\n".join(lines)


@tool
def add_deadline(title: str, due_date: str, priority: str = "medium", notes: str = "") -> str:
    """
    Add a new deadline to track.

    Args:
        title: Short description of the deadline.
        due_date: ISO 8601 datetime string, e.g. 2026-09-10T18:00:00+05:30.
        priority: One of 'low', 'medium', 'high'.
        notes: Optional extra context.

    Returns:
        Confirmation message.
    """
    deadlines = _load_deadlines()
    new_id = max([d["id"] for d in deadlines], default=0) + 1
    deadlines.append({
        "id": new_id,
        "title": title,
        "due_date": due_date,
        "priority": priority,
        "notes": notes,
    })
    _save_deadlines(deadlines)
    return f"Added deadline '{title}' (id={new_id}), due {due_date}."


@tool
def get_most_urgent(threshold_hours: int = 48) -> str:
    """
    Check whether anything is urgent enough to actively alert the user about.
    This is the tool the agent should use when deciding whether to
    interrupt the user at all, vs staying silent in the background.

    Args:
        threshold_hours: Only count things due within this many hours as "urgent".

    Returns:
        A description of the single most urgent item, or a message saying
        nothing needs attention right now.
    """
    now = datetime.now(timezone.utc)
    deadlines = _load_deadlines()

    urgent = []
    for d in deadlines:
        due = _parse_due_date(d["due_date"])
        hours_left = (due - now).total_seconds() / 3600
        if 0 <= hours_left <= threshold_hours:
            urgent.append((hours_left, d))

    if not urgent:
        return "NOTHING_URGENT"

    urgent.sort(key=lambda x: x[0])
    hours_left, d = urgent[0]
    return (
        f"URGENT: '{d['title']}' is due in {hours_left:.1f} hours "
        f"(priority: {d['priority']}). {d['notes']}"
    )
