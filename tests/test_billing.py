import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC = PROJECT_ROOT / "src"

if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from billing_reconciliation import reconcile_billing


def test_expected_billing_reconciliation():
    result = reconcile_billing()
    summary = result["summary"]

    assert result["validation"]["passed"] is True
    assert result["validation"]["issues"] == []

    assert summary["total_submitted_charges"] == 6115.00
    assert summary["excluded_voided_charges"] == 1850.00
    assert summary["excluded_duplicate_charges"] == 210.00
    assert summary["active_charges_before_bundling"] == 4055.00
    assert summary["excluded_bundled_charges"] == 75.00

    assert summary["total_allowed_medical_expenses"] == 2425.00
    assert summary["total_pip_paid"] == 1940.00
    assert summary["remaining_allowable_medical_specials"] == 485.00

    assert summary["pip_limit"] == 10000.00
    assert summary["pip_limit_remaining"] == 8060.00

    bills = {
        bill["bill_id"]: bill
        for bill in result["reconciled_bills"]
    }

    assert bills["BILL-004"]["included_in_evaluation"] is False
    assert bills["BILL-007"]["included_in_evaluation"] is False
    assert bills["BILL-008"]["included_in_evaluation"] is False

    assert bills["BILL-005"]["allowed_amount"] == 900.00
    assert bills["BILL-005"]["remaining_specials"] == 180.00


if __name__ == "__main__":
    test_expected_billing_reconciliation()
    print("PASS: Billing reconciliation is correct.")
