import json
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
BILLING_DATA = PROJECT_ROOT / "data" / "billing"


def load_json(filename: str) -> dict[str, Any]:
    with open(BILLING_DATA / filename, "r", encoding="utf-8") as file:
        return json.load(file)


def reconcile_billing() -> dict[str, Any]:
    bills = load_json("medical_bills.json")["billing_records"]
    schedule = load_json("reimbursement_schedule.json")
    pip_data = load_json("pip_payments.json")

    rates = schedule["rates"]
    payments = pip_data["payments"]

    payments_by_bill = {}
    for payment in payments:
        bill_id = payment["bill_id"]
        payments_by_bill[bill_id] = (
            payments_by_bill.get(bill_id, 0.0)
            + payment["paid_amount"]
        )

    reconciled_bills = []

    total_submitted_charges = 0.0
    total_active_charges = 0.0
    total_allowed = 0.0
    total_pip_paid = 0.0
    total_remaining_specials = 0.0

    excluded_voided = 0.0
    excluded_duplicates = 0.0
    excluded_bundled = 0.0

    for bill in bills:
        billed_amount = bill["billed_amount"]
        total_submitted_charges += billed_amount

        status = bill["status"]
        procedure_code = bill["procedure_code"]

        entry = {
            "bill_id": bill["bill_id"],
            "provider": bill["provider"],
            "date_of_service": bill["date_of_service"],
            "procedure_code": procedure_code,
            "billed_amount": billed_amount,
            "status": status,
        }

        if status == "VOIDED":
            excluded_voided += billed_amount
            entry.update({
                "included_in_evaluation": False,
                "exclusion_reason": "Voided charge replaced by corrected billing.",
                "allowed_amount": 0.0,
                "pip_paid": 0.0,
                "remaining_specials": 0.0,
            })
            reconciled_bills.append(entry)
            continue

        if status == "DUPLICATE":
            excluded_duplicates += billed_amount
            entry.update({
                "included_in_evaluation": False,
                "exclusion_reason": "Duplicate charge.",
                "allowed_amount": 0.0,
                "pip_paid": 0.0,
                "remaining_specials": 0.0,
            })
            reconciled_bills.append(entry)
            continue

        total_active_charges += billed_amount

        rate = rates.get(procedure_code)

        if rate is None:
            entry.update({
                "included_in_evaluation": False,
                "exclusion_reason": "No reimbursement rule available.",
                "allowed_amount": None,
                "pip_paid": payments_by_bill.get(bill["bill_id"], 0.0),
                "remaining_specials": None,
            })
            reconciled_bills.append(entry)
            continue

        if not rate["separately_reimbursable"]:
            excluded_bundled += billed_amount
            entry.update({
                "included_in_evaluation": False,
                "exclusion_reason": rate.get(
                    "reason",
                    "Service is not separately reimbursable."
                ),
                "allowed_amount": 0.0,
                "pip_paid": 0.0,
                "remaining_specials": 0.0,
            })
            reconciled_bills.append(entry)
            continue

        allowed_amount = min(
            billed_amount,
            rate["allowed_amount"]
        )

        pip_paid = payments_by_bill.get(bill["bill_id"], 0.0)

        remaining_specials = max(
            allowed_amount - pip_paid,
            0.0
        )

        total_allowed += allowed_amount
        total_pip_paid += pip_paid
        total_remaining_specials += remaining_specials

        entry.update({
            "included_in_evaluation": True,
            "allowed_amount": round(allowed_amount, 2),
            "pip_paid": round(pip_paid, 2),
            "remaining_specials": round(remaining_specials, 2),
        })

        reconciled_bills.append(entry)

    validation_issues = []

    known_bill_ids = {bill["bill_id"] for bill in bills}

    for payment in payments:
        if payment["bill_id"] not in known_bill_ids:
            validation_issues.append(
                f"{payment['payment_id']} references unknown bill "
                f"{payment['bill_id']}."
            )

    for entry in reconciled_bills:
        pip_paid = payments_by_bill.get(entry["bill_id"], 0.0)

        if not entry["included_in_evaluation"] and pip_paid > 0:
            validation_issues.append(
                f"{entry['bill_id']} is excluded from evaluation but has "
                f"${pip_paid:.2f} in PIP payments."
            )

        allowed = entry["allowed_amount"]
        if (
            entry["included_in_evaluation"]
            and allowed is not None
            and pip_paid > allowed
        ):
            validation_issues.append(
                f"{entry['bill_id']} has PIP payments exceeding its "
                f"allowed amount."
            )

    pip_limit = pip_data["pip_policy"]["limit"]

    if total_pip_paid > pip_limit:
        validation_issues.append(
            "Total PIP payments exceed the policy limit."
        )

    return {
        "reconciled_bills": reconciled_bills,
        "validation": {
            "passed": not validation_issues,
            "issues": validation_issues,
        },
        "summary": {
            "total_submitted_charges": round(total_submitted_charges, 2),
            "excluded_voided_charges": round(excluded_voided, 2),
            "excluded_duplicate_charges": round(excluded_duplicates, 2),
            "active_charges_before_bundling": round(total_active_charges, 2),
            "excluded_bundled_charges": round(excluded_bundled, 2),
            "total_allowed_medical_expenses": round(total_allowed, 2),
            "total_pip_paid": round(total_pip_paid, 2),
            "remaining_allowable_medical_specials": round(
                total_remaining_specials, 2
            ),
            "pip_limit": round(pip_limit, 2),
            "pip_limit_remaining": round(
                max(pip_limit - total_pip_paid, 0.0), 2
            ),
        }
    }


if __name__ == "__main__":
    print(json.dumps(reconcile_billing(), indent=2))
