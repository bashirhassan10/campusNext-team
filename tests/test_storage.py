"""Tests for persistent JSON ticket storage."""

import copy
import json
import tempfile
import unittest
from pathlib import Path

from campusflow.storage import load_tickets, save_tickets
from campusflow.tickets import create_ticket, add_note, generate_ticket_id


class TestStorage(unittest.TestCase):

    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.path = Path(self.tempdir.name) / "tickets.json"

    def tearDown(self):
        self.tempdir.cleanup()

    # ORIGINAL TESTS

    def test_missing_file_returns_empty_list(self):
        self.assertEqual(load_tickets(self.path), [])

    def test_save_and_reload_ticket(self):
        ticket = create_ticket("Internet down", "Network", "high", 12, "T001")
        save_tickets([ticket], self.path)
        self.assertEqual(load_tickets(self.path), [ticket])

    def test_empty_list_persists(self):
        save_tickets([], self.path)
        self.assertEqual(load_tickets(self.path), [])

    def test_updates_persist(self):
        ticket = create_ticket("Internet down", "Network", "high", 12, "T001")
        save_tickets([ticket], self.path)
        ticket["status"] = "resolved"
        save_tickets([ticket], self.path)
        self.assertEqual(load_tickets(self.path)[0]["status"], "resolved")

    def test_corrupt_json_raises_value_error(self):
        self.path.write_text("{not-json", encoding="utf-8")
        with self.assertRaises(ValueError):
            load_tickets(self.path)

    def test_invalid_json_structure_raises_value_error(self):
        self.path.write_text(json.dumps({"tickets": []}), encoding="utf-8")
        with self.assertRaises(ValueError):
            load_tickets(self.path)

    def test_invalid_ticket_shape_raises_value_error(self):
        self.path.write_text(json.dumps([{"id": "T001"}]), encoding="utf-8")
        with self.assertRaises(ValueError):
            load_tickets(self.path)

    def test_non_list_save_rejected(self):
        with self.assertRaises(ValueError):
            save_tickets({"id": "T001"}, self.path)

    # NEW STORAGE SAFETY TESTS

    def test_corrupt_json_rejected(self):
        self.path.write_text("{invalid json", encoding="utf-8")

        with self.assertRaises(ValueError):
            load_tickets(self.path)

    def test_duplicate_ticket_ids_rejected(self):
        ticket = create_ticket("Internet issue", "Network", "high", 12, "T001")
        duplicate = copy.deepcopy(ticket)

        with self.assertRaises(ValueError):
            save_tickets([ticket, duplicate], self.path)

        self.assertFalse(self.path.exists())

    def test_duplicate_note_ids_rejected(self):
        ticket = create_ticket("Internet issue", "Network", "high", 12, "T001")

        add_note([ticket], "T001", "Bashir", "Router checked")

        duplicate_note = copy.deepcopy(ticket["notes"][0])
        ticket["notes"].append(duplicate_note)

        with self.assertRaises(ValueError):
            save_tickets([ticket], self.path)

    def test_invalid_note_message_rejected(self):
        ticket = create_ticket("Internet issue", "Network", "high", 12, "T001")

        ticket["notes"] = [
            {
                "note_id": "N001",
                "author": "Bashir",
                "message": "Hi"
            }
        ]

        with self.assertRaises(ValueError):
            save_tickets([ticket], self.path)

    def test_invalid_note_author_rejected(self):
        ticket = create_ticket("Internet issue", "Network", "high", 12, "T001")

        ticket["notes"] = [
            {
                "note_id": "N001",
                "author": "   ",
                "message": "Router checked"
            }
        ]

        with self.assertRaises(ValueError):
            save_tickets([ticket], self.path)

    def test_legacy_ticket_without_notes_loads(self):
        ticket = create_ticket("Internet issue", "Network", "high", 12, "T001")
        ticket.pop("notes", None)

        self.path.write_text(
            json.dumps([ticket]),
            encoding="utf-8"
        )

        loaded = load_tickets(self.path)

        self.assertEqual(loaded[0]["notes"], [])

    def test_failed_save_preserves_existing_file(self):
        ticket = create_ticket("Internet issue", "Network", "high", 12, "T001")

        save_tickets([ticket], self.path)

        original_content = self.path.read_text(encoding="utf-8")

        duplicate = copy.deepcopy(ticket)

        with self.assertRaises(ValueError):
            save_tickets([ticket, duplicate], self.path)

        current_content = self.path.read_text(encoding="utf-8")

        self.assertEqual(original_content, current_content)

    def test_ticket_id_continues_after_reload(self):
        ticket = create_ticket("Internet issue", "Network", "high", 12, "T001")

        save_tickets([ticket], self.path)

        loaded = load_tickets(self.path)

        self.assertEqual(generate_ticket_id(loaded), "T002")

    def test_note_id_continues_after_reload(self):
        ticket = create_ticket("Internet issue", "Network", "high", 12, "T001")

        add_note([ticket], "T001", "Bashir", "First router check")

        save_tickets([ticket], self.path)

        loaded = load_tickets(self.path)

        second_note = add_note(
            loaded,
            "T001",
            "Bashir",
            "Second router check"
        )

        self.assertEqual(second_note["note_id"], "N002")

    def test_notes_survive_save_and_reload(self):
        ticket = create_ticket("Internet issue", "Network", "high", 12, "T001")

        add_note(
            [ticket],
            "T001",
            "Bashir",
            "Router connection checked"
        )

        save_tickets([ticket], self.path)

        loaded = load_tickets(self.path)

        self.assertEqual(
            loaded[0]["notes"][0]["message"],
            "Router connection checked"
        )

    def test_invalid_affected_users_rejected(self):
        ticket = create_ticket("Internet issue", "Network", "high", 12, "T001")

        ticket["affected_users"] = True

        with self.assertRaises(ValueError):
            save_tickets([ticket], self.path)

    def test_invalid_priority_rejected(self):
        ticket = create_ticket("Internet issue", "Network", "high", 12, "T001")

        ticket["priority"] = "low"

        with self.assertRaises(ValueError):
            save_tickets([ticket], self.path)

    def test_invalid_status_rejected(self):
        ticket = create_ticket("Internet issue", "Network", "high", 12, "T001")

        ticket["status"] = "unknown"

        with self.assertRaises(ValueError):
            save_tickets([ticket], self.path)

    def test_unassigned_in_progress_rejected(self):
        ticket = create_ticket("Internet issue", "Network", "high", 12, "T001")

        ticket["status"] = "in_progress"
        ticket["assigned_to"] = None

        with self.assertRaises(ValueError):
            save_tickets([ticket], self.path)


if __name__ == "__main__":
    unittest.main()