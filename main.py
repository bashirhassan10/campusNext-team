"""CampusFlow Next command-line interface."""

from campusflow.notes import add_note, view_notes
from campusflow.queue import get_work_queue
from campusflow.reports import build_report
from campusflow.search import search_tickets, sort_search_results
from campusflow.storage import load_tickets, save_tickets
from campusflow.tickets import (
    CATEGORIES,
    PRIORITIES,
    STATUSES,
    create_ticket,
    generate_ticket_id,
    list_tickets,
)
from campusflow.understanding_check import QUESTIONS, score_answers
from campusflow.workflow import (
    assign_ticket,
    change_ticket_status,
    reopen_ticket,
)


def show_ticket(ticket):
    print(
        f"{ticket['id']} | {ticket['title']} | {ticket['category']} | "
        f"{ticket['priority']} | {ticket['status']} | "
        f"Assigned: {ticket['assigned_to'] or '-'}"
    )


def choose_filter(label, options):
    while True:
        value = input(
            f"{label} ({'/'.join(options)}, blank for any): "
        ).strip()

        if not value:
            return ""

        canonical = {
            option.casefold(): option
            for option in options
        }.get(value.casefold())

        if canonical:
            return canonical

        print("Invalid option. Please try again.")


def search_view(tickets):
    term = input("Title contains (blank for any title): ")
    category = choose_filter("Category", CATEGORIES)
    status = choose_filter("Status", STATUSES)
    priority = choose_filter("Priority", PRIORITIES)

    results = search_tickets(
        tickets,
        title=term,
        category=category,
        status=status,
        priority=priority,
    )

    if input("Sort by priority then ticket ID? (y/N): ").strip().lower() == "y":
        results = sort_search_results(results)

    if not results:
        print("No matching tickets.")
        return

    for ticket in results:
        show_ticket(ticket)




def understanding_check():
    answers = []
    explanations = []

    print("\n=== Engineering Understanding Check ===")

    for index, (question, options, correct) in enumerate(QUESTIONS, 1):
        print(f"\nQ{index}. {question}")

        for letter, option in zip("ABCD", options):
            print(f"  {letter}. {option}")

        while True:
            answer = input("Your answer (A/B/C/D): ").strip().upper()

            if answer in ("A", "B", "C", "D"):
                break

            print("Enter A, B, C, or D.")

        answers.append(answer)

        if answer == correct:
            print("Correct.")
        else:
            print(f"Not quite. Correct answer: {correct}.")

        if index in (1, 4):
            explanations.append(
                input(f"Briefly explain your answer to Q{index}: ").strip()
            )

    score = score_answers(answers)
    print(f"Final score: {score}/6")

    from pathlib import Path

    learning_path = Path("docs/understanding-check-reflection.md")
    learning_path.parent.mkdir(parents=True, exist_ok=True)

    with learning_path.open("a", encoding="utf-8") as handle:
        handle.write("\n## Quiz attempt\n")
        handle.write(f"Score: {score}/6\n")

        for number, explanation in enumerate(explanations, 1):
            handle.write(f"Explanation {number}: {explanation}\n")


def main():
    try:
        tickets = load_tickets()
    except ValueError as error:
        print(f"Storage error: {error}")
        print("Current data was not loaded. Fix the JSON file and restart.")
        return

    while True:
        print("\n======= CAMPUSFLOW NEXT =======")

        menu_options = [
            "Create ticket",
            "List tickets",
            "Assign ticket",
            "Change ticket status",
            "View Open Work Queue",
            "View report",
            "Search tickets",
            "Add Follow-up Note",
            "View Ticket Notes",
            "Engineering Understanding Check",
            "Save and exit",
        ]

        for number, label in enumerate(menu_options, 1):
            print(f"{number}. {label}")

        choice = input("Choose an option: ").strip()

        try:
            if choice == "1":
                title = input("Ticket title: ")
                category = input("Category (Network/Hardware/Software/Other): ")
                urgency = input("Urgency (low/medium/high): ")
                affected = input("Number of affected users: ").strip()

                if not affected.isdecimal():
                    raise ValueError("Affected users must be a positive integer.")

                ticket_id = generate_ticket_id(tickets)

                ticket = create_ticket(
                    title,
                    category,
                    urgency,
                    int(affected),
                    ticket_id,
                )

                tickets.append(ticket)
                save_tickets(tickets)

                print(f"Created {ticket['id']} with {ticket['priority']} priority.")

            elif choice == "2":
                if not tickets:
                    print("No tickets yet.")
                else:
                    for ticket in list_tickets(tickets):
                        show_ticket(ticket)

            elif choice in {"3", "4", "8", "9"}:
                ticket_id = input("Ticket ID: ").strip().upper()

                ticket = next(
                    (
                        item
                        for item in tickets
                        if item["id"] == ticket_id
                    ),
                    None,
                )

                if ticket is None:
                    print("Ticket not found.")
                    continue

                if choice == "3":
                    staff = input("Assign to: ")
                    result = assign_ticket(tickets, ticket_id, staff)

                    if result:
                        save_tickets(tickets)
                        print("Ticket assigned.")
                    else:
                        print("Could not assign ticket.")

                elif choice == "4":
                    new_status = input(
                        "New status (open/in_progress/resolved): "
                    ).strip().lower()

                    if new_status == "open":
                        try:
                            reopen_ticket(tickets, ticket_id)
                        except ValueError as error:
                            print(f"Error: {error}")
                            continue

                        save_tickets(tickets)
                        print("Ticket reopened.")
                        continue

                    result = change_ticket_status(
                        tickets,
                        ticket_id,
                        new_status,
                    )

                    if result["ok"]:
                        save_tickets(tickets)
                        print("Ticket status updated.")
                    else:
                        print(result["error"])

                elif choice == "8":
                    author = input("Author label: ")
                    message = input("Note (5-300 characters): ")

                    result = add_note(
                        tickets,
                        ticket_id,
                        author,
                        message,
                    )

                    if result["ok"]:
                        save_tickets(tickets)
                        print(f"Added note {result['note']['note_id']}.")
                    else:
                        print(result["error"])

                else:
                    result = view_notes(tickets, ticket_id)

                    if not result["ok"]:
                        print(result["error"])
                    elif not result["notes"]:
                        print("No notes for this ticket.")
                    else:
                        for note in result["notes"]:
                            print(
                                f"{note['note_id']} | "
                                f"{note['author']} | "
                                f"{note['message']}"
                            )

            elif choice == "5":
                queue = get_work_queue(tickets)

                if not queue:
                    print("No open tickets.")
                else:
                    for ticket in queue:
                        show_ticket(ticket)

            elif choice == "6":
                report = build_report(tickets)

                print(f"Total tickets: {report['total']}")
                print("By status:", report["by_status"])
                print("By priority:", report["by_priority"])
                print("By category:", report["by_category"])
                print(
                    f"Unresolved: {report['unresolved']}; "
                    f"Resolved: {report['resolved']}"
                )
                print(f"Resolution: {report['resolution_percentage']}%")

            elif choice == "7":
                search_view(tickets)

            elif choice == "10":
                understanding_check()

            elif choice == "11":
                save_tickets(tickets)
                print("Saved. Goodbye!")
                break

            else:
                print("Please choose a number from 1 to 11.")

        except (ValueError, TypeError) as error:
            print(f"Error: {error}")


if __name__ == "__main__":
    main()