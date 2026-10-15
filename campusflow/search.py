"""Search and filter CampusFlow tickets."""

VALID_CATEGORIES = ("Network", "Hardware", "Software", "Other")
VALID_STATUSES = ("open", "in_progress", "resolved")
VALID_PRIORITIES = ("critical", "high", "medium", "low")


def search_tickets(tickets, title="", category="", status="", priority=""):
    """Return tickets matching every supplied filter, without modifying tickets."""
    if category and category not in VALID_CATEGORIES:
        raise ValueError(
            f"Invalid category '{category}'. "
            f"Choose one of: {', '.join(VALID_CATEGORIES)}."
        )
    if status and status not in VALID_STATUSES:
        raise ValueError(
            f"Invalid status '{status}'. "
            f"Choose one of: {', '.join(VALID_STATUSES)}."
        )
    if priority and priority not in VALID_PRIORITIES:
        raise ValueError(
            f"Invalid priority '{priority}'. "
            f"Choose one of: {', '.join(VALID_PRIORITIES)}."
        )

    results = []
    for ticket in tickets:
        if title and title.casefold() not in ticket["title"].casefold():
            continue
        if category and category != ticket["category"]:
            continue
        if status and status != ticket["status"]:
            continue
        if priority and priority != ticket["priority"]:
            continue
        results.append(ticket)

    return results
