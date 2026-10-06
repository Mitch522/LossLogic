import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC = PROJECT_ROOT / "src"

if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from causation_evaluator import evaluate_causation


def test_expected_causation_classifications():
    results = evaluate_causation()

    expected = {
        "MED-001": "RELATED_NEW",
        "MED-002": "AGGRAVATION",
        "MED-003": "PREEXISTING",
        "MED-004": "DEGENERATIVE",
        "MED-005": "UNRELATED",
    }

    actual = {
        diagnosis_id: result["classification"]
        for diagnosis_id, result in results.items()
    }

    assert actual == expected


if __name__ == "__main__":
    test_expected_causation_classifications()
    print("PASS: All causation classifications are correct.")
