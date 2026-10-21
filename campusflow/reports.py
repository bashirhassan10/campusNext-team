"""CampusFlow quality insights."""

from collections import Counter

CATEGORIES = ["Network", "Hardware", "Software", "Other"]
STATUSES = ["open", "in_progress", "resolved"]
PRIORITIES = ["critical", "high", "medium", "low"]


def build_report(tickets):
    """Build a report from the current ticket collection."""
    statuses = Counter(ticket["status"] for ticket in tickets)
    priorities = Counter(ticket["priority"] for ticket in tickets)
    categories = Counter(
        ticket.get("category")
        for ticket in tickets
        if ticket.get("category") is not None
    )

    total = len(tickets)
    resolved = statuses.get("resolved", 0)

    return {
        "total": total,
        "by_status": {
            status: statuses.get(status, 0)
            for status in sorted(STATUSES)
        },
        "by_priority": {
            priority: priorities.get(priority, 0)
            for priority in PRIORITIES
        },
        "by_category": {
            category: categories.get(category, 0)
            for category in sorted(CATEGORIES)
        },
        "unresolved": (
            statuses.get("open", 0)
            + statuses.get("in_progress", 0)
        ),
        "resolved": resolved,
        "resolution_percentage": (
            round(resolved / total * 100, 2) if total else 0.0
        ),
    }


# Backward-compatible name used by the original CampusFlow tests.
generate_report = build_report