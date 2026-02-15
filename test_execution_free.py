import os
import unittest
from unittest import mock

from picklevis_core import analyze_pickle_bytes


class ExecutionFreeTests(unittest.TestCase):
    def test_execution_free_mode_does_not_execute_payload(self):
        payload = b"cos\nsystem\n(S'echo should_not_run'\ntR."
        called = []

        def fail_if_called(*args, **kwargs):
            called.append((args, kwargs))
            raise AssertionError("os.system must not be called in execution-free mode")

        with mock.patch.object(os, "system", fail_if_called):
            analyzer = analyze_pickle_bytes(payload, execute=False)

        self.assertEqual(called, [])
        self.assertGreater(len(analyzer.picklevis_events), 0)
        opcodes = [event.opcode for event in analyzer.picklevis_events]
        self.assertIn(ord("c"), opcodes)  # GLOBAL
        self.assertIn(ord("R"), opcodes)  # REDUCE

    def test_execute_mode_runs_pickle_semantics(self):
        payload = b"cos\nsystem\n(S'echo will_try_to_run'\ntR."
        called = []

        def fake_system(cmd):
            called.append(cmd)
            return 0

        with mock.patch.object(os, "system", fake_system):
            analyzer = analyze_pickle_bytes(payload, execute=True)

        self.assertEqual(called, ["echo will_try_to_run"])
        self.assertGreater(len(analyzer.picklevis_events), 0)


if __name__ == "__main__":
    unittest.main()
