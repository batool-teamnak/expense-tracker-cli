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
    data.append({"id": len(data)+1, "amount": float(amount),
                  "category": category, "note": note,
                  "date": datetime.now().strftime("%Y-%m-%d")})
    save(data)
    print(f"Added: {category} - {amount}")

def list_expenses(month=None):
    data = load()
    if month:
        data = [e for e in data if e["date"].startswith(month)]
    for e in data:
        print(f"[{e['id']}] {e['date']} | {e['category']:12} | {e['amount']:8.2f} | {e['note']}")

def report():
    data = load()
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

if __name__ == "__main__":
    import sys
    args = sys.argv[1:]
    if not args:
        print("Usage: tracker.py [add|list|report|export]")
    elif args[0] == "add" and len(args) >= 3:
        add(args[1], args[2], args[3] if len(args) > 3 else "")
    elif args[0] == "list":
        list_expenses(args[1] if len(args) > 1 else None)
    elif args[0] == "report":
        report()
    elif args[0] == "export" and len(args) > 1:
        export(args[1])
