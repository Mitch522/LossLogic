import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC = PROJECT_ROOT / "src"

if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from claim_evaluator import evaluate_claim


def test_complete_claim_evaluation():
    result = evaluate_claim()
    summary = result["claim_summary"]

    # Claim identity
    assert result["claim"]["claim_id"] == "CLM-DEMO-2026-001"
    assert result["claim"]["claim_type"] == "AUTO_BODILY_INJURY"
    assert result["claim"]["jurisdiction"] == "Florida"

    # Demonstration safeguards
    assert result["evaluation_metadata"]["system"] == "LossLogic"
    assert result["evaluation_metadata"]["synthetic_data"] is True

    # Coverage
    assert summary["coverage_applies"] is True
    assert summary["per_person_bi_limit"] == 100000

    # Liability
    assert summary["insured_liability_percent"] == 80
    assert summary["claimant_comparative_negligence_percent"] == 20

    # Medical causation
    assert summary["related_diagnosis_ids"] == [
        "MED-001",
        "MED-002",
    ]

    assert summary["non_related_diagnosis_ids"] == [
        "MED-003",
        "MED-004",
        "MED-005",
    ]

    # Financials
    assert summary["allowed_medical_expenses"] == 2425.00
    assert summary["pip_paid"] == 1940.00
    assert summary["remaining_allowable_medical_specials"] == 485.00

    # Causation-aware BI damages
    assert summary["accident_related_allowed_medical_expenses"] == 2075.00
    assert summary["accident_related_pip_paid"] == 1660.00
    assert summary["accident_related_remaining_medical_specials"] == 415.00

    bi_bills = {
        bill["bill_id"]: bill
        for bill in result["bi_damages"]["bills"]
    }

    assert bi_bills["BILL-005"]["accident_related"] is True
    assert bi_bills["BILL-005"]["related_diagnosis_ids"] == ["MED-002"]

    assert bi_bills["BILL-009"]["included_in_evaluation"] is True
    assert bi_bills["BILL-009"]["allowed_amount"] == 350.00
    assert bi_bills["BILL-009"]["accident_related"] is False
    assert bi_bills["BILL-009"]["related_diagnosis_ids"] == []

    # Validation / review
    assert result["financials"]["validation"]["passed"] is True
    assert summary["requires_additional_review"] is False
    assert summary["review_flags"] == []


if __name__ == "__main__":
    test_complete_claim_evaluation()
    print("PASS: Complete LossLogic evaluation is correct.")
