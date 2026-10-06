import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from billing_reconciliation import reconcile_billing
from causation_evaluator import evaluate_causation
from coverage_evaluator import evaluate_coverage
from liability_evaluator import evaluate_liability


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CLAIM_FILE = PROJECT_ROOT / "data" / "coverage" / "claim.json"


def load_claim() -> dict[str, Any]:
    with open(CLAIM_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def evaluate_claim() -> dict[str, Any]:
    claim = load_claim()

    coverage = evaluate_coverage()
    liability = evaluate_liability()
    medical_causation = evaluate_causation()
    billing = reconcile_billing()

    related_diagnoses = [
        diagnosis_id
        for diagnosis_id, result in medical_causation.items()
        if result["classification"] in {"RELATED_NEW", "AGGRAVATION"}
    ]

    non_related_diagnoses = [
        diagnosis_id
        for diagnosis_id, result in medical_causation.items()
        if result["classification"]
        in {"PREEXISTING", "DEGENERATIVE", "UNRELATED"}
    ]

    related_classifications = {"RELATED_NEW", "AGGRAVATION"}

    bi_medical_bills = []
    accident_related_allowed = 0.0
    accident_related_pip_paid = 0.0
    accident_related_remaining_specials = 0.0

    for bill in billing["reconciled_bills"]:
        diagnosis_ids = bill.get("diagnosis_ids", [])

        related_diagnosis_ids = [
            diagnosis_id
            for diagnosis_id in diagnosis_ids
            if (
                diagnosis_id in medical_causation
                and medical_causation[diagnosis_id]["classification"]
                in related_classifications
            )
        ]

        accident_related = bool(related_diagnosis_ids)

        bi_bill = dict(bill)
        bi_bill["accident_related"] = accident_related
        bi_bill["related_diagnosis_ids"] = related_diagnosis_ids

        if bill["included_in_evaluation"] and accident_related:
            allowed = bill["allowed_amount"] or 0.0
            pip_paid = bill["pip_paid"] or 0.0
            remaining = bill["remaining_specials"] or 0.0

            accident_related_allowed += allowed
            accident_related_pip_paid += pip_paid
            accident_related_remaining_specials += remaining

        bi_medical_bills.append(bi_bill)

    bi_damages = {
        "bills": bi_medical_bills,
        "summary": {
            "accident_related_allowed_medical_expenses": round(
                accident_related_allowed, 2
            ),
            "accident_related_pip_paid": round(
                accident_related_pip_paid, 2
            ),
            "accident_related_remaining_medical_specials": round(
                accident_related_remaining_specials, 2
            ),
        },
    }

    review_flags = []

    if not coverage["coverage_applies"]:
        review_flags.append("Coverage is not established.")

    if not billing["validation"]["passed"]:
        review_flags.append(
            "Billing reconciliation contains validation issues."
        )

    if liability["assessment"]["confidence"] == "INSUFFICIENT":
        review_flags.append(
            "Liability requires additional professional review."
        )

    undetermined_diagnoses = [
        diagnosis_id
        for diagnosis_id, result in medical_causation.items()
        if result["classification"] == "UNDETERMINED"
    ]

    if undetermined_diagnoses:
        review_flags.append(
            "One or more medical conditions require additional "
            "causation review."
        )

    return {
        "claim": {
            "claim_id": claim["claim_id"],
            "claim_type": claim["claim_type"],
            "jurisdiction": claim["jurisdiction"],
            "loss_date": claim["loss_date"],
            "loss_location": claim["loss_location"],
        },
        "evaluation_metadata": {
            "system": "LossLogic",
            "evaluation_type": "demonstration",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "synthetic_data": True,
        },
        "coverage": coverage,
        "liability": liability,
        "medical_causation": medical_causation,
        "financials": billing,
        "bi_damages": bi_damages,
        "claim_summary": {
            "coverage_applies": coverage["coverage_applies"],
            "per_person_bi_limit": coverage["limits"]["per_person"],
            "insured_liability_percent": (
                liability["assessment"]["insured_liability_percent"]
            ),
            "claimant_comparative_negligence_percent": (
                liability["assessment"][
                    "claimant_comparative_negligence_percent"
                ]
            ),
            "related_diagnosis_ids": related_diagnoses,
            "non_related_diagnosis_ids": non_related_diagnoses,
            "allowed_medical_expenses": billing["summary"][
                "total_allowed_medical_expenses"
            ],
            "pip_paid": billing["summary"]["total_pip_paid"],
            "remaining_allowable_medical_specials": billing["summary"][
                "remaining_allowable_medical_specials"
            ],
            "accident_related_allowed_medical_expenses": bi_damages[
                "summary"
            ]["accident_related_allowed_medical_expenses"],
            "accident_related_pip_paid": bi_damages["summary"][
                "accident_related_pip_paid"
            ],
            "accident_related_remaining_medical_specials": bi_damages[
                "summary"
            ]["accident_related_remaining_medical_specials"],
            "requires_additional_review": bool(review_flags),
            "review_flags": review_flags,
        },
    }


if __name__ == "__main__":
    print(json.dumps(evaluate_claim(), indent=2))
