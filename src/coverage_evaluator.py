import json
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
COVERAGE_DATA = PROJECT_ROOT / "data" / "coverage"


def load_json(filename: str) -> dict[str, Any]:
    with open(COVERAGE_DATA / filename, "r", encoding="utf-8") as file:
        return json.load(file)


def evaluate_coverage() -> dict[str, Any]:
    claim = load_json("claim.json")
    policy = load_json("policy.json")

    facts = policy["facts"]
    bi = policy["bodily_injury_liability"]

    requirements = {
        "policy_active": policy["policy_status_on_loss_date"] == "ACTIVE",
        "loss_within_policy_period": facts["loss_within_policy_period"],
        "covered_vehicle_involved": facts["covered_vehicle_involved"],
        "permissive_driver": facts["insured_was_permissive_driver"],
        "bodily_injury_coverage_included": bi["included"],
        "no_known_exclusion": not facts["known_exclusion_applies"],
    }

    failed_requirements = [
        requirement
        for requirement, satisfied in requirements.items()
        if not satisfied
    ]

    coverage_applies = not failed_requirements

    if coverage_applies:
        conclusion = (
            "Bodily injury liability coverage applies based on the available "
            "policy and loss facts."
        )
    else:
        conclusion = (
            "Bodily injury liability coverage is not established because one "
            "or more coverage requirements are not satisfied."
        )

    return {
        "claim_id": claim["claim_id"],
        "policy_id": policy["policy_id"],
        "coverage_type": "bodily_injury_liability",
        "coverage_applies": coverage_applies,
        "requirements": requirements,
        "failed_requirements": failed_requirements,
        "limits": {
            "per_person": bi["per_person_limit"],
            "per_accident": bi["per_accident_limit"],
        },
        "coverage_issues": policy["coverage_issues"],
        "conclusion": conclusion,
    }


if __name__ == "__main__":
    print(json.dumps(evaluate_coverage(), indent=2))
