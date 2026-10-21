"""Original CampusFlow Open Work Queue."""

PRIORITY_ORDER = {
    "critical": 0,
    "high": 1,
    "medium": 2,
    "low": 3,
}


def _numeric_id(ticket):
    return int("".join(
        character for character in ticket["id"] if character.isdigit()
    ) or 0)


def get_work_queue(tickets):
    """Return only OPEN tickets, ordered by priority then numeric ID."""
    open_tickets = [
        ticket for ticket in tickets
        if ticket["status"] == "open"
    ]

    return sorted(
        open_tickets,
        key=lambda ticket: (
            PRIORITY_ORDER[ticket["priority"]],
            _numeric_id(ticket),
        ),
    )