import unittest
from join_status import classify, wait_for_join, join_button_ready


class Button:
    def __init__(self, classes='', displayed=True, enabled=True, aria_disabled=None, tabindex=None):
        self.attributes = {'class': classes, 'aria-disabled': aria_disabled, 'tabindex': tabindex}
        self.displayed = displayed
        self.enabled = enabled

    def get_attribute(self, name):
        return self.attributes.get(name)

    def is_displayed(self):
        return self.displayed

    def is_enabled(self):
        return self.enabled


class Driver:
    def __init__(self, snapshots):
        self.snapshots = iter(snapshots)
    def execute_script(self, script):
        return next(self.snapshots)

class JoinStatusTests(unittest.TestCase):
    def test_disabled_join_button_is_not_ready(self):
        self.assertFalse(join_button_ready(Button('zm-btn preview-join-button disabled zm-btn--disabled', tabindex='-1')))
        self.assertFalse(join_button_ready(Button('preview-join-button', enabled=False)))
        self.assertFalse(join_button_ready(Button('preview-join-button', aria_disabled='true')))
        self.assertTrue(join_button_ready(Button('preview-join-button')))

    def test_prejoin_is_not_success(self):
        self.assertEqual(classify({'text': 'Join Meeting', 'buttons': ['Join']})[0], 'unknown')
    def test_waiting_room_is_not_success(self):
        self.assertEqual(classify({'text': 'The host will let you in', 'buttons': ['Leave']})[0], 'waiting')
    def test_error_overrides_controls(self):
        self.assertEqual(classify({'text': 'Internal error', 'buttons': ['Leave', 'Participants']})[0], 'failed')
    def test_joined_requires_controls(self):
        self.assertEqual(classify({'buttons': ['Leave']})[0], 'unknown')
        self.assertEqual(classify({'buttons': ['Leave', 'Participants (2)']})[0], 'joined')
    def test_wait_then_admitted(self):
        driver = Driver([{'text': 'Waiting room'}, {'buttons': ['Leave', 'Chat']}, {'buttons': ['Leave', 'Chat']}])
        wait_for_join(driver, pause=lambda _: None)
    def test_internal_error_raises(self):
        with self.assertRaisesRegex(RuntimeError, 'internal error'):
            wait_for_join(Driver([{'text': 'Internal error'}]))
    def test_unknown_times_out(self):
        times = iter([0, 0, 2])
        with self.assertRaises(TimeoutError):
            wait_for_join(Driver([{}]), timeout=1, clock=lambda: next(times), pause=lambda _: None)

if __name__ == '__main__':
    unittest.main()
