# Zoom Bot Runner

This repository runs the supplied Zoom web client automation through a manually started GitHub Actions workflow. It checks for in-meeting controls before reporting a joined session. That check does not independently confirm attendance in the host's participant list.

## Run

1. Open **Actions → Zoom Bot Runner → Run workflow**.
2. For a first check, use a meeting you host, set **Number of bots** to `1`, and choose a clearly identifiable custom name.
3. Enter the meeting ID and optional passcode, then start the workflow.
4. Check the host participant list. If the run fails, download the `bot-logs` artifact and inspect `bot_logs.txt` and `diagnostics/`.

Failure screenshots may contain private meeting details. Redact them before sharing. Waiting rooms, authentication challenges, errors, and timeouts are not reported as successful joins. Authentication, CAPTCHA, and host admission must be handled normally.

`JOIN_TIMEOUT` defaults to 120 seconds. The verifier recognizes English UI text and may need updates if Zoom changes its page.

## Local checks

Run `python -m unittest discover -s tests -v`.
