"""Read-only ticket search and sorting."""

CATEGORIES = ["Network", "Hardware", "Software", "Other"]
STATUSES = ["open", "in_progress", "resolved"]
PRIORITIES = ["low", "medium", "high", "critical"]

PRIORITY_ORDER = {
    "critical": 0,
    "high": 1,
    "medium": 2,
    "low": 3,
}


def search_tickets(
    tickets,
    title="",
    category="",
    status="",
    priority="",
):
    """Return tickets matching every supplied filter.

    Title matching is a case-insensitive substring search.
    Empty filters mean that field is not filtered.
    """
    title_term = title.strip().casefold()

    if category and category not in CATEGORIES:
        raise ValueError("Invalid category filter.")

    if status and status not in STATUSES:
        raise ValueError("Invalid status filter.")

    if priority and priority not in PRIORITIES:
        raise ValueError("Invalid priority filter.")

    results = []

    for ticket in tickets:
        if title_term and title_term not in ticket["title"].casefold():
            continue

        if category and ticket["category"] != category:
            continue

        if status and ticket["status"] != status:
            continue

        if priority and ticket["priority"] != priority:
            continue

        results.append(ticket)

    return results


def sort_search_results(tickets):
    """Sort search results by priority, then numeric ticket ID."""
    def sort_key(ticket):
        numeric_id = int("".join(
            character for character in ticket["id"] if character.isdigit()
        ) or 0)

        return (PRIORITY_ORDER[ticket["priority"]], numeric_id)

    return sorted(tickets, key=sort_key)