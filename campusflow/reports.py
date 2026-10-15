def generate_report(tickets):
    """Generate a summary of ticket statistics."""

    report = {
        "total": len(tickets),
        "by_status": {
            "open": 0,
            "in_progress": 0,
            "resolved": 0,
        },
        "by_priority": {
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0,
        },
        "by_category": {
            "Network": 0,
            "Hardware": 0,
            "Software": 0,
            "Other": 0,
        },
        "unresolved": 0,
        "resolved_count": 0,
        "resolution_percentage": 0,
    }

    for ticket in tickets:
        status = ticket["status"]
        priority = ticket["priority"]
        category = ticket.get("category")

        # Count tickets by status.
        if status in report["by_status"]:
            report["by_status"][status] += 1

        # Count tickets by priority.
        if priority in report["by_priority"]:
            report["by_priority"][priority] += 1

        # Count tickets by category.
        # Older or simplified test tickets may not have a category.
        if category in report["by_category"]:
            report["by_category"][category] += 1

        # Count tickets that are not yet resolved.
        if status in ("open", "in_progress"):
            report["unresolved"] += 1

        # Count resolved tickets.
        if status == "resolved":
            report["resolved_count"] += 1

    # Calculate the resolution percentage.
    # Keep the percentage at zero when there are no tickets.
    if report["total"] > 0:
        report["resolution_percentage"] = (
            report["resolved_count"] / report["total"]
        ) * 100

    return report