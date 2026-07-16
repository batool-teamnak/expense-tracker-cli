# Expense Tracker CLI

Track expenses in local JSON files using Python 3.8+ with no dependencies.

```bash
python tracker.py add 500 food "Groceries" --date 2026-07-01
python tracker.py list --month 2026-07 --category food
python tracker.py report --month 2026-07
python tracker.py edit 1 --amount 450 --note "Updated receipt"
python tracker.py delete 1
python tracker.py export expenses.csv
python tracker.py import expenses.csv
python tracker.py --database ~/work-expenses.json add 200 transport
```

The default database is `~/.expenses.json`. The global `--database` option must
appear before the command. Both `list 2026-07` and `list --month 2026-07` work.
Dates require `YYYY-MM-DD`; month filters require `YYYY-MM`. Amounts must be
positive and finite. Categories are trimmed; notes support Unicode.

CSV import requires `date,category,amount,note` headers. Any supplied IDs are
ignored and fresh IDs allocated. Invalid rows reject the entire import. JSON
saves use atomic replacement; multiple simultaneous writers are not supported.
CSV exports cannot overwrite the active JSON database.

Run regression checks with `python -m unittest -v`.
