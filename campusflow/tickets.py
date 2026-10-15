def calculate_priority(urgency, affected_users):
    if urgency == "high" and affected_users >= 10:
        return "critical"

    elif urgency == "high" or affected_users >= 10:
        return "high"

    elif urgency == "medium" or affected_users >= 3:
        return "medium"

    else:
        return "low"

def validate_ticket(title, category, urgency, affected_users):
    if not isinstance(title, str) or not title.strip():
        raise ValueError("Title cannot be empty")

    if not isinstance(category, str):
        raise ValueError("Invalid category")

    category = category.strip().capitalize()

    if category not in ["Network", "Hardware", "Software", "Other"]:
        raise ValueError("Invalid category")

    if not isinstance(urgency, str):
        raise ValueError("Invalid urgency")

    urgency = urgency.strip().lower()

    if urgency not in ["low", "medium", "high"]:
        raise ValueError("Invalid urgency")

    if type(affected_users) is not int or affected_users <= 0:
        raise ValueError("Affected users must be a positive integer")

    return title.strip(), category, urgency, affected_users

def create_ticket(title, category, urgency, affected_users, ticket_id):

    title, category, urgency, affected_users = validate_ticket(
        title, category, urgency, affected_users
    )

    ticket = {
        "id": ticket_id,
        "title": title,
        "category": category,
        "urgency": urgency,
        "affected_users": affected_users,
        "priority": calculate_priority(urgency, affected_users),
        "status": "open",
        "assigned_to": None,
        "notes": []
    }

    return ticket    

def generate_ticket_id(tickets):
    numbers = []

    for ticket in tickets:
        number = int(ticket["id"][1:])
        numbers.append(number)

    if numbers:
        next_number = max(numbers) + 1
    else:
        next_number = 1

    return f"T{next_number:03d}" 

def list_tickets(tickets):
    return tickets       

def view_ticket(tickets, ticket_id):
    for ticket in tickets:
        if ticket["id"] == ticket_id:
            return ticket

    return None   

def next_note_id(ticket):
    notes = ticket["notes"]

    if not notes:
        return "N001"

    numbers = []

    for note in notes:
        number = int(note["note_id"][1:])
        numbers.append(number)

    return f"N{max(numbers) + 1:03d}"     

def add_note(tickets, ticket_id, author, message):
    if not isinstance(author, str) or not author.strip():
        raise ValueError("Author cannot be empty")

    if not isinstance(message, str):
        raise ValueError("Invalid message")

    message = message.strip()

    if len(message) < 5 or len(message) > 300:
        raise ValueError("Message must contain 5 to 300 characters")

    ticket = view_ticket(tickets, ticket_id)

    if ticket is None:
        raise ValueError("Ticket not found")

    if ticket["status"] not in ["open", "in_progress"]:
        raise ValueError("Cannot add notes to a resolved ticket")

    note = {
        "note_id": next_note_id(ticket),
        "author": author.strip(),
        "message": message
    }

    ticket["notes"].append(note)

    return note