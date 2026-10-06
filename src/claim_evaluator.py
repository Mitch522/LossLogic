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
            "system": "ClaimIQ",
            "evaluation_type": "demonstration",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "synthetic_data": True,
        },
        "coverage": coverage,
        "liability": liability,
        "medical_causation": medical_causation,
        "financials": billing,
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
            "requires_additional_review": bool(review_flags),
            "review_flags": review_flags,
        },
    }


if __name__ == "__main__":
    print(json.dumps(evaluate_claim(), indent=2))
