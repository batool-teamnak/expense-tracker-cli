# Expense Tracker CLI

A lightweight command-line tool to track daily expenses, categorize spending, and generate monthly reports.

## Features

- Add, edit, and delete expenses
- Categorize by food, transport, utilities, entertainment, etc.
- Monthly summary with totals per category
- Export to CSV

## Usage

```bash
python tracker.py add 500 food "Groceries"
python tracker.py list --month 2024-03
python tracker.py report
python tracker.py export expenses.csv
```

## Requirements

- Python 3.8+
- No external dependencies

## Installation

```bash
git clone https://github.com/nadir-ali-khan/expense-tracker-cli
cd expense-tracker-cli
python tracker.py
```
