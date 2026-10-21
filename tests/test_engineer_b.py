import unittest

from campusflow.notes import add_note
from campusflow.queue import get_work_queue
from campusflow.reports import build_report
from campusflow.search import search_tickets, sort_search_results
from campusflow.tickets import create_ticket
from campusflow.understanding_check import QUESTIONS, score_answers
from campusflow.workflow import (
    assign_ticket,
    change_ticket_status,
    reopen_ticket,
)


class EngineerBTests(unittest.TestCase):
    def make_ticket(
        self,
        ticket_id="T001",
        title="WiFi router issue",
        category="Network",
        urgency="low",
        users=1,
    ):
        return create_ticket(
            title,
            category,
            urgency,
            users,
            ticket_id,
        )

    def test_search_case_insensitive_substring(self):
        ticket = self.make_ticket()

        self.assertEqual(search_tickets([ticket], "WIFI"), [ticket])
        self.assertEqual(search_tickets([ticket], "router"), [ticket])

    def test_combined_filters_use_and(self):
        network_low = self.make_ticket("T001", "WiFi down", "Network", "low", 1)
        hardware_low = self.make_ticket("T002", "WiFi down", "Hardware", "low", 1)
        network_high = self.make_ticket("T003", "WiFi down", "Network", "high", 1)

        results = search_tickets(
            [network_low, hardware_low, network_high],
            title="wifi",
            category="Network",
            status="open",
            priority="low",
        )

        self.assertEqual(results, [network_low])

    def test_search_does_not_mutate_ticket(self):
        ticket = self.make_ticket()
        before = dict(ticket)

        search_tickets([ticket], "wifi")

        self.assertEqual(ticket, before)

    def test_empty_report_is_safe(self):
        report = build_report([])

        self.assertEqual(report["resolution_percentage"], 0.0)
        self.assertEqual(report["unresolved"], 0)
        self.assertEqual(report["total"], 0)

    def test_report_counts_statuses_after_reopen(self):
        open_ticket = self.make_ticket("T001", "WiFi issue")
        working_ticket = self.make_ticket("T002", "Laptop broken", "Hardware")

        assign_ticket([working_ticket], "T002", "Alex")
        change_ticket_status([working_ticket], "T002", "in_progress")

        assign_ticket([open_ticket], "T001", "Alex")
        change_ticket_status([open_ticket], "T001", "in_progress")
        change_ticket_status([open_ticket], "T001", "resolved")

        reopen_ticket([open_ticket], "T001")

        report = build_report([open_ticket, working_ticket])

        self.assertEqual(report["by_status"]["open"], 1)
        self.assertEqual(report["by_status"]["in_progress"], 1)
        self.assertEqual(report["resolved"], 0)
        self.assertEqual(report["unresolved"], 2)

    def test_queue_only_open_and_numeric_id_tie_break(self):
        ticket_ten = self.make_ticket("T010", "Issue ten")
        ticket_two = self.make_ticket("T002", "Issue two")

        working_ticket = self.make_ticket("T003", "Working")
        assign_ticket([working_ticket], "T003", "Alex")
        change_ticket_status([working_ticket], "T003", "in_progress")

        queue = get_work_queue([ticket_ten, working_ticket, ticket_two])

        self.assertEqual(queue, [ticket_two, ticket_ten])

    def test_quiz_scoring(self):
        correct_answers = [question[2] for question in QUESTIONS]

        self.assertEqual(score_answers(correct_answers), 6)

    def test_priority_sorting(self):
        low_ticket = self.make_ticket("T001", "Low issue")
        high_ticket = self.make_ticket("T002", "High issue", urgency="high")

        results = sort_search_results([low_ticket, high_ticket])

        self.assertEqual(results, [high_ticket, low_ticket])

    def test_note_can_be_added_and_viewed(self):
        ticket = self.make_ticket()
        tickets = [ticket]

        result = add_note(
            tickets,
            "T001",
            "Mentor A",
            "Wi-Fi router reboot attempted",
        )

        self.assertTrue(result["ok"])
        self.assertEqual(result["note"]["note_id"], "N001")
        self.assertEqual(len(ticket["notes"]), 1)


if __name__ == "__main__":
    unittest.main() 