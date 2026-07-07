# v28020
import json, csv, os, math
from datetime import datetime

DB = os.path.expanduser("~/.expenses.json")

def load():
    if os.path.exists(DB):
        with open(DB) as f:
            return json.load(f)
    return []

def save(data):
    with open(DB, "w") as f:
        json.dump(data, f, indent=2)

def add(amount, category, note=""):
    try:
        amount = float(amount)
    except (TypeError, ValueError):
        raise ValueError("amount must be a positive finite number") from None
    if not math.isfinite(amount) or amount <= 0:
        raise ValueError("amount must be a positive finite number")
    if not isinstance(category, str) or not category.strip():
        raise ValueError("category must not be empty")
    category = category.strip()
    data = load()
    data.append({"id": max((e["id"] for e in data), default=0) + 1, "amount": float(amount),
                  "category": category, "note": note,
                  "date": datetime.now().strftime("%Y-%m-%d")})
    save(data)
    print(f"Added: {category} - {amount}")

def edit(expense_id, amount=None, category=None, note=None):
    data = load()
    row = next((e for e in data if e["id"] == expense_id), None)
    if row is None:
        raise ValueError(f"expense {expense_id} does not exist")
    if amount is None and category is None and note is None:
        raise ValueError("provide an amount, category or note to edit")
    if amount is not None:
        amount = float(amount)
        if not math.isfinite(amount) or amount <= 0:
            raise ValueError("amount must be a positive finite number")
        row["amount"] = amount
    if category is not None:
        if not category.strip():
            raise ValueError("category must not be empty")
        row["category"] = category.strip()
    if note is not None:
        row["note"] = note
    save(data)
    print(f"Updated expense {expense_id}")

def delete(expense_id):
    data = load()
    remaining = [e for e in data if e["id"] != expense_id]
    if len(remaining) == len(data):
        raise ValueError(f"expense {expense_id} does not exist")
    save(remaining)
    print(f"Deleted expense {expense_id}")

def list_expenses(month=None):
    data = load()
    if month:
        data = [e for e in data if e["date"].startswith(month)]
    for e in data:
        print(f"[{e['id']}] {e['date']} | {e['category']:12} | {e['amount']:8.2f} | {e['note']}")

def report(month=None):
    data = load()
    if month:
        valid_month(month)
        data = [e for e in data if e["date"].startswith(month)]
    totals = {}
    for e in data:
        totals[e["category"]] = totals.get(e["category"], 0) + e["amount"]
    print("\n--- Report ---")
    for cat, total in sorted(totals.items(), key=lambda x: -x[1]):
        print(f"  {cat:15} {total:8.2f}")
    print(f"  {'TOTAL':15} {sum(totals.values()):8.2f}\n")

def export(path):
    data = load()
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["id","date","category","amount","note"])
        w.writeheader()
        w.writerows(data)
    print(f"Exported {len(data)} records to {path}")

def valid_month(value):
    import re
    if not re.fullmatch(r"\d{4}-(0[1-9]|1[0-2])", value):
        raise ValueError("month must use YYYY-MM format")
    return value

def main(argv=None):
    import argparse
    parser = argparse.ArgumentParser(description="Track expenses and export reports")
    commands = parser.add_subparsers(dest="command", required=True)
    add_parser = commands.add_parser("add")
    add_parser.add_argument("amount")
    add_parser.add_argument("category")
    add_parser.add_argument("note", nargs="?", default="")
    listing = commands.add_parser("list")
    listing.add_argument("month", nargs="?", type=valid_month)
    listing.add_argument("--month", dest="month_option", type=valid_month)
    reporting = commands.add_parser("report")
    reporting.add_argument("--month", type=valid_month)
    editing = commands.add_parser("edit")
    editing.add_argument("id", type=int)
    editing.add_argument("--amount")
    editing.add_argument("--category")
    editing.add_argument("--note")
    deleting = commands.add_parser("delete")
    deleting.add_argument("id", type=int)
    exporting = commands.add_parser("export")
    exporting.add_argument("path")
    args = parser.parse_args(argv)
    try:
        if args.command == "add":
            add(args.amount, args.category, args.note)
        elif args.command == "list":
            list_expenses(args.month_option or args.month)
        elif args.command == "report":
            report(args.month)
        elif args.command == "edit":
            edit(args.id, args.amount, args.category, args.note)
        elif args.command == "delete":
            delete(args.id)
        elif args.command == "export":
            export(args.path)
    except (ValueError, OSError) as exc:
        parser.error(str(exc))

if __name__ == "__main__":
    main()
