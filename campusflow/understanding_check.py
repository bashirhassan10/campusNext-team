QUESTIONS = [
    ("Ticket T001 is open and unassigned. A user tries to move it to in_progress.",
     ["Accept", "Reject and preserve all data", "Resolve it automatically", "Remove ticket"], "B"),
    ("The app has zero tickets. What should resolution percentage display?",
     ["Crash", "100%", "0%", "Divide by one without explanation"], "C"),
    ("Filter title='wifi', category='Network', status='open'. Which records should match?",
     ["Any record matching one filter", "Only records matching all supplied filters", "All network records", "All open records"], "B"),
    ("A resolved ticket receives 'Add note'. What should happen?",
     ["Append anyway", "Delete old notes", "Reject until reopened", "Change status silently"], "C"),
    ("The JSON file includes two tickets with the same ID. What should load do?",
     ["Keep both", "Replace memory with duplicates", "Reject the load without changing current memory", "Rename IDs silently"], "C"),
    ("A PR changes validation but has no negative-case tests. Best review action?",
     ["Approve because it runs", "Request focused tests and reasoning", "Merge immediately", "Ask AI to approve it"], "B"),
]
def score_answers(answers: list[str]) -> int:
    return sum(1 for i, q in enumerate(QUESTIONS) if i < len(answers) and answers[i].strip().upper() == q[2])
