import re
from datetime import datetime

PURCHASE_VERBS = (
    "want to buy", "wants to buy", "planning to buy", "plan to buy",
    "looking to buy", "need to buy", "wish to buy", "buy a", "buy an",
    "purchase a", "purchase an", "get a", "get an", "save for a", "save for an",
    "save up for", "afford a", "afford an",
)

DESIRE_PATTERN = re.compile(
    r"\b(want|wanna|need|wish|would like|looking for|planning to get|planning to buy|"
    r"planning for|hope to get|hope to buy)\s+"
    r"(?:(?:to|a|an|the|my)\s+)*"
    r"(?:(?:buy|get|purchase|own)\s+(?:(?:a|an|the|my)\s+)*)?",
    re.IGNORECASE,
)

PURCHASE_ITEMS = {
    "bike": "Bike", "bicycle": "Bike", "scooter": "Scooter", "motorcycle": "Bike",
    "car": "Car", "vehicle": "Vehicle", "laptop": "Laptop", "phone": "Phone",
    "mobile": "Phone", "smartphone": "Phone", "house": "Home", "home": "Home",
    "flat": "Home", "apartment": "Home", "tv": "TV", "television": "TV",
    "watch": "Watch", "camera": "Camera", "tablet": "Tablet", "ipad": "Tablet",
}

INCOME_BRACKET_MIDPOINTS = {
    "below 3 lakhs": 150000,
    "3 - 8 lakhs": 550000,
    "8 - 15 lakhs": 1150000,
    "15+ lakhs": 2000000,
}


def _first_name(full_name: str) -> str:
    return (full_name or "there").strip().split()[0] if full_name else "there"


def _normalize_money_text(text: str) -> str:
    return text.lower().replace(",", "").replace("₹", "").replace("rs.", "rs").strip()


def parse_rupee_value(text: str) -> int | None:
    """Extract any rupee amount — supports 120, 120rs, rs 35000, 5 lakh, 50k, etc."""
    normalized = _normalize_money_text(text)
    if not normalized:
        return None

    lakh_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:lakh|lakhs|lac|lacs|l)\b", normalized)
    if lakh_match:
        return int(float(lakh_match.group(1)) * 100000)

    k_match = re.search(r"(\d+(?:\.\d+)?)\s*k\b", normalized)
    if k_match:
        return int(float(k_match.group(1)) * 1000)

    patterns = [
        r"(?:rs|rupees|inr)\.?\s*(\d+(?:\.\d+)?)",
        r"(\d+(?:\.\d+)?)\s*(?:rs|rupees|inr)\b",
        r"(\d+(?:\.\d+)?)",
    ]
    for pattern in patterns:
        match = re.search(pattern, normalized)
        if match:
            value = float(match.group(1))
            if value > 0:
                return int(value)

    return None


def parse_amount(text: str) -> int | None:
    """Extract a rupee amount from natural language."""
    normalized = _normalize_money_text(text)

    lakh_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:lakh|lakhs|lac|lacs|l)\b", normalized)
    if lakh_match:
        return int(float(lakh_match.group(1)) * 100000)

    k_match = re.search(r"(\d+(?:\.\d+)?)\s*k\b", normalized)
    if k_match:
        return int(float(k_match.group(1)) * 1000)

    for pattern in [
        r"(?:for|worth|cost(?:s|ing)?|budget|price|at|of)\s*(?:rs\.?\s*)?(\d+(?:\.\d+)?)",
        r"(?:rs|rupees|inr)\.?\s*(\d+(?:\.\d+)?)",
        r"(\d+(?:\.\d+)?)\s*(?:rs|rupees|inr)\b",
        r"\b(\d{4,})\b",
    ]:
        match = re.search(pattern, normalized)
        if match:
            return int(float(match.group(1)))

    contextual = re.search(
        r"(?:for|worth|cost(?:s|ing)?|budget|price|at|of)\s*(?:rs\.?\s*)?(\d+(?:\.\d+)?)",
        normalized,
    )
    if contextual:
        return int(float(contextual.group(1)))

    return None


def detect_purchase_intent(text: str) -> dict | None:
    """Return purchase item label and amount if user expresses buy intent."""
    lower = text.lower()

    item_label = None
    for keyword, label in PURCHASE_ITEMS.items():
        if re.search(rf"\b{re.escape(keyword)}\b", lower):
            item_label = label
            break

    has_intent = (
        any(v in lower for v in PURCHASE_VERBS)
        or bool(re.search(r"\b(buy|purchase|afford|save\s+for)\b", lower))
        or bool(DESIRE_PATTERN.search(lower))
        or (item_label and bool(re.search(r"\b(want|need|wish|get|looking|planning|afford)\b", lower)))
    )
    if not has_intent:
        return None

    if not item_label:
        generic = re.search(
            r"(?:want|wanna|need|wish|buy|purchase|get|afford|save for|looking for)"
            r"(?:\s+to\s+(?:buy|get|purchase|own))?"
            r"\s+(?:a|an|the|my)?\s*(\w+)",
            lower,
        )
        if generic:
            item_label = generic.group(1).capitalize()
        else:
            item_label = "Item"

    amount = parse_amount(text)
    return {"item": item_label, "amount": amount, "raw_text": text}


def parse_monthly_salary(text: str, allow_bare_number: bool = True) -> int | None:
    """Extract monthly salary — accepts any positive amount."""
    normalized = _normalize_money_text(text)

    has_salary_context = any(
        w in normalized for w in [
            "salary", "earn", "income", "monthly", "per month", "/month",
            "take home", "ctc", "a month", "rs", "rupees", "inr",
        ]
    )

    if not has_salary_context and not allow_bare_number:
        return None

    if not has_salary_context and not re.search(r"\d", normalized):
        return None

    return parse_rupee_value(normalized)


def estimate_monthly_from_profile(user_data: dict) -> int | None:
    """Rough monthly estimate from annual income bracket."""
    income = (user_data.get("income") or "").lower()
    for bracket, annual in INCOME_BRACKET_MIDPOINTS.items():
        if bracket in income:
            return annual // 12
    return None


def get_explicit_monthly_salary(messages: list[dict], user_data: dict) -> int | None:
    """Only use salary the user explicitly stated — not income bracket estimates."""
    if user_data.get("monthly_salary"):
        return int(user_data["monthly_salary"])

    for msg in reversed(messages):
        if msg.get("role") == "user":
            salary = parse_monthly_salary(msg.get("text", ""))
            if salary:
                return salary

    return None


def resolve_pending_purchase(messages: list[dict]) -> dict | None:
    """Find purchase intent and merge budget from follow-up amount messages."""
    base = None
    amount = None
    for msg in messages:
        if msg.get("role") != "user":
            continue
        intent = detect_purchase_intent(msg.get("text", ""))
        if intent:
            base = intent
            if intent.get("amount"):
                amount = intent["amount"]
        elif base and not amount and is_amount_only_message(msg.get("text", "")):
            amount = parse_amount(msg.get("text", ""))

    if base:
        return {**base, "amount": amount or base.get("amount")}
    return None


def is_amount_only_message(text: str) -> bool:
    """True if the message looks like a bare budget answer."""
    lower = text.lower().strip()
    amount = parse_amount(text)
    if amount is None:
        return False
    words = re.sub(r"[\d₹,\.\s]+", " ", lower).split()
    filler = {"rs", "rupees", "inr", "for", "around", "about", "approx", "approximately", "budget", "is", "my"}
    return len([w for w in words if w and w not in filler]) <= 2


def is_salary_reply(text: str) -> bool:
    """True if message is a direct salary answer (any format)."""
    return parse_rupee_value(text) is not None


def format_currency(amount: int) -> str:
    return f"₹{amount:,}"


def _target_date(months: int) -> str:
    now = datetime.now()
    month = now.month + months
    year = now.year + (month - 1) // 12
    month = ((month - 1) % 12) + 1
    return datetime(year, month, 1).strftime("%B %Y")


def build_savings_plans(target_amount: int, monthly_salary: int) -> list[dict]:
    """
    Build three savings plans scaled to the user's actual salary.
    Each plan uses a different share of income — works for any amount.
    """
    monthly_salary = max(monthly_salary, 1)
    plan_templates = [
        ("Fast Track", 0.40, "Save more each month to finish sooner"),
        ("Balanced Plan", 0.25, "A steady pace that fits most budgets"),
        ("Comfortable Plan", 0.15, "Light on your wallet, still on track"),
    ]

    plans = []
    for title, rate, subtitle in plan_templates:
        monthly_savings = max(1, int(monthly_salary * rate))
        months = max(1, (target_amount + monthly_savings - 1) // monthly_savings)
        pct = round((monthly_savings / monthly_salary) * 100)
        feasible = rate <= 0.50
        plans.append({
            "title": title,
            "subtitle": subtitle,
            "months": months,
            "monthly_savings": monthly_savings,
            "salary_percent": pct,
            "target_date": _target_date(months),
            "feasible": feasible,
        })

    return plans


def format_plans_reply(
    first_name: str,
    item: str,
    target_amount: int,
    monthly_salary: int,
    plans: list[dict],
) -> str:
    lines = [
        f"Great choice, {first_name}! Let's plan your {item} purchase of {format_currency(target_amount)}.",
        f"Based on your monthly salary of {format_currency(monthly_salary)}, here are three ways to reach your goal:\n",
    ]

    for i, plan in enumerate(plans, 1):
        stretch = "" if plan.get("feasible", True) else " (stretched — consider a loan or higher income)"
        lines.append(
            f"Plan {i} — {plan['title']}\n"
            f"  • Save {format_currency(plan['monthly_savings'])}/month ({plan['salary_percent']}% of salary){stretch}\n"
            f"  • Timeline: {plan['months']} months\n"
            f"  • You'll be ready by {plan['target_date']}\n"
        )

    if any(not p.get("feasible", True) for p in plans):
        lines.append(
            "\nNote: Some plans exceed 50% of your salary. "
            "You may want to explore an SBI loan option or extend your timeline."
        )

    lines.append(
        "I've added this to your Goal Tracker on the right. "
        "Tell me which plan you'd like to follow, and I'll help you stay on track!"
    )
    return "\n".join(lines)


def format_salary_prompt(first_name: str, item: str, target_amount: int | None) -> str:
    amount_part = f" for {format_currency(target_amount)}" if target_amount else ""
    return (
        f"Absolutely, {first_name}! I'd love to help you plan your {item} purchase{amount_part}.\n\n"
        "To build a personalised savings plan, could you tell me your monthly salary "
        "(take-home pay after tax)?\n\n"
        "For example: ₹35,000 per month, 35000, or even 120rs — any amount works."
    )


def handle_purchase_planning(messages: list[dict], user_data: dict) -> dict | None:
    """
    Detect purchase intent and return a response dict, or None if not a purchase flow.
    Returns keys: reply, actions_logged, recommendations, goal_update, salary_update
    """
    last_msg = messages[-1]["text"]
    last_lower = last_msg.lower()
    first_name = _first_name(user_data.get("name", ""))

    salary_from_msg = parse_monthly_salary(last_msg)
    purchase_intent = detect_purchase_intent(last_msg)
    pending = resolve_pending_purchase(messages[:-1]) if len(messages) > 1 else None

    # User is answering with a budget amount for a pending purchase
    if not purchase_intent and pending and not pending.get("amount") and is_amount_only_message(last_msg):
        purchase_intent = {**pending, "amount": parse_amount(last_msg)}

    # User is answering salary for a pending purchase that already has a budget
    elif not purchase_intent and pending and pending.get("amount") and is_salary_reply(last_msg):
        salary = parse_monthly_salary(last_msg, allow_bare_number=True)
        if salary:
            purchase_intent = pending
            salary_from_msg = salary

    if not purchase_intent:
        return None

    item = purchase_intent["item"]
    target_amount = purchase_intent.get("amount")

    if not target_amount:
        return {
            "reply": (
                f"Got it, {first_name}! You want to buy a {item}.\n\n"
                f"What is your target budget for this {item}? "
                "For example: *₹10,000* or *85000*."
            ),
            "actions_logged": [
                "Detected purchase intent",
                f"Identified item: {item}",
                "Awaiting target amount",
            ],
            "recommendations": ["SBI Goal-Based Recurring Deposit", "SBI Flexi Deposit"],
            "goal_update": None,
            "salary_update": salary_from_msg,
        }

    monthly_salary = salary_from_msg or get_explicit_monthly_salary(messages, user_data)

    if not monthly_salary:
        return {
            "reply": format_salary_prompt(first_name, item, target_amount),
            "actions_logged": [
                "Detected purchase intent",
                f"Item: {item}, Target: {format_currency(target_amount)}",
                "Awaiting monthly salary for savings calculation",
            ],
            "recommendations": ["SBI Goal-Based Recurring Deposit", "SBI Flexi Deposit"],
            "goal_update": {
                "name": f"Purchase a {item}",
                "target_amount": target_amount,
                "status": "awaiting_salary",
                "progress": 0,
            },
            "salary_update": None,
        }

    plans = build_savings_plans(target_amount, monthly_salary)
    recommended = plans[1] if len(plans) > 1 else plans[0]

    goal_update = {
        "name": f"Purchase a {item}",
        "target_amount": target_amount,
        "monthly_salary": monthly_salary,
        "months": recommended["months"],
        "monthly_savings": recommended["monthly_savings"],
        "target_date": recommended["target_date"],
        "plans": plans,
        "status": "active",
        "progress": 0,
    }

    recs = ["SBI Goal-Based Recurring Deposit", "SBI Flexi Deposit"]
    if item.lower() in ("bike", "scooter", "motorcycle"):
        recs.insert(0, "SBI Two-Wheeler Loan")
    elif item.lower() == "car":
        recs.insert(0, "SBI Auto Loan")

    return {
        "reply": format_plans_reply(first_name, item, target_amount, monthly_salary, plans),
        "actions_logged": [
            "Extracted purchase goal",
            f"Target: {format_currency(target_amount)}",
            f"Monthly salary: {format_currency(monthly_salary)}",
            "Generated 3 savings plan options",
        ],
        "recommendations": recs,
        "goal_update": goal_update,
        "salary_update": monthly_salary,
    }
