# CampusFlow Next — Design Decisions

## Architecture

A Python 3 standard-library CLI (`main.py`) delegates business logic to `campusflow/tickets.py`, `workflow.py`, `search.py`, `reports.py` and `storage.py`. This separation supports isolated unit tests and team contributions.

## Ticket model and priority

Each ticket is a dictionary with `id`, `title`, `category`, `urgency`, `affected_users`, `priority`, `status`, `assigned_to` and `notes`. IDs follow `T001`, `T002`, etc., based on the maximum ID in the current dataset. Priority is calculated from urgency and affected-user count.

## Workflow and queue

Tickets begin `open`. Assignment is required before `in_progress`; resolution requires `in_progress`; `resolved` tickets must be explicitly reopened before status changes. The queue sorts **open** tickets by critical/high/medium/low priority and then ticket ID. Reports treat both `open` and `in_progress` as unresolved, so the queue is intentionally narrower than the unresolved count.

## Notes

Notes are stored inside tickets as `note_id`, `author` and `message`. Author cannot be blank; messages are trimmed and must be 5–300 characters. Note IDs increment per ticket (`N001`, etc.). Notes may be added only while the ticket is `open` or `in_progress`. Options 11/12 add and view notes.

## Search and reporting

Search performs case-insensitive title substring matching and combines supplied category, status and priority filters with AND semantics. Reports provide total tickets, breakdowns by status/priority/category, resolved and unresolved counts, and resolution percentage (0% for an empty dataset).

## Persistence

The application loads `tickets.json` from the working directory and saves changes to a validated JSON file via temporary-file replacement. Invalid saved data is rejected rather than silently overwritten. Older tickets lacking `notes` load with an empty list. The local JSON file is gitignored.

## Testing and review

The user reported 94 passing tests on local `main` after PR #14. GitHub PR #14 displayed zero configured checks. See `docs/final-review.md` for evidence and remaining verification.

## Limitations

Single local user, no authentication or web service, no concurrency guarantees, and no CI requirement verified. Failed disk writes may occur after an in-memory mutation. The exact mentor rubric has not been provided for independent comparison.

## Team attribution

Engineer A: Bashir Hassan. Current Engineer B: GitHub user `ngirinya` (full name to be confirmed). Historical repository documents name Timothy Yusuf for earlier work; this should be verified rather than silently reassigned.
