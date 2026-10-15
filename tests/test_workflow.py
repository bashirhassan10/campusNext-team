import unittest

from campusflow.workflow import (
    assign_ticket,
    find_ticket,
    update_status,
    reopen_ticket,
    get_ticket_queue,
)


class TestTicketAssignment(unittest.TestCase):
    def setUp(self):
        self.tickets = [
            {
                "id": "T001",
                "title": "Wi-Fi is down",
                "assigned_to": None,
            },
            {
                "id": "T002",
                "title": "Laptop is faulty",
                "assigned_to": None,
            },
        ]

    def test_assign_ticket(self):
        ticket = assign_ticket(self.tickets, "T002", "John")

        self.assertEqual(ticket["assigned_to"], "John")
        self.assertIsNone(self.tickets[0]["assigned_to"])

    def test_staff_name_is_trimmed(self):
        ticket = assign_ticket(self.tickets, "T001", "  Ada  ")

        self.assertEqual(ticket["assigned_to"], "Ada")

    def test_blank_staff_name_is_rejected(self):
        with self.assertRaises(ValueError):
            assign_ticket(self.tickets, "T001", "   ")

    def test_unknown_ticket_is_rejected(self):
        with self.assertRaises(ValueError):
            assign_ticket(self.tickets, "T999", "John")

    def test_find_ticket_returns_none_for_unknown_id(self):
        result = find_ticket(self.tickets, "T999")

        self.assertIsNone(result)


class TestTicketWorkflow(unittest.TestCase):
    def setUp(self):
        self.tickets = [
            {
                "id": "T001",
                "status": "open",
                "assigned_to": None,
            }
        ]

    def test_start_unassigned_ticket_fails(self):
        with self.assertRaises(ValueError):
            update_status(self.tickets, "T001", "in_progress")

    def test_start_assigned_ticket(self):
        self.tickets[0]["assigned_to"] = "Ada"

        ticket = update_status(self.tickets, "T001", "in_progress")

        self.assertEqual(ticket["status"], "in_progress")

    def test_resolve_ticket_in_progress(self):
        self.tickets[0]["status"] = "in_progress"
        self.tickets[0]["assigned_to"] = "Ada"

        ticket = update_status(self.tickets, "T001", "resolved")

        self.assertEqual(ticket["status"], "resolved")

    def test_invalid_status_fails(self):
        with self.assertRaises(ValueError):
            update_status(self.tickets, "T001", "waiting")

    def test_resolved_ticket_cannot_be_changed(self):
        self.tickets[0]["status"] = "resolved"

        with self.assertRaises(ValueError):
            update_status(self.tickets, "T001", "open")


class TestReopenTicket(unittest.TestCase):
    def setUp(self):
        self.tickets = [
            {
                "id": "T001",
                "status": "resolved",
                "assigned_to": "Ada",
            }
        ]

    def test_reopen_resolved_ticket(self):
        ticket = reopen_ticket(self.tickets, "T001")

        self.assertEqual(ticket["status"], "open")

    def test_assignment_is_preserved(self):
        ticket = reopen_ticket(self.tickets, "T001")

        self.assertEqual(ticket["assigned_to"], "Ada")

    def test_cannot_reopen_unresolved_ticket(self):
        self.tickets[0]["status"] = "in_progress"

        with self.assertRaises(ValueError):
            reopen_ticket(self.tickets, "T001")

    def test_unknown_ticket_cannot_be_reopened(self):
        with self.assertRaises(ValueError):
            reopen_ticket(self.tickets, "T999")


class TestTicketQueue(unittest.TestCase):
    def setUp(self):
        self.tickets = [
            {
                "id": "T010",
                "status": "open",
                "priority": "high",
            },
            {
                "id": "T002",
                "status": "open",
                "priority": "critical",
            },
            {
                "id": "T001",
                "status": "resolved",
                "priority": "critical",
            },
            {
                "id": "T003",
                "status": "open",
                "priority": "low",
            },
            {
                "id": "T004",
                "status": "open",
                "priority": "high",
            },
        ]

    def test_queue_priority_order(self):
        queue = get_ticket_queue(self.tickets)

        self.assertEqual(
            [ticket["id"] for ticket in queue],
            ["T002", "T004", "T010", "T003"],
        )

    def test_resolved_tickets_are_excluded(self):
        queue = get_ticket_queue(self.tickets)

        self.assertNotIn(
            "T001",
            [ticket["id"] for ticket in queue],
        )

    def test_original_list_is_not_reordered(self):
        original_ids = [ticket["id"] for ticket in self.tickets]

        get_ticket_queue(self.tickets)

        self.assertEqual(
            [ticket["id"] for ticket in self.tickets],
            original_ids,
        )

    def test_in_progress_tickets_are_excluded(self):
        tickets = [
            {
                "id": "T001",
                "status": "in_progress",
                "priority": "critical",
            },
            {
                "id": "T002",
                "status": "open",
                "priority": "high",
            },
        ]

        queue = get_ticket_queue(tickets)

        self.assertEqual(len(queue), 1)
        self.assertEqual(queue[0]["id"], "T002")


if __name__ == "__main__":
    unittest.main()