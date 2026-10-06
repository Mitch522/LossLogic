import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC = PROJECT_ROOT / "src"

if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from liability_evaluator import evaluate_liability


def test_expected_liability_assessment():
    result = evaluate_liability()
    assessment = result["assessment"]

    assert assessment["insured_liability_percent"] == 80
    assert assessment["claimant_comparative_negligence_percent"] == 20
    assert assessment["confidence"] == "MODERATE_HIGH"
    assert assessment["assessment_type"] == "professional_judgment"

    assert len(result["primary_contributing_conduct"]) > 0
    assert len(result["comparative_contributing_conduct"]) > 0
    assert len(result["material_evidence"]) > 0
    assert len(result["evidence_limitations"]) > 0

    assert (
        assessment["insured_liability_percent"]
        + assessment["claimant_comparative_negligence_percent"]
        == 100
    )


if __name__ == "__main__":
    test_expected_liability_assessment()
    print("PASS: Liability evaluation is correct.")
