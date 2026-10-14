import unittest

from campusflow.tickets import create_ticket, add_note, next_note_id


class TestNotes(unittest.TestCase):

    def setUp(self):
        self.tickets = [
            create_ticket("Internet issue", "Network", "high", 12, "T001")
        ]

    def test_first_note_id(self):
        self.assertEqual(next_note_id(self.tickets[0]), "N001")

    def test_add_valid_note(self):
        note = add_note(
            self.tickets, "T001", "Bashir", "Router checked"
        )

        self.assertEqual(note["note_id"], "N001")
        self.assertEqual(len(self.tickets[0]["notes"]), 1)

    def test_reject_empty_author(self):
        with self.assertRaises(ValueError):
            add_note(self.tickets, "T001", "", "Router checked")

        self.assertEqual(self.tickets[0]["notes"], [])

    def test_reject_short_message(self):
        with self.assertRaises(ValueError):
            add_note(self.tickets, "T001", "Bashir", "Hi")

        self.assertEqual(self.tickets[0]["notes"], [])

    def test_reject_resolved_ticket(self):
        self.tickets[0]["status"] = "resolved"

        with self.assertRaises(ValueError):
            add_note(
                self.tickets, "T001", "Bashir", "Router checked again"
            )

        self.assertEqual(self.tickets[0]["notes"], [])

    def test_invalid_note_does_not_consume_id(self):
        with self.assertRaises(ValueError):
            add_note(self.tickets, "T001", "", "Router checked")

        note = add_note(
            self.tickets, "T001", "Bashir", "Router checked"
        )

        self.assertEqual(note["note_id"], "N001")


if __name__ == "__main__":
    unittest.main()