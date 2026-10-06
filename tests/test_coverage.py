import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC = PROJECT_ROOT / "src"

if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from coverage_evaluator import evaluate_coverage


def test_bodily_injury_coverage_applies():
    result = evaluate_coverage()

    assert result["coverage_applies"] is True
    assert result["failed_requirements"] == []
    assert result["limits"]["per_person"] == 100000
    assert result["limits"]["per_accident"] == 300000

    assert all(result["requirements"].values())


if __name__ == "__main__":
    test_bodily_injury_coverage_applies()
    print("PASS: Coverage evaluation is correct.")
