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

    def test_category_validation(self):
        for category in ('', '  ', None):
            with self.assertRaises(ValueError):
                tracker.add(10, category)
        self.quiet(tracker.add, 10, ' food ')
        self.assertEqual(tracker.load()[0]['category'], 'food')

    def test_month_cli(self):
        self.quiet(tracker.add, 10, 'food', 'selected')
        row = tracker.load()[0]
        row['date'] = '2026-07-03'
        tracker.save([row])
        self.assertIn('selected', self.quiet(tracker.main, ['list', '--month', '2026-07']))
        self.assertNotIn('selected', self.quiet(tracker.main, ['list', '2026-08']))
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as error:
            tracker.main(['list', '--month', '2026-13'])
        self.assertEqual(error.exception.code, 2)

    def test_month_report(self):
        self.quiet(tracker.add, 10, 'food')
        self.quiet(tracker.add, 20, 'transport')
        rows = tracker.load()
        rows[0]['date'], rows[1]['date'] = '2026-07-01', '2026-08-01'
        tracker.save(rows)
        result = self.quiet(tracker.main, ['report', '--month', '2026-07'])
        self.assertIn('food', result)
        self.assertNotIn('transport', result)
        self.assertIn('10.00', result)

    def test_ids_survive_gaps(self):
        self.quiet(tracker.add, 10, 'food')
        rows = tracker.load()
        rows[0]['id'] = 9
        tracker.save(rows)
        self.quiet(tracker.add, 20, 'fuel')
        self.assertEqual([r['id'] for r in tracker.load()], [9, 10])

    def test_delete(self):
        self.quiet(tracker.add, 10, 'food')
        self.quiet(tracker.add, 20, 'fuel')
        self.quiet(tracker.main, ['delete', '1'])
        self.assertEqual([r['id'] for r in tracker.load()], [2])
        before = Path(self.db).read_bytes()
        with self.assertRaises(ValueError):
            tracker.delete(99)
        self.assertEqual(Path(self.db).read_bytes(), before)

    def test_edit(self):
        self.quiet(tracker.add, 10, 'food', 'old')
        original = tracker.load()[0]
        self.quiet(tracker.main, ['edit', '1', '--amount', '25', '--note', ''])
        row = tracker.load()[0]
        self.assertEqual((row['id'], row['date'], row['category']),
                         (original['id'], original['date'], original['category']))
        self.assertEqual((row['amount'], row['note']), (25, ''))
        before = Path(self.db).read_bytes()
        with self.assertRaises(ValueError):
            tracker.edit(1, amount=30, category=' ')
        self.assertEqual(Path(self.db).read_bytes(), before)

    def test_failed_save_preserves_database(self):
        self.quiet(tracker.add, 10, 'food')
        before = Path(self.db).read_bytes()
        with patch.object(tracker.os, 'replace', side_effect=OSError('disk failure')):
            with self.assertRaises(OSError):
                tracker.save([])
        self.assertEqual(Path(self.db).read_bytes(), before)
        self.assertEqual(list(Path(self.temp.name).iterdir()), [Path(self.db)])

    def test_invalid_database_is_preserved(self):
        for value in ({}, [{}], [{'id': 1}], [dict(id=1, amount=10, category='food', date='2026-02-30', note='')]):
            Path(self.db).write_text(json.dumps(value))
            before = Path(self.db).read_bytes()
            with self.assertRaises(ValueError):
                tracker.add(10, 'food')
            self.assertEqual(Path(self.db).read_bytes(), before)

    def test_custom_database(self):
        custom = str(Path(self.temp.name) / 'nested' / 'work.json')
        self.quiet(tracker.main, ['--database', custom, 'add', '15', 'work'])
        self.assertTrue(Path(custom).exists())
        self.assertFalse(Path(self.db).exists())
        self.assertEqual(json.loads(Path(custom).read_text())[0]['category'], 'work')

    def test_explicit_expense_date(self):
        self.quiet(tracker.main, ['add', '15', 'food', '--date', '2024-02-29'])
        self.assertEqual(tracker.load()[0]['date'], '2024-02-29')
        for date in ('2025-02-29', '2026-7-1', 'bad'):
            with self.assertRaises(ValueError):
                tracker.add(10, 'food', date=date)
        self.assertEqual(len(tracker.load()), 1)

