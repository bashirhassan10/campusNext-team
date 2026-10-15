import unittest
import tempfile
import copy
from pathlib import Path

from campusflow.tickets import (
    create_ticket,
    add_note,
    next_note_id,
    generate_ticket_id,
)

from campusflow.storage import save_tickets, load_tickets


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
                self.tickets,
                "T001",
                "Bashir",
                "Router checked again"
            )

        self.assertEqual(self.tickets[0]["notes"], [])

    def test_invalid_note_does_not_consume_id(self):
        with self.assertRaises(ValueError):
            add_note(
                self.tickets,
                "T001",
                "",
                "Router checked"
            )

        note = add_note(
            self.tickets,
            "T001",
            "Bashir",
            "Router checked"
        )

        self.assertEqual(note["note_id"], "N001")

    def test_notes_survive_save_and_reload(self):
        add_note(
            self.tickets,
            "T001",
            "Bashir",
            "Router connection checked"
        )

        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "tickets.json"

            save_tickets(self.tickets, path)
            loaded = load_tickets(path)

            self.assertEqual(
                loaded[0]["notes"][0]["note_id"],
                "N001"
            )

            self.assertEqual(
                loaded[0]["notes"][0]["message"],
                "Router connection checked"
            )

    def test_duplicate_ticket_ids_rejected(self):
        duplicate = copy.deepcopy(self.tickets[0])

        self.tickets.append(duplicate)

        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "tickets.json"

            with self.assertRaises(ValueError):
                save_tickets(self.tickets, path)

            self.assertFalse(path.exists())

    def test_ticket_id_continues_after_reload(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "tickets.json"

            save_tickets(self.tickets, path)
            loaded = load_tickets(path)

            new_id = generate_ticket_id(loaded)

            self.assertEqual(new_id, "T002")

    def test_note_id_continues_after_reload(self):
        add_note(
            self.tickets,
            "T001",
            "Bashir",
            "First router check"
        )

        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "tickets.json"

            save_tickets(self.tickets, path)
            loaded = load_tickets(path)

            second_note = add_note(
                loaded,
                "T001",
                "Bashir",
                "Second router check"
            )

            self.assertEqual(second_note["note_id"], "N002")
            self.assertEqual(len(loaded[0]["notes"]), 2)


if __name__ == "__main__":
    unittest.main()