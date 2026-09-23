"""Conservative English-language Zoom web UI join verification.

DOM verification is client-side evidence, not confirmation from the host roster.
Unknown or changed UI fails closed rather than reporting a successful join.
"""
import time


def join_button_ready(button):
    classes = (button.get_attribute('class') or '').split()
    return (button.is_displayed() and button.is_enabled()
            and 'disabled' not in classes and 'zm-btn--disabled' not in classes
            and button.get_attribute('aria-disabled') != 'true'
            and button.get_attribute('tabindex') != '-1')

SNAPSHOT = r"""
const visible = el => !!(el && el.getClientRects().length &&
    getComputedStyle(el).visibility !== 'hidden');
const buttons = [...document.querySelectorAll('button,[role="button"]')]
    .filter(visible).map(el => (el.innerText || el.getAttribute('aria-label') || '').trim());
return {text: document.body ? document.body.innerText : '', buttons};
"""

def classify(snapshot):
    text = snapshot.get('text', '').lower()
    failures = ('internal error', 'meeting has ended', 'meeting was ended',
                'removed by the host', 'incorrect passcode', 'invalid meeting id',
                'meeting is full', 'unable to join', 'failed to join',
                'connection lost', 'you have been disconnected')
    for phrase in failures:
        if phrase in text:
            return 'failed', phrase
    if any(p in text for p in ('waiting for the host', 'wait for the host',
                               'host will let you in', 'waiting room')):
        return 'waiting', 'Waiting for host/admission; not yet joined'
    if any(p in text for p in ('verify you are human', 'captcha', 'sign in to join')):
        return 'blocked', 'Authentication or verification is required'
    labels = [b.strip().lower() for b in snapshot.get('buttons', [])]
    leave = any(b in ('leave', 'leave meeting') for b in labels)
    controls = any(b.startswith(('participants', 'chat', 'mute', 'unmute',
                                 'join audio', 'start video', 'stop video')) for b in labels)
    if leave and controls:
        return 'joined', 'In-meeting controls visible'
    return 'unknown', 'No verified in-meeting controls'


def read_status(driver):
    return classify(driver.execute_script(SNAPSHOT))


def wait_for_join(driver, timeout=120, report=lambda message: None,
                  clock=time.monotonic, pause=time.sleep):
    deadline = clock() + timeout
    last_state = None
    consecutive = 0
    detail = 'No verified in-meeting controls'
    while clock() < deadline:
        state, detail = read_status(driver)
        if state != last_state:
            report(detail)
            last_state = state
        if state in ('failed', 'blocked'):
            raise RuntimeError(detail)
        consecutive = consecutive + 1 if state == 'joined' else 0
        if consecutive >= 2:
            return
        pause(1)
    raise TimeoutError(f'Join not verified within {timeout}s: {detail}')
