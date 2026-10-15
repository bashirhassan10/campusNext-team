"""Persist CampusFlow tickets in a JSON file."""

import json
import re
from pathlib import Path

from campusflow.tickets import calculate_priority


DEFAULT_PATH = Path("tickets.json")

REQUIRED_FIELDS = {
    "id",
    "title",
    "category",
    "urgency",
    "affected_users",
    "priority",
    "status",
    "assigned_to",
}

VALID_CATEGORIES = {"Network", "Hardware", "Software", "Other"}
VALID_URGENCIES = {"low", "medium", "high"}
VALID_STATUSES = {"open", "in_progress", "resolved"}


def validate_stored_ticket(ticket):
    """Validate a ticket and its notes without modifying the ticket."""

    if not isinstance(ticket, dict):
        raise ValueError("Ticket must be a dictionary")

    if not REQUIRED_FIELDS.issubset(ticket):
        raise ValueError("Missing required ticket fields")

    ticket_id = ticket["id"]

    if not isinstance(ticket_id, str) or not re.fullmatch(
        r"T[0-9]{3,}", ticket_id
    ):
        raise ValueError("Invalid ticket ID")

    title = ticket["title"]

    if not isinstance(title, str) or not title.strip():
        raise ValueError("Invalid ticket title")

    category = ticket["category"]

    if not isinstance(category, str) or category not in VALID_CATEGORIES:
        raise ValueError("Invalid ticket category")

    urgency = ticket["urgency"]

    if not isinstance(urgency, str) or urgency not in VALID_URGENCIES:
        raise ValueError("Invalid ticket urgency")

    affected_users = ticket["affected_users"]

    if type(affected_users) is not int or affected_users <= 0:
        raise ValueError("Invalid affected users")

    expected_priority = calculate_priority(urgency, affected_users)

    if ticket["priority"] != expected_priority:
        raise ValueError("Invalid ticket priority")

    status = ticket["status"]

    if not isinstance(status, str) or status not in VALID_STATUSES:
        raise ValueError("Invalid ticket status")

    assigned_to = ticket["assigned_to"]

    if assigned_to is not None:
        if not isinstance(assigned_to, str) or not assigned_to.strip():
            raise ValueError("Invalid assigned staff")

    if status == "in_progress" and assigned_to is None:
        raise ValueError("In-progress ticket must be assigned")

    notes = ticket.get("notes", [])

    if not isinstance(notes, list):
        raise ValueError("Invalid notes")

    seen_note_ids = set()

    for note in notes:

        if not isinstance(note, dict):
            raise ValueError("Note must be a dictionary")

        required_note_fields = {"note_id", "author", "message"}

        if not required_note_fields.issubset(note):
            raise ValueError("Missing required note fields")

        note_id = note["note_id"]

        if not isinstance(note_id, str) or not re.fullmatch(
            r"N[0-9]{3,}", note_id
        ):
            raise ValueError("Invalid note ID")

        if note_id in seen_note_ids:
            raise ValueError("Duplicate note ID")

        seen_note_ids.add(note_id)

        author = note["author"]

        if not isinstance(author, str) or not author.strip():
            raise ValueError("Invalid note author")

        message = note["message"]

        if not isinstance(message, str):
            raise ValueError("Invalid note message")

        if not 5 <= len(message.strip()) <= 300:
            raise ValueError("Note message must contain 5 to 300 characters")

    return True


def validate_ticket_collection(tickets):
    """Validate every ticket and reject duplicate ticket IDs."""

    if not isinstance(tickets, list):
        raise ValueError("Tickets must be a list")

    seen_ids = set()

    for ticket in tickets:

        validate_stored_ticket(ticket)

        ticket_id = ticket["id"]

        if ticket_id in seen_ids:
            raise ValueError("Duplicate ticket ID")

        seen_ids.add(ticket_id)

    return True


def load_tickets(path=DEFAULT_PATH):
    """Load tickets safely from JSON."""

    file_path = Path(path)

    if not file_path.exists():
        return []

    try:
        with file_path.open("r", encoding="utf-8") as file:
            tickets = json.load(file)

    except (json.JSONDecodeError, UnicodeDecodeError) as error:
        raise ValueError(
            f"Invalid ticket JSON in {file_path}"
        ) from error

    validate_ticket_collection(tickets)

    # Support older tickets that do not have notes.
    for ticket in tickets:
        ticket.setdefault("notes", [])

    return tickets


def save_tickets(tickets, path=DEFAULT_PATH):
    """Validate and safely save tickets to JSON."""

    validate_ticket_collection(tickets)

    file_path = Path(path)

    file_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    temporary_path = file_path.with_name(
        file_path.name + ".tmp"
    )

    try:
        with temporary_path.open("w", encoding="utf-8") as file:

            json.dump(
                tickets,
                file,
                indent=2,
                ensure_ascii=False
            )

            file.write("\n")

        temporary_path.replace(file_path)

    finally:
        if temporary_path.exists():
            temporary_path.unlink()