# CampusFlow Next

CampusFlow Next is a Python 3 command-line application for managing campus support tickets. It supports validation, prioritization, assignment, workflow, notes, search, analytics, and local JSON persistence. No third-party packages are required.

## Team and collaboration

- **Engineer A — Bashir Hassan:** ticket validation, notes logic, Add/View Notes CLI integration and tests.
- **Engineer B — ngirinya (GitHub username):** ticket search, combined filters, enhanced analytics and search tests.
- Earlier repository documentation names **Timothy Yusuf** for historical workflow contributions. Do not treat that older attribution as the identity of the current Engineer B without team confirmation.

Merged pull requests: [#12](https://github.com/bashirhassan10/campusNext-team/pull/12) (validation/notes), [#13](https://github.com/bashirhassan10/campusNext-team/pull/13) (search/analytics), and [#14](https://github.com/bashirhassan10/campusNext-team/pull/14) (final CLI integration/tests).

## Requirements and setup

Use Python 3 from the repository root:

```bash
git clone https://github.com/bashirhassan10/campusNext-team.git
cd campusNext-team
python3 main.py
```

No `pip install` is needed.

## Interactive menu

| Option | Action |
|---|---|
| 1 | Create Ticket |
| 2 | List Tickets |
| 3 | View Ticket |
| 4 | Assign Ticket |
| 5 | Update Status |
| 6 | Reopen Ticket |
| 7 | Ticket Queue |
| 8 | Generate Report |
| 9 | Exit |
| 10 | Search Tickets |
| 11 | Add Note |
| 12 | View Notes |

### Example workflow

1. Choose **1** and enter a nonempty title, category (`Network`, `Hardware`, `Software`, `Other`), urgency (`low`, `medium`, `high`), and positive integer affected-user count. The first ticket is typically `T001`.
2. Choose **4** to assign `T001` to a staff member.
3. Choose **5** to move `T001` to `in_progress`, and **5** again to mark it `resolved`. A ticket cannot be resolved directly from `open`.
4. Choose **6** to reopen a resolved ticket if needed.
5. Choose **11** to add a note while a ticket is `open` or `in_progress`. Enter the ticket ID, a nonblank author, and a message between **5 and 300 characters**. Notes have IDs such as `N001`, incremented per ticket. Notes cannot be added to resolved tickets.
6. Choose **12** and enter the ticket ID to see saved notes.
7. Choose **10** to search by case-insensitive title substring, optionally combining category, status, and priority filters. Leave a filter blank to skip it.
8. Choose **8** to view totals by status, priority and category, unresolved/resolved counts, and resolution percentage. Choose **7** for the **open-ticket** priority queue (critical → high → medium → low).

### Ticket data

Tickets include `id`, `title`, `category`, `urgency`, `affected_users`, `priority`, `status`, `assigned_to`, and `notes`. Priority is derived from urgency and affected users; it is not entered manually.

## Persistence and safety

The CLI reads and writes `tickets.json` in the **current working directory**. This local file is gitignored. Create a ticket or note, choose **9** to exit, restart `python3 main.py`, and list the ticket or view its notes to verify persistence. Legacy records without `notes` load with an empty notes list.

Malformed JSON or invalid stored tickets cause a visible error instead of overwriting existing data. Writes validate data and replace a temporary JSON file. Keep backups of important local data; JSON storage is designed for a single local user, **not** simultaneous editors.

## Automated tests

```bash
python3 -m unittest discover -s tests -v
```

**Recorded verification:** 94 tests passed on the user's local `main` after PR #14 was merged (15 October 2026). This is user-reported local execution, not a GitHub Actions CI check. The tests cover ticket creation, validation, workflow, queue, persistence, search, reports, and interactive notes paths. Run the command again after any new changes.

## Project layout

- `main.py` — interactive CLI, including search and notes
- `campusflow/tickets.py` — validation, priorities, ticket IDs and notes
- `campusflow/workflow.py` — assignment, status transitions, reopening, queue
- `campusflow/search.py` — ticket search and filters
- `campusflow/reports.py` — analytics and reporting
- `campusflow/storage.py` — validated JSON load/save
- `tests/` — unit and CLI integration tests
- `docs/design-decisions.md` — architecture, tradeoffs and limitations
- `docs/ai-learning-log.md` — AI assistance and verification record
- `docs/final-review.md` — submission-readiness checklist and outstanding items

## Known limitations

Local CLI only; no login, authorization, web UI, concurrent writes or hosted database. Queue option 7 includes **open** tickets only (not all unresolved statuses). No GitHub CI checks were shown for PR #14; local tests passing does not substitute for independent review. Confirm the exact mentor rubric and both contributors' approval before submission.
