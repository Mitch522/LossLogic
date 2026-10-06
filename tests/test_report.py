from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from report_generator import generate_report


def test_report():
    report = generate_report()

    # Synthetic-data safeguard
    assert "entirely fictional, synthetic claim data" in report

    # Core claim conclusions
    assert "**Coverage:** Applies" in report
    assert "**Liability:** 80% insured / 20% claimant" in report

    # Causation-supported financial analysis
    assert "**Financially Allowed Medical Expenses:** $2,425.00" in report
    assert "**Causation-Supported BI Medical Expenses:** $2,075.00" in report
    assert "**Remaining Causation-Supported Medical Specials:** $415.00" in report

    # Natural-language causation output
    assert "1 day after the loss" in report
    assert "day(s)" not in report

    # Causation exclusion explainability
    assert "BILL-009" in report
    assert "Chronic Rotator Cuff Tendinopathy: Pre-Existing" in report
    assert "Osteoarthritis: Degenerative" in report

    # Review status
    assert "No automated validation or review flags were identified" in report

    print("PASS: ClaimIQ report is correct.")


if __name__ == "__main__":
    test_report()
