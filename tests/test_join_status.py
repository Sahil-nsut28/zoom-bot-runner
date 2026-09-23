import unittest
from join_status import classify, wait_for_join

class Driver:
    def __init__(self, snapshots):
        self.snapshots = iter(snapshots)
    def execute_script(self, script):
        return next(self.snapshots)

class JoinStatusTests(unittest.TestCase):
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
