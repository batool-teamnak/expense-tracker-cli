import contextlib
import io
import json
import math
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import tracker

class TrackerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.db = str(Path(self.temp.name) / 'expenses.json')
        self.patch = patch.object(tracker, 'DB', self.db)
        self.patch.start()
        self.addCleanup(self.patch.stop)

    def quiet(self, fn, *args, **kwargs):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            fn(*args, **kwargs)
        return output.getvalue()

    def test_invalid_amounts_do_not_write(self):
        for amount in ('oops', 'nan', 'inf', '-inf', 0, -2):
            with self.subTest(amount=amount), self.assertRaises(ValueError):
                tracker.add(amount, 'food')
            self.assertFalse(Path(self.db).exists())
        self.quiet(tracker.add, '12.5', 'food')
        self.assertEqual(tracker.load()[0]['amount'], 12.5)

