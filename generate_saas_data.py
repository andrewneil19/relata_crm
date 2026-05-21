"""
Relata CRM - Synthetic Data Generator
Generates realistic B2B SaaS data for a portfolio data engineering project.

Output: 6 CSV files matching a normalized OLTP schema
  - plans.csv
  - accounts.csv
  - users.csv
  - subscriptions.csv
  - subscription_events.csv
  - invoices.csv

Usage: python generate_saas_data.py
"""

import csv
import random
import uuid
from datetime import datetime, timedelta
from pathlib import Path

# ── Seed for reproducibility ─────────────────────────────────────────────────
random.seed(42)

# ── Config ───────────────────────────────────────────────────────────────────
OUTPUT_DIR = Path("C:/Users/andre/Downloads")
OUTPUT_DIR.mkdir(exist_ok=True)

NUM_ACCOUNTS   = 2000
START_DATE     = datetime(2022, 1, 1)
END_DATE       = datetime(2024, 12, 31)
SIM_DAYS       = (END_DATE - START_DATE).days

# ── Reference data ───────────────────────────────────────────────────────────
INDUSTRIES = [
    "Technology", "Financial Services", "Healthcare", "Retail",
    "Manufacturing", "Professional Services", "Real Estate",
    "Media & Entertainment", "Education", "Logistics",
]

COMPANY_SIZES = ["1-10", "11-50", "51-200", "201-500", "501-1000", "1000+"]

COUNTRIES = [
    "United States", "United States", "United States",   # weighted heavily
    "Canada", "United Kingdom", "Germany", "Australia",
    "France", "Netherlands", "Singapore",
]

FIRST_NAMES = [
    "James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael",
    "Linda", "William", "Barbara", "David", "Elizabeth", "Richard", "Susan",
    "Joseph", "Jessica", "Thomas", "Sarah", "Charles", "Karen", "Emma",
    "Liam", "Olivia", "Noah", "Ava", "Sophia", "Isabella", "Mia", "Charlotte",
    "Amelia", "Harper", "Evelyn", "Abigail", "Emily", "Madison", "Ella",
    "Aiden", "Lucas", "Mason", "Ethan", "Logan", "Jackson", "Sebastian",
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller",
    "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez",
    "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin",
    "Lee", "Perez", "Thompson", "White", "Harris", "Sanchez", "Clark",
    "Ramirez", "Lewis", "Robinson", "Walker", "Young", "Allen", "King",
    "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores", "Green",
]

COMPANY_SUFFIXES = [
    "Inc", "LLC", "Corp", "Group", "Solutions", "Technologies",
    "Partners", "Ventures", "Systems", "Consulting",
]

EMAIL_DOMAINS = [
    "gmail.com", "outlook.com", "company.com", "corp.io",
    "enterprise.net", "business.co", "work.com",
]

# ── Plans ─────────────────────────────────────────────────────────────────────
PLANS = [
    {
        "plan_id":        "plan_starter",
        "plan_name":      "Starter",
        "base_price":     49.00,
        "price_per_seat": 12.00,
        "max_seats":      10,
    },
    {
        "plan_id":        "plan_pro",
        "plan_name":      "Pro",
        "base_price":     149.00,
        "price_per_seat": 20.00,
        "max_seats":      50,
    },
    {
        "plan_id":        "plan_enterprise",
        "plan_name":      "Enterprise",
        "base_price":     499.00,
        "price_per_seat": 35.00,
        "max_seats":      500,
    },
]

PLAN_MAP = {p["plan_id"]: p for p in PLANS}

# Weights: most accounts start on Starter, some on Pro, few on Enterprise
PLAN_WEIGHTS = {"plan_starter": 0.55, "plan_pro": 0.35, "plan_enterprise": 0.10}

# ── Helpers ───────────────────────────────────────────────────────────────────

def random_date(start: datetime, end: datetime) -> datetime:
    delta = (end - start).days
    return start + timedelta(days=random.randint(0, delta))


def random_company_name() -> str:
    word = random.choice(LAST_NAMES)
    suffix = random.choice(COMPANY_SUFFIXES)
    return f"{word} {suffix}"


def calc_mrr(plan_id: str, seat_count: int) -> float:
    p = PLAN_MAP[plan_id]
    return round(p["base_price"] + p["price_per_seat"] * seat_count, 2)


def fmt(dt: datetime) -> str:
    """Format datetime to ISO string."""
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def pick_initial_seats(plan_id: str) -> int:
    if plan_id == "plan_starter":
        return random.randint(1, 5)
    elif plan_id == "plan_pro":
        return random.randint(3, 20)
    else:
        return random.randint(10, 80)


def upgrade_plan(current_plan_id: str) -> str | None:
    """Return the next plan up, or None if already at top."""
    order = ["plan_starter", "plan_pro", "plan_enterprise"]
    idx = order.index(current_plan_id)
    return order[idx + 1] if idx < len(order) - 1 else None


def downgrade_plan(current_plan_id: str) -> str | None:
    """Return the next plan down, or None if already at bottom."""
    order = ["plan_starter", "plan_pro", "plan_enterprise"]
    idx = order.index(current_plan_id)
    return order[idx - 1] if idx > 0 else None


# ── Generators ────────────────────────────────────────────────────────────────

def generate_accounts() -> list[dict]:
    used_names = set()
    accounts = []
    for _ in range(NUM_ACCOUNTS):
        # Ensure unique company names
        for _ in range(10):
            name = random_company_name()
            if name not in used_names:
                used_names.add(name)
                break

        created_at = random_date(START_DATE, END_DATE - timedelta(days=30))
        accounts.append({
            "account_id":    str(uuid.uuid4()),
            "company_name":  name,
            "industry":      random.choice(INDUSTRIES),
            "company_size":  random.choice(COMPANY_SIZES),
            "country":       random.choice(COUNTRIES),
            "created_at":    fmt(created_at),
            "updated_at":    fmt(created_at + timedelta(days=random.randint(0, 30))),
        })
    return accounts


def generate_users(accounts: list[dict]) -> list[dict]:
    users = []
    used_emails = set()

    for account in accounts:
        # Each account gets 1 admin + 0-4 members
        num_members = random.randint(0, 4)
        account_created = datetime.strptime(account["created_at"], "%Y-%m-%d %H:%M:%S")

        for i in range(1 + num_members):
            first = random.choice(FIRST_NAMES)
            last  = random.choice(LAST_NAMES)
            domain = random.choice(EMAIL_DOMAINS)

            # Ensure unique email
            base_email = f"{first.lower()}.{last.lower()}"
            email = f"{base_email}@{domain}"
            suffix = 1
            while email in used_emails:
                email = f"{base_email}{suffix}@{domain}"
                suffix += 1
            used_emails.add(email)

            user_created = account_created + timedelta(days=random.randint(0, 7))
            is_active = random.random() > 0.08  # ~8% inactive

            users.append({
                "user_id":    str(uuid.uuid4()),
                "account_id": account["account_id"],
                "email":      email,
                "first_name": first,
                "last_name":  last,
                "role":       "admin" if i == 0 else "member",
                "created_at": fmt(user_created),
                "is_active":  str(is_active),
            })
    return users


def generate_subscriptions_and_events(
    accounts: list[dict],
) -> tuple[list[dict], list[dict], list[dict]]:
    """
    Simulate a subscription lifecycle per account:
      - Account signs up → creates subscription + 'new' event
      - May upgrade, downgrade, or expand seats over time
      - May churn (and some re-activate)
    Returns (subscriptions, subscription_events, invoices)
    """
    subscriptions   = []
    events          = []
    invoices        = []

    for account in accounts:
        account_created = datetime.strptime(account["created_at"], "%Y-%m-%d %H:%M:%S")
        account_id      = account["account_id"]

        # Pick starting plan
        plan_id    = random.choices(
            list(PLAN_WEIGHTS.keys()),
            weights=list(PLAN_WEIGHTS.values()),
        )[0]
        seat_count = pick_initial_seats(plan_id)
        mrr        = calc_mrr(plan_id, seat_count)

        sub_id     = str(uuid.uuid4())
        sub_start  = account_created + timedelta(days=random.randint(0, 3))
        sub_status = "active"
        sub_end    = None

        subscriptions.append({
            "subscription_id": sub_id,
            "account_id":      account_id,
            "plan_id":         plan_id,
            "status":          sub_status,
            "seat_count":      seat_count,
            "monthly_amount":  mrr,
            "start_date":      sub_start.strftime("%Y-%m-%d"),
            "end_date":        "",
            "created_at":      fmt(sub_start),
        })

        # Initial 'new' event
        events.append({
            "event_id":        str(uuid.uuid4()),
            "subscription_id": sub_id,
            "account_id":      account_id,
            "event_type":      "new",
            "from_plan_id":    "",
            "to_plan_id":      plan_id,
            "from_seats":      "",
            "to_seats":        seat_count,
            "from_mrr":        "",
            "to_mrr":          mrr,
            "event_date":      sub_start.strftime("%Y-%m-%d"),
            "created_at":      fmt(sub_start),
        })

        # ── Simulate months of activity ──────────────────────────────────────
        current_date = sub_start
        churned      = False

        while current_date < END_DATE and not churned:
            # Advance one month
            month_end = current_date + timedelta(days=30)
            if month_end > END_DATE:
                break

            # Generate invoice for this month
            invoice_date = current_date + timedelta(days=random.randint(0, 3))
            paid         = random.random() > 0.04   # ~4% failed payments
            invoices.append({
                "invoice_id":      str(uuid.uuid4()),
                "account_id":      account_id,
                "subscription_id": sub_id,
                "invoice_date":    invoice_date.strftime("%Y-%m-%d"),
                "amount":          mrr,
                "status":          "paid" if paid else "failed",
                "paid_at":         fmt(invoice_date + timedelta(days=random.randint(1, 5))) if paid else "",
                "created_at":      fmt(invoice_date),
            })

            # ── Monthly lifecycle events ─────────────────────────────────────
            roll = random.random()

            # Churn: ~2.5% monthly
            if roll < 0.025:
                churned   = True
                sub_end   = month_end
                sub_status = "cancelled"

                events.append({
                    "event_id":        str(uuid.uuid4()),
                    "subscription_id": sub_id,
                    "account_id":      account_id,
                    "event_type":      "churn",
                    "from_plan_id":    plan_id,
                    "to_plan_id":      "",
                    "from_seats":      seat_count,
                    "to_seats":        "",
                    "from_mrr":        mrr,
                    "to_mrr":          0,
                    "event_date":      month_end.strftime("%Y-%m-%d"),
                    "created_at":      fmt(month_end),
                })

                # ~20% of churned accounts reactivate
                if random.random() < 0.20:
                    gap         = timedelta(days=random.randint(30, 120))
                    react_date  = month_end + gap
                    if react_date < END_DATE:
                        new_sub_id  = str(uuid.uuid4())
                        new_plan    = random.choices(
                            list(PLAN_WEIGHTS.keys()),
                            weights=list(PLAN_WEIGHTS.values()),
                        )[0]
                        new_seats   = pick_initial_seats(new_plan)
                        new_mrr     = calc_mrr(new_plan, new_seats)

                        subscriptions.append({
                            "subscription_id": new_sub_id,
                            "account_id":      account_id,
                            "plan_id":         new_plan,
                            "status":          "active",
                            "seat_count":      new_seats,
                            "monthly_amount":  new_mrr,
                            "start_date":      react_date.strftime("%Y-%m-%d"),
                            "end_date":        "",
                            "created_at":      fmt(react_date),
                        })
                        events.append({
                            "event_id":        str(uuid.uuid4()),
                            "subscription_id": new_sub_id,
                            "account_id":      account_id,
                            "event_type":      "reactivation",
                            "from_plan_id":    "",
                            "to_plan_id":      new_plan,
                            "from_seats":      "",
                            "to_seats":        new_seats,
                            "from_mrr":        0,
                            "to_mrr":          new_mrr,
                            "event_date":      react_date.strftime("%Y-%m-%d"),
                            "created_at":      fmt(react_date),
                        })

            # Upgrade: ~3%
            elif roll < 0.055:
                new_plan = upgrade_plan(plan_id)
                if new_plan:
                    old_mrr    = mrr
                    old_plan   = plan_id
                    plan_id    = new_plan
                    mrr        = calc_mrr(plan_id, seat_count)

                    events.append({
                        "event_id":        str(uuid.uuid4()),
                        "subscription_id": sub_id,
                        "account_id":      account_id,
                        "event_type":      "upgrade",
                        "from_plan_id":    old_plan,
                        "to_plan_id":      plan_id,
                        "from_seats":      seat_count,
                        "to_seats":        seat_count,
                        "from_mrr":        old_mrr,
                        "to_mrr":          mrr,
                        "event_date":      month_end.strftime("%Y-%m-%d"),
                        "created_at":      fmt(month_end),
                    })

            # Downgrade: ~1.5%
            elif roll < 0.07:
                new_plan = downgrade_plan(plan_id)
                if new_plan:
                    old_mrr  = mrr
                    old_plan = plan_id
                    plan_id  = new_plan
                    # Reduce seats to fit new plan max
                    seat_count = min(seat_count, PLAN_MAP[new_plan]["max_seats"])
                    mrr        = calc_mrr(plan_id, seat_count)

                    events.append({
                        "event_id":        str(uuid.uuid4()),
                        "subscription_id": sub_id,
                        "account_id":      account_id,
                        "event_type":      "downgrade",
                        "from_plan_id":    old_plan,
                        "to_plan_id":      plan_id,
                        "from_seats":      seat_count,
                        "to_seats":        seat_count,
                        "from_mrr":        old_mrr,
                        "to_mrr":          mrr,
                        "event_date":      month_end.strftime("%Y-%m-%d"),
                        "created_at":      fmt(month_end),
                    })

            # Seat expansion: ~5%
            elif roll < 0.12:
                max_seats  = PLAN_MAP[plan_id]["max_seats"]
                if seat_count < max_seats:
                    old_mrr    = mrr
                    old_seats  = seat_count
                    seat_count = min(seat_count + random.randint(1, 5), max_seats)
                    mrr        = calc_mrr(plan_id, seat_count)

                    events.append({
                        "event_id":        str(uuid.uuid4()),
                        "subscription_id": sub_id,
                        "account_id":      account_id,
                        "event_type":      "expansion",
                        "from_plan_id":    plan_id,
                        "to_plan_id":      plan_id,
                        "from_seats":      old_seats,
                        "to_seats":        seat_count,
                        "from_mrr":        old_mrr,
                        "to_mrr":          mrr,
                        "event_date":      month_end.strftime("%Y-%m-%d"),
                        "created_at":      fmt(month_end),
                    })

            # Seat contraction: ~2%
            elif roll < 0.14:
                if seat_count > 1:
                    old_mrr    = mrr
                    old_seats  = seat_count
                    seat_count = max(1, seat_count - random.randint(1, 3))
                    mrr        = calc_mrr(plan_id, seat_count)

                    events.append({
                        "event_id":        str(uuid.uuid4()),
                        "subscription_id": sub_id,
                        "account_id":      account_id,
                        "event_type":      "contraction",
                        "from_plan_id":    plan_id,
                        "to_plan_id":      plan_id,
                        "from_seats":      old_seats,
                        "to_seats":        seat_count,
                        "from_mrr":        old_mrr,
                        "to_mrr":          mrr,
                        "event_date":      month_end.strftime("%Y-%m-%d"),
                        "created_at":      fmt(month_end),
                    })

            current_date = month_end

        # Update subscription end date and status if churned
        if churned:
            for sub in subscriptions:
                if sub["subscription_id"] == sub_id:
                    sub["end_date"] = sub_end.strftime("%Y-%m-%d")
                    sub["status"]   = "cancelled"
                    break

    return subscriptions, events, invoices


# ── CSV writer ────────────────────────────────────────────────────────────────

def write_csv(filename: str, rows: list[dict]) -> None:
    if not rows:
        print(f"  ⚠️  No rows for {filename}, skipping.")
        return
    path = OUTPUT_DIR / filename
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(f"  ✅ {filename:35s} {len(rows):>7,} rows")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print("\n🚀 Relata CRM — Synthetic Data Generator")
    print("=" * 50)

    print("\n📋 Generating plans...")
    write_csv("plans.csv", PLANS)

    print("\n🏢 Generating accounts...")
    accounts = generate_accounts()
    write_csv("accounts.csv", accounts)

    print("\n👤 Generating users...")
    users = generate_users(accounts)
    write_csv("users.csv", users)

    print("\n💳 Generating subscriptions, events & invoices...")
    subscriptions, events, invoices = generate_subscriptions_and_events(accounts)
    write_csv("subscriptions.csv", subscriptions)
    write_csv("subscription_events.csv", events)
    write_csv("invoices.csv", invoices)

    print("\n📊 Summary")
    print("=" * 50)
    total_mrr = sum(
        float(s["monthly_amount"])
        for s in subscriptions
        if s["status"] == "active"
    )
    churned = sum(1 for s in subscriptions if s["status"] == "cancelled")
    print(f"  Accounts:             {len(accounts):>7,}")
    print(f"  Users:                {len(users):>7,}")
    print(f"  Subscriptions:        {len(subscriptions):>7,}")
    print(f"    - Active:           {len(subscriptions) - churned:>7,}")
    print(f"    - Cancelled:        {churned:>7,}")
    print(f"  Subscription events:  {len(events):>7,}")
    print(f"  Invoices:             {len(invoices):>7,}")
    print(f"  Current MRR (active): ${total_mrr:>10,.2f}")
    print(f"\n📁 Files written to: ./{OUTPUT_DIR}/")
    print()


if __name__ == "__main__":
    main()
