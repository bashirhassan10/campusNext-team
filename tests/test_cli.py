"""Integration tests for the interactive CampusFlow CLI."""

import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from main import main
from campusflow.storage import load_tickets, save_tickets


class TestInteractiveCLI(unittest.TestCase):

    def run_cli(self, inputs):
        output = io.StringIO()

        with tempfile.TemporaryDirectory() as tempdir:
            data_file = Path(tempdir) / "tickets.json"

            with (
                patch("builtins.input", side_effect=inputs),
                patch("sys.stdout", output),
                patch(
                    "main.load_tickets",
                    side_effect=lambda: load_tickets(data_file),
                ),
                patch(
                    "main.save_tickets",
                    side_effect=lambda tickets: save_tickets(
                        tickets, data_file
                    ),
                ),
            ):
                main()

        return output.getvalue()

    # =====================================
    # EXISTING CLI TESTS
    # =====================================

    def test_menu_exit(self):
        output = self.run_cli(["9"])

        self.assertIn("Create Ticket", output)
        self.assertIn("Goodbye!", output)

    def test_empty_list_and_report(self):
        output = self.run_cli(["2", "8", "9"])

        self.assertIn("No tickets available.", output)
        self.assertIn("'total': 0", output)

    def test_create_list_view_and_report(self):
        output = self.run_cli([
            "1", "Internet not working", "Network", "high", "12",
            "2", "3", "T001", "8", "9",
        ])

        self.assertIn("Ticket created successfully!", output)
        self.assertIn("'id': 'T001'", output)
        self.assertIn("'priority': 'critical'", output)
        self.assertIn("'total': 1", output)

    def test_assign_progress_resolve_reopen_queue(self):
        output = self.run_cli([
            "1", "Internet down", "Network", "high", "12",
            "4", "T001", "Timothy",
            "5", "T001", "in_progress",
            "7",
            "5", "T001", "resolved",
            "7",
            "6", "T001",
            "9",
        ])

        self.assertIn("Assigned:", output)
        self.assertIn("Updated:", output)
        self.assertIn("No unresolved tickets.", output)
        self.assertIn("Reopened:", output)

    def test_ticket_survives_restart(self):
        with tempfile.TemporaryDirectory() as tempdir:
            data_file = Path(tempdir) / "tickets.json"
            output = io.StringIO()

            with (
                patch(
                    "main.load_tickets",
                    side_effect=lambda: load_tickets(data_file),
                ),
                patch(
                    "main.save_tickets",
                    side_effect=lambda tickets: save_tickets(
                        tickets, data_file
                    ),
                ),
                patch("sys.stdout", output),
            ):
                with patch("builtins.input", side_effect=[
                    "1", "Internet down", "Network", "high", "12", "9"
                ]):
                    main()

                with patch("builtins.input", side_effect=["2", "9"]):
                    main()

            self.assertIn("'id': 'T001'", output.getvalue())

            self.assertEqual(
                load_tickets(data_file)[0]["id"],
                "T001",
            )

    def test_invalid_input_does_not_crash(self):
        output = self.run_cli([
            "0", "1", "Bad input", "Network", "high", "abc",
            "4", "T999", "Timothy", "9",
        ])

        self.assertIn("Invalid choice.", output)
        self.assertIn("Error:", output)
        self.assertIn("Goodbye!", output)

    # =====================================
    # NEW NOTES CLI TESTS
    # =====================================

    def test_add_note_successfully(self):
        output = self.run_cli([
            "1", "Internet down", "Network", "high", "12",
            "11", "T001", "Bashir",
            "Network problem is being investigated",
            "9",
        ])

        self.assertIn("Note added successfully!", output)
        self.assertIn("Note ID: N001", output)
        self.assertIn("Author: Bashir", output)

    def test_view_notes_successfully(self):
        output = self.run_cli([
            "1", "Internet down", "Network", "high", "12",
            "11", "T001", "Bashir",
            "Network problem is being investigated",
            "12", "T001",
            "9",
        ])

        self.assertIn("=== NOTES FOR T001 ===", output)
        self.assertIn("Note ID: N001", output)

        self.assertIn(
            "Message: Network problem is being investigated",
            output,
        )

        self.assertIn("Total notes: 1", output)

    def test_cannot_add_note_to_resolved_ticket(self):
        output = self.run_cli([
            # Create ticket
            "1", "Internet down", "Network", "high", "12",

            # Assign ticket to Bashir
            "4", "T001", "Bashir",

            # Change status to in_progress
            "5", "T001", "in_progress",

            # Change status to resolved
            "5", "T001", "resolved",

            # Attempt to add note to resolved ticket
            "11", "T001", "Bashir",
            "Network problem is being investigated",

            # Exit
            "9",
        ])

        self.assertIn("Assigned:", output)
        self.assertIn("Updated:", output)

        self.assertIn(
            "Cannot add notes to a resolved ticket",
            output,
        )

        self.assertNotIn(
            "Note added successfully!",
            output,
        )

    def test_reject_empty_author(self):
        output = self.run_cli([
            "1", "Internet down", "Network", "high", "12",
            "11", "T001", "",
            "Network problem is being investigated",
            "9",
        ])

        self.assertIn("Author cannot be empty", output)

        self.assertNotIn(
            "Note added successfully!",
            output,
        )

    def test_reject_short_message(self):
        output = self.run_cli([
            "1", "Internet down", "Network", "high", "12",
            "11", "T001", "Bashir", "Hi",
            "9",
        ])

        self.assertIn(
            "Message must contain 5 to 300 characters",
            output,
        )

        self.assertNotIn(
            "Note added successfully!",
            output,
        )

    def test_note_survives_restart(self):
        with tempfile.TemporaryDirectory() as tempdir:
            data_file = Path(tempdir) / "tickets.json"
            output = io.StringIO()

            with (
                patch(
                    "main.load_tickets",
                    side_effect=lambda: load_tickets(data_file),
                ),
                patch(
                    "main.save_tickets",
                    side_effect=lambda tickets: save_tickets(
                        tickets, data_file
                    ),
                ),
                patch("sys.stdout", output),
            ):
                # First run: create ticket and add note
                with patch("builtins.input", side_effect=[
                    "1", "Internet down", "Network", "high", "12",
                    "11", "T001", "Bashir",
                    "Network problem is being investigated",
                    "9",
                ]):
                    main()

                # Second run: view saved note
                with patch("builtins.input", side_effect=[
                    "12", "T001", "9",
                ]):
                    main()

            self.assertIn(
                "=== NOTES FOR T001 ===",
                output.getvalue(),
            )

            self.assertIn(
                "Note ID: N001",
                output.getvalue(),
            )

            saved_tickets = load_tickets(data_file)

            self.assertEqual(
                saved_tickets[0]["notes"][0]["author"],
                "Bashir",
            )

            self.assertEqual(
                saved_tickets[0]["notes"][0]["message"],
                "Network problem is being investigated",
            )


if __name__ == "__main__":
    unittest.main()