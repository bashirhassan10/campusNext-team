
def find_ticket(tickets, ticket_id):
    """Find a ticket by its ID."""
    for ticket in tickets:
        if ticket["id"] == ticket_id:
            return ticket

    return None


def assign_ticket(tickets, ticket_id, staff_name):
    """Assign a ticket to a staff member."""

    # Validate the staff name.
    if not isinstance(staff_name, str) or not staff_name.strip():
        raise ValueError("Staff name cannot be empty.")

    # Find the requested ticket.
    ticket = find_ticket(tickets, ticket_id)

    # Reject unknown ticket IDs.
    if ticket is None:
        raise ValueError(f"Ticket '{ticket_id}' was not found.")

    # Update only the selected ticket.
    ticket["assigned_to"] = staff_name.strip()

    return ticket

    
def update_status(tickets, ticket_id, new_status):
    """Update a ticket's status when the transition is valid."""

    allowed_statuses = ["open", "in_progress", "resolved"]

    if new_status not in allowed_statuses:
        raise ValueError("Invalid ticket status.")

    ticket = find_ticket(tickets, ticket_id)

    if ticket is None:
        raise ValueError(f"Ticket '{ticket_id}' was not found.")

    current_status = ticket["status"]

    if current_status == "resolved":
        raise ValueError("Reopen the ticket before modifying it.")

    if current_status == "open" and new_status == "in_progress":
        if not ticket.get("assigned_to"):
            raise ValueError("Assign the ticket before starting work.")

    if current_status == "open" and new_status == "resolved":
        raise ValueError("Ticket must be in progress before resolution.")

    if current_status == "in_progress" and new_status == "open":
        raise ValueError("Use the explicit reopen operation.")

    ticket["status"] = new_status

    return ticket

def reopen_ticket(tickets, ticket_id):
    """Reopen a resolved ticket."""

    ticket = find_ticket(tickets, ticket_id)

    if ticket is None:
        raise ValueError(f"Ticket '{ticket_id}' was not found.")

    if ticket["status"] != "resolved":
        raise ValueError("Only resolved tickets can be reopened.")

    ticket["status"] = "open"

    return ticket


def get_ticket_queue(tickets):
    """Return unresolved tickets ordered by priority and ticket ID."""

    priority_order = {
        "critical": 0,
        "high": 1,
        "medium": 2,
        "low": 3,
    }

    unresolved = [
        ticket for ticket in tickets
        if ticket["status"] == "open"
    ]

    return sorted(
        unresolved,
        key=lambda ticket: (
            priority_order.get(ticket["priority"], 4),
            int(ticket["id"][1:]),
        ),
    )


