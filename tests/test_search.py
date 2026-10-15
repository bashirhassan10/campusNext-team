import unittest

from campusflow.search import search_tickets


def make_ticket(
    ticket_id="T001",
    title="Campus WiFi is down",
    category="Network",
    status="open",
    priority="high",
    assigned_to=None,
):
    return {
        "id": ticket_id,
        "title": title,
        "category": category,
        "urgency": "high",
        "affected_users": 5,
        "priority": priority,
        "status": status,
        "assigned_to": assigned_to,
    }


class SearchTicketsTests(unittest.TestCase):
    def setUp(self):
        self.tickets = [
            make_ticket(),
            make_ticket(
                "T002", "Broken laptop", "Hardware", "in_progress", "medium",
                "Ada",
            ),
            make_ticket(
                "T003", "WiFi password reset", "Software", "resolved", "low",
                "John",
            ),
        ]

    def test_title_search_is_case_insensitive(self):
        self.assertEqual(
            [t["id"] for t in search_tickets(self.tickets, title="WIFI")],
            ["T001", "T003"],
        )

    def test_category_filter(self):
        self.assertEqual(
            [t["id"] for t in search_tickets(self.tickets, category="Hardware")],
            ["T002"],
        )

    def test_status_filter(self):
        self.assertEqual(
            [t["id"] for t in search_tickets(self.tickets, status="resolved")],
            ["T003"],
        )

    def test_priority_filter(self):
        self.assertEqual(
            [t["id"] for t in search_tickets(self.tickets, priority="high")],
            ["T001"],
        )

    def test_filters_are_combined_with_and(self):
        result = search_tickets(
            self.tickets, title="wifi", category="Network", status="open"
        )
        self.assertEqual([t["id"] for t in result], ["T001"])

    def test_combined_filters_can_return_no_results(self):
        self.assertEqual(
            search_tickets(
                self.tickets, title="laptop", category="Network", status="open"
            ),
            [],
        )

    def test_empty_filters_return_all_tickets(self):
        self.assertEqual(search_tickets(self.tickets), self.tickets)

    def test_search_does_not_change_input_collection(self):
        original = [ticket.copy() for ticket in self.tickets]
        search_tickets(self.tickets, title="wifi")
        self.assertEqual(self.tickets, original)

    def test_invalid_category_raises_value_error(self):
        with self.assertRaises(ValueError):
            search_tickets(self.tickets, category="Food")

    def test_invalid_status_raises_value_error(self):
        with self.assertRaises(ValueError):
            search_tickets(self.tickets, status="waiting")

    def test_invalid_priority_raises_value_error(self):
        with self.assertRaises(ValueError):
            search_tickets(self.tickets, priority="urgent")


if __name__ == "__main__":
    unittest.main()
