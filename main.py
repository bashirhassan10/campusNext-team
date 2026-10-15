from campusflow.tickets import (
    create_ticket,
    generate_ticket_id,
    list_tickets,
    view_ticket,
)

from campusflow.workflow import (
    assign_ticket,
    update_status,
    reopen_ticket,
    get_ticket_queue,
)

from campusflow.reports import generate_report
from campusflow.storage import load_tickets, save_tickets

from campusflow.search import (
    search_tickets,
    VALID_CATEGORIES,
    VALID_STATUSES,
    VALID_PRIORITIES,
)


def get_valid_filter(prompt, valid_options):
    while True:
        value = input(prompt).strip()

        if not value:
            return ""

        if value in valid_options:
            return value

        print(
            f"Invalid input. Choose one of: "
            f"{', '.join(valid_options)}, or leave blank to skip."
        )


def main():
    try:
        tickets = load_tickets()
    except (ValueError, OSError) as error:
        print("Unable to load saved tickets:", error)
        print("Existing data was not overwritten.")
        return

    actions = {
        "1": "Create Ticket",
        "2": "List Tickets",
        "3": "View Ticket",
        "4": "Assign Ticket",
        "5": "Update Status",
        "6": "Reopen Ticket",
        "7": "Ticket Queue",
        "8": "Generate Report",
        "9": "Exit",
        "10": "Search Tickets",
    }

    while True:
        print("\n=== CAMPUSFLOW ===")

        for key, label in actions.items():
            print(f"{key}. {label}")

        try:
            choice = input("Choose 1-10: ").strip()

            if choice == "9":
                print("Goodbye!")
                break

            if choice not in actions:
                print("Invalid choice.")
                continue

            if choice == "1":
                title = input("Title: ")
                category = input(
                    "Category (Network/Hardware/Software/Other): "
                ).strip()
                urgency = input(
                    "Urgency (low/medium/high): "
                ).strip().lower()
                users = int(input("Affected users: "))

                ticket = create_ticket(
                    title,
                    category,
                    urgency,
                    users,
                    generate_ticket_id(tickets),
                )

                tickets.append(ticket)
                save_tickets(tickets)

                print("Ticket created successfully!")
                print(ticket)

            elif choice == "2":
                print("\n=== ALL TICKETS ===")

                all_tickets = list_tickets(tickets)

                print(f"Total tickets found: {len(all_tickets)}")

                if not all_tickets:
                    print("No tickets available. Create a ticket first.")
                else:
                    for ticket in all_tickets:
                        print("-" * 40)
                        print(f"ID: {ticket['id']}")
                        print(f"Title: {ticket['title']}")
                        print(f"Category: {ticket['category']}")
                        print(f"Urgency: {ticket['urgency']}")
                        print(f"Affected users: {ticket['affected_users']}")
                        print(f"Priority: {ticket['priority']}")
                        print(f"Status: {ticket['status']}")
                        print(f"Assigned to: {ticket['assigned_to']}")

                    print("-" * 40)
                    print(f"Total displayed: {len(all_tickets)}")

            elif choice == "3":
                ticket_id = input("Ticket ID: ").strip()
                ticket = view_ticket(tickets, ticket_id)

                if ticket is None:
                    print("Ticket not found.")
                else:
                    print("\n=== TICKET DETAILS ===")
                    print(ticket)

            elif choice == "4":
                ticket_id = input("Ticket ID: ").strip()
                name = input("Staff name: ")

                updated = assign_ticket(
                    tickets,
                    ticket_id,
                    name,
                )

                save_tickets(tickets)

                print("Ticket assigned successfully!")
                print(f"Assigned: {updated['assigned_to']}")
                print(updated)

            elif choice == "5":
                ticket_id = input("Ticket ID: ").strip()
                status = input(
                    "Status (open/in_progress/resolved): "
                ).strip().lower()

                updated = update_status(
                    tickets,
                    ticket_id,
                    status,
                )

                save_tickets(tickets)

                print("Ticket status updated successfully!")
                print(f"Updated: {updated['status']}")
                print(updated)

            elif choice == "6":
                ticket_id = input("Ticket ID: ").strip()

                updated = reopen_ticket(
                    tickets,
                    ticket_id,
                )

                save_tickets(tickets)

                print("Ticket reopened successfully!")
                print(f"Reopened: {updated['status']}")
                print(updated)

            elif choice == "7":
                queue = get_ticket_queue(tickets)

                if queue:
                    print("\n=== TICKET QUEUE ===")

                    for ticket in queue:
                        print(ticket)
                else:
                    print("No unresolved tickets.")

            elif choice == "8":
                report = generate_report(tickets)

                print("\n=== CAMPUSFLOW REPORT ===")
                print(report)

                print(f"\nTotal tickets: {report['total']}")

                print("\nTickets by status:")
                for status, count in report["by_status"].items():
                    print(f"  {status}: {count}")

                print("\nTickets by priority:")
                for priority, count in report["by_priority"].items():
                    print(f"  {priority}: {count}")

                print("\nTickets by category:")
                for category, count in report["by_category"].items():
                    print(f"  {category}: {count}")

                print(f"\nUnresolved tickets: {report['unresolved']}")
                print(f"Resolved tickets: {report['resolved_count']}")
                print(
                    "Resolution percentage: "
                    f"{report['resolution_percentage']:.2f}%"
                )

            elif choice == "10":
                print("\n=== SEARCH TICKETS ===")

                title = input(
                    "Title contains (leave blank to skip): "
                ).strip()

                category = get_valid_filter(
                    "Category (Network/Hardware/Software/Other, "
                    "or blank to skip): ",
                    VALID_CATEGORIES,
                )

                status = get_valid_filter(
                    "Status (open/in_progress/resolved, "
                    "or blank to skip): ",
                    VALID_STATUSES,
                )

                priority = get_valid_filter(
                    "Priority (critical/high/medium/low, "
                    "or blank to skip): ",
                    VALID_PRIORITIES,
                )

                results = search_tickets(
                    tickets,
                    title=title,
                    category=category,
                    status=status,
                    priority=priority,
                )

                if not results:
                    print("No matching tickets found.")
                else:
                    print("\n=== SEARCH RESULTS ===")

                    for ticket in results:
                        print(
                            f"ID: {ticket['id']} | "
                            f"Title: {ticket['title']} | "
                            f"Category: {ticket['category']} | "
                            f"Priority: {ticket['priority']} | "
                            f"Status: {ticket['status']} | "
                            f"Assigned to: {ticket['assigned_to']}"
                        )

        except (ValueError, OSError) as error:
            print("Error:", error)

        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break


if __name__ == "__main__":
    main()